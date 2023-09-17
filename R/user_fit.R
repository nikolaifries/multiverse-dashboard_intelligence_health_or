library(metafor)

# === USER EDIT HERE ===
# === The methods below should be edited according to the desired how-factors.
# === The methods with the prefix `fit_model` fit a meta-analytic model
# === according to the how-factor values passed to them.
# ===
# === The methods with the prefix `spec_list` compute summary effects for each
# === possible how-factor value combination.
# ===
# === The two methods should be edited in tandem, such that each meta-analytic
# === model in the `spec_list` method can be computed in the corresponding
# === `fit_model` method, given the right arguments.
# ===
# === Edit the two methods with the correct suffix (`lvl_2` or `lvl_3`),
# === according to the desired level (2 or 3).


# Compute 2-level summary effects for each how-factor value combination.
#
#  Arguments:
#      e_ids -- The effect IDs to be included.
#      data -- The meta-analytic dataset.
#      colmap -- The column-map from the configuration.
#
#  Returns:
#      List of computed summary effects.
#
specListLvl2 <- function(e_ids, data, colmap) {
  # === USER EDIT HERE
  # === Get the desired effect sizes from the data
  # Get relevant keys from colmap
  key_z <- colmap$key_z
  key_z_se <- colmap$key_z_se
  key_r <- colmap$key_r
  key_r_se <- colmap$key_r_se
  key_e_id <- colmap$key_e_id

  # Get data for included effects
  temp <- data[data[[key_e_id]] %in% e_ids, ]
  yi_z <- temp[[key_z]]
  sei_z <- temp[[key_z_se]]
  yi_r <- temp[[key_r]]
  sei_r <- temp[[key_r_se]]

  # === USER EDIT HERE
  # === Rewrite list of meta-analytic models to compute as desired
  # Compute summary effects for each how-factor value combination
  ctrl <- list(stepadj = 0.5, maxiter = 2000)
  w <- 1 / nrow(temp)
  fits <- c(
    rma(yi = yi_z, sei = sei_z, method = "FE", data = temp),
    rma(yi = yi_z, sei = sei_z, method = "DL", data = temp),
    rma(yi = yi_z, sei = sei_z, method = "REML", control = ctrl, data = temp),
    rma(yi = yi_z, sei = sei_z, method = "FE", weights = w, data = temp),
    rma(yi = yi_r, sei = sei_r, method = "FE", data = temp),
    rma(yi = yi_r, sei = sei_r, method = "DL", data = temp),
    rma(yi = yi_r, sei = sei_r, method = "REML", control = ctrl, data = temp),
    rma(yi = yi_r, sei = sei_r, method = "FE", weights = w, data = temp)
  )

  # Save summary effects in list
  spec <- NULL
  for (i in seq_along(fits)) {
    fit <- fits[[i]]
    b <- fit$b[[1]]
    # === USER EDIT HERE
    # === Edit this if-clause, depending on which models use a z effect size
    # Transform z to r
    if (i <= 3) {
      spec <- c(spec, tanh(b))
    } else {
      spec <- c(spec, b)
    }
  }

  return(spec)
}


# Fit 2-level meta-analytic model according to how-factor values.
#
#  Arguments:
#      how_values -- The how-factor values.
#      data -- The meta-analytic dataset.
#      colmap -- The column-map from the configuration.
#
#  Returns:
#      List of relevant model result values
#      (mean, lower and upper bound, p-value).
#
fitModelLvl2 <- function(how_values, data, colmap) {
  # === USER EDIT HERE
  # === Save configurated how-values in dedicated variables
  # Get how-factor values
  effect <- how_values$effect
  method <- how_values$ma_method

  # Get effect sizes from data
  if (effect == "r") {
    key_r <- colmap$key_r
    key_r_se <- colmap$key_r_se
    yi <- data[[key_r]]
    sei <- data[[key_r_se]]
  } else if (effect == "z") {
    key_z <- colmap$key_z
    key_z_se <- colmap$key_z_se
    yi <- data[[key_z]]
    sei <- data[[key_z_se]]
  }

  # === USER EDIT HERE
  # === Rewrite this part according to your needs
  # Fit meta-analytic model
  if (method == "FE") {
    fit <- rma(yi = yi, sei = sei, method = "FE")
  } else if (method == "RE_DL") {
    fit <- rma(yi = yi, sei = sei, method = "DL")
  } else if (method == "REML") {
    ctrl <- list(stepadj = 0.5, maxiter = 2000)
    fit <- rma(yi = yi, sei = sei, method = "REML", control = ctrl)
  } else if (method == "unweighted") {
    w <- 1 / nrow(data)
    fit <- rma(yi = yi, sei = sei, method = "FE", weights = w)
  }

  # Save results
  res <- list(
    mean = fit$b[[1]],
    lb = fit$ci.lb[[1]],
    ub = fit$ci.ub[[1]],
    p = fit$pval[[1]]
  )

  # Transform z to r
  if (effect == "z") {
    res$mean <- tanh(res$mean)
    res$lb <- tanh(res$lb)
    res$ub <- tanh(res$ub)
  }

  return(res)
}


# Compute 3-level summary effects for each how-factor value combination.
#
#  Arguments:
#      e_ids -- The effect IDs to be included.
#      data -- The meta-analytic dataset.
#      colmap -- The column-map from the configuration.
#
#  Returns:
#      List of computed summary effects.
#
specListLvl3 <- function(e_ids, data, colmap) {
  # === USER EDIT HERE
  # === Get the desired effect sizes from the data
  # Get relevant keys from colmap
  key_z <- colmap$key_z
  key_z_var <- colmap$key_z_var
  key_r <- colmap$key_r
  key_r_var <- colmap$key_r_var
  key_c_id <- colmap$key_c_id
  key_e_id <- colmap$key_e_id

  # Get data for included effects
  temp <- data[data[[key_e_id]] %in% e_ids, ]
  yi_z <- temp[[key_z]]
  V_z <- temp[[key_z_var]]
  yi_r <- temp[[key_r]]
  V_r <- temp[[key_r_var]]

  # Prepare 3-level dependency formula
  formula_string <- paste("~ 1 | ", key_c_id, "/", key_e_id)
  formula <- as.formula(formula_string)

  # === USER EDIT HERE
  # === Rewrite list of meta-analytic models to compute as desired
  # Compute summary effects for each how-factor value combination
  ctrl <- list(iter.max = 1000, rel.tol = 1e-8)
  fits <- c(
    rma.mv(
      data = temp, yi = yi_z, V = V_z,
      method = "REML", test = "t", random = formula, control = ctrl
    ),
    rma.mv(
      data = temp, yi = yi_z, V = V_z,
      method = "ML", test = "t", random = formula, control = ctrl
    ),
    rma.mv(
      data = temp, yi = yi_z, V = V_z,
      method = "REML", test = "z", random = formula, control = ctrl
    ),
    rma.mv(
      data = temp, yi = yi_z, V = V_z,
      method = "ML", test = "z", random = formula, control = ctrl
    )
  )

  # Save summary effects in list
  spec <- NULL
  for (i in seq_along(fits)) {
    fit <- fits[[i]]
    b <- fit$b[[1]]
    # === USER EDIT HERE
    # === Edit this if-clause, depending on which models use a z effect size
    # Transform z to r
    if (i <= 3) {
      spec <- c(spec, tanh(b))
    } else {
      spec <- c(spec, b)
    }
  }

  return(spec)
}


# Fit 3-level meta-analytic model according to how-factor values.
#
#  Arguments:
#      how_values -- The how-factor values.
#      data -- The meta-analytic dataset.
#      colmap -- The column-map from the configuration.
#
#  Returns:
#      List of relevant model result values
#      (mean, lower and upper bound, p-value).
#
fitModelLvl3 <- function(how_values, data, colmap) {
  # === USER EDIT HERE
  # === Save configurated how-values in dedicated variables
  # Get how-factor values
  effect <- how_values$effect
  method <- how_values$ma_method
  test_type <- substr(how_values$test, 1, 1)

  # Get effect sizes from data
  if (effect == "r") {
    key_r <- colmap$key_r
    key_r_var <- colmap$key_r_var
    yi <- data[[key_r]]
    V <- data[[key_r_var]]
  } else if (effect == "z") {
    key_z <- colmap$key_z
    key_z_var <- colmap$key_z_var
    yi <- data[[key_z]]
    V <- data[[key_z_var]]
  }

  # Prepare 3-level dependency formula
  key_c_id <- colmap$key_c_id
  key_e_id <- colmap$key_e_id
  formula_string <- paste("~ 1 | ", key_c_id, "/", key_e_id)
  formula <- as.formula(formula_string)

  # === USER EDIT HERE
  # === Rewrite this part according to your needs
  # Fit meta-analytic model
  if (method == "REML") {
    mod <- rma.mv(
      data = data, yi = yi, V = V, method = "REML",
      test = test_type, random = formula
    )
  } else if (method == "ML") {
    mod <- rma.mv(
      data = data, yi = yi, V = V, method = "ML",
      test = test_type, random = formula
    )
  }

  # Save results
  res <- list(
    mean = mod$b[[1]],
    lb = mod$ci.lb[[1]],
    ub = mod$ci.ub[[1]],
    p = mod$pval[[1]]
  )

  # Transform z to r
  if (effect == "z") {
    res$mean <- tanh(res$mean)
    res$lb <- tanh(res$lb)
    res$ub <- tanh(res$ub)
  }

  return(res)
}
