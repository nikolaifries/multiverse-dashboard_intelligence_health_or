import numpy as np
import os
from rpy2.robjects.packages import importr
from rpy2.robjects import ListVector, Formula, pandas2ri

# === USER EDIT HERE ===
# === Add the path to your R installation
os.environ['R_HOME'] = "C:\\Program Files\\R\\R-4.3.1"

metafor = importr('metafor')
pandas2ri.activate()

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


def spec_list_lvl_2(e_ids, data, colmap):
    """Compute 2-level summary effects for each how-factor value combination.

    Arguments:
        e_ids -- The effect IDs to be included.
        data -- The meta-analytic dataset.
        colmap -- The column-map from the configuration.

    Returns:
        List of computed summary effects.
    """
    # === USER EDIT HERE
    # === Get the desired effect sizes from the data
    # Get relevant keys from colmap
    key_z = colmap["key_z"]
    key_z_se = colmap["key_z_se"]
    key_r = colmap["key_r"]
    key_r_se = colmap["key_r_se"]
    key_e_id = colmap["key_e_id"]

    # Get data for included effects
    temp = data[data[key_e_id].isin(e_ids)]
    z = temp[key_z]
    z_se = temp[key_z_se]
    r = temp[key_r]
    r_se = temp[key_r_se]

    # === USER EDIT HERE
    # === Rewrite list of meta-analytic models to compute as desired
    # Compute summary effects for each how-factor value combination
    ctrl = ListVector(dict(stepadj=0.5, maxiter=2000))
    w = 1/len(temp)
    fits = [
        metafor.rma(yi=z, sei=z_se, method="FE"),
        metafor.rma(yi=z, sei=z_se, method="DL"),
        metafor.rma(yi=z, sei=z_se, method="REML", control=ctrl),
        metafor.rma(yi=z, sei=z_se, method="FE", weights=w),
        metafor.rma(yi=r, sei=r_se, method="FE"),
        metafor.rma(yi=r, sei=r_se, method="DL"),
        metafor.rma(yi=r, sei=r_se, method="REML", control=ctrl),
        metafor.rma(yi=r, sei=r_se, method="FE", weights=w)
    ]

    # Save summary effects in list
    spec = []
    for i, fit in enumerate(fits):
        mod = dict(zip(fit.names, list(fit)))
        b = mod["b"].item()
        # === USER EDIT HERE
        # === Edit this if-clause, depending on which models use a z effect size
        # Transform z to r
        if i <= 3:
            spec.append(np.tanh(b))
        else:
            spec.append(b)

    return spec


def fit_model_lvl_2(how_values, data, colmap):
    """Fit 2-level meta-analytic model according to how-factor values.

    Arguments:
        how_values -- The how-factor values.
        data -- The meta-analytic dataset.
        colmap -- The column-map from the configuration.

    Returns:
        Dictionary of relevant model result values
        (mean, lower and upper bound, p-value).
    """
    # === USER EDIT HERE
    # === Save configurated how-values in dedicated variables
    # Get how-factor values
    effect = how_values["effect"]
    method = how_values["ma_method"]

    # Get effect sizes from data
    if effect == "r":
        key_r = colmap["key_r"]
        key_r_se = colmap["key_r_se"]
        yi = data[key_r]
        sei = data[key_r_se]
    elif effect == "z":
        key_z = colmap["key_z"]
        key_z_se = colmap["key_z_se"]
        yi = data[key_z]
        sei = data[key_z_se]

    # === USER EDIT HERE
    # === Rewrite this part according to your needs
    # Fit meta-analytic model
    if method == "FE":
        fit = metafor.rma(yi=yi, sei=sei, method="FE")
    elif method == "RE_DL":
        fit = metafor.rma(yi=yi, sei=sei, method="DL")
    elif method == "REML":
        ctrl = ListVector(dict(stepadj=0.5, maxiter=2000))
        fit = metafor.rma(yi=yi, sei=sei, method="REML", control=ctrl)
    elif method == "unweighted":
        w = 1/len(data)
        fit = metafor.rma(yi=yi, sei=sei, method="FE", weights=w)

    # Save model results in dictionary
    mod = dict(zip(fit.names, list(fit)))
    res = {
        "mean": mod["b"].item(),
        "lb": mod["ci.lb"].item(),
        "ub": mod["ci.ub"].item(),
        "p": mod["pval"].item(),
    }

    # Transform z to r
    if effect == "z":
        res["mean"] = np.tanh(res["mean"])
        res["lb"] = np.tanh(res["lb"])
        res["ub"] = np.tanh(res["ub"])

    return res


def spec_list_lvl_3(e_ids, data, colmap):
    """Compute 3-level summary effects for each how-factor value combination.

    Arguments:
        e_ids -- The effect IDs to be included.
        data -- The meta-analytic dataset.
        colmap -- The column-map from the configuration.

    Returns:
        List of computed summary effects.
    """
    # === USER EDIT HERE
    # === Get the desired effect sizes from the data
    # Get relevant keys from colmap
    key_z = colmap["key_z"]
    key_z_var = colmap["key_z_var"]
    key_r = colmap["key_r"]
    key_r_var = colmap["key_r_var"]
    key_c_id = colmap["key_c_id"]
    key_e_id = colmap["key_e_id"]

    # Get data for included effects
    temp = data[data[key_e_id].isin(e_ids)]
    yi_z = temp[key_z]
    V_z = temp[key_z_var]
    yi_r = temp[key_r]
    V_r = temp[key_r_var]

    # Prepare 3-level dependency formula
    formula_string = f"~ 1 | {key_c_id}/{key_e_id}"
    formula = Formula(formula_string)

    # === USER EDIT HERE
    # === Rewrite list of meta-analytic models to compute as desired
    # Compute summary effects for each how-factor value combination
    fits = [
        metafor.rma(data=temp, yi=yi_z, sei=V_z,
                    method="REML", test="t", random=formula),
        metafor.rma(data=temp, yi=yi_z, sei=V_z,
                    method="ML", test="t", random=formula),
        metafor.rma(data=temp, yi=yi_z, sei=V_z,
                    method="REML", test="z", random=formula),
        metafor.rma(data=temp, yi=yi_z, sei=V_z,
                    method="ML", test="z", random=formula)
    ]
    # Save summary effects in list
    spec = []
    for i, fit in enumerate(fits):
        mod = dict(zip(fit.names, list(fit)))
        b = mod["b"].item()
        # === USER EDIT HERE
        # === Edit this if-clause, depending on which models use a z effect size
        # Transform z to r
        if i <= 3:
            spec.append(np.tanh(b))
        else:
            spec.append(b)

    return spec


def fit_model_lvl_3(how_values, data, colmap):
    """Fit 3-level meta-analytic model according to how-factor values.

    Arguments:
        how_values -- The how-factor values.
        data -- The meta-analytic dataset.
        colmap -- The column-map from the configuration.

    Returns:
        Dictionary of relevant model result values
        (mean, lower and upper bound, p-value).
    """
    # === USER EDIT HERE
    # === Save configurated how-values in dedicated variables
    # Get how-factor values
    effect = how_values["effect"]
    method = how_values["ma_method"]
    test_type = how_values["test"][0]

    # Get effect sizes from data
    if effect == "r":
        key_r = colmap["key_r"]
        key_r_var = colmap["key_r_var"]
        yi = data[key_r]
        V = data[key_r_var]
    elif effect == "z":
        key_z = colmap["key_z"]
        key_z_var = colmap["key_z_var"]
        yi = data[key_z]
        V = data[key_z_var]

    # Prepare 3-level dependency formula
    key_c_id = colmap["key_c_id"]
    key_e_id = colmap["key_e_id"]
    formula_string = f"~ 1 | {key_c_id}/{key_e_id}"
    formula = Formula(formula_string)

    # === USER EDIT HERE
    # === Rewrite this part according to your needs
    # Fit meta-analytic model
    if method == "REML":
        fit = metafor.rma_mv(yi=yi, V=V, method="REML",
                             test=test_type, random=formula, data=data)
    elif method == "ML":
        fit = metafor.rma_mv(yi=yi, V=V, method="ML",
                             test=test_type, random=formula, data=data)

    # Save results
    mod = dict(zip(fit.names, list(fit)))
    res = {
        "mean": mod["b"].item(),
        "lb": mod["ci.lb"].item(),
        "ub": mod["ci.ub"].item(),
        "p": mod["pval"].item(),
    }

    # Transform z to r
    if effect == "z":
        res["mean"] = np.tanh(res["mean"])
        res["lb"] = np.tanh(res["lb"])
        res["ub"] = np.tanh(res["ub"])

    return res
