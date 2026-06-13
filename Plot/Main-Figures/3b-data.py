import pandas as pd

target_col = 'Medical class'

# ============ 你需要自己实现的函数 ============
def is_known_gene(gene_name: str, feature_type) -> bool:
    """
    判断一个基因是否为已知基因。    
    Args:
        gene_name: 基因名称
        
    Returns:
        True 表示已知基因，False 表示未知基因。
    """
    if gene_name.startswith("amr_") and feature_type == 'g-feature':
        return True
    elif gene_name=='amr_blaSHV-187':
        return True
    elif gene_name=='gyrA_1~~~gyrA~~~gyrA_2' or gene_name=='parC_1~~~parC_3~~~parC~~~parC_2':
        return True
    else:
        return False


if __name__ == "__main__":

    # 读取CSV文件
    csv_path = r"C:/Users/yxLig/Nutstore/1/我的坚果云 (2)/Klebsiella_pneumoniae/Figures-re/fig3部分相关数据/ab-candidate_features_summary.csv"
    
    df = pd.read_csv(csv_path)
    
    # 显示数据统计结果
    print("=" * 80)
    print(f"总行数: {len(df)}")
    print(f"\n{target_col} 的类别及统计:\n")
    
    # 按Medical class分组统计
    for medical_class in df[target_col].unique():

        class_df = df[df[target_col] == medical_class]
        print(f"\n{'='*60}")
        print(f"类别: {medical_class} (共 {len(class_df)} 行)")
        print(f"{'='*60}")

        known_v=[]
        unknown_v=[]
        known_g=[]
        unknown_g=[]
        
        # 分别统计 v-feature 和 g-feature
        for feature_type in ['v-feature', 'g-feature']:

            type_df = class_df[class_df['Feature type'] == feature_type]
            
            if len(type_df) == 0:
                continue
                
            print(f"\n  {feature_type}:")
            
            for index,row in type_df.iterrows():
                gene = row['Gene']
                variant = row['Variant']
                complete_feature = f"{gene}_{variant}"
                if is_known_gene(gene,feature_type):
                    if feature_type == 'v-feature' and complete_feature not in known_v:
                        known_v.append(complete_feature)
                    elif feature_type == 'g-feature' and gene not in known_g:
                        known_g.append(gene)
                else:
                    if feature_type == 'v-feature' and complete_feature not in unknown_v:
                        unknown_v.append(complete_feature)
                    elif feature_type == 'g-feature' and gene not in unknown_g:
                        unknown_g.append(gene)
            
            print(f"    已知基因: {len(known_v) if feature_type == 'v-feature' else len(known_g)}")
            print(f"    未知基因: {len(unknown_v) if feature_type == 'v-feature' else len(unknown_g)}")
            print(f"    小计: {len(known_v) + len(unknown_v) if feature_type == 'v-feature' else len(known_g) + len(unknown_g)}")
