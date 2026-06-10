###根据选择出来的特征，组装新特征集对应的特征矩阵
import os
import list2fm as lf
import pandas as pd

# 读表型矩阵

pheno_path="/data/home/sfwang/kpn/PATRIC_data/Drug_phenotypes.csv"
phenos=pd.read_csv(pheno_path,index_col=0)
'''
phenos=pd.read_csv("/data/home/sfwang/kpn/Origin_data/Kpn_antibiotics_AST_phenotypes.csv",index_col=0)
'''

# 循环读取每个药物的特征列表，从dis_fm中抽取对应特征列，结合label组装训练矩阵
feature_folder_path="/data/home/sfwang/kpn/Panaroo-DownStream-patric/feature_set_determine/5f_avgauc_train/result/"
folder_list = [f for f in os.listdir(feature_folder_path)] # 安徽医院样本的药物列表
#folder_list = ['ETP'] # 只跑ETP

for f in folder_list:

    # 读原始大特征矩阵(100%样本)
    #whole_core_fm=pd.read_csv('/data/home/sfwang/kpn/Core/filted_whole_fm.csv',index_col=0)
    #whole_dis_fm=pd.read_csv('/data/home/sfwang/kpn/Dispensable/filted_whole_fm.csv',index_col=0)

    # 读f药对应的core和dispensable两个特征矩阵(30%样本/70%样本)
    dataset="train"
    whole_fm_path=f"/data/home/sfwang/kpn/Panaroo-DownStream-patric/ml_sort/result/{f}/"
    whole_core_fm=pd.read_csv(whole_fm_path+'core_'+dataset+'_set.csv',index_col=0)
    whole_dis_fm=pd.read_csv(whole_fm_path+'dis_'+dataset+'_set.csv',index_col=0)

    core_list=[]
    dis_list=[]
    # 读特征文件
    with open(f'/data/home/sfwang/kpn/Panaroo-DownStream-patric/feature_set_determine/5f_avgauc_train/result/{f}/feature_select_result.txt','r') as file:
        for row in file:
            if 'pvalue' in row:
                row_info=row.split(',')
                gene=row_info[0]
                if '->' not in row: 
                    dis_list.append(gene) # 非核心基因列表
                else:
                    core_list.append(gene) # 核心变异列表
    core_fm = whole_core_fm[core_list].copy()
    dispensable_fm = whole_dis_fm[dis_list].copy()
    total_fm = pd.concat([core_fm, dispensable_fm], axis=1) # 合并
    total_fm['label'] = phenos[f].reindex(total_fm.index)
    total_fm = total_fm[total_fm['label'].isin(['R', 'S'])]
    total_fm['label'] = total_fm['label'].replace({'R': 1, 'S': 0})

    total_fm.to_csv(f"/data/home/sfwang/kpn/Panaroo-DownStream-patric/feature_set_determine/5f_avgauc_train/result_{dataset}_matrix/{f}.csv")