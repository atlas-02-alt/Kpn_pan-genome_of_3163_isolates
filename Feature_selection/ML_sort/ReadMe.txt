Machine-learning feature-ranking scripts
=======================================

This folder ranks features using four machine-learning models on the training
set for each antibiotic.

General usage
-------------

script.py is the driver script. It imports RF.py, LR.py, SVM.py, and
XGboost.py. The four model files are helper modules and are usually not run
directly.

Before running script.py, check:

    pheno_path
    med_list
    result_path
    core_path
    dis_path

Driver script
-------------

script.py
    Purpose:
        Merge phenotype labels with core and dispensable feature matrices,
        split data into train/test/validation sets, and run four model-based
        feature-ranking methods on the train set.
    Split logic:
        GN samples are kept in the train/test pool. Non-GN samples are split so
        that part of them form an external validation set. The train/test pool
        is then split 70:30 with stratification when possible.
    Main inputs:
        phenotypes.csv
        final_core_feature_matrix.csv
        final_dispensable_feature_matrix.csv
    Main outputs:
        <antibiotic>
        including train/test/validation CSV files, model metrics, confusion
        matrices, and feature-importance ranking CSV files.
    Usage:

            python script.py

Model helper scripts
--------------------

RF.py
    Purpose:
        Train a RandomForestClassifier and export feature importances,
        prediction metrics, and a confusion-matrix figure.
    Usage:
        Imported and called by script.py through RF.model_train().

LR.py
    Purpose:
        Train an L1-regularized logistic regression model and export feature
        weights, prediction metrics, and a confusion-matrix figure.
    Usage:
        Imported and called by script.py through LR.model_train().

SVM.py
    Purpose:
        Train an L1-regularized linear SVM after standardization and export
        feature weights, prediction metrics, and a confusion-matrix figure.
    Usage:
        Imported and called by script.py through SVM.model_train().

XGboost.py
    Purpose:
        Train an XGBoost classifier and export feature importances, prediction
        metrics, and a confusion-matrix figure.
    Usage:
        Imported and called by script.py through XGboost.model_train().
