source("user_fit.R")

# Generate bootstrap data.
#
#  Arguments:
#      specs -- Specifications data.
#      n_iter -- The number of bootstrap iterations to run.
#      data -- The meta-analytic dataset.
#      colmap -- The column-map from the configuration.
#      level -- The meta-analysis level (2 or 3).
#      save_path -- The path to where the bootstrap data should be stored.
#
#  Returns:
#      The bootstrap data as a data frame, with the dimensions
#      (n_specs, n_iter).
#
generateBootData <- function(specs, n_iter, data, colmap, level, save_path) {
  # Get unique effect ID sets that make up specifications
  effect_sets <- as.vector(unique(specs$set_es))
  effect_sets <- lapply(strsplit(effect_sets, ","), as.numeric)

  # Prepare empty matrix for samples with n_specs rows and
  # n_iter columns
  n_specs <- nrow(specs)
  res <- matrix(numeric(n_iter * n_specs), ncol = n_iter)

  # Sample n_iter times under null hypothesis
  for (col in 1:n_iter) {
    # Compute summary effects for all effect ID sets according to how-factors
    # using bootstrapped data
    if (level == 2) {
      boot_effects <- specListLvl2(effect_sets, data, colmap)
    } else if (level == 3) {
      boot_effects <- specListLvl3(effect_sets, data, colmap)
    }
    boot_effects <- sort(unlist(boot_effects))

    # Store summary effects for each specification
    res[, col] <- boot_effects
  }

  # Compute 95%-CI for each specification
  boot_lb <- apply(res, 1, function(x) {
    quantile(x, probs = 0.025)
  })
  boot_ub <- apply(res, 1, function(x) {
    quantile(x, probs = 0.975)
  })

  # Store bootstrapped data in data frame
  boot_data <- data.frame(
    rank = 1:n_specs,
    obs = specs$mean,
    boot_lb,
    boot_ub
  )

  # Save data to CSV file
  write.table(
    boot_data,
    file = save_path,
    row.names = FALSE,
    dec = ".",
    sep = ","
  )

  return(boot_data)
}
