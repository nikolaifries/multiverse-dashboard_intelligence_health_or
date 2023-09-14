##################################################################################################
# Function to create rainforest plots in Voracek, Kossmeier, & Tran (2018) Which data to         #
# meta-analyze, and how? A specification-curve and multiverse-analysis approach to meta-analysis #
# Author: Michael Kossmeier (michael.kossmeier@univie.ac.at)                                     #
# Code last edited: July 31, 2018                                                                #
##################################################################################################
sca_rainforest <- function(x,  names = NULL , summary_name = "Summary", highlightID = NULL,
                                confidence_level = 0.95, col = "Blues", highlight_col = "firebrick", method = "FE",
                                xlab = "Effect Size", detail_level = 1, text_size = 3, x_limit = NULL,
                                x_breaks = NULL, trans_function = NULL) {
  es <- x[, 1]
  se <- x[, 2]
  n <- length(es)
  
  mod <- metafor::rma.uni(yi = es, sei = se, method = method)
  summary_es <- mod$b[[1]]
  summary_se <- sqrt(mod$vb[[1]])
  
  # if not exactly one name for every study is suppied the default is used (numbers 1 to the number of studies)
  if(is.null(names) || n != length(names)) {
    names <- 1:n
  }
  
  # Determine IDs for studies and summary effects (correspond to plotting coordinates in the rainforest plot)
  ids <- c(n:1, -1)
  
  # create dataframe for plotting point estimates and confidence intervals
  plotdata <- data.frame("x" = c(es, summary_es), "se" = c(se, summary_se),
                         "ID" = ids, "names" = c(names, summary_name))
  
  # Add confidence intervals
  plotdata <- data.frame(rbind(plotdata, plotdata),
                         "ci_value" = c(plotdata$x - qnorm(1-(1-confidence_level)/2, 0, 1)*plotdata$se,
                                        plotdata$x + qnorm(1-(1-confidence_level)/2, 0, 1)*plotdata$se))
  
  # function ll constructs a likelihood raindrop of a study. The raindrop is built out of
  # several distinct segments (to color shade the raindrop)
  ll <- function(x, max.range, max.weight) {
    # width of the region over which the raindop is built
    se.factor <- ceiling(qnorm(1-(1-confidence_level)/2, 0, 1))
    width <- abs((x[1] - se.factor * x[2]) - (x[1] + se.factor * x[2]))
    
    # max.range is internally determined as the width of the broadest raindop.
    # The number of points to construct the raindrop is chosen proportional to
    # the ratio of the width of the raindrop and the max.range,
    # because slim/dense raindrops do not need as many support points as very broad ones.
    # Minimum is 200 points (for the case that width/max.range gets very small)
    length.out <- max(c(floor(1000 * width / max.range), 200))
    
    # Create sequence of points to construct the raindrop. The number of points is chosen by length.out
    # and can be changed by the user with the parameter detail_level.
    # At least 50 support points (for detail level << 1) per raindrop are chosen
    support <- seq(x[1] - se.factor * x[2], x[1] + se.factor * x[2], length.out = max(c(length.out * detail_level, 50)))
    
    # The values for the likelihood drop are determined: The likelihood for different hypothetical true values
    # minus likelihood for the observed value (i.e. the maximum likelihood) plus the confidence.level quantile of the chi square
    # distribution with one degree of freedeom divided by two.
    # Explanation: -2*(log(L(observed)/L(hypothetical))) is an LRT test and approx. chi^2 with 1 df and significance threshold
    # qchisq(confidence.level, df = 1).
    # That means by adding the confidence.level quantile of the chi square
    # distribution with one degree of freedom (the significance threshold) divided by two,
    # values with l_mu < 0 differ significantly from the observed value.
    threshold <- qchisq(confidence_level, df = 1)/2
    l_mu <- log(dnorm(x[1], mean = support, sd = x[2])) - log(dnorm(x[1], mean = x[1], sd = x[2])) + threshold
    
    #scale raindrop such that it is proportional to the meta-analytic weight and has height smaller than 0.5
    l_mu <- l_mu/max(l_mu) * x[3]/max.weight * 0.495
    
    # Force raindrops of studies to have minimum height of 0.05 (i.e. approx. one tenth of the raindrop with maximum height)
    if(max(l_mu) < 0.05) {
      l_mu <- l_mu/max(l_mu) * 0.05
    }
    
    # mirror values for raindrop
    l_mu_mirror <- -l_mu
    
    # select only likelihood values that are equal or larger than zero,
    # i.e. values that also lie in the confidence interval (using normality assumption)
    sel <- which(l_mu >= 0)
    
    # Construct data.frame
    d <- data.frame("support" = c(support[sel], rev(support[sel])), "log_density" = c(l_mu[sel], rev(l_mu_mirror[sel])))
    
    # The number of segments for shading is chosen as follows: 40 segements times the detail_level per drop
    # as default. The minimum count of segments is 20 (If detail_level is << 1), with the exception that
    # if there are too few points for 20 segments then nrow(d)/4 is used (i.e. at least 4 points per segment)
    data.frame(d, "segment" = cut(d$support, max(c(40*detail_level), min(c(20, nrow(d)/4)))))
  }
  
  # compute the max range of all likelihood drops for function ll.
  max.range <- max(abs((es + qnorm(1-(1-confidence_level)/2) * se) - (es - (qnorm(1-(1-confidence_level)/2) * se))))
  
  # computes all likelihood values and segments (if shading == T). The output is a list, where every element
  # constitutes one study raindop
  weights <- 1/se^2
  rel_weights <- weights/sum(weights)
  res <- apply(cbind(es,se, rel_weights), 1,  FUN = function(x) {ll(x, max.range = max.range, max.weight = max(rel_weights))})
  
  # name every list entry, i.e. raindrop
  names(res) <- n:1
  
  # The prep.data function prepares the list of raindrops in three ways for plotting (shading of segments):
  # 1) the values are sorted by segments, such that the same segments of each raindrop are joined together
  # 2) segments are renamed with integer values from 1 to the number of segments per raindrop
  # 3) to draw smooth raindrops the values at the right hand boundary of each segment have to be the first
  # values at the left hand boundary of the next segment on the right.
  prep.data <- function(res) {
    res <- lapply(res, FUN = function(x) {x <- x[order(x$segment), ]})
    res <- lapply(res, FUN = function(x) {x$segment <- factor(x$segment, labels = 1:length(unique(x$segment))); x})
    res <- lapply(res, FUN = function(x) {
      seg_n <- length(unique(x$segment))
      first <- sapply(2:seg_n, FUN = function(n) {min(which(as.numeric(x$segment) == n))})
      last <-  sapply(2:seg_n, FUN = function(n) {max(which(as.numeric(x$segment) == n))})
      neighbor.top <-   x[c(aggregate(support~segment, FUN = which.max, data=x)$support[1],
                            cumsum(aggregate(support~segment, FUN = length, data=x)$support)[-c(seg_n-1, seg_n)] +
                              aggregate(support~segment, FUN = which.max, data=x)$support[-c(1, seg_n)]), c("support", "log_density")]
      neighbor.bottom <-   x[c(aggregate(support~segment, FUN = which.max, data=x)$support[1],
                               cumsum(aggregate(support~segment, FUN = length, data=x)$support[-c(seg_n-1, seg_n)])+
                                 aggregate(support~segment, FUN = which.max, data=x)$support[-c(1, seg_n)]) + 1, c("support", "log_density")]
      x[first, c("support", "log_density")] <- neighbor.top
      x[last, c("support", "log_density")] <- neighbor.bottom
      x
    }
    )
    res
  }
  res <- prep.data(res)
  
  # merge the list of raindops in one dataframe for plotting
  res <- plyr::ldply(res)
  
  # Plotting parameters y axis
  y_limit <- c(-2, n + 1)
  y_tick_names <- c(as.vector(names), as.vector(summary_name))
  y_breaks <- ids
  
  # Construct summary diamond
  summarydata <- data.frame("x.diamond" = c(summary_es - qnorm(1 - (1 - confidence_level) / 2, 0, 1) * summary_se,
                                            summary_es,
                                            summary_es + qnorm(1 - (1 - confidence_level) / 2, 0, 1) * summary_se,
                                            summary_es),
                            "y.diamond" = c(-1,
                                            -0.7,
                                            -1,
                                            -1.3))
  
  if(is.null(x_limit)) {
    x_limit <- c(min(0,  range(plotdata$ci_value)[1] - diff(range(plotdata$ci_value))*0.05), 
                 max(0, range(plotdata$ci_value)[2] + diff(range(plotdata$ci_value))*0.05))
  }
  
  # To shade all segments of each raindop symmetrically the min abs(log_density) per raindrop is used
  # as aesthetic to fill the segments. This is necessary because otherwise the first log_density value per
  # segment would be used leading to asymmetrical shading
  min.ld <- aggregate(log_density ~ segment + .id, FUN  = function(x) {min(abs(x))}, data = res)
  names(min.ld) <- c("segment", ".id", "min_log_density")
  res <- merge(res, min.ld, sort = F)
  
  # Set Color palette for shading
  if(!(col %in% c("Blues", "Greys", "Oranges", "Greens", "Reds", "Purples"))) { # Was a supported color specifed by the user?
    warning("Supported arguments for col are Blues, Greys, Oranges, Greens, Reds, and Purples. Default Blues is used")
    col <- "Blues"
  }
  col <- RColorBrewer::brewer.pal(n = 9, name = col)
  
  # Create Rainforest plot
  p <-
    ggplot(data = res, aes(y = .id, x = support)) +
    geom_vline(xintercept = 0, linetype = 2, size = 0.25) +
    geom_polygon(data = res, aes(x = support, y = as.numeric(.id) + log_density,
                                 color = min_log_density, fill = min_log_density,
                                 group = paste(.id, segment)), size = 0.1) +
    geom_polygon(data = res[res$.id == n - highlightID + 1, ], aes(x = support, y = as.numeric(.id) + log_density,
                                                                   group = paste(.id, segment)), color = highlight_col, fill = highlight_col, size = 0.1) +
    geom_point(data = plotdata, shape = "I", aes(x = x, y = ID), col = "grey", size = 1) +
    geom_line(data = plotdata, col = "grey", aes(x = ci_value, y = ID, group = ID), size = 0.1) +
    geom_polygon(data = summarydata, aes(x = x.diamond, y = y.diamond), color="black", fill = col[9], size = 0.1) +
    scale_fill_gradient(high = col[9], low = col[3], guide = FALSE) +
    scale_color_gradient(high = col[9], low = col[3], guide = FALSE) +
    scale_y_continuous(name = "",
                       breaks = y_breaks,
                       labels = y_tick_names) + 
    coord_cartesian(xlim = x_limit, ylim = y_limit, expand = F)
  # define x scale (transformation, breaks, labels) -------------------------
  if(!is.null(trans_function) && identical(trans_function, exp)) {
    if(is.null(x_breaks)) {
      x_breaks <- log(c(rev(1/(2*2^(0:ceiling(max(abs(x_limit)))))), 1, 2*2^(0:ceiling(max(abs(x_limit))))))
    } 
    p <- p +
      scale_x_continuous(name = xlab,
                         breaks = x_breaks, 
                         labels = function(x) {round(trans_function(x), 3)}) 
  } else {
    if(!is.null(trans_function) && identical(trans_function, tanh)) {
      if(is.null(x_breaks)) {
        p <- p +
          scale_x_continuous(name = xlab,
                             labels = function(x) {round(trans_function(x), 3)}) 
      } else {
        p <- p +
          scale_x_continuous(name = xlab,
                             breaks = x_breaks, 
                             labels = function(x) {round(trans_function(x), 3)})
      }
    } else {
      if(is.null(x_breaks)) {
        if(!is.null(trans_function)) {
          p <- p +
            scale_x_continuous(name = xlab,
                               labels = function(x) {round(trans_function(x), 3)}) 
        } else {
          p <- p +
            scale_x_continuous(name = xlab)
        }
      } else {
        if(!is.null(trans_function)) {
          p <- p +
            scale_x_continuous(name = xlab,
                               breaks = x_breaks,
                               labels = function(x) {round(trans_function(x), 3)}) 
        } else {
          p <- p +
            scale_x_continuous(name = xlab,
                               breaks = x_breaks)
        }
      }
    }
  }
  p <- p + 
    theme(axis.line = element_line(colour = "black", linetype = "solid"),
          text = element_text(size = 1/0.352777778*text_size),
          panel.border = element_rect(fill = NA, colour = "black"),
          panel.background = element_blank(),
          panel.grid.major.y = element_blank(),
          panel.grid.minor.y = element_blank(),
          panel.grid.major.x = element_line("grey"),
          panel.grid.minor.x = element_line("grey"))
  p
}