import numpy as np
import os
import pandas as pd
import pyreadr

def _save_data(data, path, title):
    dir = os.path.abspath(os.path.dirname(path))
    data.to_csv(f"{dir}/data_{title}.csv", index=False)

# def preprocess_data(path, title):
#     res = pyreadr.read_r(path)
#     data = res["Chernobyl"]
#     data.drop(columns=["es.id"], inplace=True)
#     data["radiation"].fillna("low", inplace=True)
#     _save_data(data, path, title)
#     return data

def preprocess_data(path, title):
    data = pd.read_csv(path, sep=";", header=0, encoding="ISO-8859-1")
    for col in ["r", "r_se", "z", "z_se"]:
        data[col] = data[col].str.replace(',', '.').astype(float)
    _save_data(data, path, title)
    return data

# def preprocess_data(path, title):
#     data = pd.read_csv(path, sep=";", header=0, encoding="ISO-8859-1")
#     for col in ["r", "r_se", "z", "z_se"]:
#         data[col] = data[col].str.replace(',', '.').astype(float)
#     data["Study_name"] = data["Study_name"].apply(lambda x: x.split(", ")[0])
#     data["z_var"] = data["z_se"] ** 2
#     data["r_var"] = data["r_se"] ** 2
#     _save_data(data, path, title)
#     return data

# def preprocess_data(path, title):
#     data = pd.read_spss(path)
#     data = data[["StudyID", "correlation", "religiosityMeasure", "sample", "publicationstatus", "N", "variance_r"]]
#     data["sample"] = data["sample"].cat.add_categories("Mixed")
#     data["sample"].fillna("Mixed", inplace=True)
#     data["r_se"] = np.sqrt(data["variance_r"])
#     data["z"] = np.arctanh(data["correlation"])
#     data["z_se"] = data["r_se"] / (1 - data["correlation"]**2)
#     _save_data(data, path, title)
#     return data