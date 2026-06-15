# Kpn Pan-Genome Analysis of 3,163 Isolates

(Draft version; ReadMe files still under revision)

This repository contains scripts, trained models, and plotting utilities for a pan-genome-based analysis of 3,163 *Klebsiella pneumoniae* isolates. The workflow covers pan-genome construction, feature extraction, feature selection, candidate determination, model training, downstream analysis, and figure generation.

## Directory Guide

The repository is organized by analysis stage, so each top-level directory represents one major part of the pipeline.

| Directory | Purpose |
| --- | --- |
| `Pan-genome_construction/` | Builds and post-processes the pan-genome, including genome annotation, Panaroo execution, GFF updates, AMR annotation, and gene cluster cleaning of pan-genome outputs. |
| `Feature_extraction/` | Identifies core-gene variants through single-base-resolution alignment, annotates variants with snpEff, retains non-synonymous variants, and encodes them together with dispensable gene presence/absence into binary feature matrices. |
| `Feature_selection/` | Screens the full feature set using statistical tests and ranks features based on machine-learning-derived importance scores. |
| `Candidates_determine_and_model_train/` | Determines candidate features, prepares selected feature matrices, trains models, tests and validates performance, and saves model artifacts. |
| `Further_analyzation/` | Performs downstream biological analyses, including candidate-feature prioritization and transposon-associated genomic pattern analysis. |
| `Plot/` | Contains scripts for generating main and supplementary figures. |
| `Trained_models/` | Stores serialized trained model artifacts for 17 antimicrobial phenotypes. |
| `AMR_phenotypes/` | Contains AMR phenotype data for HuiNet isolates (with GN-prefixed sample IDs) and PATRIC isolates (with GC-prefixed sample IDs); some PATRIC phenotypes are not available in the source database. |

## Code Guide

Usage documentation for each script will be provided in the README file in the same folder.

## Workflow Overview

```text
Genome assemblies (annotated)
      |
      v
Pan-genome construction and AMR annotation
      |
      v
Gene cluster cleaning
      |
      v
Core-gene variant calling and synonymous substitution filtering
      |
      v
Rare feature filtering
      |
      v
Feature selection by statistical tests and ML-based ranking
      |
      v
Candidate determination and model training
      |                           |
      v                           |
Model testing and validation      |
                                  v
                          Downstream analysis
```
