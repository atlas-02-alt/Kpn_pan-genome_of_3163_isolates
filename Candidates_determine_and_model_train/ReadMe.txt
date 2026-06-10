(1) Train set
    ↓
    5-fold CV
    ↓
    选模型 / 选超参数

(2) 用全部 train set refit 最优模型

(3) Independent test set
    ↓
    单次预测
    ↓
    单个 AUC + ROC

ensemble_avg.py:
集成模型训练函数
保存文件：①指标dataframe ②各样本预测概率和预测标签 ③roc-auc曲线图 ④训练好的模型（.pkl格式）
※所有由soft_ensemble函数直接保存的文件，最后都要定点调用并保存。否则最后生成的是循环迭代的最后一个K值对应的数据。
（此处五折交叉验证是在30%样本上进行的）

list2fm.py:
由特征名构成的list组装特征矩阵的函数

find_Kmed_avg.py
该代码文件要运行两遍。
第一遍：35种药物区间统一设为100，看K-auc曲线变化趋势，确定在什么区间上取最大点（前提是auc到0.8）。
第二遍：在确定的区间上找最大点。
保存文件：①特征值列表和最大auc值 ②K-auc曲线图

selected_fm.py:
根据定好的特征，输出每个药物的significant特征集对应的特征矩阵

model_save.py:
以某个特定的特征矩阵作输入，输出训练好的模型和对应指标

test.py：
在30%测试集上检验在70%上训练的模型的效果