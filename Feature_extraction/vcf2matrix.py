import pandas as pd
import os
import numpy as np
import json

pheno_csvpath="/data/home/sfwang/kpn/Panaroo-DownStream-both/phenotypes.csv"
phenos=pd.read_csv(pheno_csvpath,index_col=0)
GN_list=phenos.index.tolist()

def vcf_process(vcf_path):
    # 读取snpEff注释后的、由samtools和bcf合成的.vcf文件
    # ①去除文件头，剩下部分转为dataframe格式
    # ②对df的列名进行修正，去除多余数据
    # ③删除所有同义替换行

    # 模块①+③
    df = pd.DataFrame()
    with open(vcf_path,'r') as vcf_file:
        for row in vcf_file:
            if row[0:2]!='##': #去除文件头
                row=(row.rstrip('\n'))
                new_line=row.split('	') #读入该行信息
                if row[0]=="#": #获取列名
                    df=pd.DataFrame(columns=new_line)
                else: #获取dataframe内容
                    # 如果不是同义替换，则将该行数据加入dataframe
                    if 'synonymous_variant' not in row:
                        df.loc[len(df)] = new_line

    # 模块②
    # 1.删除多余列
    df=df.drop(['ID','QUAL','FILTER','INFO','FORMAT'],axis=1)
    # 2.处理列名
    column_array=df.columns.tolist()
    for i in range(0,len(column_array)):
        if '.fa.bam' in column_array[i]:
            column_array[i]=column_array[i].split('/')[2].split('.')[0]
    df.columns=column_array

    return df

def feature_matrix(vcf):
    # 若没有剩下任何变异（即 DataFrame 没有行），直接返回空 DataFrame
    if vcf.empty:
        return pd.DataFrame(columns=vcf.columns)

    # 定义转换函数
    def transform(value):
        return 0 if value == '.:.' or value == '0:60,.' else 1

    # 安全使用 vectorize 并指定输出类型
    vfunc = np.vectorize(transform, otypes=[int])
    vcf.iloc[:, 4:] = vfunc(vcf.iloc[:, 4:].values)

    return vcf

def transform(fm):

    ### 命名各变异，并合并同样本的特征
    # 确定本次训练使用的基因，读取对应特征矩阵

    fm_index=[]
    for index, row in fm.iterrows():
        ind=str(row["POS"])+'_'+row["REF"]+'->'+row["ALT"]
        fm_index.append(ind)
    fm.index=fm_index
    fm=fm.drop(['#CHROM','POS','REF','ALT'],axis=1)
    fm=fm.transpose()

    # 判断fm是否为空，若为空，直接返回
    if fm.empty:
        return fm

    # 合并同isolate的变异情况
    # 用正则提取组名：G开头到第一个 -
    fm['Isolate'] = fm.index.to_series().str.extract(r'^(G[^-]+)')
    # 按组名分组，每组取最大值（相当于：列中只要有 1 就算 1）；GN列不需要出现在新的特征矩阵里
    new_fm = fm.groupby(fm['Isolate']).max()

    # 用全0行填补缺少的isolate行
    zero_row = np.zeros(len(new_fm.columns))
    Isolates = new_fm.index.tolist()
    for isolate in GN_list:
        if isolate not in Isolates:
            new_fm.loc[isolate]=zero_row

    return new_fm

def filt_rare(df: pd.DataFrame, threshold: int = 3) -> pd.DataFrame:

    # 计算每一列中 '0' 和 '1' 的数量
    zeros_count = (df == 0).sum(axis=0)
    ones_count = (df == 1).sum(axis=0)
    
    # 保留 '1' 数量大于 threshold 的列
    filtered_df = df.loc[:, ones_count > threshold]

    # 在此基础上，保留 '0' 数量大于 threshold 的列
    filtered_twice_df = filtered_df.loc[:, zeros_count > threshold]
    
    return filtered_twice_df

if __name__=='__main__':

    # 这块记得改读写路径
    read_path="/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/ann_vcf/"
    write_path="/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/feature_matrix/"

    with open("/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/amr_panaroo_dict.json", "r", encoding="utf-8") as f:
        amr_map_panaroo = json.load(f)

    files = os.listdir(read_path)
    for file in files:
        print(file)
        gene=(file.split('.'))[0]
        file_path=read_path+file
        fm1=vcf_process(file_path)
        fm2=feature_matrix(fm1)
        fm3=transform(fm2)
        if fm3.empty:
            print(f"Warning: {gene} has no valid features at result 3.")
            continue
        else:
            fm4=filt_rare(fm3)
            if fm4.empty:
                print(f"Warning: {gene} has no valid features at result 4.")
                continue

        # 替换在amr数据库中有比对结果的基因簇名
        if gene in amr_map_panaroo:
            mapped_gene = amr_map_panaroo[gene]
        else:
            mapped_gene = gene
            
        fm4.to_csv(write_path+mapped_gene+'.csv')