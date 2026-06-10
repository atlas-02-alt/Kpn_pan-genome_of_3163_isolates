from collections import Counter
import pandas as pd
import os

def process_ml_sort(med,core_dis,thresh):
    # 对指定药物的指定类型的fm（core/dis），进行train上模型排序结果的4选2
    path=f'/data/home/sfwang/kpn/Panaroo-DownStream-both/ml_sort/{med}/'

    if not os.path.exists(f"{path}{core_dis}_xgb_importance.csv"):
        return []
    
    # 读取数据文件
    all_elements=[]
    models=['xgb','lr','rf','svm']
    for model in models:
        df = pd.read_csv(f"{path}{core_dis}_{model}_importance.csv")      
        # 获取第一列
        first_column = df.iloc[:, 0]        
        # 确定k的值不超过列的长度
        actual_t = min(thresh, len(first_column))        
        # 获取前k个元素并转换为list
        result_list = first_column.head(actual_t).tolist()
        # 加入大列表
        all_elements.extend(result_list)
    
    # 统计每个元素的出现次数
    element_counts = Counter(all_elements)
    print(element_counts)
    # 筛选出现次数 ≥ 2 的元素
    result = [elem for elem, count in element_counts.items() if count >= 2]
    print(result)

    return result

def build_fm(feature_list,fm):
    # 从fm中抽取feature_list种每个元素对应的列+target列，组装新的小特征矩阵
    new_fm = fm[feature_list + ['label']] 
    new_fm = new_fm.astype(int)
    return new_fm