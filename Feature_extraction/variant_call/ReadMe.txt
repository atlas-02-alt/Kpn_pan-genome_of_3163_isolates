Core-gene variant-calling preparation scripts
=============================================

This folder prepares core-gene sequences and reference sequences for alignment
and variant calling.

Scripts
-------

extract_gn_contigs.py
    Purpose:
        Extract the GN191724 reference contig from each core-gene MSA. If a
        matching reference sequence is not found, the entire MSA is moved to a
        no-match folder.
    Usage:

            python extract_gn_contigs.py <msa_dir> <output_contigs_dir> <no_match_dir>

generate_align_reference.py
    Purpose:
        Merge all core-gene reference FASTA files into one FASTA file used for
        alignment/variant extraction. Gene names are replaced with AMR names
        when found in amr_panaroo_dict.json.
    Main inputs:
        core_gene_references
        amr_panaroo_dict.json
    Main output:
        all_core_align_references.fasta
    Usage:
        Edit folder_path, output_file, and json_dict path if needed, then run:

            python generate_align_reference.py

ref_for_alignment.py
    Purpose:
        Copy each core-gene reference sequence into its alignment subfolder as
        ref.fa.
    Main input:
        core_gene_references
    Main output:
        ref.fa
    Usage:

            python ref_for_alignment.py

split_msa_by_contig.py
    Purpose:
        Split each core-gene MSA into one FASTA file per contig/sample, with
        one output subfolder per gene cluster.
    Usage:

            python split_msa_by_contig.py <msa_dir> <output_dir>

align-merge.pbs
    Purpose:
        Cluster submission script for aligning per-contig sequences against
        the gene reference and merging alignment or variant-calling outputs.
    Usage:
        Edit paths, environment settings, and resource requests for the current
        cluster, then submit:

            qsub align-merge.pbs
