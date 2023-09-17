import numpy as np
import os
import pandas as pd
import pyreadr
import re


def _save_data(data, path, title):
    """Save the preprocessed data.

    Arguments:
        data -- The preprocessed data as a pandas DataFrame.
        path -- The path where the unprocessed data was stored (working dir).
        title -- The title of the dataset.
    """
    dir = os.path.abspath(os.path.dirname(path))
    # Naming convention can be changed, but prefix `data_`
    # should stay for Dashboard
    data.to_csv(f"{dir}/data_{title}.csv", index=False)


# === USER EDIT HERE ===
# === Add your preprocessing code here. The saveData_() call should
# === not be removed. Other functions expect a data frame. For reference,
# === examine the examples below.


def preprocess_dataEDIT(path, title):
    """Preprocess and save the meta-analytic dataset.

    Arguments:
        path -- The path to the dataset.
        title -- The title of the dataset (for saving).

    Returns:
        The preprocessed dataset as a pandas DataFrame.
    """
    # === USER EDIT HERE ===
    # === Preprocess the dataset
    data = None
    _save_data(data, path, title)
    return data


# def preprocess_data(path, title):
#     """Preprocessing for Chernobyl example (level 3)."""
#     res = pyreadr.read_r(path)
#     data = res["Chernobyl"]
#     data.drop(columns=["es.id"], inplace=True)
#     data["radiation"].fillna("low", inplace=True)
#     _save_data(data, path, title)
#     return data


# def preprocess_data(path, title):
#     """Preprocessing for Intelligence & Religion example (level 2)."""
#     data = pd.read_spss(path)
#     data = data[["StudyID", "correlation", "religiosityMeasure",
#                  "sample", "publicationstatus", "N", "variance_r"]]
#     data["sample"] = data["sample"].cat.add_categories("Mixed")
#     data["sample"].fillna("Mixed", inplace=True)
#     data["r_se"] = np.sqrt(data["variance_r"])
#     data["z"] = np.arctanh(data["correlation"])
#     data["z_se"] = data["r_se"] / (1 - data["correlation"]**2)
#     _save_data(data, path, title)
#     return data


def preprocess_data(path, title):
    """Preprocessing for Intelligence & Religion example (level 3)."""
    data = pd.read_spss(path)
    data = data[["StudyID", "correlation", "religiosityMeasure",
                "sample", "publicationstatus", "N", "variance_r"]]
    data["StudyID"] = data["StudyID"].apply(
        lambda x: re.sub(r'^\(\d+\)\s*', '', x))
    data["sample"] = data["sample"].cat.add_categories("Mixed")
    data["sample"].fillna("Mixed", inplace=True)
    data["r_se"] = np.sqrt(data["variance_r"])
    data["z"] = np.arctanh(data["correlation"])
    data["z_se"] = data["r_se"] / (1 - data["correlation"]**2)
    data["z_var"] = data["z_se"]**2
    _save_data(data, path, title)
    return data


# def preprocess_data(path, title):
#     """Preprocessing for R2D:4D example (level 2)."""
#     data = pd.read_csv(path, sep=";", header=0, encoding="ISO-8859-1")
#     for col in ["r", "r_se", "z", "z_se"]:
#         data[col] = data[col].str.replace(',', '.').astype(float)
#     _save_data(data, path, title)
#     return data


# def preprocess_data(path, title):
#     """Preprocessing for R2D:4D example (level 3)."""
#     data = pd.read_csv(path, sep=";", header=0, encoding="ISO-8859-1")
#     for col in ["r", "r_se", "z", "z_se"]:
#         data[col] = data[col].str.replace(',', '.').astype(float)
#     data["Study_name"] = data["Study_name"].apply(lambda x: x.split(", ")[0])
#     data["z_var"] = data["z_se"] ** 2
#     data["r_var"] = data["r_se"] ** 2
#     _save_data(data, path, title)
#     return data
