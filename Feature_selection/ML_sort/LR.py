import pandas as pd
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from sklearn import metrics
import seaborn as sns

def model_train(train_data,test_data,save_path,med,type):

    # 特征和目标变量
    X = train_data.drop(columns=["label"])  # 特征
    y = train_data["label"]  # 目标变量
    X_test = test_data.drop(columns=["label"])
    y_test = test_data["label"]

    # 创建逻辑回归模型
    model = LogisticRegression(random_state=42, penalty='l1', solver='liblinear', C=0.1, max_iter=5000, n_jobs=-1)

    # 训练模型
    model.fit(X, y)

    # 对测试集进行预测
    y_pred = model.predict(X_test)
    # 写预测结果到文件
    with open(save_path+type+'_lr_metrics.txt','w') as f:
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
    plt.savefig(save_path+type+'_lr_conf_matrix.png')

    # 输出各特征的权重
    feature_weights = model.coef_
    feature_names = X.columns.tolist()  # 替换为实际特征名称
    weights = feature_weights[0]  # 获取权重数组
    # 将特征名称和权重保存到 DataFrame
    df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': weights
    })
    # 排序
    df = df.sort_values(by='Importance', key=lambda col: col.abs(), ascending=False)
    #df = df[~df['Importance'].isin([0, 0.0])]
    df.to_csv(save_path+type+'_lr_importance.csv', index=False, encoding='utf-8-sig')