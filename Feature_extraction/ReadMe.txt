Feature extraction scripts
==========================

This folder contains scripts for converting core-gene variants and
dispensable-gene presence/absence into machine-learning feature matrices.

General usage
-------------

These scripts mostly use fixed relative paths. Check the path variables near
the top or in the __main__ block before running.

Scripts
-------

vcf2matrix.py
    Purpose:
        Convert snpEff-annotated VCF files into binary feature matrices after
        removing synonymous variants. It also merges contigs from the same
        isolate, fills missing isolates with zero rows, filters rare features,
        and replaces AMR-related cluster names using amr_panaroo_dict.json.
    Main inputs:
        ann_vcf (folder that contains all vcf files annotated by snpEff)
        phenotypes.csv
        amr_panaroo_dict.json
    Main output:
        Per-gene CSV files under feature_matrix
    Usage:

            python vcf2matrix.py

concat_core_feature_matrix.py
    Purpose:
        Concatenate per-gene core-variant feature matrices into one final core
        feature matrix. Feature names are prefixed with the gene name.
    Main inputs:
        feature_matrix (folder that contains all feature matrices for each core gene)
        phenotypes.csv
    Main output:
        final_core_feature_matrix.csv
    Usage:

            python concat_core_feature_matrix.py

generate_dispensable_fm.py
    Purpose:
        Generate a binary dispensable-gene presence/absence matrix from
        dispensable gene MSA files. Columns are renamed with AMR names when a
        mapping exists, and features with too few 1s or too few 0s are reported
        as rare/uninformative.
    Main inputs:
        dispensable_gene_sequences (folder that contains all dispensable genes' sequence files)
        amr_panaroo_dict.json
    Main output:
        final_dispensable_fm.csv
    Usage:

            python generate_dispensable_fm.py
