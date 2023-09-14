import pandas as pd
   
def prepare_data(colmap, raw=None, data=None):
    if data is None:
        data = pd.read_csv(raw, sep=",", header=0)

    key_c = colmap["key_c"]
    key_c_id = colmap["key_c_id"]
    key_e_id = colmap["key_e_id"]

    if key_c_id not in data:
        clusters = data[key_c].unique()
        cluster_ids = {}
        c_id = 1
        for c in clusters:
            cluster_ids[c] = c_id
            c_id += 1
        data[key_c_id] = data[key_c].map(cluster_ids)

    data.sort_values(by=key_c_id, inplace=True)
    
    if key_e_id not in data:
        data[key_e_id] = [e_id for e_id in range(1, len(data) + 1)]
    
    cols = data.columns.tolist()
    for c in [key_e_id, key_c, key_c_id]:
        cols.insert(0, cols.pop(cols.index(c)))
    
    data = data.reindex(columns=cols)

    data = data.astype({colmap["key_n"]: "int64"})

    return data