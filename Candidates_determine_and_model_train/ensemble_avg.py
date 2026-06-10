import joblib
import pandas as pd
import json
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score

def train_ensemble_with_cv(labeled_train_data, labeled_test_data, med, random_state=42, model_save=False):

    save_path = f"/data/home/sfwang/kpn/Panaroo-DownStream-both/feature_set_determine/5f_avgauc_train/result/{med}/"

    labeled_train_data = labeled_train_data.sort_index(axis=0)
    X_train = labeled_train_data.drop(columns=["label"])
    X_train = X_train.sort_index(axis=1)
    y_train = labeled_train_data["label"]

    if X_train.empty:
        results = pd.DataFrame()
        return results

    # =========================
    # 1. Define base models
    # =========================
    models = {
        'Logistic Regression': make_pipeline(StandardScaler(), LogisticRegression(random_state=random_state, penalty='l1', solver='liblinear', max_iter=5000, n_jobs=-1)),
        'Random Forest': RandomForestClassifier(random_state=random_state, max_features='sqrt', n_jobs=-1),
        'SVM': make_pipeline(StandardScaler(), SVC(random_state=random_state, kernel='linear', class_weight='balanced', max_iter=5000, probability=True)),
        'XGBoost': XGBClassifier(random_state=random_state, subsample=0.8, colsample_bytree=0.4, n_jobs=-1),
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

    # =========================
    # 2. Parameter search space
    # =========================
    param_grid = {
        # Logistic Regression
        'lr__logisticregression__C': [0.01, 0.1, 1.0],

        # Random Forest
        'rf__n_estimators': [300, 500],
        'rf__max_depth': [None, 10],

        # SVM
        'svm__svc__C': [0.01, 0.1, 1.0],

        # XGBoost
        'xgb__max_depth': [3, 5],
        'xgb__learning_rate': [0.05, 0.1],
        'xgb__n_estimators': [300, 500],

        # Ensemble weights
        'weights': [
            [1, 1, 1, 1],
            [2, 1, 1, 1],
            [1, 2, 1, 1],
            [1, 1, 2, 1],
            [1, 1, 1, 2]
        ]
    }

    # =========================
    # 3. Cross-validation setup
    # =========================
    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=random_state
    )

    search = RandomizedSearchCV(
        estimator=voting_model,
        param_distributions=param_grid,
        n_iter=100,
        scoring='roc_auc',
        cv=cv,
        n_jobs=-1,
        refit=True,
        return_train_score=True
    )

    # =========================
    # 4. Run CV search
    # =========================
    search.fit(X_train, y_train)

    # =========================
    # 5. Collect results
    # =========================
    best_model = search.best_estimator_ # 如果model_save为True，则在后续保存该模型
    best_params = search.best_params_ # search到的超参，以字典格式储存，键值和param_grid一一对应
    best_cv_auc = search.best_score_
    cv_results = pd.DataFrame(search.cv_results_)
    print(best_params)

    # =========================
    # 6. test on test datset
    # =========================
    labeled_test_data = labeled_test_data.sort_index(axis=0)
    X_test = labeled_test_data.drop(columns=["label"])
    X_test = X_test.sort_index(axis=1)
    y_test = labeled_test_data["label"]
    # ---------------------------
    # 6.1. 用选择好的超参定义新模型
    # ---------------------------
    lr = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            random_state=random_state,
            penalty='l1',
            solver='liblinear',
            max_iter=5000,
            n_jobs=-1,
            C=best_params['lr__logisticregression__C']
        )
    )

    rf = RandomForestClassifier(
        random_state=random_state,
        max_features='sqrt',
        n_jobs=-1,
        n_estimators=best_params['rf__n_estimators'],
        max_depth=best_params['rf__max_depth'],
    )

    svm = make_pipeline(
        StandardScaler(),
        SVC(
            random_state=random_state,
            kernel='linear',
            class_weight='balanced',
            max_iter=5000,
            probability=True,
            C=best_params['svm__svc__C'],
        )
    )

    xgb = XGBClassifier(
        random_state=random_state,
        subsample=0.8,
        colsample_bytree=0.4,
        n_jobs=-1,
        max_depth=best_params['xgb__max_depth'],
        learning_rate=best_params['xgb__learning_rate'],
        n_estimators=best_params['xgb__n_estimators']
    )

    ensemble = VotingClassifier(
        estimators=[
            ('lr', lr),
            ('rf', rf),
            ('svm', svm),
            ('xgb', xgb)
        ],
        voting='soft',
        weights=best_params['weights'],  # 投票权重
        n_jobs=-1
    )

    # ---------------------------
    # 6.2. 在新数据上预测概率
    # ---------------------------
    ensemble.fit(X_train, y_train)
    y_prob = ensemble.predict_proba(X_test)[:, 1]

    # ---------------------------
    # 6.3. 计算 AUC
    # ---------------------------
    auc_on_test = roc_auc_score(y_test, y_prob)

    # ---------------------------
    # 6.4. 绘制roc-auc曲线图，并把在test集上的各指标写出到文件
    # ---------------------------
    if model_save:
        # 1.保存在整个train上fit过的模型
        model_path = save_path + 'best_model.pkl'
        joblib.dump(ensemble, model_path)
        # 2.把超参调优结果best_params写出到文件
        with open(save_path + 'best_params.json', 'w') as f:
            json.dump(best_params, f, indent=4)
        # 3. 画roc-auc曲线并保存
        rf.fit(X_train, y_train)
        lr.fit(X_train, y_train)
        svm.fit(X_train, y_train)
        xgb.fit(X_train, y_train)
        # 计算每个模型的 ROC 曲线
        fpr_rf, tpr_rf, _ = roc_curve(y_test, rf.predict_proba(X_test)[:, 1])
        fpr_lr, tpr_lr, _ = roc_curve(y_test, lr.predict_proba(X_test)[:, 1])
        fpr_svm, tpr_svm, _ = roc_curve(y_test, svm.predict_proba(X_test)[:, 1])
        fpr_xgb, tpr_xgb, _ = roc_curve(y_test, xgb.predict_proba(X_test)[:, 1])
        fpr_voting, tpr_voting, _ = roc_curve(y_test, ensemble.predict_proba(X_test)[:, 1])
        # 计算 AUC 值
        roc_auc_rf = auc(fpr_rf, tpr_rf)
        roc_auc_lr = auc(fpr_lr, tpr_lr)
        roc_auc_svm = auc(fpr_svm, tpr_svm)
        roc_auc_xgb = auc(fpr_xgb, tpr_xgb)
        roc_auc_voting = auc(fpr_voting, tpr_voting)
        # 绘制 ROC 曲线
        plt.figure(figsize=(10, 8))
        # 绘制每个基模型的 ROC 曲线
        plt.plot(fpr_rf, tpr_rf, color='darkorange', lw=2, label='Random Forest (AUC = %0.2f)' % roc_auc_rf)
        plt.plot(fpr_lr, tpr_lr, color='blue', lw=2, label='Logistic Regression (AUC = %0.2f)' % roc_auc_lr)
        plt.plot(fpr_svm, tpr_svm, color='green', lw=2, label='SVM (AUC = %0.2f)' % roc_auc_svm)
        plt.plot(fpr_xgb, tpr_xgb, color='red', lw=2, label='XGBoost (AUC = %0.2f)' % roc_auc_xgb)
        # 绘制集成模型的 ROC 曲线
        plt.plot(fpr_voting, tpr_voting, color='purple', lw=2, label='Voting Classifier (AUC = %0.2f)' % roc_auc_voting)
        # 绘制随机猜测的基准线
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        # 添加标题和标签
        plt.title('ROC Curve of Five Models')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend(loc='lower right')
        # 保存图像
        plt.savefig(f"{save_path}roc_auc_5models.pdf")
        plt.clf()
        # 再画一张只有集成模型的roc曲线图
        # 绘制 ROC 曲线
        plt.figure(figsize=(10, 8))
        # 绘制集成模型的 ROC 曲线
        plt.plot(fpr_voting, tpr_voting, color='purple', lw=2, label='Voting Classifier (AUC = %0.2f)' % roc_auc_voting)
        # 绘制随机猜测的基准线
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        # 添加标题和标签
        plt.title('ROC Curve of Ensemble Model')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend(loc='lower right')
        # 保存图像
        plt.savefig(f"{save_path}roc_auc_ensemble.pdf")

    return auc_on_test