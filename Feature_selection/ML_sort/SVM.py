import pandas as pd
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
import matplotlib.pyplot as plt
import seaborn as sns

def model_train(train_data,test_data,save_path,med,type):

    # 假设 df 是你的 DataFrame，其中包含特征和目标变量
    X = train_data.drop('label', axis=1)  # 特征矩阵
    y = train_data['label']  # 目标变量
    X_test = test_data.drop(columns=["label"])
    y_test = test_data["label"]

    # 标准化数据
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_test_scaled = scaler.fit_transform(X_test)

    model = LinearSVC(random_state=42, loss='squared_hinge', class_weight='balanced', penalty='l1', C=0.1, dual=False, max_iter=5000)
    model.fit(X_scaled, y)

    # 获取特征权重
    feature_weights = model.coef_
    feature_names = X.columns.tolist()
    weights = feature_weights[0]
    weights_df = pd.DataFrame({
        "Feature":feature_names,
        "Importance":weights
        })
    weights_df = weights_df.sort_values(by='Importance', key=lambda col: col.abs(), ascending=False)
    weights_df.to_csv(save_path+type+'_svm_importance.csv', index=False, encoding='utf-8-sig')

    # 评估模型
    y_pred = model.predict(X_test_scaled)
    # 写预测结果到文件
    with open(save_path+type+'_svm_metrics.txt','w') as f:
        f.write('accuracy: '+str(metrics.accuracy_score(y_test,y_pred))+'\n')
        f.write('precision: '+str(metrics.precision_score(y_test,y_pred))+'\n')
        f.write('recall: '+str(metrics.recall_score(y_test,y_pred))+'\n')
        f.write('f1: '+str(metrics.f1_score(y_test,y_pred))+'\n')
    
    # 输出混淆矩阵
    conf_matrix = metrics.confusion_matrix(y_test, y_pred, labels=[0,1])
    # 可视化
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Predicted Sensitive', 'Predicted Resistant'], 
                yticklabels=['Actual Sensitive', 'Actual Resistant'])
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title(med+' Confusion Matrix')
    plt.savefig(save_path+type+'_svm_conf_matrix.png')