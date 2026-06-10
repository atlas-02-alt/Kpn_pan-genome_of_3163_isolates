import os
import joblib
import pandas as pd
from sklearn.metrics import roc_auc_score

# 从之前分好的validation数据集里拿特征列和表型，组成验证用的矩阵，并保存
model_root = "/data/home/sfwang/kpn/Panaroo-DownStream-both/feature_set_determine/5f_avgauc_train/result"
fm_root = "/data/home/sfwang/kpn/Panaroo-DownStream-both/ml_sort"
train_root = "/data/home/sfwang/kpn/Panaroo-DownStream-both/feature_set_determine/5f_avgauc_train/result_train_matrix"
val_fm_save_root = "/data/home/sfwang/kpn/Panaroo-DownStream-both/feature_set_determine/5f_avgauc_train/result_validation_matrix"
metrices_save_root = "/data/home/sfwang/kpn/Panaroo-DownStream-both/feature_set_determine/5f_avgauc_train/validation_result"

for med in os.listdir(fm_root):

    path = os.path.join(fm_root, med)
    if os.path.isdir(path):
        print(path)

        # 加载训练好的模型
        pkl_path = f"{model_root}/{med}/best_model.pkl"
        if not os.path.exists(pkl_path):
            print(f"没有模型: {pkl_path}")
            continue
        with open(pkl_path, "rb") as f:
            model = joblib.load(f)

        # 读取训练时的特征列（含表型）
        #train_fm = pd.read_csv(f"{train_root}/{med}.csv", index_col=0)
        #feature_cols = train_fm.columns.tolist()
        feature_cols = model.feature_names_in_.tolist()

        # 从整个validation数据集中提取对应的特征列和表型
        val_core_data = pd.read_csv(f"{fm_root}/{med}/core_validation_set.csv", index_col=0)
        val_dis_data = pd.read_csv(f"{fm_root}/{med}/dis_validation_set.csv", index_col=0)
        val_total_data = pd.concat([val_core_data, val_dis_data], axis=1) # 合并
        val_total_data = val_total_data.loc[:, ~val_total_data.columns.duplicated()] # 去重列（label）
        val_total_data = val_total_data[feature_cols + ["label"]]
        val_total_data.to_csv(f"{val_fm_save_root}/{med}.csv")

        # 在validation上进行预测，并计算auc。所有药的auc写到同一个txt文档。
        X = val_total_data.drop(columns=["label"])
        if X.shape[0] == 0:
            print(f"没有验证数据集")
            continue
        y_true = val_total_data['label']
        y_prob = model.predict_proba(X)[:, 1]
        try:
            auc_on_val = roc_auc_score(y_true, y_prob)
        except Exception as e:
            print(f"预测失败: {e}")
            auc_on_val="NA"

        with open(f"{metrices_save_root}/auc.txt",'a') as f:
            f.write(f"{med}: {str(auc_on_val)} \n")