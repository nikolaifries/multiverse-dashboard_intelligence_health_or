source("sca_rainforest.R")
source("sca_gosh.R")

# Get fill data for each specification.
#
# The fill data is a vector that indicate the which- and how-
# factors that comprise a specification. The size of the number corresponds
# to the number of samples that contribute (i.e. the value of k).
#
#  Arguments:
#      n_which -- The number of which-factors.
#      which_lists -- The which-factors.
#      n_how -- The number of how-factors.
#      how_lists -- The how-factors.
#      specs -- The specification data.
#
#  Returns:
#      A list containing the fill data for each specification.
#
getSpecFillData <- function(n_which, which_lists, n_how, how_lists, specs) {
  # Combine which- and how- factors into a single list
  group_factors <- c(which_lists, how_lists)

  # Get complete list of values
  group_factor_values <- rev(unlist(group_factors))
  n_factors <- n_which + n_how

  spec_fill_data <- list()

  # Get fill data for each specification
  for (rank in specs$rank) {
    spec <- specs[specs$rank == rank, ]

    # The first columns in the specification data are factors
    spec_id <- as.numeric(group_factor_values %in% as.character(
      unlist(spec[, 1:n_factors])
    ))

    # Key should be string, not number, for interoperability with Python
    # Multiply binary vector with k
    spec_fill_data[[as.character(rank)]] <- spec_id * spec$k
  }

  return(spec_fill_data)
}


# Get cluster fill data for each specification.
#
# The cluster fill data is a vector that indicate the percentage of
# available samples from each cluster that belongs to the specification.
#
#  Arguments:
#      data -- The meta-analytic dataset.
#      specs -- The specification data.
#      colmap -- The column-map from the configuration.
#
#  Returns:
#      A list containing the cluster fill data for each specification.
#
getClusterFillData <- function(data, specs, colmap) {
  # Get relevant keys from colmap
  key_c_id <- colmap$key_c_id
  key_e_id <- colmap$key_e_id
  key_c <- colmap$key_c

  cluster_fill_data <- list()

  # Get fill data for each specification
  for (rank in specs$rank) {
    spec <- specs[specs$rank == rank, ]

    # Get the sets of cluster- and effect- IDs that contribute
    set_c_ids <- as.integer(unlist(strsplit(spec$set, ",")))
    set_e_ids <- as.integer(unlist(strsplit(spec$set_es, ",")))
    fills <- rep(0, length(unique(data[[key_c_id]])))

    # For each cluster ID in the set, compute the percentage and set
    # the value at the corresponding index of the vector
    for (c_id in set_c_ids) {
      # Get all effect IDs in cluster
      c_data <- data[data[[key_c_id]] == c_id, ]
      c_e_ids <- c_data[[key_e_id]]

      # Filter for effect IDs that are in the specification
      spec_c_e_ids <- c_e_ids[c_e_ids %in% set_e_ids]

      # Compute percentage and set value at corresponding index
      c_fill <- length(spec_c_e_ids) * 100 / length(c_e_ids)
      fills[c_id] <- c_fill
    }

    # Key should be string, not number, for interoperability with Python
    # Reverse the vector for correct plotting
    cluster_fill_data[[as.character(rank)]] <- rev(fills)
  }

  # Prepare list of cluster names as labels
  c_ids <- sort(unique(data[[key_c_id]]))
  cluster_fill_data[["labels"]] <- sapply(c_ids, function(c_id) {
    c_data <- data[data[[key_c_id]] == c_id, ]
    return(c_data[1, key_c])
  })

  return(cluster_fill_data)
}


# Get list of colors for plotting, from warm to cold.
#
# The maximum amount of colors is 11. If the amount of fill_levels is less,
# the list of colors is reduced.
#
#  Arguments:
#      fill_levels -- The amount of different fill values
#                     (unique values of k).
#
#  Returns:
#      A list of colors.
#
getColors <- function(fill_levels) {
  colors <- RColorBrewer::brewer.pal(min(11, fill_levels - 1), "Spectral")
  return(colors)
}


# Get color scale, consisting of repeated colors.
#
#  Arguments:
#      colors -- The list of colors.
#      fill_levels -- The amount of different fill values
#                     (unique values of k).
#
#  Returns:
#      A list of repeated colors of length fill_levels-1.
#
getColorScale_ <- function(colors, fill_levels) {
  color_indices <- floor(seq(1, length(colors), length.out = fill_levels - 1))
  color_scale <- colors[color_indices]
  return(color_scale)
}


# Plot caterpillar.
#
#  Arguments:
#      specs -- The specification data.
#      colors -- The list of colors.
#      title -- The analysis title.
#      x_range -- The range of specification numbers.
#      fill_levels -- The amount of fill levels.
#
#  Returns:
#      ggplot figure.
#
plotCaterpillar <- function(specs, colors, title, x_range, fill_levels) {
  color_scale <- getColorScale_(colors, fill_levels)

  # Prepare y-axis limits
  y_l_limit <- min(specs$lb)
  y_u_limit <- max(specs$ub)
  y_range_diff <- y_u_limit - y_l_limit
  y_limits <- c(
    y_l_limit - (y_range_diff * 0.1),
    y_u_limit + (y_range_diff * 0.1)
  )

  # Prepare y-axis breaks
  y_breaks <- round(seq(
    round(y_limits[1], 1),
    round(y_limits[2], 1),
    round((y_limits[2] - y_limits[1]) / 5, 1)
  ), 1)

  # Plot caterpillar
  fig <- ggplot(data = specs, aes(x = rank, y = mean)) +
    geom_errorbar(
      aes(ymin = lb, ymax = ub, col = as.factor(k)),
      width = 0, size = 0.25
    ) +
    geom_line(col = "black", linewidth = 0.25) +
    geom_hline(yintercept = 0, linetype = 2, linewidth = 0.25) +
    scale_x_continuous(name = "") +
    scale_y_continuous(name = "Summary effect (r)", breaks = y_breaks) +
    scale_color_manual(values = color_scale) +
    coord_cartesian(ylim = y_limits, xlim = x_range, expand = FALSE) +
    theme_bw() +
    theme(
      legend.position = "none",
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      panel.grid.major.x = element_blank(),
      panel.grid.minor.x = element_blank(),
      panel.grid.major.y = element_line(),
      panel.grid.minor.y = element_blank(),
      plot.margin = margin(t = 5.5, r = 5.5, b = -15, l = 5.5, unit = "pt")
    )

  # Add title if it exists
  if (!is.null(title)) {
    fig <- fig + ggtitle(title)
  }

  return(fig)
}


# Plot cluster tilemap.
#
#  Arguments:
#      specs -- The specification data.
#      cluster_fill_data -- See get_cluster_fill_data().
#      n_total_specs -- The total number of specifications.
#      title -- The analysis title.
#      x_range -- The range of specification numbers.
#
#  Returns:
#      ggplot figure.
#
plotClusterTiles <- function(specs, cluster_fill_data, n_total_specs, title,
                             x_range) {
  # Reverse labels for correct plotting
  y_labels <- rev(cluster_fill_data[["labels"]])
  n_clusters <- length(y_labels)

  # Get separate list without labels
  cluster_fill_data_2 <- cluster_fill_data[!names(cluster_fill_data) %in% "labels"]

  # Draw horizontal lines for clarity
  y_intercepts <- seq(1, n_clusters - 1) + 0.5

  # Get fill-values
  z <- factor(unlist(cluster_fill_data_2))
  n_z_levels <- length(levels(z))

  # Prepare colorscale
  if (n_z_levels < 4) {
    color_scale <- tail(RColorBrewer::brewer.pal(3, "Greens"), n_z_levels - 1)
  } else {
    color_scale <- RColorBrewer::brewer.pal(n_z_levels - 1, "Greens")
  }
  color_scale <- c("white", color_scale)

  # Prepare plot data for ggplot
  plot_data <- data.frame(
    x = rep(1:n_total_specs, each = n_clusters),
    y = factor(rep(y_labels, times = n_total_specs), levels = y_labels),
    z = z
  )

  # Plot cluster tilemap
  fig <- ggplot(data = plot_data, aes(x = x, y = y, fill = z)) +
    geom_raster() +
    geom_hline(yintercept = y_intercepts) +
    scale_x_continuous(position = "bottom") +
    scale_y_discrete(labels = y_labels) +
    scale_fill_manual(values = color_scale) +
    labs(x = "", y = "") +
    coord_cartesian(expand = F, xlim = x_range) +
    theme_bw() +
    theme(
      legend.position = "none",
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      axis.text = element_text(colour = "black"),
      axis.ticks = element_line(colour = "black"),
      plot.margin = margin(t = 5.5, r = 5.5, b = -15, l = 5.5, unit = "pt")
    )

  # Add title if it exists
  if (!is.null(title)) {
    fig <- fig + ggtitle(title)
  }

  return(fig)
}


# Get intercept points for each factor.
#
#  Arguments:
#      y_labels -- The list of factor labels.
#
#  Returns:
#      List of intercept points.
#
getYIntercepts_ <- function(y_labels) {
  # Split each label and retain key
  group_labels <- lapply(
    unlist(y_labels),
    function(x) unlist(strsplit(x, ":"))[1]
  )

  # Check how many values are present for each factor
  cumulative_n_groups <- NULL
  prev_gl <- group_labels[[1]]
  i <- 0
  for (gl in group_labels) {
    if (gl != prev_gl) {
      cumulative_n_groups <- c(cumulative_n_groups, i)
    }
    i <- i + 1
    prev_gl <- gl
  }

  # Shift by 0.5 for correct plotting
  y_intercept <- cumulative_n_groups + 0.5
  return(y_intercept)
}


# Plot specification tilemap.
#
#  Arguments:
#      specs -- The specification data.
#      n_total_specs -- The total number of specifications.
#      spec_fill_data -- See get_spec_fill_data().
#      labels -- The factor labels.
#      colors -- The list of colors.
#      title -- The analysis title.
#      x_range -- The range of specification numbers.
#      fill_levels -- The amount of fill levels.
#
#  Returns:
#      ggplot figure.
#
plotSpecTiles <- function(specs, n_total_specs, spec_fill_data, labels,
                          colors, title, x_range, fill_levels) {
  # Reverse labels for correct plotting
  y_labels <- rev(labels)
  n_factors <- length(y_labels)

  # Horizontal lines for each factor
  y_intercept <- getYIntercepts_(y_labels)

  # Get color scale, ensure white "background"
  color_scale <- getColorScale_(colors, fill_levels)
  color_scale <- c("white", color_scale)

  # Prepare plot data for ggplot
  plot_data <- data.frame(
    x = rep(1:n_total_specs, each = n_factors),
    y = factor(rep(y_labels, times = n_total_specs), levels = y_labels),
    z = factor(unlist(spec_fill_data))
  )

  # Plot specification tilemap
  fig <- ggplot(data = plot_data, aes(x = x, y = y, fill = z)) +
    geom_raster() +
    geom_hline(yintercept = y_intercept) +
    scale_x_continuous(position = "bottom") +
    scale_y_discrete(labels = y_labels) +
    scale_fill_manual(values = color_scale) +
    labs(x = "Specification number", y = "Which/How factors") +
    coord_cartesian(expand = F, xlim = x_range) +
    theme_bw() +
    theme(
      legend.position = "none",
      axis.text = element_text(colour = "black"),
      axis.ticks = element_line(colour = "black"),
      plot.margin = margin(t = 5.5, r = 5.5, b = 5.5, l = 5.5, unit = "pt")
    )

  # Add title if it exists
  if (!is.null(title)) {
    fig <- fig + ggtitle(title)
  }

  return(fig)
}


# Plot cluster size barplot.
#
#  Arguments:
#      specs -- The specification data.
#      k_range -- The range of sample sizes.
#      n_total_specs -- The total number of specifications.
#      title -- The analysis title.
#      x_range -- The range of specification numbers.
#
#  Returns:
#      ggplot figure.
#
plotClusterSize <- function(specs, k_range, n_total_specs, title, x_range) {
  # Prepare y-axis breaks
  k_step <- round((k_range[2] - k_range[1]) / 4 / 2) * 2
  y_breaks <- seq(k_range[1], k_range[2], k_step)

  # Plot cluster size barplot
  fig <- ggplot(data = specs, aes(x = rank, y = kc)) +
    geom_col(width = 1, fill = "darkslategray") +
    scale_x_continuous(name = "") +
    scale_y_continuous(name = "# Clusters", breaks = y_breaks) +
    coord_cartesian(ylim = k_range, xlim = x_range, expand = FALSE) +
    theme_bw() +
    theme(
      legend.position = "none",
      axis.title = element_text(size = 8),
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      panel.grid.major.x = element_blank(),
      panel.grid.minor.x = element_blank(),
      panel.grid.major.y = element_line(),
      panel.grid.minor.y = element_blank(),
      plot.margin = margin(t = 5.5, r = 5.5, b = -8, l = 5.5, unit = "pt")
    )

  # Add title if it exists
  if (!is.null(title)) {
    fig <- fig + ggtitle(title)
  }

  return(fig)
}


# Plot sample size barplot.
#
#  Arguments:
#      specs -- The specification data.
#      k_range -- The range of sample sizes.
#      n_total_specs -- The total number of specifications.
#      title -- The analysis title.
#      x_range -- The range of specification numbers.
#
#  Returns:
#      ggplot figure.
#
plotSampleSize <- function(specs, k_range, n_total_specs, title, x_range) {
  # Prepare y-axis breaks
  k_step <- round((k_range[2] - k_range[1]) / 4 / 2) * 2
  y_breaks <- seq(k_range[1], k_range[2], k_step)

  # Plot sample size barplot
  fig <- ggplot(data = specs, aes(x = rank, y = k)) +
    geom_col(width = 1) +
    scale_x_continuous(name = "") +
    scale_y_continuous(name = "# Samples", breaks = y_breaks) +
    coord_cartesian(ylim = k_range, xlim = x_range, expand = FALSE) +
    theme_bw() +
    theme(
      legend.position = "none",
      axis.title = element_text(size = 8),
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      panel.grid.major.x = element_blank(),
      panel.grid.minor.x = element_blank(),
      panel.grid.major.y = element_line(),
      panel.grid.minor.y = element_blank(),
      plot.margin = margin(t = 5.5, r = 5.5, b = -8, l = 5.5, unit = "pt")
    )

  # Add title if it exists
  if (!is.null(title)) {
    fig <- fig + ggtitle(title)
  }

  return(fig)
}


# Plot the multiverse summary figure.
#
#  Arguments:
#      specs -- The specification data.
#      n_total_specs -- The total number of specifications.
#      k_range -- The range of sample sizes.
#      cluster_fill_data -- See get_cluster_fill_data().
#      spec_fill_data -- See get_spec_fill_data().
#      labels -- The factor labels.
#      colors -- The list of colors.
#      level -- The level of the meta-analysis (2 or 3).
#      title -- The analysis title.
#      x_range -- The range of specification numbers.
#      fill_levels -- The amount of fill levels.
#
#  Returns:
#       ggplot figure.
#
plotMultiverse <- function(specs, n_total_specs, k_range, cluster_fill_data,
                           spec_fill_data, labels, colors, level, title,
                           x_range, fill_levels) {
  # Cluster tilemap
  if (level == 3) {
    fig_cluster_tiles <- plotClusterTiles(
      specs, cluster_fill_data, n_total_specs, title, x_range
    )

    # Set title to NULL, so it is not plotted anymore
    title <- NULL

    # Cluster sample size
    fig_cluster_size <- plotClusterSize(
      specs, k_range, n_total_specs, title, x_range
    )
  }

  # Caterpillar
  fill_levels <- length(unique(unlist(spec_fill_data)))
  fig_caterpillar <- plotCaterpillar(specs, colors, title, x_range, fill_levels)

  # Set title to NULL, so it is not plotted anymore
  title <- NULL

  # Sample size
  fig_sample_size <- plotSampleSize(
    specs, k_range, n_total_specs, title, x_range
  )

  # Specification tilemap
  fig_spec_tiles <- plotSpecTiles(
    specs, n_total_specs, spec_fill_data, labels, colors, title, x_range, fill_levels
  )

  # Arrange individual panels into one plot and align vertically
  if (level == 2) {
    fig <- ggarrange(
      fig_caterpillar,
      fig_sample_size,
      fig_spec_tiles,
      nrow = 3,
      ncol = 1,
      heights = c(3, 1, 6),
      align = "v"
    )
  } else if (level == 3) {
    fig <- ggarrange(
      fig_cluster_tiles,
      fig_caterpillar,
      fig_cluster_size,
      fig_sample_size,
      fig_spec_tiles,
      nrow = 5,
      ncol = 1,
      heights = c(3.5, 1.8, 0.6, 0.6, 3.5),
      align = "v"
    )
  }

  return(fig)
}


# Plot inferential specification plot.
#
#  Arguments:
#      boot_data -- The bootstrap sampling data.
#      x_range -- The range of specification numbers.
#      title -- The analysis title.
#
#  Returns:
#      ggplot figure.
#
plotInferential <- function(boot_data, x_range, title) {
  fig <- ggplot(data = boot_data, aes(x = rank, y = obs)) +
    geom_ribbon(
      aes(x = rank, ymin = boot_lb, ymax = boot_ub),
      fill = "gray", color = "black", lty = "dotted",
      alpha = 0.7, linewidth = 0.25
    ) +
    geom_line(col = "firebrick", linewidth = 0.5) +
    geom_hline(yintercept = 0, linetype = 2, linewidth = 0.25) +
    scale_x_continuous(name = "Specification number") +
    scale_y_continuous(name = "Summary effect") +
    ggtitle(title) +
    coord_cartesian(xlim = x_range, expand = FALSE) +
    theme_bw() +
    theme(legend.position = "none")

  return(fig)
}


# Plot p-value histogram.
#
#  Arguments:
#      specs -- The specification data.
#      title -- The analysis title.
#
#  Returns:
#      ggplot figure
#
plotPValuesHist <- function(specs, title) {
  # First bin should contain all significant values
  breaks <- seq(from = 0, to = 1, by = 0.05)

  # Prepare plot data for ggplot
  height <- as.numeric(prop.table(table(cut(specs$p, breaks))))
  plotdata <- data.frame(height, breaks = breaks[-21] + 0.025)

  # Plot figure
  fig <- ggplot(data = plotdata, aes(x = breaks, y = height)) +
    geom_bar(
      stat = "identity", width = 0.05, color = "black", fill = "azure4"
    ) +
    geom_bar(aes(x = breaks, y = ifelse(breaks < 0.05, height, 0)),
      col = "black", fill = "lightgray",
      stat = "identity", width = 0.05
    ) +
    coord_cartesian(xlim = c(-0.01, 1.01), ylim = c(0, 0.15), expand = FALSE) +
    labs(y = "Proportion", x = "Specification p-values") +
    theme_bw() +
    theme(
      strip.text.x = element_text(face = "bold"),
      axis.title.x = element_text(color = "white"),
      strip.background = element_rect(colour = NA, fill = NA),
      panel.background = element_rect(colour = "black"),
      plot.margin = margin(t = 5.5, r = 9.5, b = 5.5, l = 5.5, "pt")
    ) +
    ggtitle(title)

  return(fig)
}


# Plot rainforest.
#
#  Arguments:
#      data -- The meta-analytic dataset.
#      colmap -- The column-map from the configuration.
#      title -- The analysis title.
#
#  Returns:
#      ggplot figure
#
plotRainforest <- function(data, colmap, title) {
  # Get relevant columns from configuration
  key_z <- colmap$key_z
  key_z_se <- colmap$key_z_se
  key_c <- colmap$key_c

  # Plot rainforest
  sca_rainforest(
    x = cbind(data[[key_z]], data[[key_z_se]]),
    trans_function = tanh,
    x_breaks = atanh(c(-0.5, 0, 0.5, 0.8)),
    names = data[[key_c]],
    detail_level = 30,
    xlab = "Effect size (r)",
    highlightID = 1,
    text_size = 2.5,
    x_limit = atanh(c(-0.6, 0.9))
  ) + ggtitle(title)
}


# Plot GOSH-plot.
#
#  Arguments:
#      data -- The meta-analytic dataset.
#      colmap -- The column-map from the configuration.
#      title -- The analysis title.
#
#  Returns:
#      ggplot figure
#
plotGosh <- function(data, colmap, title) {
  # Get relevant columns from configuration
  key_z <- colmap$key_z
  key_z_se <- colmap$key_z_se

  # Plot GOSH-plot
  sca_gosh(
    x = cbind(data[[key_z]], data[[key_z_se]]),
    random_samples = 100000,
    pointsize = 0.5,
    trans_function = tanh,
    x_breaks = atanh(c(-0.4, -0.2, 0, 0.2, 0.4)),
    cols = c("steelblue4", "firebrick"),
    xlab = "Summary effect (r)",
    text_size = 2.5,
    x_limit = atanh(c(-0.4, 0.4))
  ) + ggtitle(title)
}
