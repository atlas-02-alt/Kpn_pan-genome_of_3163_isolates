AMR annotation scripts
======================

This folder contains scripts for annotating pan-genome representative
sequences against antimicrobial-resistance databases and mapping AMR hits back
to Panaroo gene-cluster names.

General usage
-------------

Most scripts use fixed relative paths. Check the paths near the top of each
script before running.

Scripts
-------

AMR_annotate_fasta.pbs
    Purpose:
        Run ABRicate against NCBI, CARD, and ResFinder databases on the
        pan-genome representative FASTA.
    Main input:
        pan_genome_average_represent.fa
    Main outputs:
        both_ncbi_results.tab
        both_card_results.tab
        both_resfinder_results.tab
    Usage:
        Activate the AMR_ann environment then submit.

AMR_annotate_csv.py
    Purpose:
        Combine ABRicate hits with Panaroo gene_presence_absence.csv and keep
        gene clusters with a hit in at least one AMR database.
    Main inputs:
        gene_presence_absence.csv
        ABRicate result tables under AMR_annotation
    Main output:
        amr_gene_presence_absence_longCentroidID.csv
    Usage:
        Edit panaroo_csv, abricate_files, and output_filtered if needed, then
        run:

            AMR_annotate_csv.py

map_amr_and_panaroo.py

    ※Before running this code, please insert a new column at the beginning 
    of amr_gene_presence_absence.csv and manually enter the annotation result 
    for each gene cluster. The final selection of annotation sources or 
    database results to be adopted for each gene cluster should be determined 
    by the user.

    Purpose:
        Build a JSON dictionary mapping Panaroo gene-cluster IDs to AMR gene
        names. AMR names are prefixed with "amr_".
    Main input:
        amr_gene_presence_absence.csv
    Main output:
        amr_panaroo_dict.json
    Usage:
        Edit the input/output paths if needed, then run:

            python map_amr_and_panaroo.py

rgi-annotation.pbs
    Purpose:
        Extract CDS/rRNA/tRNA sequences from post-Panaroo GFF files and run RGI
        annotation-related processing on the resulting FASTA files.
    Main input:
        postpanaroo_gffs
    Main output:
        postpanaroo_fas
    Usage:
        Edit GFF_DIR, OUTPUT_BASE_DIR, THREADS, and environment settings if
        needed, then submit.

rgi_result_analyse.py
    Purpose:
        Parse RGI JSON outputs and collect unique functional mutation models
        with selected model_type_id values.
    Main input:
        rgi_results
    Main output:
        all_functional_mutations.txt
    Usage:
        Edit rgi_root if needed, then run:

            python rgi_result_analyse.py
