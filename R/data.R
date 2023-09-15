# Prepare the meta-analytic dataset for multiverse
# analysis.
#
#  Arguments:
#      colmap -- The column-map from the configuration.
#      data -- The meta-analytic data.
#
#  Returns:
#      Prepared data as a data frame.
#
prepareData <- function(colmap, data) {
  # Get relevant keys from colmap
  key_c <- colmap$key_c
  key_c_id <- colmap$key_c_id
  key_e_id <- colmap$key_e_id

  # If a cluster ID does not exist, create it
  if (!(key_c_id %in% colnames(data))) {
    # Get set of clusters by name
    clusters <- unique(data[[key_c]])

    # Create ID map, mapping an ID to each cluster
    cluster_ids <- list()
    c_id <- 1
    for (c in clusters) {
      cluster_ids[[c]] <- c_id
      c_id <- c_id + 1
    }

    # Add cluster ID column into DataFrame
    data[[key_c_id]] <- unlist(
      lapply(data[[key_c]], FUN = function(x) cluster_ids[[x]])
    )
  }

  # Sort meta-analytic data by cluster ID
  data <- data[order(data[[key_c_id]]), ]

  # If an effect ID does not exist, create it
  if (!(key_e_id %in% colnames(data))) {
    data[[key_e_id]] <- seq(1, nrow(data))
  }

  # Reorder columns such that cluster ID, cluster name
  # and effect ID are the first three columns
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
