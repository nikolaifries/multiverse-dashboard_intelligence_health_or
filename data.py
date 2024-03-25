import pandas as pd


def prepare_data(colmap, raw=None, data=None):
    """Prepare the meta-analytic dataset for multiverse
       analysis.

    Arguments:
        colmap -- The column-map from the configuration.

    Keyword Arguments:
        raw -- The raw meta-analytic data, needed in Plotly 
               Dashboard (default: {None}).
        data -- The meta-analytic data as a pandas DataFrame
                (default: {None}).

    Returns:
        Prepared data as a pandas DataFrame.
    """
    # Read raw input into pandas DataFrame, if data
    # is not provided as such
    if data is None:
        data = pd.read_csv(raw, sep=",", header=0, escapechar='\\', na_values=['NA'], keep_default_na=False)

    # Get relevant keys from colmap
    key_c = colmap["key_c"]
    key_c_id = colmap["key_c_id"]
    key_e_id = colmap["key_e_id"]

    # If a cluster ID does not exist, create it
    if key_c_id not in data:
        # Get set of clusters by name
        clusters = data[key_c].unique()

        # Create ID map, mapping an ID to each cluster
        cluster_ids = {}
        c_id = 1
        for c in clusters:
            cluster_ids[c] = c_id
            c_id += 1

        # Add cluster ID column into DataFrame
        data[key_c_id] = data[key_c].map(cluster_ids)

    # Sort meta-analytic data by cluster ID
    data.sort_values(by=key_c_id, inplace=True)

    # If an effect ID does not exist, create it
    if key_e_id not in data:
        data[key_e_id] = [e_id for e_id in range(1, len(data) + 1)]

    # Reorder columns such that cluster ID, cluster name
    # and effect ID are the first three columns
    cols = data.columns.tolist()
    for c in [key_e_id, key_c, key_c_id]:
        cols.insert(0, cols.pop(cols.index(c)))

    # Reindex DataFrame and set type of sample size to integer
    data = data.reindex(columns=cols)
    data = data.astype({colmap["key_n"]: "int64"})

    return data
