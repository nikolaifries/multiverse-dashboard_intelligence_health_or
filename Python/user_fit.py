import numpy as np
import os
from rpy2.robjects.packages import importr
from rpy2.robjects import ListVector, Formula, pandas2ri
pandas2ri.activate()

os.environ['R_HOME'] = "C:\\Program Files\\R\\R-4.3.1"
metafor = importr('metafor')

def spec_list_lvl_2(e_ids, data, colmap):
    key_z = colmap["key_z"]
    key_z_se = colmap["key_z_se"]
    key_r = colmap["key_r"]
    key_r_se = colmap["key_r_se"]

    key_e_id = colmap["key_e_id"]

    temp = data[data[key_e_id].isin(e_ids)]
    control = dict(stepadj=0.5, maxiter=2000)
    z = temp[key_z]
    z_se = temp[key_z_se]
    r = temp[key_r]
    r_se = temp[key_r_se]
    fits = [
        metafor.rma(yi=z, sei=z_se, method="FE"),
        metafor.rma(yi=z, sei=z_se, method="DL"),
        metafor.rma(yi=z, sei=z_se, method="REML", control=ListVector(control)),
        metafor.rma(yi=z, sei=z_se, method="FE", weights=1/len(temp)),
        metafor.rma(yi=r, sei=r_se, method="FE"),
        metafor.rma(yi=r, sei=r_se, method="DL"),
        metafor.rma(yi=r, sei=r_se, method="REML", control=ListVector(control)),
        metafor.rma(yi=r, sei=r_se, method="FE", weights=1/len(temp))
    ]
    spec = []
    for i, fit in enumerate(fits):
        mod = dict(zip(fit.names, list(fit)))
        b = mod["b"].item()
        if i <= 3:
            spec.append(np.tanh(b))
        else:
            spec.append(b)
    return spec

def fit_model_lvl_2(effect, method, data, colmap):
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

    if method == "FE":
        fit = metafor.rma(yi=yi, sei=sei, method="FE")
    elif method == "RE_DL":
        fit = metafor.rma(yi=yi, sei=sei, method="DL")
    elif method == "REML":
        control = dict(stepadj=0.5, maxiter=2000)
        fit = metafor.rma(yi=yi, sei=sei, method="REML",
                          control=ListVector(control))
    elif method == "unweighted":
        fit = metafor.rma(yi=yi, sei=sei, method="FE", weights=1/len(data))

    mod = dict(zip(fit.names, list(fit)))
    res = {
        "mean": mod["b"].item(),
        "lb": mod["ci.lb"].item(),
        "ub": mod["ci.ub"].item(),
        "p": mod["pval"].item(),
    }

    if effect == "z":
        res["mean"] = np.tanh(res["mean"])
        res["lb"] = np.tanh(res["lb"])
        res["ub"] = np.tanh(res["ub"])

    return res

def spec_list_lvl_3(e_ids, data, colmap):
    key_z = colmap["key_z"]
    key_z_var = colmap["key_z_var"]
    key_r = colmap["key_r"]
    key_r_var = colmap["key_r_var"]

    key_c_id = colmap["key_c_id"]
    key_e_id = colmap["key_e_id"]
    formula_string = f"~ 1 | {key_c_id}/{key_e_id}"
    random = Formula(formula_string)

    temp = data[data[key_e_id].isin(e_ids)]
    yi_z = temp[key_z]
    V_z = temp[key_z_var]
    yi_r = temp[key_r]
    V_r = temp[key_r_var]
    fits = [
        metafor.rma(data = temp, yi=yi_z, sei=V_z, method="REML", test="t", random=random),
        metafor.rma(data = temp, yi=yi_z, sei=V_z, method="ML", test="t", random=random),
        metafor.rma(data = temp, yi=yi_z, sei=V_z, method="REML", test="z", random=random),
        metafor.rma(data = temp, yi=yi_z, sei=V_z, method="ML", test="z", random=random)
    ]
    spec = []
    for i, fit in enumerate(fits):
        mod = dict(zip(fit.names, list(fit)))
        b = mod["b"].item()
        if i <= 3:
            spec.append(np.tanh(b))
        else:
            spec.append(b)
    return spec


def fit_model_lvl_3(effect, method, test, data, colmap):
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

    key_c_id = colmap["key_c_id"]
    key_e_id = colmap["key_e_id"]
    formula_string = f"~ 1 | {key_c_id}/{key_e_id}"
    random = Formula(formula_string)

    test_type = test[0]

    if method == "REML":
        fit = metafor.rma_mv(yi=yi, V=V, method="REML", test=test_type, random=random, data=data)
    elif method == "ML":
        fit = metafor.rma_mv(yi=yi, V=V, method="ML", test=test_type, random=random, data=data)

    mod = dict(zip(fit.names, list(fit)))
    res = {
        "mean": mod["b"].item(),
        "lb": mod["ci.lb"].item(),
        "ub": mod["ci.ub"].item(),
        "p": mod["pval"].item(),
    }

    if effect == "z":
        res["mean"] = np.tanh(res["mean"])
        res["lb"] = np.tanh(res["lb"])
        res["ub"] = np.tanh(res["ub"])

    return res
