args <- commandArgs(trailingOnly = TRUE)

get_arg <- function(flag, default = NULL) {
  idx <- which(args == flag)
  if (length(idx) == 0 || idx[length(idx)] == length(args)) return(default)
  args[idx[length(idx)] + 1]
}

find_first_existing <- function(paths) {
  hits <- paths[file.exists(paths)]
  if (length(hits) == 0) return(NA_character_)
  hits[1]
}

default_csv <- find_first_existing(c(
  "../../Figures-re/fig4部分相关数据/supplement/phenotypes_3163.csv",
  "../Figures-re/fig4部分相关数据/supplement/phenotypes_3163.csv",
  "./phenotypes_3163.csv",
  "c:/Users/DELL/Nutstore/1/我的坚果云/Klebsiella_pneumoniae/Figures-re/fig4部分相关数据/supplement/phenotypes_3163.csv"
))

corrected_default_csv <- find_first_existing(c(
  "../../Figures-re/fig4部分相关数据/supplement/phenotypes_3163.csv",
  "../Figures-re/fig4部分相关数据/supplement/phenotypes_3163.csv",
  "./phenotypes_3163.csv",
  "c:/Users/DELL/Nutstore/1/我的坚果云/Klebsiella_pneumoniae/Figures-re/fig4部分相关数据/supplement/phenotypes_3163.csv"
))
if (!is.na(corrected_default_csv)) {
  default_csv <- corrected_default_csv
}

input_csv <- get_arg("--pheno-csv", default_csv)
mode <- get_arg("--mode", NA_character_)
if (is.na(mode)) {
  stop("Please pass --mode HuiNET or --mode Houston")
}
mode <- match.arg(mode, c("HuiNET", "Houston"))
mode_paths <- c(
  HuiNET = find_first_existing(c(
    "fig5d-further_analyse/HuiNET_pattern_summary.csv"
  )),
  Houston = find_first_existing(c(
    "fig5d-further_analyse/Houston_pattern_summary.csv"
  ))
)
input_tsv <- mode_paths[[mode]]
out_prefix <- get_arg("--out-prefix", paste0("fig4g_", mode, "_pattern_lor"))
top_n <- as.integer(get_arg("--top-n", "10"))
houston_year_csv <- "PATRIC_Houston_samples_year.csv"

if (!file.exists(input_tsv)) {
  stop(paste0("Cannot find fixed pattern CSV for ", mode, " mode: ", input_tsv))
}
if (is.na(input_csv) || !file.exists(input_csv)) {
  stop("Cannot find phenotype CSV. Please pass --pheno-csv <path/to/phenotypes_3163.csv>")
}
if (!is.finite(top_n) || top_n <= 0) {
  stop("--top-n must be a positive integer")
}

pattern_df <- read.csv(input_tsv, check.names = FALSE, stringsAsFactors = FALSE)
pheno_df <- read.csv(input_csv, row.names = 1, check.names = FALSE, stringsAsFactors = FALSE)

needed_cols <- c("CAZ", "CXM", "CZO")
if (!all(needed_cols %in% colnames(pheno_df))) {
  miss <- needed_cols[!(needed_cols %in% colnames(pheno_df))]
  stop(paste0("Phenotype CSV is missing required columns: ", paste(miss, collapse = ", ")))
}
if (!all(c("abbreviation", "samples") %in% colnames(pattern_df))) {
  stop("Pattern TSV must contain columns: abbreviation, samples")
}
if (nrow(pattern_df) < top_n) {
  stop("Pattern TSV contains fewer rows than --top-n")
}

top_patterns <- pattern_df[seq_len(top_n), c("abbreviation", "samples"), drop = FALSE]
sample_ids <- rownames(pheno_df)

if (mode == "HuiNET") {
  analysis_ids <- sample_ids[grepl("^GN[0-9]{2}", sample_ids)]
  year_by_sample <- setNames(
    paste0("20", sub("^GN([0-9]{2}).*$", "\\1", analysis_ids)),
    analysis_ids
  )
} else {
  if (!file.exists(houston_year_csv)) {
    stop(paste0("Cannot find Houston sample whitelist/year CSV: ", houston_year_csv))
  }
  houston_year_df <- read.csv(houston_year_csv, check.names = FALSE, stringsAsFactors = FALSE)
  if (ncol(houston_year_df) < 2) {
    stop("Houston sample whitelist/year CSV must contain at least two columns")
  }
  houston_ids <- trimws(as.character(houston_year_df[[1]]))
  houston_years <- trimws(as.character(houston_year_df[[2]]))
  keep <- nzchar(houston_ids) & nzchar(houston_years)
  houston_year_df <- data.frame(
    sample_id = houston_ids[keep],
    year = houston_years[keep],
    stringsAsFactors = FALSE
  )
  houston_year_df <- houston_year_df[!duplicated(houston_year_df$sample_id), , drop = FALSE]
  analysis_ids <- intersect(sample_ids, houston_year_df$sample_id)
  year_by_sample <- setNames(houston_year_df$year, houston_year_df$sample_id)
  year_by_sample <- year_by_sample[analysis_ids]
}

year_labels <- sort(unique(year_by_sample))

if (length(analysis_ids) == 0 || length(year_labels) == 0) {
  stop(paste0("No analyzable samples with year labels were found for ", mode, " mode"))
}

parse_samples <- function(x) {
  parts <- trimws(unlist(strsplit(x, ";", fixed = TRUE)))
  parts[nzchar(parts)]
}

calc_lor_counts <- function(pattern_samples, phenotype_vec, year_label, year_by_sample) {
  sample_names <- names(phenotype_vec)
  phenotype_vec <- trimws(as.character(phenotype_vec))
  names(phenotype_vec) <- sample_names

  in_year <- sample_names %in% names(year_by_sample)[year_by_sample == year_label]
  phenotype_vec <- phenotype_vec[in_year]
  valid <- phenotype_vec %in% c("R", "S")

  if (!any(valid)) {
    return(c(
      lor = NA_real_, one_and_r = 0, zero_and_r = 0,
      one_and_s = 0, zero_and_s = 0, raw_lor = NA_real_, valid_n = 0
    ))
  }

  phenotype_vec <- phenotype_vec[valid]
  valid_ids <- names(phenotype_vec)
  has_pattern <- valid_ids %in% pattern_samples

  one_and_r <- sum(has_pattern & phenotype_vec == "R")
  zero_and_r <- sum(!has_pattern & phenotype_vec == "R")
  one_and_s <- sum(has_pattern & phenotype_vec == "S")
  zero_and_s <- sum(!has_pattern & phenotype_vec == "S")
  zero_margin <- any(c(
    one_and_r + one_and_s,
    zero_and_r + zero_and_s,
    one_and_r + zero_and_r,
    one_and_s + zero_and_s
  ) == 0)
  lor <- if (zero_margin) {
    NA_real_
  } else {
    log2(((one_and_r + 0.5) / (zero_and_r + 0.5)) / ((one_and_s + 0.5) / (zero_and_s + 0.5)))
  }
  raw_lor <- if (all(c(one_and_r, zero_and_r, one_and_s, zero_and_s) > 0)) {
    log2((one_and_r / zero_and_r) / (one_and_s / zero_and_s))
  } else {
    NA_real_
  }

  c(
    lor = lor,
    one_and_r = one_and_r,
    zero_and_r = zero_and_r,
    one_and_s = one_and_s,
    zero_and_s = zero_and_s,
    raw_lor = raw_lor,
    valid_n = length(phenotype_vec)
  )
}

pattern_samples_list <- lapply(top_patterns$samples, function(sample_text) {
  intersect(parse_samples(sample_text), analysis_ids)
})
names(pattern_samples_list) <- top_patterns$abbreviation

pattern_hits <- sum(lengths(pattern_samples_list))
if (pattern_hits == 0) {
  stop(paste0("No selected pattern samples passed the ", mode, " sample filter"))
}

lor_by_drug <- list()
detail_by_drug <- list()
long_rows <- list()

for (drug in needed_cols) {
  phenotype_vec <- pheno_df[[drug]]
  names(phenotype_vec) <- rownames(pheno_df)

  mat <- matrix(
    NA_real_,
    nrow = nrow(top_patterns),
    ncol = length(year_labels),
    dimnames = list(top_patterns$abbreviation, year_labels)
  )
  detail_rows <- vector("list", nrow(top_patterns))
  names(detail_rows) <- top_patterns$abbreviation

  for (pattern in top_patterns$abbreviation) {
    pattern_details <- list()
    for (i in seq_along(year_labels)) {
      counts <- calc_lor_counts(pattern_samples_list[[pattern]], phenotype_vec, year_labels[i], year_by_sample)
      mat[pattern, year_labels[i]] <- counts[["lor"]]
      pattern_details[[length(pattern_details) + 1]] <- data.frame(
        setNames(as.list(c(
          counts[["lor"]],
          counts[["one_and_r"]],
          counts[["zero_and_r"]],
          counts[["one_and_s"]],
          counts[["zero_and_s"]],
          counts[["raw_lor"]]
        )), paste0(year_labels[i], c(
          "_lor",
          "_one_and_r",
          "_zero_and_r",
          "_one_and_s",
          "_zero_and_s",
          "_raw_lor"
        ))),
        check.names = FALSE
      )
      long_rows[[length(long_rows) + 1]] <- data.frame(
        drug = drug,
        pattern = pattern,
        year = year_labels[i],
        lor = counts[["lor"]],
        one_and_r = counts[["one_and_r"]],
        zero_and_r = counts[["zero_and_r"]],
        one_and_s = counts[["one_and_s"]],
        zero_and_s = counts[["zero_and_s"]],
        valid_n = counts[["valid_n"]],
        stringsAsFactors = FALSE
      )
    }
    detail_rows[[pattern]] <- do.call(cbind, pattern_details)
  }

  lor_by_drug[[drug]] <- mat
  detail_by_drug[[drug]] <- do.call(rbind, detail_rows)
}

long_df <- do.call(rbind, long_rows)
table_file <- paste0(out_prefix, "_long.tsv")
write.table(long_df, file = table_file, sep = "\t", quote = FALSE, row.names = FALSE, na = "null")

for (drug in needed_cols) {
  matrix_file <- paste0(out_prefix, "_", drug, "_matrix.tsv")
  write.table(
    data.frame(pattern = rownames(detail_by_drug[[drug]]), detail_by_drug[[drug]], check.names = FALSE),
    file = matrix_file,
    sep = "\t",
    quote = FALSE,
    row.names = FALSE,
    na = "null"
  )
}

finite_vals <- unlist(lapply(lor_by_drug, function(mat) mat[is.finite(mat)]), use.names = FALSE)
if (length(finite_vals) == 0) {
  stop("No finite yearly internal LOR values were produced")
}

cat("Pattern CSV:", input_tsv, "\n")
cat("Phenotype CSV:", input_csv, "\n")
cat("Mode:", mode, "\n")
cat("Year labels:", paste(year_labels, collapse = ", "), "\n")
if (mode == "Houston") {
  cat("Houston whitelist/year CSV:", houston_year_csv, "\n")
}
cat("Saved:", table_file, "\n")
for (drug in needed_cols) {
  cat("Saved:", paste0(out_prefix, "_", drug, "_matrix.tsv"), "\n")
}
