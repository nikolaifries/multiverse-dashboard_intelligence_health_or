import json

def read_config(data=None, path=None):
    if data is not None:
        json_data = json.load(data)
    elif path is not None:
        with open(path, "r") as config_file:
            json_data = json.load(config_file)

    which_lists = {}
    how_lists = {}
    labels = []

    n_which = json_data["which"]["n"]
    n_how = json_data["how"]["n"]

    for i in range(n_which):
        key = json_data["which"]["keys"][i]
        key_label = json_data["which"]["keys_labels"][i]

        values = json_data["which"]["values"][i]
        values_labels = json_data["which"]["values_labels"][i]
        add_all_value = json_data["which"]["add_all_values"][i]

        if add_all_value:
            all_value = f"all_{key}"
            values.append(all_value)

        which_lists[key] = values

        all_label = json_data["which"]["all_label"]

        for value_label in values_labels:
            l = f"{key_label}: {value_label}"
            labels.append(l)
        
        if add_all_value:
            l = f"{key_label}: {all_label}"
            labels.append(l)

    for i in range(n_how):
        key = json_data["how"]["keys"][i]
        key_label = json_data["how"]["keys_labels"][i]

        values = json_data["how"]["values"][i]
        values_labels = json_data["how"]["values_labels"][i]

        how_lists[key] = values

        for value_label in values_labels:
            l = f"{key_label}: {value_label}"
            labels.append(l)

    config = {
        "n_which": n_which,
        "which_lists": which_lists,
        "n_how": n_how,
        "how_lists": how_lists,
        "labels": labels,
        "title": json_data["title"],
        "level": json_data["level"],
        "colmap": json_data["colmap"],
        "k_min": json_data["k_min"],
        "n_boot_iter": json_data["n_boot_iter"]
    }
    return config