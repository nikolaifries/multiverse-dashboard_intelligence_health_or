source("user_fit.R")

generateSpecs <- function(data, which_lists, how_lists, colmap, k_min,
                          level, save_path) {
  # Generate all combinations of which/how factors
  group_factors <- c(which_lists, how_lists)
  specs <- expand.grid(group_factors)
  n_specs <- nrow(specs)
  
  # Add to-be-filled columns with NA values
  tbf_keys = list(
    "mean", "lb", "ub", "p", "k", "set"
  )
  na_cols <- list()
  for (key in tbf_keys) {
    na_cols[[key]] <- rep(NA, n_specs)
  }
  
  key_c_id <- colmap$key_c_id
  key_e_id <- colmap$key_e_id
  
  # Create specification data frame
  specs <- data.frame(specs, na_cols)
  
  # Iterate over all specifications and store the set of studies that
  # fit each specification
  for (i in 1:n_specs) {
    # Copy data into temporary variable
    temp_data <- data
    
    # Select specification
    spec <- specs[i, ]
    
    # Iterate over all which-factors and filter data that fits
    for (key in names(which_lists)) {
      # Get value for which-factor
      spec_val <- spec[, key]
      
      # Do not filter data if value encompasses is group-value
      if (startsWith(as.character(spec_val), "all_")) {
        next
      }
      
      # Filter
      temp_data <- temp_data[temp_data[[key]] == spec_val, ]
    }
    
    # Disregard data subsets with less than 2 studies
    if(nrow(temp_data) < k_min) {
      next
    }
    
    c_ids <- sort(unique(temp_data[[key_c_id]]))
    e_ids <- sort(temp_data[[key_e_id]])
    # Get set of studies (IDs and amount) that fit the specification
    study_set <- paste(c_ids, collapse = ",")
    es_set <- paste(e_ids, collapse = ",")
    specs$set[i] <- study_set
    specs$set_es[i] <- es_set
    specs$k[i] <- nrow(temp_data)
    specs$kc[i] <- length(c_ids)
    
    # Fit meta-analytic model with filtered data according to how-factors
    effect <- spec$effect
    method <- spec$ma_method
    
    if (level == 2) {
      res <- fitModelLvl2(effect, method, temp_data, colmap)
    }
    else if (level == 3) {
      test <- spec$test
      res <- fitModelLvl3(effect, method, test, temp_data, colmap)
    }
    
    # Save model results in specifications data frame
    specs[i, names(res)] <- unlist(res)
  }
  
  # Remove all specifications which were not used
  specs_full <- specs[complete.cases(specs), ]
  
  # Only keep unique study/sample subsets
  specs_full <- specs_full[!duplicated(specs_full[, c("mean", "set", names(how_lists))]), ]
  
  # Add binary indicator if all studies are included in the subset
  c_ids <- sort(unique(data[[key_c_id]]))
  all_studies_list <- paste(c_ids, collapse =",")
  full_set <- (specs_full$set == all_studies_list)
  specs_full$full_set <- as.numeric(full_set)
  
  specs_full$rank <- rank(specs_full$mean, ties.method = "random")
  specs_full$ci <- specs_full$ub - specs_full$lb
  
  specs_full <- specs_full[order(specs_full$rank), ]
  
  # Save specs to CSV file
  write.table(specs_full, file = save_path, row.names = FALSE, dec = ".", sep = ",")
  
  return(specs_full)
}