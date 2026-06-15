# Kpn Pan-Genome Analysis of 3,163 Isolates

(Draft version; still under revision)
剩余任务：1.准确化workflow 2.给每个代码文件写说明，让人看懂怎么用

This repository contains scripts, trained models, and plotting utilities for a pan-genome-based analysis of 3,163 *Klebsiella pneumoniae* isolates. The workflow covers pan-genome construction, feature extraction, feature selection, candidate determination, model training, downstream analysis, and figure generation.

Usage documentation for each script will be provided in the README file in the same folder.

## Workflow Overview

```text
Genome assemblies (annotated)
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
