import os

def get_file_names_without_extension(folder_path):
    file_names = []
    # 遍历文件夹下的所有文件
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 分离文件名和后缀
            name, _ = os.path.splitext(file)
            file_names.append(name)
    return file_names

if __name__=='__main__':
    folder_path = "/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/core_gene_references/"
    file_names = get_file_names_without_extension(folder_path) # 获取不带后缀的文件名列表（所有基因名列表）
    print(len(file_names))

    snp_configure_path="/data/home/sfwang/software/snpEff/snpEff.config"
    with open(snp_configure_path,'a') as wfile:
        for gene in file_names:
            wfile.write('\n'+gene+'.genome : '+gene)
            wfile.write('\n'+gene+'.reference : /data/home/sfwang/software/snpEff/data/genomes/')
            wfile.write('\n'+gene+'.retrieval_date : 2025.10.05')
            wfile.write('\n')
