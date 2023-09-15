from itertools import product
import numpy as np
import pandas as pd
from tqdm import tqdm

from user_fit import fit_model_lvl_2, fit_model_lvl_3

def generate_specs(data, which_lists, how_lists, colmap, k_min, level, save_path):
    group_factors = dict(which_lists, **how_lists)
    cart_prod = product(*[values for values in group_factors.values()])
    specs = pd.DataFrame(cart_prod, columns=list(group_factors.keys()))
    n_specs = len(specs)

    tbf_keys = ["mean", "lb", "ub", "p", "k", "set"]
    for key in tbf_keys:
        specs[key] = [None] * n_specs

    key_c_id = colmap["key_c_id"]
    key_e_id = colmap["key_e_id"]

    for i in tqdm(range(n_specs)):
        temp_data = data
        spec = specs.iloc[i]

        for key in which_lists.keys():
            spec_val = spec[key]
            if spec_val.startswith("all_"):
                continue
            temp_data = temp_data[temp_data[key] == spec_val]

        if temp_data.shape[0] < k_min:
            continue

        c_ids = sorted(temp_data[key_c_id].unique())
        e_ids = sorted(temp_data[key_e_id])
        study_set = (",").join([str(c_id) for c_id in c_ids])
        es_set = (",").join([str(e_id) for e_id in e_ids])
        specs.at[i, "set"] = study_set
        specs.at[i, "set_es"] = es_set
        specs.at[i, "k"] = len(temp_data)
        specs.at[i, "kc"] = len(c_ids)

        effect = spec["effect"]
        method = spec["ma_method"]
        if level == 2:
            res = fit_model_lvl_2(
                effect,
                method,
                temp_data,
                colmap
            )
        elif level == 3:
            test = spec["test"]
            res = fit_model_lvl_3(
                effect,
                method,
                test,
                temp_data,
                colmap
            )
        specs.at[i, res.keys()] = res.values()

    specs_full = specs.dropna(axis=0, how="any")
    specs_full = specs_full.drop_duplicates(subset=["mean", "set", *how_lists.keys()])

    c_ids = sorted(data[key_c_id].unique())
    all_studies_list = (",").join([str(c_id) for c_id in c_ids])
    full_set = (specs_full["set"] == all_studies_list)

    specs_full["full_set"] = full_set.astype("int64")
    specs_full.reset_index(drop=True, inplace=True)

    specs_full["rank"] = np.argsort(np.argsort(specs_full["mean"])) + 1
    specs_full["ci"] = specs_full["ub"] - specs_full["lb"]

    specs_full.sort_values(by="rank", inplace=True)

    for key in ["mean", "lb", "ub", "ci", "p"]:
        specs_full[key] = specs_full[key].astype("float64")
    for key in ["k", "kc"]:
        specs_full[key] = specs_full[key].astype("int64")

    specs_full.to_csv(save_path, index=False)

    return specs_full