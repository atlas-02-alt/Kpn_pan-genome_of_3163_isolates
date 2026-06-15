Downstream analysis scripts
===========================

This folder contains downstream analyses for selected candidate features,
including permutation-based feature importance, gene-order pattern discovery,
and pattern-prevalence analysis over time.

Scripts
-------

permutation_ranking.py
    Purpose:
        Compute permutation importance for saved models using concatenated test
        and validation feature matrices. Results can be normalized and written
        per antibiotic.
    Usage:
        Edit MODEL_PATH_TEMPLATE, TEST_PATH_TEMPLATE, VALIDATION_PATH_TEMPLATE,
        OUTPUT_DIR, and other options near the top of the script, then run:

            python permutation_ranking.py

find_genes_position_pattern.py
    Purpose:
        Analyze the genomic order patterns of target genes in each sample using
        a CSV matrix and matching GFF/GFF3 files. Only when genes are on a same
        contig and adjacent will them be considered to form a pattern with more
        than one gene.
    Usage:

            python find_genes_position_pattern.py --csv <matrix.csv> --gff-dir <gff_dir> --out-dir <output_dir>

        Optional arguments include --target-genes, --sample-start-col, and
        --min-genes-per-pattern. Run --help for details.

count_empty_pattern_samples.py
    Purpose:
        Count samples where all target-gene rows are empty in a CSV matrix,
        which means that these samples don't have any gene patterns you are
        interested in.
    
    Usage:

            python count_empty_pattern_samples.py --csv <matrix.csv> --out <status.tsv>

        Optional arguments include --target-genes, --gff-dir,
        --sample-start-col, and --check-sample.

pattern_cochran_armitage_analyze.py
    Purpose:
        Run Cochran-Armitage trend tests for gene-order pattern prevalence
        across collection years. HuiNET years are parsed from GN sample IDs and
        Houston years are read from a sample-year table. 
    Usage:

            python pattern_cochran_armitage_analyze.py --collection both --phenotype <phenotypes.csv> --huinet-summary <HuiNET_pattern_summary.csv> --houston-summary <Houston_pattern_summary.csv> --houston-year <PATRIC_Houston_samples_year.csv> --outdir <results>
