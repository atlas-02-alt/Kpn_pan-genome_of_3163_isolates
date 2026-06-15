Statistical-test feature selection scripts
=========================================

This folder contains scripts for statistical screening of feature-antibiotic
pairs before model-based ranking.

General usage
-------------

The scripts use fixed relative paths. Check pheno_path, fm_path, and output
paths before running. They expect phenotype labels to be "R" or "S".

Scripts
-------

toolkit.py
    Purpose:
        Shared helper functions. merge_label_to_fm() appends an antibiotic
        label column to a feature matrix, keeps only R/S samples, and converts
        labels to 1/0.
    Usage:
        Imported by other scripts; normally not run directly.

chi_analyse.py
    Purpose:
        Run chi-square tests for each feature-antibiotic pair. Zero cells in
        the 2x2 contingency table are corrected by adding 0.5.
    Main inputs:
        phenotypes.csv
        final_core_feature_matrix.csv
    Main output:
        core_chisquare.csv
    Usage:

            python chi_analyse.py

kw_analyse.py
    Purpose:
        Run Kruskal-Wallis tests for each feature-antibiotic pair after
        filtering zero-variance features.
    Main inputs:
        phenotypes.csv
        final_core_feature_matrix.csv
    Main output:
        core_kw.csv
    Usage:

            python kw_analyse.py

chi_kw.py
    Purpose:
        Find feature-antibiotic pairs significant in both chi-square and
        Kruskal-Wallis tests at p < 0.05, then save the selected features in a
        JSON dictionary keyed by antibiotic.
    Main inputs:
        dispensable_chisquare.csv
        dispensable_kw.csv
    Main output:
        chi_and_kw_dispensable.json
    Usage:
        Edit the input/output paths for core or dispensable features as needed,
        then run:

            python chi_kw.py
