source("sca_rainforest.R")
source("sca_gosh.R")

getClusterFillData <- function(data, specs, colmap) {
  key_c_id <- colmap$key_c_id
  key_e_id <- colmap$key_e_id
  key_c <- colmap$key_c
  
  cluster_fill_data <- list()
  
  for (rank in specs$rank) {
    spec <- specs[specs$rank == rank, ]
    set_c_ids <- as.integer(unlist(strsplit(spec$set, ",")))
    set_e_ids <- as.integer(unlist(strsplit(spec$set_es, ",")))
    fills <- rep(0, length(unique(data[[key_c_id]])))
    
    for (c_id in set_c_ids) {
      c_data <- data[data[[key_c_id]] == c_id, ]
      c_e_ids <- c_data[[key_e_id]]
      spec_c_e_ids <- c_e_ids[c_e_ids %in% set_e_ids]
      c_fill <- length(spec_c_e_ids) * 100 / length(c_e_ids)
      fills[c_id] <- c_fill
    }
    
    cluster_fill_data[[as.character(rank)]] <- rev(fills)
  }
  c_ids <- sort(unique(data[[key_c_id]]))
  cluster_fill_data[["labels"]] <- sapply(c_ids, function(c_id) {
    c_data <- data[data[[key_c_id]] == c_id, ]
    return(c_data[1, key_c])
  })
  
  return(cluster_fill_data)
}

getSpecFillData <- function(n_which, which_lists,
                            n_how, how_lists, specs) {
  group_factors <- c(which_lists, how_lists)
  group_factor_values <- rev(unlist(group_factors))
  n_factors <- n_which + n_how
  
  spec_fill_data <- list()
  
  for (rank in specs$rank) {
    spec <- specs[specs$rank == rank, ]
    spec_id <- as.numeric(group_factor_values %in% as.character(unlist(spec[, 1:n_factors])))
    spec_fill_data[[as.character(rank)]] = spec_id * spec$k
  }
  
  return(spec_fill_data)
}

getColors <- function(fill_levels) {
  colors <- RColorBrewer::brewer.pal(min(11, fill_levels - 1), "Spectral")
  return(colors)
}

plotCaterpillar <- function(specs, n_total_specs, colors, k_range,
                            title, x_range, fill_levels) {
  color_scale <- getColorScale_(colors, fill_levels)
  
  y_l_limit = min(specs$lb)
  y_u_limit = max(specs$ub)
  y_range_diff = y_u_limit - y_l_limit
  y_limits = c(y_l_limit - (y_range_diff * 0.1),
               y_u_limit + (y_range_diff * 0.1))
  
  y_breaks <- round(seq(
    round(y_limits[1], 1),
    round(y_limits[2], 1),
    round((y_limits[2] - y_limits[1]) / 5, 1)
  ), 1)
  
  fig <- ggplot(data = specs, aes(x = rank, y = mean)) +
    geom_errorbar(aes(ymin = lb, ymax = ub, col = as.factor(k)), width = 0, size = 0.25) +
    geom_line(col = "black", size = 0.25) + 
    geom_hline(yintercept = 0, linetype = 2, size = 0.25) +
    scale_x_continuous(name = "") +
    scale_y_continuous(name = "Summary effect (r)", breaks = y_breaks) + 
    scale_color_manual(values = color_scale) +
    coord_cartesian(ylim = y_limits, xlim = x_range, expand = FALSE) +
    theme_bw() +
    theme(legend.position = "none",
          axis.text.x = element_blank(),
          axis.ticks.x = element_blank(),
          panel.grid.major.x = element_blank(),
          panel.grid.minor.x = element_blank(),
          panel.grid.major.y = element_line(),
          panel.grid.minor.y = element_blank(),
          plot.margin = margin(t = 5.5, r = 5.5, b = -15, l = 5.5, unit = "pt"))
  
  if (!is.null(title)) {
    fig <- fig + ggtitle(title)
  }
  
  return(fig)
}

plotClusterTiles <- function(specs, cluster_fill_data, n_total_specs,
                             title, x_range) {
  y_labels <- rev(cluster_fill_data[["labels"]])
  cluster_fill_data_2 <- cluster_fill_data[!names(cluster_fill_data) %in% "labels"]
  n_clusters <- length(y_labels)
  
  y_intercepts <- seq(1, n_clusters - 1) + 0.5
  z <- factor(unlist(cluster_fill_data_2))
  n_z_levels <- length(levels(z))
  
  if (n_z_levels < 4) {
    color_scale <- tail(RColorBrewer::brewer.pal(3, "Greens"), n_z_levels - 1)
  } else {
    color_scale <- RColorBrewer::brewer.pal(n_z_levels - 1, "Greens")
  }
  color_scale <- c("white", color_scale)
  
  plot_data <- data.frame(
    x=rep(1:n_total_specs, each = n_clusters),
    y=factor(rep(y_labels, times = n_total_specs), levels = y_labels),
    z=z
  )
  fig <- ggplot(data = plot_data, aes(x = x, y = y, fill = z)) +
    geom_raster() +
    geom_hline(yintercept = y_intercepts) +
    scale_x_continuous(position = "bottom") +
    scale_y_discrete(labels = y_labels) +
    scale_fill_manual(values = color_scale) +
    labs(x = "", y = "") +
    coord_cartesian(expand = F, xlim = x_range) +
    theme_bw() +
    theme(legend.position = "none",
          axis.text.x = element_blank(),
          axis.ticks.x = element_blank(),
          axis.text = element_text(colour = "black"),
          axis.ticks = element_line(colour = "black"),
          plot.margin = margin(t = 5.5, r = 5.5, b = -15, l = 5.5, unit = "pt"))
  
  if (!is.null(title)) {
    fig <- fig + ggtitle(title)
  }
  
  return(fig)
}

plotSpecTiles <- function(specs, n_total_specs, spec_fill_data,
                          labels, colors, k_range, title, x_range, fill_levels) {
  y_labels <- rev(labels)
  n_factors <- length(y_labels)
  
  y_intercept <- getYIntercepts_(y_labels)
  color_scale <- getColorScale_(colors, fill_levels)
  color_scale <- c("white", color_scale)
  
  plot_data <- data.frame(
    x=rep(1:n_total_specs, each = n_factors),
    y=factor(rep(y_labels, times = n_total_specs), levels = y_labels),
    z=factor(unlist(spec_fill_data))
  )
  fig <- ggplot(data = plot_data, aes(x = x, y = y, fill = z)) +
    geom_raster() +
    geom_hline(yintercept = y_intercept) +
    scale_x_continuous(position = "bottom") +
    scale_y_discrete(labels = y_labels) +
    scale_fill_manual(values = color_scale) +
    labs(x = "Specification number", y = "Which/How factors") +
    coord_cartesian(expand = F, xlim = x_range) +
    theme_bw() +
    theme(legend.position = "none",
          axis.text = element_text(colour = "black"),
          axis.ticks = element_line(colour = "black"),
          plot.margin = margin(t = 5.5, r = 5.5, b = 5.5, l = 5.5, unit = "pt"))
  
  if (!is.null(title)) {
    fig <- fig + ggtitle(title)
  }
  
  return(fig)
}

plotClusterSize <- function(specs, k_range, n_total_specs, title, x_range) {
  k_step <- round((k_range[2] - k_range[1]) / 4 / 2) * 2
  y_breaks <- seq(k_range[1], k_range[2], k_step)
  
  fig <- ggplot(data = specs, aes(x = rank, y = kc)) +
    geom_col(width = 1, fill = "darkslategray") +
    scale_x_continuous(name = "") +
    scale_y_continuous(name = "# Clusters", breaks = y_breaks) +
    coord_cartesian(ylim = k_range, xlim = x_range, expand = FALSE) +
    theme_bw() +
    theme(legend.position = "none",
          axis.title = element_text(size = 8),
          axis.text.x = element_blank(),
          axis.ticks.x = element_blank(),
          panel.grid.major.x = element_blank(),
          panel.grid.minor.x = element_blank(),
          panel.grid.major.y = element_line(),
          panel.grid.minor.y = element_blank(),
          plot.margin = margin(t = 5.5, r = 5.5, b = -8, l = 5.5, unit = "pt"))
  
  if (!is.null(title)) {
    fig <- fig + ggtitle(title)
  }
  
  return(fig)
}

plotSampleSize <- function(specs, k_range, n_total_specs, title, x_range) {
  k_step <- round((k_range[2] - k_range[1]) / 4 / 2) * 2
  y_breaks <- seq(k_range[1], k_range[2], k_step)
  
  fig <- ggplot(data = specs, aes(x = rank, y = k)) +
    geom_col(width = 1) +
    scale_x_continuous(name = "") +
    scale_y_continuous(name = "# Samples", breaks = y_breaks) +
    coord_cartesian(ylim = k_range, xlim = x_range, expand = FALSE) +
    theme_bw() +
    theme(legend.position = "none",
          axis.title = element_text(size = 8),
          axis.text.x = element_blank(),
          axis.ticks.x = element_blank(),
          panel.grid.major.x = element_blank(),
          panel.grid.minor.x = element_blank(),
          panel.grid.major.y = element_line(),
          panel.grid.minor.y = element_blank(),
          plot.margin = margin(t = 5.5, r = 5.5, b = -8, l = 5.5, unit = "pt"))
  
  if (!is.null(title)) {
    fig <- fig + ggtitle(title)
  }
  
  return(fig)
}

getYIntercepts_ <- function(y_labels) {
  group_labels <- lapply(unlist(y_labels), function(x) unlist(strsplit(x, ":"))[1])
  cumulative_n_groups <- NULL
  prev_gl = group_labels[[1]]
  i <- 0
  for (gl in group_labels) {
    if (gl != prev_gl) {
      cumulative_n_groups <- c(cumulative_n_groups, i)
    }
    i <- i + 1
    prev_gl = gl
  }
  y_intercept <- cumulative_n_groups + 0.5
  return(y_intercept)
}

getColorScale_ <- function(colors, fill_levels) {
  color_indices <- floor(seq(1, length(colors), length.out = fill_levels - 1)) # TODO
  color_scale <- colors[color_indices]
  return(color_scale)
}

plotMultiverse <- function(specs, n_total_specs, k_range, cluster_fill_data,
                           spec_fill_data, labels, colors, level,
                           title, x_range, fill_levels) {
  
  if (level == 3) {
    fig_cluster_tiles <- plotClusterTiles(specs, cluster_fill_data, n_total_specs,
                                          title, x_range)
    title <- NULL
    fig_cluster_size <- plotClusterSize(specs, k_range, n_total_specs, title, x_range)
  }
  
  fill_levels <- length(unique(unlist(spec_fill_data)))
  fig_caterpillar <- plotCaterpillar(specs, n_total_specs, colors, k_range,
                                     title, x_range, fill_levels)
  title <- NULL
  fig_sample_size <- plotSampleSize(specs, k_range, n_total_specs, title, x_range)
  fig_spec_tiles <- plotSpecTiles(specs, n_total_specs, spec_fill_data, labels, 
                                  colors, k_range, title, x_range, fill_levels)
  
  if (level == 2) {
    fig <- ggarrange(fig_caterpillar, fig_sample_size, fig_spec_tiles,
                     nrow = 3, ncol = 1, heights=c(3,1,6), align="v")
  } else if (level == 3) {
    fig <- ggarrange(fig_cluster_tiles, fig_caterpillar, fig_cluster_size, fig_sample_size, fig_spec_tiles,
                     nrow = 5, ncol = 1, heights=c(3.5, 1.8, 0.6, 0.6, 3.5), align="v")
  }
  return(fig)
}

plotInferential <- function(boot_data, x_range, title) {
  fig <- ggplot(data = boot_data, aes(x = rank, y = obs)) +
    geom_ribbon(aes(x =  rank, ymin = boot_lb, ymax = boot_ub), fill = "gray", color = "black", lty = "dotted", alpha = 0.7, size = 0.25) +
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

plotPValuesHist <- function(specs, title) {
  breaks <- seq(from = 0, to = 1, by = 0.05)
  height <- as.numeric(prop.table(table(cut(specs$p, breaks))))
  plotdata <- data.frame(height, breaks = breaks[-21] + 0.025)
  fig <- ggplot(data = plotdata, aes(x = breaks, y = height)) +
    geom_bar(stat = "identity", width = 0.05, color="black", fill = "azure4") +
    geom_bar(aes(x = breaks, y = ifelse(breaks < 0.05, height, 0)), col = "black", fill = "lightgray", 
             stat = "identity", width = 0.05) +
    coord_cartesian(xlim = c(-0.01, 1.01), ylim = c(0, 0.15), expand = F) +
    labs(y = "Proportion", x = "Specification p-values") +
    theme_bw() +
    theme(strip.text.x = element_text(face="bold"),
          axis.title.x = element_text(color = "white"),
          strip.background = element_rect(colour=NA, fill=NA),
          panel.background = element_rect(colour = "black"),
          plot.margin = margin(t = 5.5, r = 9.5, b = 5.5, l = 5.5, "pt")) +
    ggtitle(title)
  
  return(fig)
}

plotScaRainforest <- function(data, colmap, title) {
  key_z <- colmap$key_z
  key_z_se <- colmap$key_z_se
  key_c <- colmap$key_c
  sca_rainforest(
    x = cbind(data[[key_z]], data[[key_z_se]]),
    trans_function = tanh,
    x_breaks = atanh(c(-0.5, 0, 0.5, 0.8)),
    names = data[[key_c]],
    detail_level = 30,
    xlab = "Effect size (r)",
    highlightID = 1, 
    text_size = 2.5,
    x_limit = atanh(c(-0.6, 0.9))) + ggtitle(title)
}

plotGosh <- function(data, colmap, title) {
  key_z <- colmap$key_z
  key_z_se <- colmap$key_z_se
  
  sca_gosh(
    x = cbind(data[[key_z]], data[[key_z_se]]),
    random_samples = 100000,
    pointsize = 0.5, 
    trans_function = tanh,
    x_breaks = atanh(c(-0.4, -0.2, 0, 0.2, 0.4)),
    cols = c("steelblue4", "firebrick"),
    xlab = "Summary effect (r)",
    text_size = 2.5,
    x_limit = atanh(c(-0.4, 0.4))) + ggtitle(title)
}
