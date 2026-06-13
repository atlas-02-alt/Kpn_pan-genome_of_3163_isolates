library(data.table)

full_feature_path <- "../../Figures-re/fig3部分相关数据/supplement/final_dispensable_feature_matrix.csv"
full_phenotype_path <- "../../Figures-re/fig5相关数据/supplement/phenotypes_3163.csv"
target_feature_path <- "fig5d-result/fig5c-amk-feature-matrix.csv"
target_phenotype_path <- "fig5d-result/fig5c-amk-phenotype-matrix-raw.csv"

sample_col <- "Unnamed: 0"

old_feature <- fread(target_feature_path, nrows = 0)
feature_cols <- setdiff(names(old_feature), sample_col)

full_feature_header <- names(fread(full_feature_path, nrows = 0))
full_feature_sample_col <- full_feature_header[1]
missing_features <- setdiff(feature_cols, full_feature_header)
if (length(missing_features) > 0) {
  stop("Missing feature columns in full matrix: ", paste(missing_features, collapse = ", "))
}

selected_feature_cols <- c(full_feature_sample_col, feature_cols)
full_feature <- fread(full_feature_path, select = selected_feature_cols)
setnames(full_feature, full_feature_sample_col, sample_col)

full_phenotype <- fread(full_phenotype_path, header = TRUE)
setnames(full_phenotype, names(full_phenotype)[1], sample_col)
full_phenotype <- full_phenotype[AMK %in% c("S", "I", "R"), .(sample_id = get(sample_col), AMK)]
setnames(full_phenotype, "sample_id", sample_col)

sample_order <- intersect(full_phenotype[[sample_col]], full_feature[[sample_col]])
feature_out <- full_feature[match(sample_order, full_feature[[sample_col]])]
phenotype_out <- full_phenotype[match(sample_order, full_phenotype[[sample_col]])]

target_feature_tmp <- paste0(target_feature_path, ".new")
target_phenotype_tmp <- paste0(target_phenotype_path, ".new")

fwrite(feature_out, target_feature_tmp)
fwrite(phenotype_out, target_phenotype_tmp)

if (file.exists(target_feature_path)) {
  unlink(target_feature_path)
}
if (file.exists(target_phenotype_path)) {
  unlink(target_phenotype_path)
}
file.rename(target_feature_tmp, target_feature_path)
file.rename(target_phenotype_tmp, target_phenotype_path)

message("Saved feature matrix: ", target_feature_path, " (", nrow(feature_out), " samples x ", length(feature_cols), " features)")
message("Saved phenotype matrix: ", target_phenotype_path)
message("AMK counts:")
print(phenotype_out[, .N, by = AMK][order(AMK)])
