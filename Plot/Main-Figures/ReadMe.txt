Main figure scripts
===================

This folder contains the Python and R scripts currently used to prepare data
or draw main-text figure panels. The scripts are not a single automated
pipeline. Some accept command-line arguments, while others contain fixed input
paths, output paths, selected features, or plotting values. Relative paths are
resolved from the directory in which a command is run. Prepare the required
intermediate files and review the path and parameter settings in each script
before running it.

General usage
-------------

Python scripts without required command-line arguments:

    python <script>.py

R scripts without required command-line arguments:

    Rscript <script>.R

Scripts with required or useful command-line arguments have concrete examples
in their individual entries below. Several plotting scripts call plt.show() or
print a ggplot object without saving it; these are identified explicitly.

Scripts
-------

2a.py
    Purpose:
        Read a gene-by-sample gene_contig_matrix.tsv, convert non-empty cells
        to gene presence, and reorder samples as GN, then GC, then other
        samples. Classify genes over the full dataset as core, dispensable, or
        rare, calculate the observed cumulative union as samples are added,
        and draw a stacked pan-genome accumulation curve. The script also
        writes the curve values and per-gene prevalence classifications.
    Usage:
        The input matrix is required. Output paths and classification
        thresholds are optional arguments. For example:

            python 2a.py --input gene_contig_matrix.tsv

2a.R
    Purpose:
        Read the fixed file add1-pangenome_accumulation_curve_summary.tsv and
        redraw its core, dispensable, and rare counts as a ggplot2 stacked area
        chart. The script writes add1-pangenome_accumulation_curve.pdf and
        add1-pangenome_accumulation_curve.png. These fixed names do not match
        the default output names of 2a.py unless they are edited or renamed.
    Usage:
        Edit input_file, output_pdf, and output_png if needed, then run:

            Rscript 2a.R

2b-data.py
    Purpose:
        Read amr_panaroo_dict.json and compare its AMR identifiers and mapped
        identifiers with the filenames in fixed core, dispensable, and rare
        gene-sequence directories. Count AMR entries assigned to each gene
        class, collect unmatched entries, and print the classification results
        and final core/dispensable/rare counts. The script does not write a
        summary table.
    Usage:
        Place the JSON file and four sequence directories at the fixed paths,
        or edit those paths, then run:

            python 2b-data.py

2c-data.py
    Purpose:
        Scan VCF or VCF.GZ files in the fixed annotated-variant directory and
        inspect sample genotypes for each ALT allele. Classify alleles as SNP,
        insertion, deletion, complex, or symbolic structural variant, and
        count whether each allele occurs in both GN and GC samples, GN samples
        only, or GC samples only. Counts are printed. Unexpected sample IDs,
        variants found in neither group, and unhandled genotype values are
        written to diagnostic TSV files when present.
    Usage:
        Edit vcf_dir and the diagnostic output constants if needed, then run:

            python 2c-data.py

2c.py
    Purpose:
        Draw a two-panel stacked bar chart from variant counts hard-coded in
        the script. The left panel contains SNP counts and the right panel
        contains insertion and deletion counts, each divided into Shared,
        GC Only, and GN Only. The figure is saved as 2e_variant_counts.pdf.
    Usage:
        Edit the data dictionary or output filename if needed, then run:

            python 2c.py

2d-data.py
    Purpose:
        Read uncompressed *.vcf files from the fixed snpEff annotation
        directory, extract every effect term from the ANN field, count the
        terms across files, and print them in descending frequency order. No
        output file is written.
    Usage:
        Edit the VCF glob path if needed, then run:

            python 2d-data.py

2d-bar.py
    Purpose:
        Draw a bar chart of the less frequent snpEff effect categories from a
        hard-coded count dictionary. Synonymous and missense counts are not in
        this dictionary. The plot is displayed with plt.show() and is not
        saved by the script.
    Usage:
        Edit the hard-coded data if needed, then run:

            python 2d-bar.py

2d-pie.py
    Purpose:
        Group a hard-coded snpEff effect-count dictionary into Synonymous,
        Missense, and Other categories and draw a pie chart. The three totals
        are printed, and the plot is displayed with plt.show() without being
        saved.
    Usage:
        Edit the hard-coded data if needed, then run:

            python 2d-pie.py

2efg.py
    Purpose:
        Read a tab-delimited KEGG enrichment table, retain rows below a q-value
        cutoff, and draw a horizontal bar plot of -log10(qvalue). When
        GeneRatio is present it controls the bar colors. The selected rows are
        reported in the terminal and the figure is saved as a PDF using the
        requested output stem. The number of selected rows is reported in the
        terminal.
    Usage:
        The defaults are core_dis.list.xls, a q-value cutoff of 0.05, and a
        PDF output in the current working directory. For example:

            python 2efg.py --input core_dis.list.xls --output kegg-barplot.pdf

3b-data.py
    Purpose:
        Read the fixed candidate-feature summary CSV and, within each Medical
        class, count distinct known and unknown variant features and gene
        features. Known status is determined by the hard-coded is_known_gene
        rules. The per-class counts are printed; no data file is written.
    Usage:
        Edit csv_path or the known-gene rules if needed, then run:

            python 3b-data.py

3b.py
    Purpose:
        Read the med sheet of the fixed candidate-distribution workbook and
        draw its first two data columns as a horizontal stacked bar chart.
        Rows use fixed per-row colors and the two columns use solid and
        hatched fills to represent the workbook categories. The plot is
        displayed with plt.show() and is not saved.
    Usage:
        Edit the workbook path, selected columns, row colors, or labels if
        needed, then run:

            python 3b.py

3c.py
    Purpose:
        Draw a per-antibiotic test ROC-AUC bar chart for 17 antibiotics using
        values hard-coded in the script. The figure is saved to the fixed path
        ./Figures-re/fig4/4b-test.pdf.
    Usage:
        Edit the hard-coded AUC values or output path if needed, then run:

            python 3c.py

3d.py
    Purpose:
        Read the fixed ablation-comparison workbook and compare test and
        validation AUC values for Total, Core, and Dispensable feature sets.
        Draw six boxplots with the individual antibiotic values overlaid. The
        plot is displayed with plt.show() and is not saved.
    Usage:
        Edit file_path if needed, then run:

            python 3d.py

3de-u_test.py
    Purpose:
        Read the fixed ablation-comparison workbook copy, remove NIT, and run a
        one-sided Mann-Whitney U test of test-auc greater than dis-test-auc.
        The statistic, p-value, and a significance message are printed.
    Usage:
        Edit file_path or the compared column names if needed, then run:

            python 3de-u_test.py

3e.py
    Purpose:
        Read the fixed ablation-comparison workbook and compare Total with
        Known-only feature sets for test and validation AUC. Draw four
        boxplots, overlay individual antibiotic values, and connect each
        paired Total/Known observation. The plot is displayed with plt.show()
        and is not saved.
    Usage:
        Edit file_path if needed, then run:

            python 3e.py

4a-data.py
    Purpose:
        Read a feature-analysis Excel workbook, select the top-N gene features
        with rank ties or all gene features for specified antibiotics, and
        form their ordered union. Match that union against a FASTA file after
        removing one trailing numeric suffix from each FASTA identifier, then
        write the matched records to a new FASTA file. An optional text file
        can record the union feature list.
    Usage:
        Input paths have fixed defaults but can be supplied as arguments. For
        example:

            python 4a-data.py --xlsx features_analyse.xlsx --fasta proteins.fa --drugs IPM,MEM,ETP --mode top --top-n 5 --out-fa selected.fa --out-features selected.txt

4a.py
    Purpose:
        Read one or two tab-delimited KEGG enrichment tables and retain rows
        below a q-value cutoff. With one table, draw one horizontal enrichment
        panel and write a PDF plus a selected-row TSV. With --input-bottom,
        draw vertically stacked top and bottom panels with a shared GeneRatio
        color scale, and write the requested figure, a PDF copy, and separate
        selected-row TSV files for the two panels.
    Usage:
        Single-table example:

            python 4a.py --input core.list.xls --output core-kegg.png

        Two-panel example:

            python 4a.py --input core.list.xls --input-bottom dispensable.list.xls --output core-dispensable-kegg.png

4bc-graph-data.py
    Purpose:
        Read the fixed snpEff-annotated VCF into a DataFrame, reduce sample
        genotype fields to binary absence/presence values, transpose the data
        into a sample-by-variant matrix, and count samples in the four binary
        combinations of the fixed variants 947_G->A and 948_G->T. The four
        counts are printed. Writing the feature matrix is currently commented
        out.
    Usage:
        Edit file_path and the two selected variant columns if needed, then
        run:

            python 4bc-graph-data.py

4bc-lor-data.py
    Purpose:
        Join a fixed binary feature matrix to a phenotype table for the fixed
        target feature and first selected antibiotic, calculate the four
        feature/phenotype contingency counts, and print them. The current code
        then replaces those calculated counts with the hard-coded values 7,
        1768, 7, and 119, adds 0.5 to each cell, and prints the resulting
        log2 odds ratio.
    Usage:
        Review the hard-coded replacement counts as well as fpath, ppath,
        target_gene, and selected_antibiotics before running:

            python 4bc-lor-data.py

4bc-lor.py
    Purpose:
        Render the hard-coded 2-by-2 array [[1768, 7], [119, 7]] as a table
        with no axes. Save it to the fixed path
        ./Figures-re/fig5/5d-ompA-NIT-LorData.pdf and also display it with
        plt.show().
    Usage:
        Edit the table values or output path if needed, then run:

            python 4bc-lor.py

4d.R
    Purpose:
        Read a fixed binary feature matrix and phenotype matrix, retain common
        samples, and draw a clustered feature presence/absence heatmap. CAZ,
        CXM, and CZO S/I/R phenotypes are shown as column annotations. The
        current call writes PDF and PNG files with the fixed
        fig5d-result/fig5c-Ceph3-heatmap prefix.
    Usage:
        Edit the paths, antibiotics, output prefix, or title in the final
        plot_feature_heatmap call if needed, then run:

            Rscript 4d.R

4e.R
    Purpose:
        Draw a gene-order diagram for the three hard-coded haplotypes P3, P2,
        and P1 using fixed gene names, lengths, gaps, and colors. The ggplot is
        printed to the active graphics device; the script does not save a
        file.
    Usage:
        Edit the hard-coded haplotype data or add a save call if needed, then
        run:

            Rscript 4e.R

4f.R
    Purpose:
        Read the fixed normalized HuiNET yearly pattern-count CSV, keep its
        first three rows, and draw a 2006-2020-style prevalence heatmap. Rows
        are labelled P1, P2, and P3 in input order. The script writes the fixed
        PDF HuiNET_year_counts_2006_2020_normalized_heatmap_top3.pdf.
    Usage:
        Edit infile or out_pdf if needed, then run:

            Rscript 4f.R

4g-data.R
    Purpose:
        Calculate year-specific internal log2 odds ratios for the first N
        gene-order patterns and the CAZ, CXM, and CZO phenotypes. In HuiNET
        mode, years are inferred from GN sample IDs. In Houston mode, samples
        and years come from PATRIC_Houston_samples_year.csv. Pattern-summary
        paths are fixed by mode, while the phenotype CSV can be supplied by an
        argument. The script writes one long TSV and one detailed matrix TSV
        per antibiotic; it does not draw a figure.
    Usage:
        --mode is required and must be HuiNET or Houston. For example:

            Rscript 4g-data.R --mode HuiNET --pheno-csv phenotypes_3163.csv --out-prefix fig4g_HuiNET_pattern_lor --top-n 10

4g.R
    Purpose:
        Read the long TSV generated by 4g-data.R, select requested drugs and
        patterns, calculate Pearson correlations between year and internal
        LOR, and write a correlation summary TSV. For each selected pattern,
        draw yearly LOR points and drug-specific linear fits and save a PDF.
        When --pages is supplied, matching PNG pages are also written.
    Usage:
        --values-tsv is required. An output prefix can be supplied explicitly
        or inferred from an input basename ending in _long.tsv. For example:

            Rscript 4g.R --values-tsv fig4g_HuiNET_pattern_lor_long.tsv --out-prefix fig4g_HuiNET_pattern_lor --patterns P1,P2,P3
