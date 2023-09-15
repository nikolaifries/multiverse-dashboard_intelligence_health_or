library(foreign)

saveData_ <- function(data, path, title) {
  dir <- file.path(dirname(path))
  file <- paste0(dir, "/data_", title, ".csv")
  write.table(data, file = file, row.names = FALSE, dec = ".", sep = ",")
}

# preprocessData <- function(path, title) {
#   load(file = path)
#   data <- Chernobyl
#   rm(Chernobyl)
#   data$radiation[is.na(data$radiation)] <- "low"
#   saveData_(data, path, title)
#   return(data)
# }

# preprocessData <- function(path, title) {
#   data = read.csv2(path, sep = ";", header = TRUE)
#   saveData_(data, path, title)
#   return(data)
# }

# preprocessData <- function(path, title) {
#   data = read.csv2(DATA_PATH, sep = ";", header = TRUE)
#   data$Study_name <- sapply(strsplit(data$Study_name, ", "), function(x) x[1])
#   data$z_var <- data$z_se^2
#   data$r_var <- data$r_se^2
#   saveData_(data, path, title)
#   return(data)
# }

preprocessData <- function(path, title) {
  data <- data.frame(read.spss(path))
  data <- data[, c("StudyID", "correlation", "religiosityMeasure", "sample", "publicationstatus", "N", "variance_r")]
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