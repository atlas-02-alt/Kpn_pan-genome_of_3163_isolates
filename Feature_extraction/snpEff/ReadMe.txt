snpEff annotation scripts
=========================

This folder prepares per-gene snpEff databases and runs annotation of variant
VCF files so that synonymous variants can be identified and filtered later.

General usage
-------------

Most scripts use fixed relative paths and should be run from the project root
or from the directory expected by the path variables. Check the paths before
running.

Scripts
-------

add_configure.py
    Purpose:
        Append one genome configuration block per core-gene cluster to
        snpEff.config.
    Main input:
        core_gene_references
    Main output:
        Appended entries in snpEff.config
    Usage:
        If old custom entries exist in snpEff.config, clean them first. Then
        run:

            python add_configure.py

make_genomes_folders.py
    Purpose:
        Create one snpEff data folder per core gene under data.
    Main input:
        core_gene_sequences_with_ref
    Main output:
        <gene>
    Usage:

            python make_genomes_folders.py

ref_to_genomes_folder.py
    Purpose:
        Copy reference FASTA files from alignment folders into
        genomes using the gene/folder name.
    Main input:
        alignment
    Main output:
        <gene>.fa
    Usage:

            python ref_to_genomes_folder.py

generate_gff.pbs
    Purpose:
        Generate GFF files required by snpEff for each per-gene database.
        Some sequence conversions may fail and require correction by
        add_gff_info.py and synonym_annotation_sp.pbs.
    Usage:
        Edit paths and environment settings if needed, then submit:

            qsub generate_gff.pbs

add_gff_info.py
    Purpose:
        For GFF files that failed conversion, insert a fallback CDS annotation
        line using sequence length information from the file.
    Main input:
        empty_files.txt
    Main output:
        Modified genes.gff files
    Usage:
        Edit file_list and NEW_LINE if needed, then run:

            python add_gff_info.py

synonym_annotation.pbs
    Purpose:
        Run snpEff annotation on VCF files and generate annotated VCF outputs.
        Empty annotated VCF files indicate genes whose GFF conversion needs
        manual correction.
    Usage:

            qsub synonym_annotation.pbs

synonym_annotation_sp.pbs
    Purpose:
        Re-run snpEff annotation for problematic or empty VCF outputs after
        GFF correction.
    Usage:
        Prepare the empty-file list expected by the script, adjust paths if
        needed, then submit:

            qsub synonym_annotation_sp.pbs
