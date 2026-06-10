import os
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix
from xgboost import XGBClassifier
from sklearn.metrics import make_scorer, f1_score, matthews_corrcoef, accuracy_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score
import joblib

def model_test(med, labeled_data):

    # 导入训练时用的特征矩阵（原始训练数据或列名）
    train_df = pd.read_csv(f"/data/home/sfwang/kpn/Panaroo-DownStream-patric/feature_set_determine/5f_avgauc_train/result_train_matrix/{med}.csv", index_col=0)  # 训练时的特征矩阵
    train_df = train_df.sort_index(axis=1)
    model_features = list(train_df.columns)  # 按训练时的列顺序保存

    # 导入训练好的模型
    model = joblib.load(f"/data/home/sfwang/kpn/Panaroo-DownStream-patric/feature_set_determine/5f_avgauc_train/result/{med}/model_train_final.pkl")

    # 预测
    X = labeled_data[model_features]
    X = X.drop(columns=["label"])
    y_true = labeled_data["label"]  # 真实标签列
    y_pred = model.predict(X)

    # 计算混淆矩阵
    cm = confusion_matrix(y_true, y_pred)
    print("混淆矩阵:")
    print(cm)

    # 有些指标需要概率
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X)[:, 1]
    else:
        # 对于不支持 predict_proba 的模型（比如部分 SVM），用 decision_function
        y_proba = model.decision_function(X)

    # 计算指标并存成字典
    metrics_dict = {}
    if y_true is not None and len(set(y_true)) > 1:
        metrics_dict = {
            "F1": f1_score(y_true, y_pred, average="weighted"),
            "MCC": matthews_corrcoef(y_true, y_pred),
            "AUC": roc_auc_score(y_true, y_proba),
            "Accuracy": accuracy_score(y_true, y_pred),
            "Precision": precision_score(y_true, y_pred, average="weighted"),
            "Recall": recall_score(y_true, y_pred, average="weighted"),
        }
        print(metrics_dict)
    elif len(set(y_true)) == 1:
        metrics_dict = {
            "F1": f1_score(y_true, y_pred, average="weighted"),
            "MCC": matthews_corrcoef(y_true, y_pred),
            "AUC": None,
            "Accuracy": accuracy_score(y_true, y_pred),
            "Precision": precision_score(y_true, y_pred, average="weighted"),
            "Recall": recall_score(y_true, y_pred, average="weighted"),
        }
    else:
        print("没有标签列，无法计算指标。")

    return metrics_dict

if __name__ == "__main__":

    # 获取药物列表
    feature_folder_path="/data/home/sfwang/kpn/Panaroo-DownStream-patric/feature_set_determine/5f_avgauc_train/result/"
    folder_list = [f for f in os.listdir(feature_folder_path)]
    #folder_list = ['ETP'] # 只跑NIT

    # 拿test对应的特征矩阵来训练
    for med in folder_list:
        print(med)
        df=pd.read_csv(f"/data/home/sfwang/kpn/Panaroo-DownStream-patric/feature_set_determine/5f_avgauc_train/result_test_matrix/{med}.csv", index_col=0)
        result=model_test(med, df)
        with open(f"/data/home/sfwang/kpn/Panaroo-DownStream-patric/feature_set_determine/5f_avgauc_train/test_result/{med}.txt", "w") as f:
            for key, value in result.items():
                f.write(f'{key}: {value}\n')