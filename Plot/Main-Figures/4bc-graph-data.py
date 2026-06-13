import pandas as pd
import numpy as np

def vcf_process(vcf_path):
    # 读取snpEff注释后的、由samtools和bcf合成的.vcf文件
    # ①去除文件头，剩下部分转为dataframe格式
    # ②对df的列名进行修正，去除多余数据

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

    return fm

if __name__=='__main__':

    file_path="C:\\Users\\yxLig\\Nutstore\\1\\我的坚果云 (2)\\Klebsiella_pneumoniae\\Figures-re\\fig5相关数据\\fucK.ann.vcf"
    fm1=vcf_process(file_path)
    fm2=feature_matrix(fm1)
    fm3=transform(fm2)
    #得到每条基因的特征构成的矩阵
    #fm3.to_csv("C:/Users/yxLig/Nutstore/1/我的坚果云 (2)/Klebsiella_pneumoniae/Figures-new/fig5-中间文件/rsxC_2~~~rsxC_3~~~rsxC_1_test.csv")
    path00=[]
    path01=[]
    path10=[]
    path11=[]
    for index, row in fm3[['947_G->A','948_G->T']].iterrows():
        a, b = row['947_G->A'], row['948_G->T']
        if a==0 and b==0 and index not in path00:
            path00.append(index)
        elif a==0 and b==1 and index not in path01:
            path01.append(index)
        elif a==1 and b==0 and index not in path10:
            path10.append(index)
        elif a==1 and b==1 and index not in path11:
            path11.append(index)
    print("path00:",len(path00))
    print("path01:",len(path01))
    print("path10:",len(path10))
    print("path11:",len(path11))