import json


def read_config(data=None, path=None):
    """Read and process configuration file.

    Keyword Arguments:
        data -- The raw configuration data, needed in Plotly Dashboard
                (default: {None}).
        path -- The path to the configuration file (default: {None}).

    Returns:
        Configuration dictionary containing the needed data.
    """
    # If raw data is provided, directly load it into JSON
    # Otherwise, load JSON from file
    if data is not None:
        json_data = json.load(data)
    elif path is not None:
        with open(path, "r") as config_file:
            json_data = json.load(config_file)

    # Prepare empty dictionaries for which- and how-factors, and
    # empty list for labels
    which_lists = {}
    how_lists = {}
    labels = []

    # Get amount of which- and how- factors
    n_which = json_data["which"]["n"]
    n_how = json_data["how"]["n"]

    # Process which-factors
    # Get all-label value
    all_label = json_data["which"]["all_label"]
    for i in range(n_which):
        # Get key and key label
        key = json_data["which"]["keys"][i]
        key_label = json_data["which"]["keys_labels"][i]

        # Get values, value labels and information about all-values
        values = json_data["which"]["values"][i]
        values_labels = json_data["which"]["values_labels"][i]
        add_all_value = json_data["which"]["add_all_values"][i]

        # Append all-value (e.g. all_sex, all_race), if desired
        # for this factor
        if add_all_value:
            all_value = f"all_{key}"
            values.append(all_value)

        # Add to list of which-factors
        which_lists[key] = values

        # Append labels
        for value_label in values_labels:
            l = f"{key_label}: {value_label}"
            labels.append(l)

        # Add all-label (e.g. "sex: either"), if desired
        # for this factor
        if add_all_value:
            l = f"{key_label}: {all_label}"
            labels.append(l)

    # Process which-factors
    for i in range(n_how):
        # Get key and key label
        key = json_data["how"]["keys"][i]
        key_label = json_data["how"]["keys_labels"][i]

        # Get values and value labels
        values = json_data["how"]["values"][i]
        values_labels = json_data["how"]["values_labels"][i]

        # Add to list of how-factors
        how_lists[key] = values

        # Append labels
        for value_label in values_labels:
            l = f"{key_label}: {value_label}"
            labels.append(l)

    # Return configuration dictionary containing the needed data
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
