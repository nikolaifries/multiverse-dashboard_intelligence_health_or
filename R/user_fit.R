library(metafor)

specListLvl2 <- function(e_ids, data, colmap) {
  key_z <- colmap$key_z
  key_z_se <- colmap$key_z_se
  key_r <- colmap$key_r
  key_r_se <- colmap$key_r_se

  key_e_id <- colmap$key_e_id

  temp <- data[data[[key_e_id]] %in% e_ids, ]
  yi_z <- temp[[key_z]]
  sei_z <- temp[[key_z_se]]
  yi_r <- temp[[key_r]]
  sei_r <- temp[[key_r_se]]
  spec <- c(
    tanh(rma(yi = yi_z, sei = sei_z, method = "FE", data = temp)$b[[1]]),
    tanh(rma(yi = yi_z, sei = sei_z, method = "DL", data = temp)$b[[1]]),
    tanh(rma(yi = yi_z, sei = sei_z, method = "REML", control = list(stepadj = 0.5, maxiter = 2000), data = temp)$b[[1]]),
    tanh(rma(yi = yi_z, sei = sei_z, method = "FE", weights = 1 / nrow(temp), data = temp)$b[[1]]),
    rma(yi = yi_r, sei = sei_r, method = "FE", data = temp)$b[[1]],
    rma(yi = yi_r, sei = sei_r, method = "DL", data = temp)$b[[1]],
    rma(yi = yi_r, sei = sei_r, method = "REML", control = list(stepadj = 0.5, maxiter = 2000), data = temp)$b[[1]],
    rma(yi = yi_r, sei = sei_r, method = "FE", weights = 1 / nrow(temp), data = temp)$b[[1]]
  )
  return(spec)
}

fitModelLvl2 <- function(how_values, data, colmap) {
  effect <- how_values$effect
  method <- how_values$ma_method
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

  if (method == "FE") {
    mod <- rma(yi = yi, sei = sei, method = "FE")
  } else if (method == "RE_DL") {
    mod <- rma(yi = yi, sei = sei, method = "DL")
  } else if (method == "REML") {
    mod <- rma(yi = yi, sei = sei, method = "REML", control = list(stepadj = 0.5, maxiter = 2000))
  } else if (method == "unweighted") {
    mod <- rma(yi = yi, sei = sei, method = "FE", weights = 1 / nrow(data))
  }

  # Save results
  res <- list(
    mean = mod$b[[1]],
    lb = mod$ci.lb[[1]],
    ub = mod$ci.ub[[1]],
    p = mod$pval[[1]]
  )
  # Transform results
  if (effect == "z") {
    res$mean <- tanh(res$mean)
    res$lb <- tanh(res$lb)
    res$ub <- tanh(res$ub)
  }

  return(res)
}

specListLvl3 <- function(e_ids, data, colmap) {
  key_z <- colmap$key_z
  key_z_var <- colmap$key_z_var
  key_r <- colmap$key_r
  key_r_var <- colmap$key_r_var

  key_c_id <- colmap$key_c_id
  key_e_id <- colmap$key_e_id
  formula_string <- paste("~ 1 | ", key_c_id, "/", key_e_id)
  formula <- as.formula(formula_string)

  temp <- data[data[[key_e_id]] %in% e_ids, ]
  yi_z <- temp[[key_z]]
  V_z <- temp[[key_z_var]]
  yi_r <- temp[[key_r]]
  V_r <- temp[[key_r_var]]
  spec <- c(
    tanh(rma.mv(data = temp, yi = yi_z, V = V_z, method = "REML", test = "t", random = formula, control = list(iter.max = 1000, rel.tol = 1e-8))$b[[1]]),
    tanh(rma.mv(data = temp, yi = yi_z, V = V_z, method = "ML", test = "t", random = formula, control = list(iter.max = 1000, rel.tol = 1e-8))$b[[1]]),
    tanh(rma.mv(data = temp, yi = yi_z, V = V_z, method = "REML", test = "z", random = formula, control = list(iter.max = 1000, rel.tol = 1e-8))$b[[1]]),
    tanh(rma.mv(data = temp, yi = yi_z, V = V_z, method = "ML", test = "z", random = formula, control = list(iter.max = 1000, rel.tol = 1e-8))$b[[1]])
  )
  return(spec)
}

fitModelLvl3 <- function(effect, method, test, data, colmap) {
  effect <- how_values$effect
  method <- how_values$ma_method
  test_type <- substr(how_values$test, 1, 1)
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

  key_c_id <- colmap$key_c_id
  key_e_id <- colmap$key_e_id
  formula_string <- paste("~ 1 | ", key_c_id, "/", key_e_id)
  formula <- as.formula(formula_string)

  if (method == "REML") {
    mod <- rma.mv(data = data, yi = yi, V = V, method = "REML", test = test_type, random = formula)
  } else if (method == "ML") {
    mod <- rma.mv(data = data, yi = yi, V = V, method = "ML", test = test_type, random = formula)
  }

  # Save results
  res <- list(
    mean = mod$b[[1]],
    lb = mod$ci.lb[[1]],
    ub = mod$ci.ub[[1]],
    p = mod$pval[[1]]
  )
  # Transform results
  if (effect == "z") {
    res$mean <- tanh(res$mean)
    res$lb <- tanh(res$lb)
    res$ub <- tanh(res$ub)
  }

  return(res)
}
