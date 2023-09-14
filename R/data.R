prepareData <- function(colmap, data) {
  key_c <- colmap$key_c
  key_c_id <- colmap$key_c_id
  key_e_id <- colmap$key_e_id
  
  if (!(key_c_id %in% colnames(data))) {
    clusters <- unique(data[[key_c]])
    cluster_ids <- list()
    c_id <- 1
    for (c in clusters) {
      cluster_ids[[c]] <- c_id
      c_id <- c_id + 1
    }
    data[[key_c_id]] <- unlist(lapply(data[[key_c]], FUN = function(x) cluster_ids[[x]]))
  }
  
  data <- data[order(data[[key_c_id]]), ]
  
  if (!(key_e_id %in% colnames(data))) {
    data[[key_e_id]] <- seq(1, nrow(data))
  }
  
  cols <- colnames(data)
  cols_without_keys <- cols[
    (cols != key_c) &
    (cols != key_c_id) &
    (cols != key_e_id)
  ]
  col_order <- c(key_c_id, key_c, key_e_id, cols_without_keys)
  data <- data[, col_order]
  return(data)
}