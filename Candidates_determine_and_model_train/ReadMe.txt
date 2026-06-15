Candidate determination and model-training scripts
=================================================

This folder contains scripts for selecting final candidate feature sets,
training soft-voting ensemble models, saving final feature matrices and models,
and evaluating them on test and validation data.

General usage
-------------

Most scripts use fixed relative paths and antibiotic lists. Check the path
variables and med_list/K_list values before running.

Typical workflow
----------------

1. Use find_Kmed_avg.py to scan feature-ranking cutoffs and choose the best
   cutoff K for each antibiotic.
2. Use selected_fm.py to assemble selected feature matrices from the chosen
   feature lists.
3. Use model_save.py to train and save the final soft-voting model.
4. Use test.py and validation.py to evaluate saved models on independent test
   and validation matrices.

Scripts
-------

list2fm.py
    Purpose:
        Helper functions for feature selection. process_ml_sort() keeps
        features that appear in at least two of four model-ranking lists within
        the cutoff threshold. build_fm() extracts selected feature columns plus
        the label column from a feature matrix.
    Usage:
        Imported by find_Kmed_avg.py and selected_fm.py; normally not run
        directly.

ensemble_avg.py
    Purpose:
        Train a soft-voting ensemble using logistic regression, random forest,
        SVM, and XGBoost. Hyperparameters and ensemble weights are selected by
        randomized search with 5-fold stratified cross-validation. The selected
        model is then evaluated on the test set.
    Outputs:
        Metrics tables, prediction probabilities/labels, ROC-AUC curves, and
        optionally trained model files.
    Usage:
        Imported by find_Kmed_avg.py or other training scripts through
        train_ensemble_with_cv().

find_Kmed_avg.py
    Purpose:
        Determine the best feature cutoff K for each antibiotic by combining
        statistical-test results and ML rankings, training the ensemble model
        over a series of thresholds, and selecting the threshold with the best
        ROC-AUC.
    Main inputs:
        chi_and_kw_core.json
        chi_and_kw_dispensable.json
        <antibiotic>
    Main outputs:
        <antibiotic>
    Usage:
        Edit med_list and K_list. In practice this script may be run twice:
        first with a broad interval to inspect K-AUC trends, then with a
        narrower interval around the best region.

            python find_Kmed_avg.py

selected_fm.py
    Purpose:
        Assemble selected feature matrices for each antibiotic from the final
        feature lists in feature_select_result.txt.
    Main output:
        Selected train/test matrices under the configured result matrix folder.
    Usage:
        Edit dataset and path variables as needed, then run:

            python selected_fm.py

model_save.py
    Purpose:
        Train the final model on a selected feature matrix and save the model
        plus training metrics and ROC outputs.
    Usage:
        Edit input matrix paths and output paths as needed, then run:

            python model_save.py

test.py
    Purpose:
        Load saved final models and evaluate them on test-set feature matrices.
        Metrics include F1, MCC, AUC, accuracy, precision, and recall.
    Usage:
        Check the train/test matrix roots and model paths, then run:

            python test.py

validation.py
    Purpose:
        Build validation feature matrices using each saved model's feature
        order, predict on validation samples, and append validation AUC values
        to auc.txt.
    Usage:
        Check model_root, fm_root, validation output folders, and metric output
        folder, then run:

            python validation.py
