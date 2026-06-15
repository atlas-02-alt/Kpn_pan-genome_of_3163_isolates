Pan-genome construction scripts
===============================

This folder contains scripts used to annotate genomes, run Panaroo, update GFF
files, and generate representative pan-genome reference sequences.

General usage
-------------

Most scripts in this folder use fixed relative paths. Before running them,
check the input and output paths near the top of each script and edit them for
the current working directory.

PBS or shell scripts can be submitted on a cluster with:

    qsub <script>.pbs

Python scripts can be run with:

    python <script>.py

Scripts
-------

Prokka_annotation.pbs
    Purpose:
        Batch annotation of genome assemblies with Prokka.
    Usage:
        Edit the input genome directory, output directory, conda environment,
        and cluster resource settings if needed, then submit with qsub.

run_Panaroo.pbs
    Purpose:
        Run Panaroo on GFF files to construct the pan-genome. The current
        command uses strict cleaning, pan alignment, MAFFT, a core threshold of
        0.9, 48 threads, and writes results to result.
    Usage:
        Put input .gff files in the working directory or adjust the -i path,
        activate the panaroo environment, then run:

            qsub run_Panaroo.pbs

update_gff.pbs
    Purpose:
        Run panaroo-generate-gffs to update input GFF files for downstream
        Panaroo analysis.
    Usage:
        Place source GFF files under GFFs or edit the -i path. Submit with:

            qsub update_gff.pbs

longCentroidID_ref_from_gml.py
    Purpose:
        Build a complete pan-genome reference FASTA by mapping each Panaroo
        cluster to its longCentroidID and retrieving the corresponding DNA
        sequence from gene_data.csv.
    Main inputs:
        cluster_centroid_summary.tsv
        gene_data.csv
    Main output:
        complete_pan_genome_reference.fasta
    Usage:
        Edit gml_file, csv_file, tsv_file, and out_fasta if needed, then run:

            python longCentroidID_ref_from_gml.py

average_cluster_sequence.py
    Purpose:
        Generate one representative sequence for each gene cluster. Single
        sequence FASTA files are copied directly; MSA files are converted into
        a consensus sequence by taking the most frequent non-gap base at each
        alignment position.
    Main input:
        aligned_gene_sequences
    Main output:
        pan_genome_represent.fa
    Usage:
        Edit msa_dir and out_fasta if needed, then run:

            python average_cluster_sequence.py
