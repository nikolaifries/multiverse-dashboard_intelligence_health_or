library(jsonlite)

# Read and process configuration file.
#
#  Arguments:
#      path -- The path to the configuration file.
#
#  Returns:
#      Configuration list containing the needed data.
#
readConfig <- function(path) {
  # Load JSON from file, without simplifying
  json_data <- fromJSON(path, simplifyMatrix = FALSE)

  # Prepare empty lists for which- and how-factors, and
  # empty variable for labels
  which_lists <- list()
  how_lists <- list()
  labels <- NULL

  # Get amount of which- and how- factors
  n_which <- json_data$which$n
  n_how <- json_data$how$n

  # Get lists of keys, key-labels, values, value-labels and boolean
  # flags for all-values for which-factors
  which_keys <- json_data$which$keys
  which_keys_labels <- json_data$which$keys_labels
  which_values <- json_data$which$values
  which_values_labels <- json_data$which$values_labels
  which_add_all_values <- json_data$which$add_all_values

  # Get lists of keys, key-labels, values, value-labels for how-factors
  how_keys <- json_data$how$keys
  how_keys_labels <- json_data$how$keys_labels
  how_values <- json_data$how$values
  how_values_labels <- json_data$how$values_labels

  # Check if lengths match
  for (wl in list(
    which_keys, which_keys_labels, which_values,
    which_values_labels, which_add_all_values
  )) {
    if (length(wl) != n_which) {
      print(wl)
      print("ERROR: Configuration of which-factors is incorrect.")
      return(NULL)
    }
  }
  for (hl in list(how_keys, how_keys_labels, how_values, how_values_labels)) {
    if (length(hl) != n_how) {
      print("ERROR: Configuration of how-factors is incorrect.")
      return(NULL)
    }
  }

  # Process which-factors
  # Get all-label value
  all_label <- json_data$which$all_label
  for (i in 1:n_which) {
    # Get key and key label
    key <- which_keys[i]
    key_label <- which_keys_labels[i]

    # Get values, value labels and information about all-values
    values <- which_values[[i]]
    values_labels <- which_values_labels[[i]]
    add_all_value <- which_add_all_values[[i]]

    # Append all-value (e.g. all_sex, all_race), if desired
    # for this factor
    if (add_all_value) {
      all_value <- paste("all_", key, sep = "")
      values <- append(values, all_value)
    }

    # Add to list of which-factors
    which_lists[[key]] <- values

    # Append labels
    for (value_label in values_labels) {
      l <- paste(key_label, value_label, sep = ": ")
      labels <- c(labels, l)
    }

    # Add all-label (e.g. "sex: either"), if desired
    # for this factor
    if (add_all_value) {
      l <- paste(key_label, all_label, sep = ": ")
      labels <- c(labels, l)
    }
  }

  # Process which-factors
  for (i in 1:n_how) {
    # Get key and key label
    key <- how_keys[i]
    key_label <- how_keys_labels[i]

    # Get values and value labels
    values <- how_values[[i]]
    values_labels <- how_values_labels[[i]]

    # Add to list of how-factors
    how_lists[[key]] <- values

    # Append labels
    for (value_label in values_labels) {
      l <- paste(key_label, value_label, sep = ": ")
      labels <- c(labels, l)
    }
  }

  # Return configuration list containing the needed data
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
