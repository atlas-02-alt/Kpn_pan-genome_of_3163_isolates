Supplementary figure scripts
============================

This folder contains the Python and R scripts currently used to prepare data
or draw supplementary figure panels. These scripts are independent rather
than a single automated pipeline. Their input paths, output paths, selected
features, and plotting values are mostly fixed in the source code. Relative
paths are resolved from the directory in which a command is run. Prepare the
required intermediate files and review the settings in each script before
running it.

General usage
-------------

Python scripts:

    python <script>.py

R scripts:

    Rscript <script>.R

None of the scripts in this folder currently defines command-line arguments.
Edit fixed paths or parameters in the relevant script when necessary. Some
plots are displayed interactively without being saved; these are identified
below.

Scripts
-------

sfig1A.py
    Purpose:
        Read two fixed two-column text files containing strain IDs and contig
        N50 values for pure short-read and hybrid long+short-read assemblies.
        Merge the records, sort them by descending N50, and draw a bar chart
        colored by assembly method. The plot is displayed with plt.show() and
        is not saved by the script.
    Usage:
        Edit the two input paths if needed, then run:

            python sfig1A.py

sfig1B-data.py
    Purpose:
        Scan all *.gff files in the fixed ./GFFs directory, count records whose
        third field is CDS, sort samples by descending CDS count, and write
        sample ID and count pairs to ./sample_gene_counts.txt.
    Usage:
        Edit input_directory or output_txt if needed, then run:

            python sfig1B-data.py

sfig1B.py
    Purpose:
        Read a fixed per-sample gene-count file and two fixed contig-N50 files.
        Assign samples to pure short-read or hybrid long+short-read groups by
        their presence in the two N50 files, perform a one-sided Mann-Whitney U
        test for greater gene counts in the hybrid group, and draw a boxplot.
        The plot is displayed with plt.show(). Although OUTPUT_FILE is defined,
        the current script does not use it and does not save the figure.
    Usage:
        Edit INPUT_FILE and the two N50 input paths if needed, then run:

            python sfig1B.py

sfig6.py
    Purpose:
        Collect selected core-variant and dispensable-gene features from fixed
        feature-selection result files for 17 antibiotics. Check whether each
        feature occurs within the antibiotic-specific number of leading rows
        in RF, LR, SVM, and XGBoost importance tables. Write the resulting
        binary support matrix to model_evidence_support_summary.csv and
        display its model-set intersections as an UpSet plot. The UpSet plot
        is not saved because its save call is currently commented out.
    Usage:
        Edit target_dir, folder_path, antibiotic list, or rank thresholds if
        needed, then run:

            python sfig6.py

sfig13.R
    Purpose:
        Read the fixed normalized HuiNET yearly pattern-count CSV and draw a
        heatmap of all pattern rows across the available year columns. Rows
        are labelled P1, P2, and so on in input order, and values represent the
        percentage in sampled isolates. The script writes both
        HuiNET_year_counts_2006_2020_normalized_heatmap.png and
        HuiNET_year_counts_2006_2020_normalized_heatmap.pdf.
    Usage:
        Edit infile, out_png, or out_pdf if needed, then run:

            Rscript sfig13.R
