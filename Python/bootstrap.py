import numpy as np
import pandas as pd
from tqdm import tqdm
from user_fit import spec_list_lvl_2, spec_list_lvl_3

def generate_boot_data(specs, n_iter, data, colmap, level, save_path):
    effect_sets = np.unique(specs["set_es"])
    effect_sets = [[int(x) for x in es.split(",")] for es in effect_sets]
    n_specs = len(specs)
    res = np.zeros((n_specs, n_iter))

    key_z = colmap["key_z"]
    key_z_se = colmap["key_z_se"]
    key_r = colmap["key_r"]
    key_r_se = colmap["key_r_se"]
    key_n = colmap["key_n"]

    for col in tqdm(range(n_iter)):
        z_se = 1 / np.sqrt(data[key_n])
        data[key_z] = np.random.normal(0, z_se, len(data))
        data[key_z_se] = z_se
        data[key_r] = np.tanh(data[key_z])
        data[key_r_se] = (1 - data[key_r]**2) * z_se

        boot_effects = []
        if level == 2:
            for es in effect_sets:
                boot_effects.append(spec_list_lvl_2(es, data, colmap))
        elif level == 3:
            for es in effect_sets:
                boot_effects.append(spec_list_lvl_3(es, data, colmap))

        res[:, col] = sorted(np.array(boot_effects).flatten())
    
    boot_bounds = np.quantile(res, [0.025, 0.975], axis=1)
    boot_lb = boot_bounds[0]
    boot_ub = boot_bounds[1]

    boot_data_dict = {
        "rank": [i+1 for i in range(n_specs)],
        "obs": specs["mean"],
        "boot_lb": boot_lb,
        "boot_ub": boot_ub
    }
    boot_data = pd.DataFrame(boot_data_dict)
    boot_data.to_csv(save_path, index=False)
    return boot_data