##################################################################################################
# Function to create gosh plots in Voracek, Kossmeier, & Tran (2018) Which data to               #
# meta-analyze, and how? A specification-curve and multiverse-analysis approach to meta-analysis #
# Contact: michael.kossmeier@univie.ac.at                                                        #
# Code last edited: July 30, 2018                                                                #
##################################################################################################
sca_gosh <- function(x, highlightID = 1, cols = c("#08519C", "#DEEBF7"), pointsize = 2, random_samples = NULL,
                     text_size = 3, xlab = "Effect size", x_limit = NULL, x_breaks = NULL, trans_function = NULL) {
  
  subset_statistics <- function(subsets, data) {
    es <- data[subsets, 1]
    se <- data[subsets, 2]
    k <- length(es)
    w <- 1/se^2
    M <- sum(es*w)/sum(w)
    Q <- sum(w*(es - M)^2)
    I2 <- ifelse(Q != 0, ifelse(100*(Q - (k-1))/Q >= 0, 100*(Q - (k-1))/Q, 0), 0) 
    data.frame(M = M, I2 = I2)
  }
  
  #all subset meta-analysis
  k <- nrow(x) #number of studies
  
  
  if(!is.null(random_samples)) {
    if(random_samples < 2^nrow(x) - 1) {
      mult_const <- 1
      list_length <- 0
      while(list_length < random_samples) {
        iter_k <- rep(1:k, times = random_samples*mult_const)
        l <- lapply(iter_k, function(x) {sort(sample(1:k, x, replace = F))})
        l <- l[!duplicated(l)]
        list_length <- length(l)
        if(list_length < random_samples) {
          mult_const <- mult_const*2
        }
      }
      subsets <- l[1:random_samples]
    } else {
      subsets <- unlist(sapply(1:k, FUN = function(x) combn(1:k, x, simplify = FALSE)),
                        recursive = FALSE) # all combinations sum(choose(k, 1:k))
    }
  } else {
    subsets <- unlist(sapply(1:k, FUN = function(x) combn(1:k, x, simplify = FALSE)),
                      recursive = FALSE) #all combinations sum(choose(k, 1:k))
  }
  
  subset_results <- lapply(subsets, FUN = function(y) {
    data.frame(subset_to_highlight = as.numeric(highlightID %in% y), subset_statistics(subsets = y, data = x))})
  
  plotdata <- plyr::ldply(subset_results)

  y_limit <- c(-10, 110)
  if(is.null(x_limit)) {
    x_limit <- c(min(plotdata$M) - diff(range(plotdata$M))*0.1, max(plotdata$M) + diff(range(plotdata$M))*0.1)
  }

  scatter <- ggplot(plotdata, aes(x = M, y = I2)) +
    geom_point(aes(fill = as.factor(subset_to_highlight)), size = pointsize, stroke = pointsize*0.1, shape = 21, color = "black") + # alpha = 0.2
    labs(x = xlab, y = expression(I^{2})) + 
    scale_fill_manual(values=c("0" = cols[1], "1" = cols[2])) +
    coord_cartesian(xlim = x_limit, ylim = y_limit, expand = F)
    # define x scale (transformation, breaks, labels) -------------------------
    if(!is.null(trans_function) && identical(trans_function, exp)) {
      if(is.null(x_breaks)) {
        x_breaks <- log(c(rev(1/(2*2^(0:ceiling(max(abs(x_limit)))))), 1, 2*2^(0:ceiling(max(abs(x_limit))))))
      } 
      scatter <- scatter +
        scale_x_continuous(name = xlab,
                           breaks = x_breaks, 
                           labels = function(x) {round(trans_function(x), 3)}) 
    } else {
      if(!is.null(trans_function) && identical(trans_function, tanh)) {
        if(is.null(x_breaks)) {
          scatter <- scatter +
            scale_x_continuous(name = xlab,
                               labels = function(x) {round(trans_function(x), 3)}) 
        } else {
          scatter <- scatter +
          scale_x_continuous(name = xlab,
                             breaks = x_breaks, 
                             labels = function(x) {round(trans_function(x), 3)})
        }
      } else {
        if(is.null(x_breaks)) {
          if(!is.null(trans_function)) {
            scatter <- scatter +
              scale_x_continuous(name = xlab,
                                 labels = function(x) {round(trans_function(x), 3)}) 
          } else {
            scatter <- scatter +
              scale_x_continuous(name = xlab)
          }
        } else {
          if(!is.null(trans_function)) {
            scatter <- scatter +
              scale_x_continuous(name = xlab,
                                 breaks = x_breaks,
                                 labels = function(x) {round(trans_function(x), 3)}) 
          } else {
            scatter <- scatter +
              scale_x_continuous(name = xlab,
                                 breaks = x_breaks)
          }
        }
      }
    }
    scatter <- scatter +
    theme_bw() +
    theme(legend.position = "none",
          text = element_text(size = 1/0.352777778*text_size),
          panel.border = element_rect(fill = NA, colour = "black"),
          panel.grid.major.y = element_line("grey"),
          panel.grid.minor.y = element_line("grey"),
          panel.grid.major.x = element_line("grey"),
          panel.grid.minor.x = element_line("grey"),
          plot.margin = margin(t = 0, r = 0, b = 5.5, l = 5.5, "pt"))
  
  density_M <- ggplot(plotdata, aes(x = M)) +
    geom_density(trim = F, aes(y = ..density.., fill = as.factor(subset_to_highlight)), alpha = 0.75) +
    labs(x = "", y = expression(I^{2})) + 
    coord_cartesian(ylim = c(0, max(density(plotdata$M[plotdata$subset_to_highlight == 0])$y,
                                    density(plotdata$M[plotdata$subset_to_highlight == 1])$y)*1.1),
                    xlim = x_limit, expand = F) +
    scale_y_continuous(breaks = 0, labels = 100) +
    scale_fill_manual(values=c("0" = cols[1], "1" = cols[2]))
  
    # define x scale (transformation, breaks, labels) -------------------------
    if(!is.null(trans_function) && identical(trans_function, exp)) {
      if(is.null(x_breaks)) {
        x_breaks <- log(c(rev(1/(2*2^(0:ceiling(max(abs(x_limit)))))), 1, 2*2^(0:ceiling(max(abs(x_limit))))))
      } 
      density_M <- density_M +
        scale_x_continuous(name = xlab,
                           breaks = x_breaks, 
                           labels = function(x) {round(trans_function(x), 3)}) 
    } else {
      if(!is.null(trans_function) && identical(trans_function, tanh)) {
        if(is.null(x_breaks)) {
          density_M <- density_M +
            scale_x_continuous(name = xlab,
                               labels = function(x) {round(trans_function(x), 3)}) 
        } else {
          density_M <- density_M +
            scale_x_continuous(name = xlab,
                               breaks = x_breaks, 
                               labels = function(x) {round(trans_function(x), 3)})
        }
      } else {
        if(is.null(x_breaks)) {
          if(!is.null(trans_function)) {
            density_M <- density_M +
              scale_x_continuous(name = xlab,
                                 labels = function(x) {round(trans_function(x), 3)}) 
          } else {
            density_M <- density_M +
              scale_x_continuous(name = xlab)
          }
        } else {
          if(!is.null(trans_function)) {
            density_M <- density_M +
              scale_x_continuous(name = xlab,
                                 breaks = x_breaks,
                                 labels = function(x) {round(trans_function(x), 3)}) 
          } else {
            density_M <- density_M +
              scale_x_continuous(name = xlab,
                                 breaks = x_breaks)
          }
        }
      }
    }
  
  density_M <- density_M +
    theme_bw() +
    theme(legend.position = "none",
          panel.border = element_rect(fill = NA, colour = "white"),
          text = element_text(size = 1/0.352777778*text_size),
          axis.text.y = element_text(colour = "white"),
          axis.text.x = element_blank(),
          axis.ticks.x =  element_blank(),
          axis.ticks.y = element_line(colour = "white"),
          axis.title = element_text(colour = "white"),
          panel.grid.major.y = element_blank(),
          panel.grid.minor.y = element_blank(),
          panel.grid.major.x = element_blank(),
          panel.grid.minor.x = element_blank(),
          plot.margin = margin(t = 0, r = 5.5, b = -14.5, l = 5.5, "pt"))
  
  density_I2 <- ggplot(plotdata, aes(x = I2)) +
    geom_density(trim = F, aes(y = ..density.., fill = as.factor(subset_to_highlight)), alpha = 0.75) +
    labs(x = "", y = xlab) + 
    scale_y_continuous(breaks = max(density(plotdata$I2[plotdata$subset_to_highlight == 0])$y,
                                    density(plotdata$I2[plotdata$subset_to_highlight == 1])$y), labels = 0) +
    scale_fill_manual(values=c("0" = cols[1], "1" = cols[2])) +
    theme(legend.position = "none",
          panel.background = element_blank(),
          text = element_text(size = 1/0.352777778*text_size),
          axis.text.x = element_text(colour = "white"),
          axis.text.y = element_blank(),
          axis.ticks.x =  element_line(colour = "white"),
          axis.ticks.y =  element_blank(),
          panel.border = element_rect(fill = NA, colour = "white"),
          axis.title = element_text(colour = "white"),
          panel.grid.major.y = element_blank(),
          panel.grid.minor.y = element_blank(),
          panel.grid.major.x = element_blank(),
          panel.grid.minor.x = element_blank(),
          plot.margin = margin(t = 0, r = 0, b = 5.5, l = -14.5, "pt")) +
    coord_flip(xlim = y_limit, ylim = c(0, max(density(plotdata$I2[plotdata$subset_to_highlight == 0])$y,
                                               density(plotdata$I2[plotdata$subset_to_highlight == 1])$y)*1.1), expand = F)
  
  blank <- ggplot(plotdata, aes(x = M, y = I2)) +
            labs(x = "", y = "") +
            coord_cartesian(expand = F) +
            theme(legend.position = "none",
                  text = element_text(size = 1/0.352777778*text_size),
                  axis.text.x = element_blank(),
                  axis.text.y = element_blank(),
                  axis.ticks.x =  element_blank(),
                  axis.ticks.y =  element_blank(),
                  panel.border = element_rect(fill = NA, colour = "white"),
                  panel.background = element_blank(),
                  panel.grid.major.y = element_blank(),
                  panel.grid.minor.y = element_blank(),
                  panel.grid.major.x = element_blank(),
                  panel.grid.minor.x = element_blank(), 
                  plot.margin = margin(t = 0, r = 0, b = -14.5, l = -14.5, "pt"))
  
  
  layout_matrix <- matrix(c(1, 1, 1, 1, 2, 4, 4, 4, 4, 3, 4, 4, 4, 4, 3, 4, 4, 4, 4, 3, 4, 4, 4, 4, 3), nrow = 5, byrow = T)
  
  
  p <- gridExtra::arrangeGrob(density_M, blank, density_I2, scatter,
                   layout_matrix = layout_matrix)

as_ggplot(p)
}
