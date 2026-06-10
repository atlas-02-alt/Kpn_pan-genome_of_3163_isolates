import joblib
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_validate, KFold, cross_val_predict
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import (
    make_scorer, f1_score, matthews_corrcoef, accuracy_score,
    precision_score, recall_score, roc_auc_score, roc_curve, confusion_matrix, auc
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

os.environ["PYTHONHASHSEED"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"

def ens_soft(labeled_data, med):

    save_path = f"/data/home/sfwang/kpn/Panaroo-DownStream-patric/feature_set_determine/5f_avgauc_train/result/{med}/"

    labeled_data = labeled_data.sort_index(axis=0)
    X = labeled_data.drop(columns=["label"])
    X = X.sort_index(axis=1)
    y = labeled_data["label"]

    if X.empty:
        results = pd.DataFrame()
        return results

    scoring = {
        'f1': make_scorer(f1_score, pos_label=1),
        'mcc': make_scorer(matthews_corrcoef),
        'auc': make_scorer(roc_auc_score, response_method='predict_proba'),
        'accuracy': make_scorer(accuracy_score),
        'precision': make_scorer(precision_score, pos_label=1),
        'recall': make_scorer(recall_score, pos_label=1),
    }

    models = {
        'Logistic Regression': make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=42)),
        'Random Forest': RandomForestClassifier(random_state=42, n_jobs=-1),
        'SVM': make_pipeline(StandardScaler(), SVC(probability=True, random_state=42)),
        'XGBoost': XGBClassifier(random_state=42, n_jobs=-1),
    }

    voting_model = VotingClassifier(
        estimators=[
            ('lr', models['Logistic Regression']),
            ('rf', models['Random Forest']),
            ('svm', models['SVM']),
            ('xgb', models['XGBoost'])
        ],
        voting='soft',
        n_jobs=-1
    )
    models['Soft Voting'] = voting_model

    results = pd.DataFrame(columns=['global AUC', 'auc_list', 'F1_list', 'MCC_list', 'Acc_list', 'Pre_list', 'Rec_list', 'mean_auc'],
                           index=['Logistic Regression', 'Random Forest', 'SVM', 'XGBoost', 'Soft Voting'])
    details = pd.DataFrame()
    details['true label'] = y

    cv = KFold(n_splits=5, shuffle=True, random_state=42)  # 五折交叉验证

    # average roc_auc准备
    fpr_dict = {}
    tpr_dict = {}

    for model_name, model in models.items():
        print(f"Evaluating {model_name}...")

        # 交叉验证指标
        cv_results = cross_validate(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
        y_pred = cross_val_predict(model, X, y, cv=cv, n_jobs=-1)
        y_pred_probs = cross_val_predict(model, X, y, cv=cv, method='predict_proba', n_jobs=-1)

        prob_col_name = f"{model_name} predict probabiliy"
        pred_col_name = f"{model_name} predict label"

        details[prob_col_name] = np.array(y_pred_probs[:, 1])
        details[pred_col_name] = np.array(y_pred)

        glob_auc = roc_auc_score(y, y_pred_probs[:, 1])
        auc_list = cv_results['test_auc']
        f1_list = cv_results['test_f1']
        mcc_list = cv_results['test_mcc']
        acc_list = cv_results['test_accuracy']
        pre_list = cv_results['test_precision']
        rec_list = cv_results['test_recall']

        results.at[model_name, 'global AUC'] = glob_auc
        results.at[model_name, 'auc_list'] = auc_list.tolist()
        results.at[model_name, 'F1_list'] = f1_list.tolist()
        results.at[model_name, 'MCC_list'] = mcc_list.tolist()
        results.at[model_name, 'Acc_list'] = acc_list.tolist()
        results.at[model_name, 'Pre_list'] = pre_list.tolist()
        results.at[model_name, 'Rec_list'] = rec_list.tolist()

        cm = confusion_matrix(y, y_pred, labels=[1, 0])
        print("Confusion Matrix:")
        print(cm)

        # === 平均 ROC 计算 ===
        mean_fpr = np.linspace(0, 1, 100)
        tprs = []
        aucs = []

        for train_idx, test_idx in cv.split(X, y):
            model.fit(X.iloc[train_idx], y.iloc[train_idx])
            probas_ = model.predict_proba(X.iloc[test_idx])
            fpr, tpr, _ = roc_curve(y.iloc[test_idx], probas_[:, 1])
            tprs.append(np.interp(mean_fpr, fpr, tpr))
            tprs[-1][0] = 0.0
            aucs.append(auc(fpr, tpr))

        mean_tpr = np.mean(tprs, axis=0)
        mean_tpr[-1] = 1.0
        mean_auc = np.mean(aucs)

        fpr_dict[model_name] = mean_fpr
        tpr_dict[model_name] = mean_tpr
        results.at[model_name, 'mean_auc'] = mean_auc   # 保存平均AUC

    results.to_csv(f"{save_path}metrices_train_final.csv")
    details.to_csv(f"{save_path}prob_train_final.csv")

    # Plot ROC for base models
    base_models = ['Logistic Regression', 'Random Forest', 'SVM', 'XGBoost', 'Soft Voting']
    plt.figure(figsize=(8, 6))
    for model_name in base_models:
        plt.plot(fpr_dict[model_name], tpr_dict[model_name],
                 label=f"{model_name} (AUC = {results.at[model_name, 'mean_auc']:.3f})")
    plt.plot([0, 1], [0, 1], 'k--', label='Random Guess')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Mean ROC Curves for Base Models')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f"{save_path}roc_auc_5models_train_final.pdf")
    plt.clf()

    # Plot ROC for Soft Voting only
    plt.figure(figsize=(6, 5))
    plt.plot(fpr_dict['Soft Voting'], tpr_dict['Soft Voting'],
             label=f"Soft Voting (AUC = {results.at['Soft Voting', 'mean_auc']:.3f})")
    plt.plot([0, 1], [0, 1], 'k--', label='Random Guess')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Mean ROC Curve - Soft Voting Ensemble')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f"{save_path}roc_auc_ens_train_final.pdf")

    # 训练并保存最终模型（.pkl）
    print("\nTraining final soft voting model on full data...")
    final_model = voting_model.fit(X, y)
    joblib.dump(final_model, f"{save_path}model_train_final.pkl")

    # 最终返回用于衡量特征集优劣的平均auc
    auc4cmp = results.at['Soft Voting', 'auc_list']
    average = sum(auc4cmp) / len(auc4cmp)
    return average

if __name__=='__main__':

    folder_path = "/data/home/sfwang/kpn/Panaroo-DownStream-patric/feature_set_determine/5f_avgauc_train/result_train_matrix/"

    for root, dirs, files in os.walk(folder_path):

        #files=['ETP.csv']  # 只跑ETP

        for file in files:

            if file.endswith(".csv"):
                full_path = os.path.join(root, file)
                print(full_path)
                total_fm = pd.read_csv(full_path, index_col=0)
                med = (file.split('.'))[0]

                ### 五折交叉验证
                # 调完函数就ok
                total_auc=ens_soft(total_fm,med)