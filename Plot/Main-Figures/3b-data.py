import pandas as pd

target_col = 'Medical class'

# ============ Function you need to implement yourself ============
def is_known_gene(gene_name: str, feature_type) -> bool:
    """
    Determine whether a gene is known.
    Args:
        gene_name: Gene name

    Returns:
        True means known gene; False means unknown gene.
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

    # Read the CSV file
    csv_path = r"./Figures-re/fig3-related-data/ab-candidate_features_summary.csv"

    df = pd.read_csv(csv_path)

    # Display data statistics
    print("=" * 80)
    print(f"Total rows: {len(df)}")
    print(f"\n{target_col} categories and statistics:\n")

    # Group statistics by Medical class
    for medical_class in df[target_col].unique():

        class_df = df[df[target_col] == medical_class]
        print(f"\n{'='*60}")
        print(f"Category: {medical_class} (total {len(class_df)} rows)")
        print(f"{'='*60}")

        known_v=[]
        unknown_v=[]
        known_g=[]
        unknown_g=[]

        # Count v-feature and g-feature separately
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

            print(f"    Known genes: {len(known_v) if feature_type == 'v-feature' else len(known_g)}")
            print(f"    Unknown genes: {len(unknown_v) if feature_type == 'v-feature' else len(unknown_g)}")
            print(f"    Subtotal: {len(known_v) + len(unknown_v) if feature_type == 'v-feature' else len(known_g) + len(unknown_g)}")
