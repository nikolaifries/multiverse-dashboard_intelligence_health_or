source("user_fit.R")

generateBootData <- function(specs, n_iter, data, colmap, level, save_path) {
  # Sort effect sizes in ascending order
  specs_means <- sort(specs$mean)
  
  # Get sets of studies for each specification
  effect_sets <- as.vector(unique(specs$set_es))
  effect_sets <- lapply(strsplit(effect_sets, ","), as.numeric)
  
  # Prepare empty matrix for samples with n_iter columns
  # and n_specs rows
  n_specs <- nrow(specs)
  res <- matrix(numeric(n_iter * n_specs), ncol = n_iter)
  
  key_z <- colmap$key_z
  key_z_se <- colmap$key_z_se
  key_r <- colmap$key_r
  key_r_se <- colmap$key_r_se
  key_n <- colmap$key_n
  
  # Sample n_iter times under null hypothesis
  for (col in 1:n_iter) {
    # Draw randomly new effect size and compute standard error
    z_se <- 1 / sqrt(data[[key_n]] - 3)
    data[[key_z]] <- rnorm(nrow(data), mean = 0, sd = z_se)
    data[[key_z_se]] <- z_se
    data[[key_r]] <- tanh(data[[key_z]])
    data[[key_r_se]] <- (1 - data[[key_r]]^2) * z_se
    
    # Compute summary effects for all study sets according to how-factors
    # using bootstrapped data
    if (level == 2) {
      boot_effects <- lapply(effect_sets, FUN = function(x) specListLvl2(x, data, colmap))
    } else if (level == 3) {
      boot_effects <- lapply(effect_sets, FUN = function(x) specListLvl3(x, data, colmap))
    }
    boot_effects <- sort(unlist(boot_effects))
    
    # Store summary effects for each specification
    res[, col] <- boot_effects
  }
  
  # Compute 95%-CI for each specification
  boot_lb <- apply(res, 1, function(x) {quantile(x, probs = 0.025)})
  boot_ub <- apply(res, 1, function(x) {quantile(x, probs = 0.975)})
  
  # Store bootstrapped data in data frame
  boot_data <- data.frame(
    rank = 1:n_specs,
    obs = specs_means,
    boot_lb,
    boot_ub
  )
  
  # Save data to CSV file
  write.table(boot_data, file = save_path, row.names = FALSE, dec = ".", sep = ",")
  
  return(boot_data)
}