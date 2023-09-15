from itertools import product
import numpy as np
import pandas as pd
from tqdm import tqdm

from user_fit import fit_model_lvl_2, fit_model_lvl_3


def generate_specs(data, which_lists, how_lists, colmap, k_min, level,
                   save_path):
    """Generate specifications.

    Arguments:
        data -- The meta-analytic dataset.
        which_lists -- The which-factors.
        how_lists -- The how-factors.
        colmap -- The column-map from the configuration.
        k_min -- The minimum number of effects to include a specification.
        level -- The meta-analysis level (2 or 3).
        save_path -- The path to where the specification data should be
                     stored.

    Returns:
        The specification data as a pandas DataFrame.
    """
    # Generate all combinations of which/how factors and get their
    # total number (the amount of specifications)
    group_factors = dict(which_lists, **how_lists)
    cart_prod = product(*[values for values in group_factors.values()])
    specs = pd.DataFrame(cart_prod, columns=list(group_factors.keys()))
    n_specs = len(specs)

    # Add to-be-filled columns with None values
    tbf_keys = ["mean", "lb", "ub", "p", "k", "set"]
    for key in tbf_keys:
        specs[key] = [None] * n_specs

    # Get relevant keys from colmap
    key_c_id = colmap["key_c_id"]
    key_e_id = colmap["key_e_id"]

    # Iterate over all specifications and filter the data according to
    # the which-factors, then perform meta-analytic computations according to
    # how-factors.
    for i in tqdm(range(n_specs)):
        # Copy data into temporary variable
        temp_data = data

        # Select specification
        spec = specs.iloc[i]

        # Iterate over all which-factors and filter data that fits
        for key in which_lists.keys():
            # Get specification value for which-factor
            spec_val = spec[key]

            # Do not filter data if value is an all-value
            if spec_val.startswith("all_"):
                continue

            # Filter
            temp_data = temp_data[temp_data[key] == spec_val]

        # Disregard data subsets with less than k_min studies
        if len(temp_data) < k_min:
            continue

        # Get sets of cluster- and effect IDs that fulfill the specification
        c_ids = sorted(temp_data[key_c_id].unique())
        e_ids = sorted(temp_data[key_e_id])
        # Store IDs as comma-joined lists in specification data
        study_set = (",").join([str(c_id) for c_id in c_ids])
        es_set = (",").join([str(e_id) for e_id in e_ids])
        specs.at[i, "set"] = study_set
        specs.at[i, "set_es"] = es_set
        # Store the amount of clusters (kc) and effect sizes (k) that
        # contribute to the specification
        specs.at[i, "k"] = len(temp_data)
        specs.at[i, "kc"] = len(c_ids)

        # Fit meta-analytic model with filtered data according to how-factors
        how_values = {k: spec[k] for k in how_lists.keys()}
        if level == 2:
            res = fit_model_lvl_2(
                how_values,
                temp_data,
                colmap
            )
        elif level == 3:
            res = fit_model_lvl_3(
                how_values,
                temp_data,
                colmap
            )

        # Save model results in specifications data frame
        specs.at[i, res.keys()] = res.values()

    # Remove all specifications which were not used
    specs_full = specs.dropna(axis=0, how="any")

    # Only keep unique study/sample subsets # TODO
    specs_full = specs_full.drop_duplicates(
        subset=["mean", "set", *how_lists.keys()]
    )

    # Add binary indicator if all studies are included in the subset
    c_ids = sorted(data[key_c_id].unique())
    all_studies_list = (",").join([str(c_id) for c_id in c_ids])
    full_set = (specs_full["set"] == all_studies_list)
    specs_full["full_set"] = full_set.astype("int64")

    specs_full.reset_index(drop=True, inplace=True)

    # Rank specifications according to mean in ascending order
    specs_full["rank"] = np.argsort(np.argsort(specs_full["mean"])) + 1
    # Store CI interval width in dedicated column
    specs_full["ci"] = specs_full["ub"] - specs_full["lb"]

    # !important Sort specifications by rank
    specs_full.sort_values(by="rank", inplace=True)

    # Ensure correct datatypes in pandas DataFrame
    for key in ["mean", "lb", "ub", "ci", "p"]:
        specs_full[key] = specs_full[key].astype("float64")
    for key in ["k", "kc"]:
        specs_full[key] = specs_full[key].astype("int64")

    # Save specs to CSV file
    specs_full.to_csv(save_path, index=False)

    return specs_full
