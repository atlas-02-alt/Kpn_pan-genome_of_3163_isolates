import os
import json

def replace_contig_name(folder_path, output_file, name_dict):
    with open(output_file, 'w') as outfile:
        # 遍历文件夹中的所有文件
        for filename in os.listdir(folder_path):
            if filename.endswith('.fa'):
                file_path = os.path.join(folder_path, filename)
                # 去掉文件名的后缀 (如 .fa)
                contig_name = filename.replace('.fa', '')
                
                # 使用字典进行第二次替换
                for key, value in name_dict.items():
                    if key==contig_name:
                        contig_name = value
                        break
                
                with open(file_path, 'r') as infile:
                    # 读取文件内容
                    lines = infile.readlines()

                    # 处理FASTA文件的第一行contig名称替换
                    if lines[0].startswith('>'):
                        # 替换contig名字
                        lines[0] = f'>{contig_name}\n'
                    
                    # 写入更新后的内容
                    outfile.write(''.join(lines))  # 写入 contig 名字和 DNA 序列

def read_json_file(json_file_path):
    with open(json_file_path, 'r') as json_file:
        return json.load(json_file)

folder_path = "/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/core_gene_references/"  # 文件夹路径
output_file = "/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/all_core_align_references.fasta"  # 合并后的fasta文件
json_dict = read_json_file("/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/amr_panaroo_dict.json")

replace_contig_name(folder_path, output_file, json_dict)

###把所有的fasta文件合并成一个fasta文件