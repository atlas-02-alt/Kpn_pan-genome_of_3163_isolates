library(ggplot2)
library(gggenes)
library(dplyr)

df <- data.frame(
  haplotype = c("P3", "P3", "P3", "P3",
                "P2",
                "P1", "P1", "P1"),
  gene = c("ISEcp1", "group_12673", "blaCTX-M-15", "group_2412",
           "blaCTX-M-14",
           "ISEcp1", "group_12673", "blaCTX-M-14"),
  length = c(1263, 123, 876, 321,
             876,
             1263, 123, 876)
)

gap <- 35
# Smaller value -> tighter spacing between haplotype tracks
hap_gap <- 0.2

hap_levels <- unique(df$haplotype)
n_hap <- length(hap_levels)

df <- df %>%
  group_by(haplotype) %>%
  mutate(
    xmin = cumsum(lag(length + gap, default = 0)),
    xmax = xmin + length
  ) %>%
  ungroup() %>%
  mutate(
    hap_id = as.numeric(factor(haplotype, levels = hap_levels)),
    y = 1 + (hap_id - 1) * hap_gap
  )

gene_cols <- c(
  "group_12673" = "#4C78A8",
  "blaCTX-M-15" = "#E45756",
  "ISEcp1" = "#72B7B2",
  "group_2412" = "#54A24B",
  "blaCTX-M-14" = "#F58518"
)

p <- ggplot(df, aes(xmin = xmin, xmax = xmax, y = y, fill = gene)) +
  geom_gene_arrow(
    arrowhead_width = unit(0, "mm"),
    arrow_body_height = unit(5.0, "mm"),
    color = NA,
    linewidth = 0
  ) +
  scale_fill_manual(values = gene_cols) +
  scale_y_continuous(
    breaks = 1 + (seq_len(n_hap) - 1) * hap_gap,
    labels = hap_levels,
    limits = c(0.2, n_hap + 0.2),
    expand = c(0, 0)
  ) +
  theme_genes() +
  theme(
    axis.title = element_blank(),
    panel.grid = element_blank()
  )

print(p)