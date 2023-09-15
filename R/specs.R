source("user_fit.R")

# Generate specifications.
#
#  Arguments:
#      data -- The meta-analytic dataset.
#      which_lists -- The which-factors.
#      how_lists -- The how-factors.
#      colmap -- The column-map from the configuration.
#      k_min -- The minimum number of effects to include a specification.
#      level -- The meta-analysis level (2 or 3).
#      save_path -- The path to where the specification data should be
#                   stored.
#
#  Returns:
#      The specification data as a data frame.
#
generateSpecs <- function(data, which_lists, how_lists, colmap, k_min,
                          level, save_path) {
  # Generate all combinations of which/how factors and get their
  # total number (the amount of specifications)
  group_factors <- c(which_lists, how_lists)
  specs <- expand.grid(group_factors)
  n_specs <- nrow(specs)

  # Add to-be-filled columns with NA values
  tbf_keys <- list(
    "mean", "lb", "ub", "p", "k", "set"
  )
  na_cols <- list()
  for (key in tbf_keys) {
    na_cols[[key]] <- rep(NA, n_specs)
  }

  # Create specification data frame
  specs <- data.frame(specs, na_cols)

  # Get relevant keys from colmap
  key_c_id <- colmap$key_c_id
  key_e_id <- colmap$key_e_id

  # Iterate over all specifications and filter the data according to
  # the which-factors, then perform meta-analytic computations according to
  # how-factors.
  for (i in 1:n_specs) {
    # Copy data into temporary variable
    temp_data <- data

    # Select specification
    spec <- specs[i, ]

    # Iterate over all which-factors and filter data that fits
    for (key in names(which_lists)) {
      # Get specification value for which-factor
      spec_val <- spec[, key]

      # Do not filter data if value is an all-value
      if (startsWith(as.character(spec_val), "all_")) {
        next
      }

      # Filter
      temp_data <- temp_data[temp_data[[key]] == spec_val, ]
    }

    # Disregard data subsets with less than k_min studies
    if (nrow(temp_data) < k_min) {
      next
    }

    # Get sets of cluster- and effect IDs that fulfill the specification
    c_ids <- sort(unique(temp_data[[key_c_id]]))
    e_ids <- sort(temp_data[[key_e_id]])
    # Store IDs as comma-joined lists in specification data
    study_set <- paste(c_ids, collapse = ",")
    es_set <- paste(e_ids, collapse = ",")
    specs$set[i] <- study_set
    specs$set_es[i] <- es_set
    # Store the amount of clusters (kc) and effect sizes (k) that
    # contribute to the specification
    specs$k[i] <- nrow(temp_data)
    specs$kc[i] <- length(c_ids)

    # Fit meta-analytic model with filtered data according to how-factors
    how_values <- list()
    for (k in names(how_lists)) {
      how_values[[k]] <- spec[[k]]
    }
    if (level == 2) {
      res <- fitModelLvl2(how_values, temp_data, colmap)
    } else if (level == 3) {
      res <- fitModelLvl3(how_values, temp_data, colmap)
    }

    # Save model results in specifications data frame
    specs[i, names(res)] <- unlist(res)
  }

  # Remove all specifications which were not used
  specs_full <- specs[complete.cases(specs), ]

  # Only keep unique study/sample subsets
  cols <- c("mean", "set", names(how_lists))
  specs_full <- specs_full[!duplicated(specs_full[, cols]), ]

  # Add binary indicator if all studies are included in the subset
  c_ids <- sort(unique(data[[key_c_id]]))
  all_studies_list <- paste(c_ids, collapse = ",")
  full_set <- (specs_full$set == all_studies_list)
  specs_full$full_set <- as.numeric(full_set)

  # Rank specifications according to mean in ascending order
  specs_full$rank <- rank(specs_full$mean, ties.method = "random")
  # Store CI interval width in dedicated column
  specs_full$ci <- specs_full$ub - specs_full$lb

  # !important Sort specifications by rank
  specs_full <- specs_full[order(specs_full$rank), ]

  # Save specs to CSV file
  write.table(
    specs_full,
    file = save_path,
    row.names = FALSE,
    dec = ".",
    sep = ","
  )

  return(specs_full)
}
