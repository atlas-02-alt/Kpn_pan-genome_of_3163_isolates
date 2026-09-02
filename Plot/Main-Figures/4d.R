library(data.table)
library(pheatmap)

sample_col <- "Unnamed: 0"
sir_colors <- c("S" = "#2E8B57", "I" = "#FFD700", "R" = "#DC143C")

plot_feature_heatmap <- function(
  feature_path,
  phenotype_path,
  antibiotics,
  out_prefix,
  title,
  width = 12,
  height = 4
) {
  gene_presence_absence <- fread(feature_path, sep = ",", stringsAsFactors = FALSE)
  phenotype_info <- fread(phenotype_path, sep = ",", stringsAsFactors = FALSE)

  feature_cols <- setdiff(names(gene_presence_absence), sample_col)
  gene_presence_absence_matrix <- as.data.frame(
    gene_presence_absence[, feature_cols, with = FALSE]
  )
  rownames(gene_presence_absence_matrix) <- gene_presence_absence[[sample_col]]

  gene_matrix <- as.matrix(gene_presence_absence_matrix)
  mode(gene_matrix) <- "numeric"

  annotation_data <- as.data.frame(phenotype_info[, antibiotics, with = FALSE])
  annotation_data[annotation_data == ""] <- NA
  rownames(annotation_data) <- phenotype_info[[sample_col]]
  for (col in colnames(annotation_data)) {
    annotation_data[[col]] <- factor(annotation_data[[col]], levels = c("S", "I", "R"))
  }

  common_samples <- intersect(rownames(gene_matrix), rownames(annotation_data))
  heatmap_matrix <- t(gene_matrix[common_samples, , drop = FALSE])
  annotation_data <- annotation_data[common_samples, , drop = FALSE]

  annotation_colors <- setNames(
    replicate(length(antibiotics), sir_colors, simplify = FALSE),
    antibiotics
  )

  draw_heatmap <- function(filename = NA) {
    pheatmap(
      heatmap_matrix,
      filename = filename,
      cluster_rows = TRUE,
      cluster_cols = TRUE,
      clustering_distance_rows = "binary",
      clustering_distance_cols = "binary",
      clustering_method = "ward.D2",
      treeheight_row = 35,
      treeheight_col = 35,
      annotation_col = annotation_data,
      annotation_colors = annotation_colors,
      show_rownames = TRUE,
      show_colnames = FALSE,
      color = c("#F7FBFF", "#2171B5"),
      breaks = c(-0.5, 0.5, 1.5),
      legend_breaks = c(0, 1),
      legend_labels = c("Absent", "Present"),
      fontsize = 10,
      fontsize_row = 8,
      fontsize_col = 8,
      border_color = NA,
      annotation_legend = TRUE,
      main = title,
      width = width,
      height = height
    )
  }

  out_pdf <- paste0(out_prefix, ".pdf")
  out_png <- paste0(out_prefix, ".png")
  draw_heatmap(out_pdf)
  draw_heatmap(out_png)

  message("Saved: ", out_pdf)
  message("Saved: ", out_png)
}

plot_feature_heatmap(
  feature_path = "fig5d-result/fig5c-Ceph3-feature-matrix.csv",
  phenotype_path = "fig5d-result/fig5c-Ceph3-phenotype-matrix-raw.csv",
  antibiotics = c("CAZ", "CXM", "CZO"),
  out_prefix = "fig5d-result/fig5c-Ceph3-heatmap",
  title = "Cephalosporin Feature Presence/Absence Heatmap"
)
