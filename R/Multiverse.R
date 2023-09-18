library(ggplot2)
library(ggpubr)
library(metafor)

source("bootstrap.R")
source("config.R")
source("data.R")
source("plotting.R")
source("specs.R")
source("user_data.R")

# === USER EDIT HERE ===
# Set paths to dataset, working directory, choose what data to generate

TITLE <- "R2D4D_2"
DIR <- "../examples/R2D4D"
DATA_PATH <- paste0(DIR, "/R2D4D.csv")

# TITLE <- "Chernobyl_3"
# DIR <- "../examples/Chernobyl"
# DATA_PATH <- paste0(DIR, "/Chernobyl.rda")

# TITLE = "IandR_2"
# DIR = "../examples/IandR"
# DATA_PATH = paste0(DIR, "/iandr.sav")

PREPROCESS_DATA <- T # Load (False) or preprocess data (True)
GENERATE_SPECS <- T # Load (False) or generate specs (True)
GENERATE_BOOTDATA <- T # Load (False) or generate boot data (True)

CONFIG_PATH <- paste0(DIR, "/config_", TITLE, ".json")
PP_DATA_PATH <- paste0(DIR, "/data_", TITLE, ".csv")
SPECS_PATH <- paste0(DIR, "/specs_", TITLE, ".csv")
BOOT_PATH <- paste0(DIR, "/boot_", TITLE, ".csv")

# === USER EDIT STOP

config <- readConfig(CONFIG_PATH)
if (!is.null(config)) {
  c_info <- NULL
  c_info <- c(c_info, paste(config$title, "- Level", config$level, "Meta-Analysis"))
  c_info <- c(c_info, paste("  ", "Minimum Nr. of Samples to include Specification:", config$k_min))
  c_info <- c(c_info, paste("  ", "Bootstrap Iterations:", config$n_boot_iter))
  c_info <- c(c_info, paste("  ", config$n_which, "Which-Factors:"))
  n_which_combos <- 1
  for (which_f in names(config$which_lists)) {
    values <- config$which_lists[[which_f]]
    values_str <- paste(values, collapse = ", ")
    n_which_combos <- n_which_combos * length(values)
    c_info <- c(c_info, paste("    ", which_f, ":", values_str))
  }
  c_info <- c(c_info, paste("  (", n_which_combos, "Which-Factor Combinations )"))
  c_info <- c(c_info, paste("  ", config$n_how, "How-Factors:"))
  for (how_f in names(config$how_lists)) {
    values <- config$how_lists[[how_f]]
    values_str <- paste(values, collapse = ", ")
    c_info <- c(c_info, paste("    ", how_f, ":", values_str))
  }
  c_info <- c(c_info, paste("  ", "Labels"))
  for (label in config$labels) {
    c_info <- c(c_info, paste("    ", label))
  }
  c_info <- c(c_info, paste("  ", "Column-Map"))
  for (key in names(config$colmap)) {
    c_info <- c(c_info, paste("    ", key, ":", config$colmap[[key]]))
  }

  cat(c_info, sep = "\n")
}

if (PREPROCESS_DATA) {
  ma_data <- preprocessData(DATA_PATH, title = TITLE)
} else {
  ma_data <- read.table(PP_DATA_PATH, sep = ",", header = TRUE)
}
print(dim(ma_data))
print(head(ma_data))

data <- prepareData(config$colmap, ma_data)
print(dim(data))
print(head(data))

if (GENERATE_SPECS) {
  specs <- generateSpecs(
    data,
    config$which_lists,
    config$how_lists,
    config$colmap,
    config$k_min,
    config$level,
    SPECS_PATH
  )
} else {
  specs <- read.table(SPECS_PATH, sep = ",", header = TRUE)
}
print(dim(specs))
print(head(specs))

if (GENERATE_BOOTDATA) {
  boot_data <- generateBootData(
    specs,
    config$n_boot_iter,
    data,
    config$colmap,
    config$level,
    BOOT_PATH
  )
} else {
  boot_data <- read.table(BOOT_PATH, sep = ",", header = TRUE)
}
print(dim(boot_data))
print(head(boot_data))

cluster_fill_data <- getClusterFillData(data, specs, config$colmap)
spec_fill_data <- getSpecFillData(
  config$n_which,
  config$which_lists,
  config$n_how,
  config$how_lists,
  specs
)
fill_levels <- length(unique(unlist(spec_fill_data)))
colors <- getColors(fill_levels)

colmap <- config$colmap # Column-mapping from the configuration file
k_range <- c(config$k_min, max(specs$k)) # Range of k-values (# Samples)
labels <- config$labels # Factor-labels
level <- config$level # Meta-analytic level (2 or 3)
n_total_specs <- nrow(specs) # Total number of specifications
title <- config$title # Title of Meta-Analysis
x_range <- c(1 - 0.5, n_total_specs + 0.5) # x-axis range

# === USER EDIT HERE ===
# Choose which figures to plot / save

fig_inferential <- plotInferential(boot_data, x_range, title)
fig_p_hist <- plotPValuesHist(specs, title)
fig_multiverse <- plotMultiverse(
  specs, n_total_specs, k_range, cluster_fill_data,
  spec_fill_data, labels, colors, level, title,
  x_range, fill_levels
)
fig_caterpillar <- plotCaterpillar(specs, colors, title, x_range, fill_levels)
fig_cluster_tiles <- plotClusterTiles(
  specs, cluster_fill_data, n_total_specs, title, x_range
)
fig_cluster_size <- plotClusterSize(
  specs, k_range, n_total_specs, title, x_range
)
fig_sample_size <- plotSampleSize(
  specs, k_range, n_total_specs, title, x_range
)
fig_spec_tiles <- plotSpecTiles(
  specs, n_total_specs, spec_fill_data, labels, colors, title, x_range,
  fill_levels
)
# fig_rainforest <- plotRainforest(data, colmap, title)
# fig_gosh <- plotGosh(data, colmap, title)

# ggsave("multiverse.pdf", fig_multiverse, width = 16 * 1.2, height = 50 * 1.2, dpi = 600, units = "cm")
