import numpy as np
import pandas as pd

from bootstrap import generate_boot_data
from config import read_config
from data import prepare_data
from plotting import (get_cluster_fill_data, get_spec_fill_data,
                      get_colors, plot_treemap, plot_multiverse,
                      plot_caterpillar, plot_sample_size, plot_cluster_size,
                      plot_spec_tiles, plot_cluster_tiles, plot_inferential,
                      plot_p_hist)
from specs import generate_specs
from user_data import preprocess_data

# === USER EDIT HERE ===
# Set paths to dataset, working directory, choose what data to generate

TITLE = "R2D4D_3"
DIR = "../examples/R2D4D"
DATA_PATH = f"{DIR}/R2D4D.csv"

# TITLE = "Chernobyl_3"
# DIR = "../examples/Chernobyl"
# DATA_PATH = f"{DIR}/Chernobyl.rda"

# TITLE = "IandR_2"
# DIR = "../examples/IandR"
# DATA_PATH = f"{DIR}/iandr.sav"

PREPROCESS_DATA = True  # Load of preprocess data
GENERATE_SPECS = True  # Load or generate specs
GENERATE_BOOTDATA = True  # Load or generate boot data

PP_DATA_PATH = f"{DIR}/data_{TITLE}.csv"
CONFIG_PATH = f"{DIR}/config_{TITLE}.json"
SPECS_PATH = f"{DIR}/specs_{TITLE}.csv"
BOOT_PATH = f"{DIR}/boot_{TITLE}.csv"

config = read_config(path=CONFIG_PATH)
if config is not None:
    c_info = [
        f"{config['level']} - Level Meta-Analysis",
        f"   Minimum Nr. of Samples to include Specification: {config['k_min']}",
        f"   Bootstrap Iterations: {config['n_boot_iter']}",
        f"   {config['n_which']} Which-Factors:",
        *[f"     {k} : {(', ').join(v)}" for k,
          v in config['which_lists'].items()],
        f"   {config['n_how']} How-Factors:",
        *[f"     {k} : {(', ').join(v)}" for k,
          v in config['how_lists'].items()],
        f"   Labels",
        *[f"     {l}" for l in config['labels']],
        f"   Column-Map",
        *[f"     {k} : {v}" for k, v in config['colmap'].items()]
    ]
    print(("\n").join(c_info))

if PREPROCESS_DATA:
    ma_data = preprocess_data(DATA_PATH, title=TITLE)
else:
    ma_data = pd.read_csv(PP_DATA_PATH)
print(f"Data Shape: {ma_data.shape}")
ma_data.head()

data = prepare_data(config["colmap"], data=ma_data)
print(f"Data Shape: {data.shape}")
data.head()

if GENERATE_SPECS:
    specs = generate_specs(
        data,
        config["which_lists"],
        config["how_lists"],
        config["colmap"],
        config["k_min"],
        config["level"],
        SPECS_PATH
    )
else:
    specs = pd.read_csv(SPECS_PATH)
print(specs.shape)
specs.head()

if GENERATE_BOOTDATA:
    boot_data = generate_boot_data(
        specs,
        config["n_boot_iter"],
        data,
        config["colmap"],
        config["level"],
        BOOT_PATH
    )
else:
    boot_data = pd.read_csv(BOOT_PATH)
print(boot_data.shape)
boot_data.head()

cluster_fill_data = get_cluster_fill_data(
    data,
    specs,
    config["colmap"]
)
spec_fill_data = get_spec_fill_data(
    config["n_which"],
    config["which_lists"],
    config["n_how"],
    config["how_lists"],
    specs
)
fill_levels = len(np.unique([v for v in spec_fill_data.values()]))
colors = get_colors(fill_levels)

colmap = config["colmap"]
k_range = [config["k_min"], max(specs["k"])]
labels = config["labels"]
level = config["level"]
n_total_specs = len(specs)
title = config["title"]

# === USER EDIT HERE ===
# Choose which figures to plot / save

treemap = plot_treemap(data, title, colmap)

fig_inferential = plot_inferential(boot_data, title, n_total_specs)

fig_p_hist = plot_p_hist(specs, title, n_total_specs)

fig = plot_multiverse(
    specs,
    n_total_specs,
    k_range,
    cluster_fill_data,
    spec_fill_data,
    labels,
    colors,
    config["level"],
    title,
    fill_levels
)

fig_cluster_tiles = plot_cluster_tiles(
    specs, cluster_fill_data, n_total_specs, title)

fig_caterpillar = plot_caterpillar(
    specs, n_total_specs, colors, k_range, title, fill_levels)

fig_cluster_size = plot_cluster_size(specs, k_range, n_total_specs, title)

fig_sample_size = plot_sample_size(specs, k_range, n_total_specs, title)

fig_spec_tiles = plot_spec_tiles(
    specs, n_total_specs, spec_fill_data, labels, colors, k_range, title, fill_levels)

# fig.write_image("multiverse.pdf", width=1000, height=1500)
