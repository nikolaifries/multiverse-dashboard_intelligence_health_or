readConfig <- function(config_path) {
  # Load JSON and initiate lists
  json_data <- fromJSON(config_path, simplifyMatrix = FALSE)
  which_lists <- list()
  how_lists <- list()
  labels <- NULL
  
  n_which <- json_data$which$n
  n_how <- json_data$how$n
  
  for (i in 1:n_which) {
    # Get key and key label
    key <- json_data$which$keys[i]
    key_label <- json_data$which$keys_labels[i]
    
    # Get values and value labels
    values <- json_data$which$values[[i]]
    values_labels <- json_data$which$values_labels[[i]]
    add_all_value = json_data$which$add_all_values[[i]]
    
    # Append all-value (e.g. all_sex, all_race)
    if (add_all_value) {
      all_value <- paste("all_", key, sep = "")
      values <- append(values, all_value)
    }
    
    # Add to list of which-factors
    which_lists[[key]] <- values
    
    # Get all-label value
    all_label <- json_data$which$all_label
    
    # Append labels
    for (value_label in values_labels) {
      l <- paste(key_label, value_label, sep = ": ")
      labels <- c(labels, l)
    }
    
    # Add all-label (e.g. "sex: either")
    if (add_all_value) {
      l <- paste(key_label, all_label, sep = ": ")
      labels <- c(labels, l)
    }
  }
  
  for (i in 1:n_how) {
    # Get key and key label
    key <- json_data$how$keys[i]
    key_label <- json_data$how$keys_labels[i]
    
    # Get values and value labels
    values <- json_data$how$values[[i]]
    values_labels <- json_data$how$values_labels[[i]]
    
    # Add to list of how-factors
    how_lists[[key]] <- values
    
    # Append labels
    for (value_label in values_labels) {
      l <- paste(key_label, value_label, sep = ": ")
      labels <- c(labels, l)
    }
  }
  
  # Return which-lists, how-lists and labels
  config <- list(
    n_which = n_which,
    which_lists = which_lists,
    n_how = n_how,
    how_lists = how_lists,
    labels = labels,
    title = json_data$title,
    level = json_data$level,
    colmap = json_data$colmap,
    k_min = json_data$k_min,
    n_boot_iter = json_data$n_boot_iter
  )
  return(config)
}