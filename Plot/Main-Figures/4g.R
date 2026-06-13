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

input_values <- get_arg("--values-tsv", NA_character_)
out_prefix <- get_arg("--out-prefix", NA_character_)
if (is.na(out_prefix) && !is.na(input_values)) {
  out_prefix <- sub("_(long|values)\\.tsv$", "", basename(input_values))
}
out_prefix <- sub("_barplot$", "", out_prefix)
out_prefix <- gsub("_barplot_", "_", out_prefix, fixed = TRUE)
drug_arg <- get_arg("--drugs", "CAZ,CXM,CZO")
needed_cols <- trimws(unlist(strsplit(drug_arg, ",", fixed = TRUE)))
needed_cols <- needed_cols[nzchar(needed_cols)]
pages_arg <- get_arg("--pages", NA_character_)
patterns_arg <- get_arg("--patterns", "P1,P2,P3")
png_dpi <- suppressWarnings(as.integer(get_arg("--png-dpi", "300")))
if (!is.finite(png_dpi) || png_dpi <= 0) png_dpi <- 300

if (is.na(input_values) || !file.exists(input_values)) {
  stop("Cannot find values TSV. Please pass --values-tsv <path/to/*_values.tsv>")
}
if (is.na(out_prefix) || !nzchar(out_prefix)) {
  stop("Please pass --out-prefix <output_prefix> or use a --values-tsv ending in _long.tsv")
}
if (length(needed_cols) == 0) {
  stop("--drugs must contain at least one drug name")
}

values_df <- read.delim(
  input_values,
  sep = "\t",
  check.names = FALSE,
  stringsAsFactors = FALSE,
  na.strings = c("NA", "null", "")
)
required_cols <- c("drug", "pattern", "year", "lor")
if (!all(required_cols %in% colnames(values_df))) {
  miss <- required_cols[!(required_cols %in% colnames(values_df))]
  stop(paste0("Values TSV is missing required columns: ", paste(miss, collapse = ", ")))
}

values_df <- values_df[values_df$drug %in% needed_cols, , drop = FALSE]
values_df$year <- suppressWarnings(as.integer(values_df$year))
values_df$lor <- suppressWarnings(as.numeric(values_df$lor))

patterns <- unique(values_df$pattern)
year_num <- sort(unique(values_df$year[is.finite(values_df$year)]))
if (length(patterns) == 0 || length(year_num) == 0) {
  stop("No usable pattern/year rows were found in values TSV")
}
page_num <- seq_along(patterns)
selected_pages <- page_num
if (!is.na(pages_arg) && nzchar(pages_arg)) {
  selected_pages <- suppressWarnings(as.integer(trimws(unlist(strsplit(pages_arg, ",", fixed = TRUE)))))
  selected_pages <- selected_pages[is.finite(selected_pages)]
  if (length(selected_pages) == 0) {
    stop("--pages must contain at least one page number")
  }
  bad_pages <- selected_pages[selected_pages < 1 | selected_pages > length(patterns)]
  if (length(bad_pages) > 0) {
    stop(paste0("Requested page(s) out of range: ", paste(bad_pages, collapse = ", ")))
  }
} else if (!is.na(patterns_arg) && nzchar(patterns_arg)) {
  requested_patterns <- trimws(unlist(strsplit(patterns_arg, ",", fixed = TRUE)))
  requested_patterns <- requested_patterns[nzchar(requested_patterns)]
  selected_patterns <- requested_patterns[requested_patterns %in% patterns]
  if (length(selected_patterns) == 0) {
    stop(paste0(
      "None of the requested patterns were found in values TSV: ",
      paste(requested_patterns, collapse = ", ")
    ))
  }
  selected_pages <- match(selected_patterns, patterns)
}
selected_patterns <- patterns[selected_pages]

pcc_rows <- list()
for (pattern in patterns) {
  for (drug in needed_cols) {
    sub_df <- values_df[values_df$pattern == pattern & values_df$drug == drug, , drop = FALSE]
    ok <- is.finite(sub_df$year) & is.finite(sub_df$lor)
    pcc_test <- if (sum(ok) >= 3) {
      suppressWarnings(cor.test(sub_df$year[ok], sub_df$lor[ok], method = "pearson"))
    } else {
      NULL
    }
    pcc <- if (sum(ok) >= 2) cor(sub_df$year[ok], sub_df$lor[ok], method = "pearson") else NA_real_
    p_value <- if (is.null(pcc_test)) NA_real_ else pcc_test$p.value
    direction <- ifelse(
      is.na(pcc), "NA",
      ifelse(pcc > 0, "positive", ifelse(pcc < 0, "negative", "zero"))
    )
    pcc_rows[[length(pcc_rows) + 1]] <- data.frame(
      pattern = pattern,
      drug = drug,
      n_years = sum(ok),
      pcc = pcc,
      p_value = p_value,
      direction = direction,
      stringsAsFactors = FALSE
    )
  }
}

pcc_df <- do.call(rbind, pcc_rows)
pcc_file <- paste0(out_prefix, "_pcc.tsv")
write.table(pcc_df, file = pcc_file, sep = "\t", quote = FALSE, row.names = FALSE)

default_colors <- c(CAZ = "#2166ac", CXM = "#b2182b", CZO = "#1b9e77")
fallback_colors <- grDevices::rainbow(length(needed_cols))
drug_colors <- setNames(fallback_colors, needed_cols)
drug_colors[names(default_colors)[names(default_colors) %in% needed_cols]] <-
  default_colors[names(default_colors) %in% needed_cols]
drug_pch <- setNames(seq(16, length.out = length(needed_cols)), needed_cols)

draw_limited_fit <- function(x, y, col, lwd = 1.1) {
  if (length(x) < 2 || length(unique(x)) < 2) return(invisible(NULL))

  fit <- lm(y ~ x)
  x_seq <- seq(min(x, na.rm = TRUE), max(x, na.rm = TRUE), length.out = 200)
  y_hat <- as.numeric(predict(fit, newdata = data.frame(x = x_seq)))
  keep <- is.finite(y_hat)
  if (sum(keep) < 2) return(invisible(NULL))

  lines(x_seq[keep], y_hat[keep], col = col, lwd = lwd)
  invisible(NULL)
}

draw_dot_page <- function(pattern) {
  plot_df <- values_df[values_df$pattern == pattern, , drop = FALSE]
  y_vals <- plot_df$lor[is.finite(plot_df$lor)]
  if (length(y_vals) == 0) {
    y_min <- -1
    y_max <- 1
  } else {
    y_min <- min(y_vals)
    y_max <- max(y_vals)
    if (identical(y_min, y_max)) {
      y_min <- y_min - 1
      y_max <- y_max + 1
    }
  }
  y_span <- max(1e-9, y_max - y_min)
  y_pad <- y_span * 0.20
  y_lim <- c(y_min - y_pad, y_max + y_pad)
  x_lim <- range(year_num, na.rm = TRUE)
  legend_x <- x_lim[2] + diff(x_lim) * 0.01

  legend_labels <- character(0)
  for (drug in needed_cols) {
    pcc <- pcc_df$pcc[pcc_df$pattern == pattern & pcc_df$drug == drug]
    p_value <- pcc_df$p_value[pcc_df$pattern == pattern & pcc_df$drug == drug]
    direction <- pcc_df$direction[pcc_df$pattern == pattern & pcc_df$drug == drug]
    p_label <- ifelse(is.na(p_value), "p=NA", sprintf("p=%.2g", p_value))
    legend_labels <- c(legend_labels, sprintf("%s  r=%.2f  %s  %s", drug, pcc, p_label, direction))
  }
  right_mar <- max(9.8, 4.2 + max(nchar(c("Pearson r", legend_labels))) * 0.25)

  par(mar = c(5.2, 4.2, 2.4, right_mar), xpd = FALSE)
  plot(
    NA, NA,
    xlim = x_lim,
    ylim = y_lim,
    xaxt = "n",
    yaxt = "n",
    xlab = "Year",
    ylab = "Year-internal LOR",
    bty = "n",
    main = paste0(pattern, " yearly internal LOR")
  )
  axis(1, at = year_num, labels = year_num, las = 2, cex.axis = 0.78)
  axis(2, las = 1, cex.axis = 0.82)
  if (y_lim[1] <= 0 && y_lim[2] >= 0) {
    abline(h = 0, col = "#777777", lwd = 0.8, lty = 3)
  }

  for (drug in needed_cols) {
    sub_df <- plot_df[plot_df$drug == drug, , drop = FALSE]
    ok <- is.finite(sub_df$year) & is.finite(sub_df$lor)
    points(sub_df$year[ok], sub_df$lor[ok], col = drug_colors[[drug]], pch = drug_pch[[drug]], cex = 1.6)
    if (sum(ok) >= 2) {
      draw_limited_fit(sub_df$year[ok], sub_df$lor[ok], col = drug_colors[[drug]], lwd = 1.1)
    }
  }

  old_xpd <- par(xpd = NA)
  legend(
    x = legend_x,
    y = y_max + y_pad,
    legend = legend_labels,
    col = drug_colors[needed_cols],
    pch = drug_pch[needed_cols],
    lty = 1,
    lwd = 1.1,
    border = NA,
    bty = "n",
    cex = 0.82,
    xjust = 0,
    yjust = 1,
    title = "Pearson r"
  )
  par(old_xpd)
}

dot_pdf_files <- character(0)
for (pattern in selected_patterns) {
  dot_pdf <- paste0(out_prefix, "_dotplot_pcc_", pattern, ".pdf")
  pdf(file = dot_pdf, width = 12.5, height = 5.2, onefile = FALSE)
  draw_dot_page(pattern)
  dev.off()
  dot_pdf_files <- c(dot_pdf_files, dot_pdf)
}

png_files <- character(0)
if (!is.na(pages_arg) && nzchar(pages_arg)) {
  for (i in seq_along(selected_patterns)) {
    png_file <- sprintf("%s_dotplot_pcc_page%02d.png", out_prefix, selected_pages[i])
    png(filename = png_file, width = 12.5 * png_dpi, height = 5.2 * png_dpi, res = png_dpi)
    draw_dot_page(selected_patterns[i])
    dev.off()
    png_files <- c(png_files, png_file)
  }
}

cat("Values TSV:", input_values, "\n")
cat("Drugs:", paste(needed_cols, collapse = ", "), "\n")
cat("Patterns:", paste(selected_patterns, collapse = ", "), "\n")
cat("Pages:", paste(selected_pages, collapse = ", "), "\n")
cat("Saved:", pcc_file, "\n")
cat("Saved PDF:", paste(dot_pdf_files, collapse = ", "), "\n")
if (length(png_files) > 0) {
  cat("Saved PNG:", paste(png_files, collapse = ", "), "\n")
}
