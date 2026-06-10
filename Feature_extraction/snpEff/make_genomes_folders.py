#在`snpEff/data`下构建所需文件夹
import os
from config_add import get_file_names_without_extension

folder_path = "/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/core_gene_sequences_with_ref/"

file_names = get_file_names_without_extension(folder_path)

write_folder = "/data/home/sfwang/software/snpEff/data/" 
for f in file_names:
    gene_name=(f.split('.'))[0]
    os.makedirs(write_folder+gene_name,exist_ok=True)
