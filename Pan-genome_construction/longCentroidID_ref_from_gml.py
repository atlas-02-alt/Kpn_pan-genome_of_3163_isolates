import networkx as nx
import csv
import ast

gml_file = "./both-align-results-strict-adv/final_graph.gml"
out_file = "./both-align-results-strict-adv/cluster_centroid_summary.tsv"

'''
# 读取 GML（networkx 是按需加载节点属性的，不会一次性 print）
G = nx.read_gml(gml_file)

with open(out_file, "w") as f:
    f.write("cluster\tlongCentroidID\tcentroid\n")

    for node, data in G.nodes(data=True):
        cluster_name = data.get("name", node)

        long_centroid = data.get("longCentroidID", "NA")
        centroid = data.get("centroid", "NA")

        # 处理 centroid 是 list / set 的情况
        if isinstance(centroid, (list, set, tuple)):
            centroid = ";".join(map(str, centroid))

        f.write(f"{cluster_name}\t{long_centroid}\t{centroid}\n")
'''

csv_file = "./both-align-results-strict-adv/gene_data.csv"
out_fasta = "./both-align-results-strict-adv/complete_pan_genome_reference.fasta"
tsv_file = out_file

# --------------------------------------------------
# 1. 读取 clusters.tsv
#    提取：cluster_name -> clustering_id
# --------------------------------------------------
cluster_to_cid = {}

with open(tsv_file) as f:
    next(f)  # skip header
    for line in f:
        fields = line.rstrip("\n").split("\t")
        cluster = fields[0].strip()
        long_centroid_raw = fields[1].strip()

        try:
            # 把字符串 "[300, '0_1_9']" 解析成 Python list
            parsed = ast.literal_eval(long_centroid_raw)

            # 约定：第二个元素是真正的 clustering_id
            cid = str(parsed[1]).strip()

            cluster_to_cid[cluster] = cid

        except Exception as e:
            # 如果解析失败，直接跳过（也可以 raise）
            continue

print(f"[INFO] clusters parsed: {len(cluster_to_cid)}")

# --------------------------------------------------
# 2. 读取 sequences.csv
#    建立：clustering_id -> dna_sequence
# --------------------------------------------------
seq_dict = {}

with open(csv_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        cid = row["clustering_id"].strip()
        dna = row["dna_sequence"].strip()

        # 如果一个 clustering_id 出现多次，这里保留第一次
        if cid not in seq_dict:
            seq_dict[cid] = dna

print(f"[INFO] unique clustering_id in CSV: {len(seq_dict)}")

# --------------------------------------------------
# 3. 写 FASTA：每个 cluster 一条序列
# --------------------------------------------------
written = 0
with open(out_fasta, "w") as out:
    for cluster, cid in cluster_to_cid.items():
        seq = seq_dict.get(cid)
        if seq:
            out.write(f">{cluster}\n{seq}\n")
            written += 1

print(f"[INFO] FASTA written: {written}")