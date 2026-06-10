import pandas as pd
from sklearn.model_selection import train_test_split
import os
import RF,LR,SVM,XGboost
import numpy as np
def merge_label_to_fm(fm,label):

    fm = fm.copy()
    fm["label"] = label

    fm = fm[fm["label"].isin(["R", "S"])]
    fm["label"] = fm["label"].map({"R": 1, "S": 0})

    return fm

def tt_split(df,result_path,med,type):

    # 分割特征和标签
    X = df.drop('label', axis=1)  # 特征
    y = df['label']  # 标签

    # 按7:3比例分割，并保证各类别比例一致
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.3, 
        random_state=42,  # 随机种子，保证可重复性
        stratify=y  # 按标签分层分割
    )

    # 合并特征和标签，并导出为文件
    train_set = pd.concat([X_train, y_train], axis=1)
    test_set = pd.concat([X_test, y_test], axis=1)

    if not os.path.exists(result_path+med+'/'):
        os.makedirs(result_path+med+'/')
    train_set.to_csv(result_path+med+'/'+type+'_train_set.csv')
    test_set.to_csv(result_path+med+'/'+type+'_test_set.csv')

    return train_set,test_set

if __name__ == '__main__':

    # 读RS耐药表型数据
    pheno_path="/data/home/sfwang/kpn/Panaroo-DownStream-both/phenotypes.csv"
    phenos=pd.read_csv(pheno_path,index_col=0)
    # 读取35种抗生素名 
    #med_list=phenos.columns.tolist()
    med_list=['CFP','CMZ','CSL','CZA','DOX','MOX','NET','PIP','TMP']

    # 设置存放结果的根目录
    result_path = '/data/home/sfwang/kpn/Panaroo-DownStream-both/ml_sort/'

    # 读入两个基本特征矩阵，并放入list
    core_path = "/data/home/sfwang/kpn/Panaroo-DownStream-both/final_core_feature_matrix.csv"
    core = pd.read_csv(core_path,index_col=0)
    dis_path = "/data/home/sfwang/kpn/Panaroo-DownStream-both/final_dispensable_feature_matrix.csv"
    dis = pd.read_csv(dis_path,index_col=0)
    fm_dict = {'core':core,'dis':dis}

    for med in med_list:

        label=phenos[med]
        print(f"Processing : {med}")

        for type in fm_dict:

            # 合并标签到特征矩阵
            whole_data = merge_label_to_fm(fm_dict[type], label)
            # 如果已经有了分割好的数据集结果文件，则不用再执行分割和保存步骤。
            # 分割出X1(train+test)和validation集，validation直接保存，data用于后续排序
            y = whole_data['label']
            mask_gn = whole_data.index.str.startswith("GN") # 所有以GN开头的编号
            # 安徽样本
            X_gn = whole_data[mask_gn]
            y_gn = y[mask_gn]
            # patric样本
            X_non_gn = whole_data[~mask_gn]
            y_non_gn = y[~mask_gn]
            # 切割patric样本，55分。
            try:
                if len(y_non_gn) == 0: #没有patric样本，validation是空集
                    X_non_gn_1 = pd.DataFrame(columns=X_non_gn.columns)
                    X_non_gn_2 = pd.DataFrame(columns=X_non_gn.columns)
                    y_non_gn_1 = pd.Series(dtype=y_non_gn.dtype)
                    y_non_gn_2 = pd.Series(dtype=y_non_gn.dtype)
                else:
                    unique, counts = np.unique(y_non_gn, return_counts=True)
                    stratify_y = y_non_gn if counts.min() >= 2 else None #如果某个耐药表型类别样本数小于2，则不进行分层抽样
                    X_non_gn_1, X_non_gn_2, y_non_gn_1, y_non_gn_2 = train_test_split(
                        X_non_gn, y_non_gn,
                        test_size=0.5,
                        random_state=42,
                        stratify=stratify_y
                    )

            except ValueError as e:
                # 其他 ValueError：继续往外抛或跳过
                print(f"[split error] {e}")
                continue

            X1 = pd.concat([X_gn, X_non_gn_1]).astype(int) 
            y1 = pd.concat([y_gn, y_non_gn_1]).astype(int) 
            validation_fm=pd.concat([X_non_gn_2, y_non_gn_2], axis=1)
            
            # 从X1中分割训练集和测试集
            train_fm,test_fm=tt_split(X1,result_path,med,type)
            y_train = train_fm['label']
            # 分割以后的训练集有可能只剩下一种表型，这种情况下弃用该药物。
            if y_train.nunique() < 2:
                print("Skip: only one class in y_train")
                continue

            #debug
            print(y_train.head())
            print(y_train.dtype)
            print(y_train.nunique())
            print(y_train.isna().sum())

            # 随机森林模型排序
            RF.model_train(train_fm,test_fm,result_path+med+'/',med,type)
            # 逻辑回归模型排序
            LR.model_train(train_fm,test_fm,result_path+med+'/',med,type)
            # LightGBM模型排序
            XGboost.model_train(train_fm,test_fm,result_path+med+'/',med,type)
            # SVM模型排序
            SVM.model_train(train_fm,test_fm,result_path+med+'/',med,type)

            # 保存validation集
            validation_fm.to_csv(result_path+med+'/'+type+'_validation_set.csv')