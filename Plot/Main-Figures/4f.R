infile <- 'HuiNET_year_counts_2006_2020_from_pattern_summary_normalized.csv'
out_pdf <- 'HuiNET_year_counts_2006_2020_normalized_heatmap_top3.pdf'

title_txt <- 'Yearly Prevalence (%) of Distinct Gene-Order Patterns Among HuiNET Isolates (Top 3 Rows)'

# read normalized percentage table and keep only first 3 rows
df <- read.csv(infile, header=TRUE, check.names=FALSE, stringsAsFactors=FALSE)
df <- head(df, 3)

id_col <- if ('pattern_key' %in% colnames(df)) 'pattern_key' else 'normalized_order'
x_cols <- setdiff(colnames(df), id_col)
x_cols <- x_cols[order(as.integer(x_cols))]
mat <- as.matrix(df[, x_cols])
storage.mode(mat) <- 'numeric'

y_labels <- paste0('(P', seq_len(nrow(df)), ') ', df[[id_col]])

x_int <- as.integer(x_cols)
x_labels <- if (max(x_int, na.rm=TRUE) <= 99) sprintf('%d', 2000 + x_int) else as.character(x_cols)

pal <- colorRampPalette(c('#f9f9ff', '#dbe7ff', '#b7c9ff', '#9f9ad9', '#b85fa8', '#d94b6b', '#ef3b2c'))(256)

zlim <- c(0, max(mat, na.rm=TRUE))
if (!is.finite(zlim[2]) || zlim[2] <= 0) zlim[2] <- 1

plot_heatmap <- function(dev_fun, outfile) {
  dev_fun(outfile)
  layout(matrix(c(1, 2), nrow=1), widths=c(13.5, 2.6))

  par(mar=c(4.8, 24, 3.8, 1.2), bty='n', xpd=NA)
  mat_plot <- mat[nrow(mat):1, , drop=FALSE]
  y_plot_labels <- rev(y_labels)

  image(
    x=seq_len(ncol(mat_plot)),
    y=seq_len(nrow(mat_plot)),
    z=t(mat_plot),
    col=pal,
    zlim=zlim,
    axes=FALSE,
    frame.plot=FALSE,
    xlab='Year',
    ylab=''
  )
  axis(1, at=seq_len(ncol(mat_plot)), labels=x_labels, las=2, cex.axis=0.9)
  axis(2, at=seq_len(nrow(mat_plot)), labels=y_plot_labels, las=2, cex.axis=0.85)
  title(main=title_txt, cex.main=0.95)

  par(mar=c(4.5, 0.6, 3.5, 8.2), bty='n')
  zseq <- seq(zlim[1], zlim[2], length.out=257)
  zmat <- matrix(zseq[-length(zseq)], nrow=1)
  image(
    x=c(0, 1),
    y=zseq,
    z=zmat,
    col=pal,
    axes=FALSE,
    frame.plot=FALSE,
    xlab='',
    ylab=''
  )
  axis(4, las=2, cex.axis=0.85)
  mtext('Percentage in sampled isolates', side=4, line=3.8, cex=0.9)

  dev.off()
}

plot_heatmap(function(f) pdf(f, width=15, height=5.6), out_pdf)

cat('Written:', out_pdf, '\n')
