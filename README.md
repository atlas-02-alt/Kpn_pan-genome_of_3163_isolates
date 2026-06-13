# Kpn Pan-Genome Analysis of 3,163 Isolates

(Draft version; still under revision)

This repository contains scripts, trained models, and plotting utilities for a pan-genome-based analysis of 3,163 *Klebsiella pneumoniae* isolates. The workflow covers pan-genome construction, feature extraction, feature selection, candidate determination, model training, downstream analysis, and figure generation.

## Directory Guide

- The repository is organized by analysis stage, so each top-level directory represents one major part of the pipeline.

| Directory | Purpose |
| --- | --- |
| `Pan-genome_construction/` | Builds and post-processes the pan-genome, including genome annotation, Panaroo execution, GFF updates, AMR annotation, and gene cluster cleaning of pan-genome outputs. |
| `Feature_extraction/` | Identifies core-gene variants through single-base-resolution alignment, annotates variants with snpEff, retains non-synonymous variants, and encodes them together with dispensable gene presence/absence into binary feature matrices. |
| `Feature_selection/` | Screens the full feature set using statistical tests and ranks features based on machine-learning-derived importance scores. |
| `Candidates_determine_and_model_train/` | Determines candidate features, prepares selected feature matrices, trains models, tests and validates performance, and saves model artifacts. |
| `Further_analyzation/` | Performs downstream biological analyses, including candidate-feature prioritization and transposon-associated genomic pattern analysis. |
| `Plot/` | Contains scripts for generating main and supplementary figures. |
| `Trained_models/` | Stores serialized trained model artifacts for 17 antimicrobial phenotypes. |

## Project Structure

```text
Kpn_pan-genome_of_3163_isolates/
|-- README.md
|-- .gitignore
|-- Pan-genome_construction/
|   |-- Prokka_annotation.pbs
|   |-- run_Panaroo.pbs
|   |-- update_gff.pbs
|   |-- average_cluster_sequence.py
|   |-- longCentroidID_ref_from_gml.py
|   |-- AMR/
|   |   |-- AMR_annotate_csv.py
|   |   |-- AMR_annotate_fasta.pbs
|   |   |-- map_amr_and_panaroo.py
|   |   |-- rgi-annotation.pbs
|   |   `-- rgi_result_analyse.py
|   `-- cleaning_and_postupdate/
|       |-- clean_gene_presence_absence.py
|       |-- clean_msa_outliers.py
|       |-- classify_msa_by_ids.py
|       |-- contig_index_transform.py
|       |-- filt_serious_diff.py
|       |-- move_invalid_msa.py
|       |-- msa_contig_length_stats.py
|       `-- remove-.py
|-- Feature_extraction/
|   |-- concat_core_feature_matrix.py
|   |-- generate_dispensable_fm.py
|   |-- vcf2matrix.py
|   |-- snpEff/
|   |   |-- add_configure.py
|   |   |-- add_gff_info.py
|   |   |-- generate_gff.pbs
|   |   |-- make_genomes_folders.py
|   |   |-- ref_to_genomes_folder.py
|   |   |-- synonym_annotation.pbs
|   |   `-- synonym_annotation_sp.pbs
|   `-- variant_call/
|       |-- align-merge.pbs
|       |-- extract_gn_contigs.py
|       |-- generate_align_reference.py
|       |-- ref_for_alignment.py
|       `-- split_msa_by_contig.py
|-- Feature_selection/
|   |-- ML_sort/
|   |   |-- LR.py
|   |   |-- RF.py
|   |   |-- SVM.py
|   |   |-- XGboost.py
|   |   `-- script.py
|   `-- statistical_test/
|       |-- chi_analyse.py
|       |-- chi_kw.py
|       |-- kw_analyse.py
|       `-- toolkit.py
|-- Candidates_determine_and_model_train/
|   |-- ReadMe.txt
|   |-- ensemble_avg.py
|   |-- find_Kmed_avg.py
|   |-- list2fm.py
|   |-- model_save.py
|   |-- selected_fm.py
|   |-- test.py
|   `-- validation.py
|-- Further_analyzation/
|   |-- find_genes_position_pattern.py
|   `-- pattern_cochran_armitage_analyze.py
|-- Plot/
|   |-- Main-Figures/
|   |   |-- 2a.py
|   |   |-- 2b-data.py
|   |   |-- 2b.py
|   |   |-- 2c.R
|   |   |-- 2c.py
|   |   |-- 2d-data.py
|   |   |-- 2e-data.py
|   |   |-- 2e.py
|   |   |-- 2f-bar.py
|   |   |-- 2f-data.py
|   |   |-- 2f-pie.py
|   |   `-- 2ghi.py
|   `-- Supplement_Figures/
|       `-- sfig5.py
`-- Trained_models/
    |-- AMK_best_model.pkl
    |-- CAZ_best_model.pkl
    |-- CIP_best_model.pkl
    |-- CXM_best_model.pkl
    |-- CZO_best_model.pkl
    |-- ETP_best_model.pkl
    |-- FOX_best_model.pkl
    |-- GEN_best_model.pkl
    |-- IPM_best_model.pkl
    |-- LVX_best_model.pkl
    |-- MEM_best_model.pkl
    |-- NIT_best_model.pkl
    |-- SAM_best_model.pkl
    |-- SXT_best_model.pkl
    |-- TCY_best_model.pkl
    |-- TOB_best_model.pkl
    `-- TZP_best_model.pkl
```

## Workflow Overview

```text
Genome assemblies
      |
      v
Pan-genome construction and AMR annotation
      |
      v
Feature extraction from pan-genome, SNP, and annotation outputs
      |
      v
Feature selection by statistical tests and ML-based ranking
      |
      v
Candidate determination and model training
      |
      v
Trained models, downstream analysis, and publication figures
```