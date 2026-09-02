import os

def count_genes_in_gff(gff_file):
    count = 0
    with open(gff_file, 'r') as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
            feature_type = parts[2]
            # Count CDS entries here; modify as needed
            if feature_type == "CDS":
                count += 1
    return count

def main(input_dir, output_file):
    gene_counts = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".gff"):
            filepath = os.path.join(input_dir, filename)
            sample_id = os.path.splitext(filename)[0]
            count = count_genes_in_gff(filepath)
            gene_counts.append((sample_id, count))

    # Sort by gene count in descending order
    gene_counts.sort(key=lambda x: x[1], reverse=True)

    # Write the output file
    with open(output_file, 'w') as out_f:
        for sample_id, count in gene_counts:
            out_f.write(f"{sample_id} {count}\n")

    print(f"Counting complete; results written to {output_file}")

if __name__ == "__main__":
    # You can modify the path below
    input_directory = "./GFFs/"  # Directory containing GFF files
    output_txt = "./sample_gene_counts.txt"
    main(input_directory, output_txt)