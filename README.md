# Multiverse Tools

This repository provides code to conduct specification curve and multiverse meta-analysis (see [Voracek et al. (2019)](https://doi.org/10.1027/2151-2604/a000357)) on a meta-analytic dataset. It is an adaptation of the existing code by [Voracek et al. (2019)](https://doi.org/10.1027/2151-2604/a000357), which was hard-coded towards a specific use-case/dataset. It could also handle only 2-level meta-analyses. In contrast, our code can be easily reused for other meta-analyses, requiring only minimal adaptations by the user.

The code is available in both `Python` and `R`. The visualizations are coded in `Plotly` and `ggplot2` respectively. The computation of meta-analytic summary effects is done with the help of the R-package `metafor`, which is utilized in the `Python` code via the `Python`-`R` bridge `rpy2`.

In addition, the `Python` code offers an interactive Dashboard, created with `Plotly Dash`. It pertains only to the visualization part of the multiverse analysis process, meaning it has to fed with existing data (see Section [Dashboard](#dashboard)). This allows the user to the computational part of the analysis in `R` and the visualization part in `Python`, which is the approach we recommend. However, the individual steps of the analysis are interoperable, meaning it is up to the user, which code is used for which parts.

## Navigation

The code is separated by language into the respective directories [`Python/`](Python/) and [`R/`](R/). Files with the same name contain equivalent methods with equivalent functionality (e.g. `Python/bootstrap.py` and `R/bootstrap.R`). Both directories contain a notebook (*Jupyter Notebook* [`Multiverse.ipynb`](Python/Multiverse.ipynb) and *R-Markdown Notebook* [`Multiverse.Rmd`](R/Multiverse.Rmd)) for interactive code execution. The notebooks guide you through the multiverse analysis steps. Alternatively, the user can use the scripts TODO. The `Plotly Dashboard` can be launched by executing the [`dashboard.py`](Python/dashboard.py) file, or from the notebook.

## Tutorial

In order to conduct a multiverse analysis, the user must do two things:
1) adapt the code accordingly, and
2) provide a configuration file.

### Code

Code that must/can be customized by the user is limited to files with the prefix `user_` in the name, that is [`user_data.py`](Python/user_data.py) and [`user_fit.py`](Python/user_fit.py), and the corresponding files in `R`.

Each part of the code that must/can be adapted is marked with a comment `# === USER EDIT HERE ===`, followed by explanatory comments prefixed with `# === `.

- **`user_data`**: In this file, the user must implement the `preprocess_data(path, title)` method. A skeleton is provided, with the suffix `EDIT` in the method name. In addition, the file contains several implementations of the method that pertain to the supplied examples (see [Examples](#examples)). The method will be used to preprocess the meta-analytic dataset. For more information, see the documentation inside the file.

- **`user_fit`**: In this file, the user must adapt the `spec_list(e_ids, data, colmap)` and `fit_model(how_values, data, colmap)` methods. The methods are fully implemented as an example (see [Examples](#examples)). The parts of the code that can be adapted are marked accordingly. For each method, two version are implemented, one for 2-level (suffix `_lvl_2`) and one for 3-level (suffix `_lvl_3`) analyses. Ensure that you adapt the desired method.

### Configuration File

The user must provide a JSON configuration file that tailors the multiverse analysis. We provide a skeleton configuration in [`config_skeleton.json`](config_skeleton.json), as well as full configuration files for each example (see [Examples](#examples)). Each field in the JSON file is required.

We will use the file [`config_R2D4D.json`](examples/R2D4D/config_R2D4D_2.json) from the *R2D4D* example, to explain each field.


First, some important configuration values:
```
{
    "title": "R2D:4D",      // The title of the meta-analytic data, it will be used
                               in the visualizations
    "level": 2,             // The meta-analysis level (2 or 3)
    "k_min": 2,             // The minimum number of effect size samples needed
                               to include a specification
    "n_boot_iter": 100,     // The number of bootstrap sampling iterations to run.
    
    ...
```

Next, the column map. It maps specific column names from the meta-analytic dataset to data-agnostic values. It also specifies the column name, under which cluster (study) and effect (individual effect sizes) IDs are stored in the data. These IDs should be numeric. If they don't exist, they will be created under the specified name.

```
    ...
    "colmap": {
        "key_c": "Study_name",      // The column that identifies a cluster (study)
        "key_c_id": "c_id",         // The desired column name for cluster IDs. If
                                       column does not exist, IDs will be created.
        "key_e_id": "e_id",         // The desired column name for effect IDs. If
                                       column does not exist, IDs will be created.
        "key_z": "z",               // The column with the *z* effect size.
        "key_z_se": "z_se",         // The column with the *z* std. error.
        "key_r": "r",               // The column with the *r* effect size.
        "key_r_se": "r_se",         // The column with the *r* std. error.
        "key_main_es": "z",         // The column with the main effect size.
        "key_main_es_se": "z_se",   // The column with the main effect std. error.
        "key_n": "N"                // The column with the sample size.
    },
    ...
```

Finally, we define the **Which**- and **How**- factors. Each factor has a *key*, and *values*, as well as a *key label* and *value labels*. The *key* identifies the column in the meta-analytic dataset, and *values* is a list of possible values within this column. The corresponding labels specify, how the factor and its value will be called in the plot. In addition, **Which**-Factors can have an *all-value* or not, which must be specified via a boolean flag. The *all-label* dictates, how *all-values* will be called in the plot. 

In addition, the user must specify the number of **Which**- and **How**- factors. This is redundant, but helps identify problems with the configuration file. We assume the amount is entered correctly, and can check if the corresponding amount of keys, values, labels, etc. is present.

```
"which": {
    "n": 6,                         // The number of which-factors
    "keys": ["sex", "method", "age_group", "sample", "race", "published_estimate"],
                                    // The which-factor keys, identifying the
                                       columns in the dataset
    "keys_labels": ["sex", "measure", "age", "group", "ethnicity", "report"],
                                    // The labels for each key
    "add_all_values": [true, true, true, true, true, true],
                                    // The boolean flag for each factor, specifying
                                       whether it has an all-value or not
    "values": [                     // The values for each which-factor, as used in
                                       the dataset
        ["men", "women"],           // The possible values for the factor "sex"
        ["direct", "image"],        // The possible values for the factor "method"
        ["adults", "non-adults"],
        ["healthy", "clinical"],
        ["white", "other"],
        ["yes", "no"]
    ],
    "values_labels": [              // The labels for each value of each factor
        ["male", "female"],         // The labels for the values "men" and "women"
                                       of the factor "sex"
        ["direct", "image"],
        ["adults", "non-adults"],
        ["healthy", "patients"],
        ["White", "non-White"],
        ["full", "not"]
    ],
    "all_label": "either"           // The label for all-values
},
"how": {                            // The definition of how-factors, analogous
                                       to the which-factors
    "n": 2,
    "keys": ["effect", "ma_method"],
    "keys_labels": ["metric", "model"],
    "values": [
        ["r", "z"],
        ["FE", "RE_DL", "REML", "unweighted"]
    ],
    "values_labels": [
        ["r", "z"],
        ["FEM", "REM", "REML", "UWM"]
    ]
}
```
To make things clearer, an example: according to the config file, we have a column `"sex"` in our dataset, that contains categorical values, either `"men"` or `"women"`. Because the corresponding boolean flag for that factor (the first in the list) is set to `true`, we will differentiate between specifications for the value `"men"`, the value `"women"` and also for either one of those values. As specified by the labels, the factor will be displayed as `sex: male`, `sex: female` and `sex: either` in our plots.

Note that, even if you do not want to change the labels, the fields must be filled out in the config file. In the case of no desired changes, just copy the key and the values as-is into the label fields. This is the case for the values of the factor `method`. The key's label is changed to `measure`, but the values and their labels are the same. 

## Examples

In the directory [`examples/`](examples/), we provide three examples. Each directory contains a *meta-analytic dataset*, along with *configuration files*, the *preprocessed data*, the *specification data* and the *bootstrap data* for both 2- and 3-level analyses (filenames are suffixed by either `_2` or `_3` according to the analysis level). These files can be directly used in the dashboard for an interactive analysis.

For the **R2D4D** example, we provide HTML exports of the `R` and `Python` notebooks, for both 2- and 3-level analyses. They are easy-to-read guides through the multiverse analysis process, and showcase the `ggplot2` and `Plotly` figures respectively.

## Dashboard

The `Plotly Dashboard` can be used by executing the [`dashboard.py`](Python/dashboard.py) file. The directory [`assets/`](Python/assets/) contains a `.css` file for styling. Typically, the dashboard will be accessible via localhost, port 8050, i.e. http://127.0.0.1:8050/. The dashboard requires an "upload" (they are loaded into web storage, and will be removed once the browser is closed) of the configuration file, the preprocessed data, the specification data and the bootstrap data. Each respective filename must be prefixed with `config`, `data`, `specs` and `boot` respectively. The notebooks and scripts adhere to this naming convention.

For a short video walkthrough of the dashboard, go [here](https://youtube.com). TODO

## Issues and Contributions

In case of issues, feel free to contact [`dominik.vesely7@gmail.com`](mailto:dominik.vesely7@gmail.com), or open a GitHub issue. For contributions, change requests, ideas, etc., feel free to open a pull request, or get in contact directly.

## License and Credit

See the [LICENSE](LICENSE.md) file for license rights and limitations. If you use this code in your work, please cite [Voracek et al. (2019)](https://doi.org/10.1027/2151-2604/a000357) with the citation below, and refer to this repository (e.g. with a URL in a footnote).

```
@article{voracek2019,
    author = {Voracek, Martin and Kossmeier, Michael and Tran, Ulrich S.},
    title = {Which Data to Meta-Analyze, and How?},
    journal = {Zeitschrift für Psychologie},
    volume = {227},
    number = {1},
    pages = {64-82},
    year = {2019},
    doi = {10.1027/2151-2604/a000357},
    URL = {https://doi.org/10.1027/2151-2604/a000357}
}
```