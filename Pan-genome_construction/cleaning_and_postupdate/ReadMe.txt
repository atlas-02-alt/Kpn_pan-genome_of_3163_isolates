Pan-genome cleaning and post-update scripts
==========================================

This folder contains scripts used after Panaroo to clean MSA files, identify
problematic gene clusters, classify genes by prevalence, and build a
gene-by-sample contig matrix.

Recommended workflow
--------------------

1. Remove gap or non-ATCG characters from aligned gene sequences if needed.
2. Summarize MSA length distributions.
3. Filter gene clusters with serious reference/mode length differences.
4. Move invalid MSA files out of the analysis set, which don't exist in the reference genome.
5. Remove remaining length outlier contigs.
6. Classify cleaned genes as core, dispensable, or rare.

Scripts
-------

remove-.py
    Purpose:
        Remove non-ATCG characters, including alignment gap characters, from
        FASTA/MSA sequences.
    Main input:
        aligned_gene_sequences
    Main output:
        gene_sequences
    Usage:
        Edit input_folder and output_folder if needed, then run:

            python remove-.py

msa_contig_length_stats.py
    Purpose:
        For each MSA, calculate the modal sequence length, reference length,
        total sequence count, and number of sequences outside mode +/- 20%.
    Usage:

            python msa_contig_length_stats.py <pan_genome_reference.fa> <msa_dir> <output.tsv>

filt_serious_diff.py
    Purpose:
        Filter the MSA length summary and identify clusters where the reference
        length and modal MSA length differ by more than 100 bp and more than
        20%.
    Usage:

            python filt_serious_diff.py <msa_length_summary.tsv> <serious_diff.tsv>

move_invalid_msa.py
    Purpose:
        Move low-confidence MSA files listed in serious_diff.tsv into an
        invalid folder so that they are not used in downstream analysis.
    Usage:

            python move_invalid_msa.py <serious_diff.tsv> <msa_dir> <output_dir>

clean_msa_outliers.py
    Purpose:
        Remove contig sequences whose lengths are outside mode +/- 20% within
        each MSA and write cleaned MSA files to a new folder.
    Usage:

            python clean_msa_outliers.py <msa_dir> <output_dir>

classify_msa_by_ids.py
    Purpose:
        Classify cleaned gene-cluster MSA files by sample prevalence:
        core genes are present in more than 90% of 3,163 isolates;
        dispensable genes are present in more than 3 isolates but below the
        core threshold; rare genes are present in at most 3 isolates.
    Usage:

            python classify_msa_by_ids.py <cleaned_msa_dir> <classified_output_dir>

clean_gene_presence_absence.py
    Purpose:
        Build a gene-by-sample matrix from .fas files. Rows are genes, columns
        are samples, and each cell records the full contig/header names where
        the gene is present.
    Usage:

            python clean_gene_presence_absence.py -i <input_fas_dir> -o <gene_contig_matrix.tsv>

contig_index_transform.py
    Purpose:
        Convert contig/header identifiers in the gene-by-sample matrix using
        Panaroo gene_data.csv mappings. It builds or reuses an on-disk SQLite
        mapping database for large files.
    Usage:
        Run with --help to see all available options:

            python contig_index_transform.py --help
