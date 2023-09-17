library(foreign)

# Save the preprocessed data.
#
#  Arguments:
#      data -- The preprocessed data as a pandas DataFrame.
#      path -- The path where the unprocessed data was stored (working dir).
#      title -- The title of the dataset.
#
saveData_ <- function(data, path, title) {
  dir <- file.path(dirname(path))
  # Naming convention can be changed, but prefix `data_`
  # should stay for Dashboard
  file <- paste0(dir, "/data_", title, ".csv")
  write.table(data, file = file, row.names = FALSE, dec = ".", sep = ",")
}

# === USER EDIT HERE ===
# === Add your preprocessing code here. The saveData_() call should
# === not be removed. Other functions expect a data frame. For reference,
# === examine the examples below.

# Preprocess and save the meta-analytic dataset.
#
#  Arguments:
#      path -- The path to the dataset.
#      title -- The title of the dataset (for saving).
#  Returns:
#      The preprocessed dataset.
#
preprocessDataEDIT <- function(path, title) {
  # === USER EDIT HERE ===
  # === Preprocess the dataset
  data <- NULL
  saveData_(data, path, title)
  return(data)
}

# Preprocessing for Chernobyl example (level 3).
# preprocessData <- function(path, title) {
#   load(file = path)
#   data <- Chernobyl
#   rm(Chernobyl)
#   data$radiation[is.na(data$radiation)] <- "low"
#   saveData_(data, path, title)
#   return(data)
# }

# Preprocessing for Intelligence & Religion example (level 2).
# preprocessData <- function(path, title) {
#   data <- data.frame(read.spss(path))
#   data <- data[, c(
#     "StudyID", "correlation", "religiosityMeasure",
#     "sample", "publicationstatus", "N", "variance_r"
#   )]
#   data$sample <- as.character(data$sample)
#   data$sample[is.na(data$sample)] <- "Mixed"

#   data$religiosityMeasure <- as.character(data$religiosityMeasure)
#   data$publicationstatus <- as.character(data$publicationstatus)

#   data$r_se <- sqrt(data$variance_r)
#   data$z <- atanh(data$correlation)
#   data$z_se <- data$r_se / (1 - data$correlation^2)
#   saveData_(data, path, title)
#   return(data)
# }

# Preprocessing for Intelligence & Religion example (level 3).
preprocessData <- function(path, title) {
  data <- data.frame(read.spss(path))
  data <- data[, c(
    "StudyID", "correlation", "religiosityMeasure",
    "sample", "publicationstatus", "N", "variance_r"
  )]
  data$StudyID <- gsub("^\\(\\d+\\)\\s*", "", data$StudyID)
  data$sample <- as.character(data$sample)
  data$sample[is.na(data$sample)] <- "Mixed"

  data$religiosityMeasure <- as.character(data$religiosityMeasure)
  data$publicationstatus <- as.character(data$publicationstatus)

  data$r_se <- sqrt(data$variance_r)
  data$z <- atanh(data$correlation)
  data$z_se <- data$r_se / (1 - data$correlation^2)
  saveData_(data, path, title)
  return(data)
}

# Preprocessing for R2D:4D example (level 2).
# preprocessData <- function(path, title) {
#   data <- read.csv2(path, sep = ";", header = TRUE)
#   saveData_(data, path, title)
#   return(data)
# }

# Preprocessing for R2D:4D example (level 3).
# preprocessData <- function(path, title) {
#   data = read.csv2(DATA_PATH, sep = ";", header = TRUE)
#   data$Study_name <- sapply(strsplit(data$Study_name, ", "), function(x) x[1])
#   data$z_var <- data$z_se^2
#   data$r_var <- data$r_se^2
#   saveData_(data, path, title)
#   return(data)
# }
