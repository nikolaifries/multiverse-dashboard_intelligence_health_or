import numpy as np
import pandas as pd
from rpy2.robjects.packages import importr
from rpy2.robjects import ListVector
from tqdm import tqdm

def generate_boot_data(specs, n_iter, data):
    specs_means = sorted(specs["mean"])
    study_sets = np.unique(specs["set"])
    study_sets = [[int(x) for x in ss.split(",")] for ss in study_sets]
    n_specs = len(specs)
    res = np.zeros((n_specs, n_iter))

    for col in tqdm(range(n_iter)):
        z_se = 1 / np.sqrt(data["N"])
        data["z"] = np.random.normal(0, z_se, len(data))
        data["z_se"] = z_se
        data["r"] = np.tanh(data["z"])
        data["r_se"] = (1 - data["r"]**2) * z_se

        boot_effects = []
        for ss in study_sets:
            ss = np.array(ss) - 1
            boot_effects.append(spec_list(ss, data))

        res[:, col] = sorted(np.array(boot_effects).flatten())
    
    boot_bounds = np.quantile(res, [0.025, 0.975], axis=1)
    boot_lb = boot_bounds[0]
    boot_ub = boot_bounds[1]

    boot_data_dict = {
        "x_var": [i+1 for i in range(n_specs)],
        "obs": specs_means,
        "boot_lb": boot_lb,
        "boot_ub": boot_ub
    }
    boot_data = pd.DataFrame(boot_data_dict)
    boot_data.head()

def spec_list(study_ids, data):
    metafor = importr('metafor')

    temp = data.iloc[study_ids]
    control = dict(stepadj=0.5, maxiter=2000)
    r = temp["r"]
    r_se = temp["r_se"]
    z = temp["z"]
    z_se = temp["z_se"]
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