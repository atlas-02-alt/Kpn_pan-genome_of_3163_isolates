import pandas as pd
import os
from collections import Counter
from upsetplot import from_indicators, UpSet
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.family'] = 'Arial'

model_list=['rf','lr','svm','xgb']
med_list = ['CZO','FOX','CXM','CAZ','ETP','IPM','MEM','SAM','TZP','GEN','AMK','TOB','TCY','CIP','LVX','NIT','SXT']

target_dir = "/data/home/sfwang/kpn/Panaroo-DownStream-both/feature_set_determine/5f_avgauc_train/result/"
folder_list = [f for f in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, f))]
dis_feature_list=[]
core_feature_list=[]
for f in med_list:
    with open(f'{target_dir}{f}/feature_select_result.txt','r') as file:
        for row in file:
            if 'pvalue' in row:
                if '->' in row:
                    row_info=row.split(',')
                    gene_f=row_info[0]
                    if gene_f not in core_feature_list:
                        core_feature_list.append(gene_f)
                else:
                    row_info=row.split(',')
                    gene=row_info[0]
                    if gene not in dis_feature_list:
                        dis_feature_list.append(gene)

pass_model=pd.DataFrame(index=dis_feature_list+core_feature_list,columns=model_list)
pass_model = pass_model.fillna(0)
print(pass_model)
print(pass_model.shape)

folder_path='/data/home/sfwang/kpn/Panaroo-DownStream-both/ml_sort/'
thr_list=[100,100,100,100,100,100,60,100,35,100,50,100,100,50,100,100,100]
for i in range(0,17,1):
    med=med_list[i]
    threshold=thr_list[i]
    dfc_xgb=pd.read_csv(f"{folder_path}{med}/core_xgb_importance.csv")
    dfc_lr=pd.read_csv(f"{folder_path}{med}/core_lr_importance.csv")
    dfc_svm=pd.read_csv(f"{folder_path}{med}/core_svm_importance.csv")
    dfc_rf=pd.read_csv(f"{folder_path}{med}/core_rf_importance.csv")
    dfd_xgb=pd.read_csv(f"{folder_path}{med}/dis_xgb_importance.csv")
    dfd_lr=pd.read_csv(f"{folder_path}{med}/dis_lr_importance.csv")
    dfd_svm=pd.read_csv(f"{folder_path}{med}/dis_svm_importance.csv")
    dfd_rf=pd.read_csv(f"{folder_path}{med}/dis_rf_importance.csv")
    for index, row in pass_model.iterrows():
        if '->' in index:
            #核心基因
            if dfc_xgb[dfc_xgb['Feature'] == index].index[0]<threshold:
                pass_model.loc[index, 'xgb']=1
            if dfc_lr[dfc_lr['Feature'] == index].index[0]<threshold:
                pass_model.loc[index, 'lr']=1 
            if dfc_svm[dfc_svm['Feature'] == index].index[0]<threshold:
                pass_model.loc[index, 'svm']=1 
            if dfc_rf[dfc_rf['Feature'] == index].index[0]<threshold:
                pass_model.loc[index, 'rf']=1 
        else:
            #非核心基因
            if dfd_xgb[dfd_xgb['Feature'] == index].index[0]<threshold:
                pass_model.loc[index, 'xgb']=1
            if dfd_lr[dfd_lr['Feature'] == index].index[0]<threshold:
                pass_model.loc[index, 'lr']=1 
            if dfd_svm[dfd_svm['Feature'] == index].index[0]<threshold:
                pass_model.loc[index, 'svm']=1 
            if dfd_rf[dfd_rf['Feature'] == index].index[0]<threshold:
                pass_model.loc[index, 'rf']=1 

pass_model.to_csv("./model_evidence_support_summary.csv")

sets = {}
for col in pass_model.columns:
    sets[col] = set(pass_model.index[pass_model[col] == 1])
# 计算每种集合组合出现的次数
comb_counter = Counter()
for idx, row in pass_model.iterrows():
    key = ''.join(str(int(b)) for b in row)  # e.g., '1011'
    comb_counter[key] += 1
# 用于 upsetplot：从0/1矩阵构造多集合关系
df_bool = pass_model.astype(bool)
data = from_indicators(df_bool.columns.tolist(), df_bool)
upset = UpSet(data, subset_size='count',show_counts=True)
upset.plot()
plt.show()
#plt.savefig('./fig3b.pdf')