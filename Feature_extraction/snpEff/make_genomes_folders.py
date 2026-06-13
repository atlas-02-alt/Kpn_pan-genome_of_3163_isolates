#Create required folders under `snpEff/data`
import os
from add_configure import get_file_names_without_extension

folder_path = "./both-align-results-strict-adv/core_gene_sequences_with_ref/"

file_names = get_file_names_without_extension(folder_path)

write_folder = "./snpEff/data/"
for f in file_names:
    gene_name=(f.split('.'))[0]
    os.makedirs(write_folder+gene_name,exist_ok=True)
