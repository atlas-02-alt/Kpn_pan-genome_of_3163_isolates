library(ggplot2)

input_file <- "add1-pangenome_accumulation_curve_summary.tsv"
output_pdf <- "add1-pangenome_accumulation_curve.pdf"
output_png <- "add1-pangenome_accumulation_curve.png"

dat <- read.delim(input_file, header = TRUE, sep = "\t", check.names = FALSE)

required_cols <- c("n_sampled", "core_genes", "dispensable_genes", "rare_genes")
missing_cols <- setdiff(required_cols, names(dat))
if (length(missing_cols) > 0) {
  stop("Missing required column(s): ", paste(missing_cols, collapse = ", "))
}

dat <- dat[order(dat$n_sampled), ]

plot_dat <- data.frame(
  n_sampled = rep(dat$n_sampled, times = 3),
  gene_class = factor(
    rep(c("Core", "Dispensable", "Rare"), each = nrow(dat)),
    levels = c("Rare", "Dispensable", "Core")
  ),
  gene_count = c(dat$core_genes, dat$dispensable_genes, dat$rare_genes)
)

if (.Platform$OS.type == "windows") {
  windowsFonts(Arial = windowsFont("Arial"))
}

p <- ggplot(plot_dat, aes(x = n_sampled, y = gene_count, fill = gene_class)) +
  geom_area(color = "white", linewidth = 0.15, alpha = 0.95) +
  scale_fill_manual(
    name = NULL,
    values = c(
      "Core" = "#4E79A7",
      "Dispensable" = "#59A14F",
      "Rare" = "#F28E2B"
    ),
    breaks = c("Core", "Dispensable", "Rare")
  ) +
  scale_x_continuous(
    name = "Number of genomes sampled",
    expand = expansion(mult = c(0.01, 0.02))
  ) +
  scale_y_continuous(
    name = "Number of pan-genome genes",
    labels = function(x) format(x, big.mark = ",", scientific = FALSE),
    expand = expansion(mult = c(0.02, 0.06))
  ) +
  theme_classic(base_family = "Arial", base_size = 12) +
  theme(
    legend.position = c(0.03, 0.95),
    legend.justification = c(0, 1),
    legend.background = element_blank(),
    legend.key.size = unit(0.45, "cm"),
    legend.text = element_text(size = 11, color = "black"),
    axis.title = element_text(size = 13, color = "black"),
    axis.text = element_text(size = 11, color = "black"),
    axis.line = element_line(color = "black", linewidth = 0.5),
    axis.ticks = element_line(color = "black", linewidth = 0.5),
    plot.margin = margin(10, 12, 8, 10)
  )

ggsave(output_pdf, plot = p, width = 6.5, height = 4.5, device = cairo_pdf)
ggsave(output_png, plot = p, width = 6.5, height = 4.5, dpi = 300, bg = "white")

message("Saved: ", output_pdf)
message("Saved: ", output_png)
