import base64
from dash import Dash, dcc, Output, Input, State, ALL
import flask
import dash_bootstrap_components as dbc
import io
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from components import get_data_tab, get_multiverse_tab, get_other_tab, get_spec_infos, get_header, get_footer
from config import read_config
from data import prepare_data
from plotting import get_spec_fill_data, get_cluster_fill_data, get_colors, plot_multiverse


def _get_empty_figure():
    fig = go.Figure()
    fig.add_annotation(
        text="No Matching Specifications Found",
        xref="paper",
        yref="paper",
        font=dict(size=28),
        showarrow=False
    )
    fig.update_layout(
        plot_bgcolor="white",
        xaxis=dict(linecolor="black", mirror=True, linewidth=1, tickvals=[]),
        yaxis=dict(linecolor="black", mirror=True, linewidth=1, tickvals=[]),
        height=1000
    )
    return fig


external_stylesheets = []
server = flask.Flask(__name__)
app = Dash(__name__, external_stylesheets=external_stylesheets,
           prevent_initial_callbacks="initial_duplicate",
           suppress_callback_exceptions=True,
           server=server)

app.title = "Multiverse dashboard"

app.layout = dbc.Container([
    dcc.Store(id="memory", storage_type="session"),
    get_header(),
    dbc.Row([
        dbc.Tabs([
            dbc.Tab(
                id="outTabData",
                children=None,
                label="Dataset",
                tab_id="tab-data",
                tab_style={"marginLeft": "10px"}
            ),
            dbc.Tab(
                id="outTabMultiverse",
                children=None,
                label="Multiverse Analysis",
                tab_id="tab-mv"
            ),
            dbc.Tab(
                id="outTabOther",
                children=None,
                label="Other Plots",
                tab_id="tab-op"
            )
        ], active_tab="tab-data")
    ]),
    get_footer(),
], fluid=True)


@app.callback(
    Output("outTabData", "children"),
    Output("outTabMultiverse", "children"),
    Output("outTabOther", "children"),
    Input("memory", "data"),
    prevent_initial_call=True
)
def get_tab_content(memory):
    if memory is None:
        return None, None, None
    config = memory["config"]
    data = pd.DataFrame(memory["data"])
    data_tab_content = get_data_tab(config, data)
    multiverse_tab_content = get_multiverse_tab(
        data,
        memory["factor_lists"],
        memory["kc_range"],
        memory["k_range"],
        memory["n_total_specs"],
        config["colmap"]
    )
    other_tab_content = get_other_tab(
        pd.DataFrame(memory["boot_data"]),
        pd.DataFrame(memory["specs"]),
        #memory["config"]["title"],
        "",
        memory["n_total_specs"]
    )
    return data_tab_content, multiverse_tab_content, other_tab_content


@app.callback(
    Output("memory", "data"),
    Output("outHeaderTitle", "children"),
    Output("outHeaderLevel", "children"),
    Output("outUpload", "children"),
    State("memory", "data"),
    State("inUpload", "filename"),
    Input("inUpload", "contents"),
    prevent_initial_call=False
)
def upload(memory, filenames, contents):
    uploads = []
    if contents == None:
        contents = []
        filenames = [
            "static_data/boot_HR.csv",
            "static_data/config_HR.json",
            "static_data/data_HR.csv",
            "static_data/specs_HR.csv",
        ]

        for f in filenames:
            file = open(f, "r", encoding="utf-8")
            contents.append(file.read())
            file.close()

    for f, c in sorted(zip(filenames, contents)):
        uploads.append(f)
        if c.startswith("data:application"):
            c_type, c_string = c.split(",")
            c_decoded = base64.b64decode(c_string)
            c_decoded_str = io.StringIO(c_decoded.decode("ISO-8859-1"))
        else:
            c_decoded_str = io.StringIO(c)

        if os.path.basename(f).startswith("boot"):
            boot_data = pd.read_csv(c_decoded_str)

        if os.path.basename(f).startswith("config"):
            config = read_config(data=c_decoded_str)

        if os.path.basename(f).startswith("data"):
            data = prepare_data(config["colmap"], raw=c_decoded_str)

        if os.path.basename(f).startswith("specs"):
            specs = pd.read_csv(c_decoded_str)

    cluster_fill_data = get_cluster_fill_data(data, specs, config["colmap"])
    spec_fill_data = get_spec_fill_data(
        config["n_which"],
        config["which_lists"],
        config["n_how"],
        config["how_lists"],
        specs
    )
    fill_levels = len(np.unique([v for v in spec_fill_data.values()]))
    colors = get_colors(fill_levels)

    k_min = config["k_min"]
    k_max = max(specs["k"])
    k_range = [k_min, k_max]

    kc_min = min(specs["kc"])
    kc_max = max(specs["kc"])
    kc_range = [kc_min, kc_max]

    n_es = len(data)
    n_total_specs = len(specs)

    key_c_id = config["colmap"]["key_c_id"]
    key_c = config["colmap"]["key_c"]
    key_e_id = config["colmap"]["key_e_id"]

    n_clusters = len(data[key_c_id].unique())

    level = config["level"]

    factor_lists = dict(config["which_lists"], **config["how_lists"])

    memory = {
        "config": config,
        "boot_data": boot_data.to_dict(),
        "specs": specs.to_dict(),
        "data": data.to_dict(),
        "cluster_fill_data": cluster_fill_data,
        "spec_fill_data": spec_fill_data,
        "colors": colors,
        "k_range": k_range,
        "kc_range": kc_range,
        "n_es": n_es,
        "n_total_specs": n_total_specs,
        "key_c_id": key_c_id,
        "key_c": key_c,
        "key_e_id": key_e_id,
        "n_clusters": n_clusters,
        "level": level,
        "factor_lists": factor_lists
    }

    title = f"# {config['title']}"
    level_header = f"Level: {level}"
    return memory, title, level_header, ("  \n").join(uploads)


@app.callback(
    Output("inRefresh", "n_clicks"),
    Output({"type": "inSelect", "index": ALL}, "value"),
    Output("inSpecNr", "value"),
    Output("inCISwitch", "value"),
    Output("inCICases", "options", allow_duplicate=True),
    Output("inCICases", "value"),
    Output("inPFilterSwitch", "value"),
    Output("inPMarkerSwitch", "value"),
    Output("inPValues", "options", allow_duplicate=True),
    Output("inPValues", "value"),
    Output("inRangeKC", "value"),
    Output("inRangeK", "value"),
    Output("inEffectSizes", "value"),
    Output("inStudyChecklist", "value", allow_duplicate=True),
    Output("inESChecklist", "value", allow_duplicate=True),
    State("memory", "data"),
    State("inPValues", "options"),
    State("inCICases", "options"),
    State("inRefresh", "n_clicks"),
    Input("inReset", "n_clicks"),
)
def reset_filters(memory, p_options, ci_options, refresh_clicks, _):
    data = pd.DataFrame(memory["data"])
    key_c_id = memory["key_c_id"]
    key_e_id = memory["key_e_id"]
    factor_lists = memory["factor_lists"]

    for item in [*p_options, *ci_options]:
        item["disabled"] = True
    selects = [None for _ in factor_lists.keys()]
    spec_nr = None
    ci_switch = []
    ci_cases_options = ci_options
    ci_cases = 0
    p_filter_switch = []
    p_marker_switch = []
    p_value_options = p_options
    p_value = 0.05
    kc_range = memory["kc_range"]
    k_range = memory["k_range"]
    effect_sizes = 0
    study_checklist = [str(c_id) for c_id in data[key_c_id].unique()]
    es_checklist = [str(e_id) for e_id in sorted(data[key_e_id])]
    if refresh_clicks is not None:
        refresh_clicks += 1
    return (refresh_clicks, selects, spec_nr, ci_switch, ci_cases_options, ci_cases,
            p_filter_switch, p_marker_switch, p_value_options, p_value,
            kc_range, k_range, effect_sizes, study_checklist, es_checklist)


@app.callback(
    Output("inPValues", "options"),
    State("inPValues", "options"),
    Input("inPMarkerSwitch", "value"),
    Input("inPFilterSwitch", "value"),
)
def toggle_p_radio_items(options, p_marker_switch, p_filter_switch):
    disabled = not (p_marker_switch or p_filter_switch)
    for item in options:
        item["disabled"] = disabled
    return options


@app.callback(
    Output("inCICases", "options"),
    State("inCICases", "options"),
    Input("inCISwitch", "value"),
)
def toggle_ci_radio_items(options, value):
    for item in options:
        item["disabled"] = (value == [])
    return options


@app.callback(
    Output("inStudyChecklist", "value"),
    State("memory", "data"),
    State("inStudyChecklist", "value"),
    Input("inToggleAll", "n_clicks"),
)
def select_deselect_c(memory, study_set, n_clicks):
    data = pd.DataFrame(memory["data"])
    key_c_id = memory["key_c_id"]
    n_clusters = memory["n_clusters"]
    if n_clicks is None:
        return study_set
    if len(study_set) == n_clusters:
        return []
    else:
        return [str(c_id) for c_id in data[key_c_id].unique()]


@app.callback(
    Output("inESChecklist", "value"),
    State("memory", "data"),
    State("inESChecklist", "value"),
    Input("inToggleAllES", "n_clicks"),
)
def select_deselect_e(memory, es_set, n_clicks):
    data = pd.DataFrame(memory["data"])
    n_es = memory["n_es"]
    key_e_id = memory["key_e_id"]
    if n_clicks is None:
        return es_set
    if len(es_set) == n_es:
        return []
    else:
        return [str(e_id) for e_id in sorted(data[key_e_id])]


@app.callback(
    Output("outSpecInfoSN", "children"),
    [Output(f"outSpecInfo{v}", "children") for _, v in get_spec_infos()],
    State("memory", "data"),
    Input("multiverse", "clickData")
)
def display_click_data(memory, clickData):
    data = pd.DataFrame(memory["data"])
    specs = pd.DataFrame(memory["specs"])
    cluster_fill_data = memory["cluster_fill_data"]
    key_c_id = memory["key_c_id"]
    key_e_id = memory["key_e_id"]
    key_c = memory["key_c"]
    level = memory["level"]
    factor_lists = memory["factor_lists"]

    if clickData is None:
        return ("Specification Nr.: -", *(["-"] * len(get_spec_infos())))

    points = clickData["points"][0]
    cn = 5 if level == 3 else 3
    if points["curveNumber"] == cn and points["customdata"] == "":
        return ("Specification Nr.: -", *(["-"] * len(get_spec_infos())))

    spec_nr = points["x"]
    spec_data = specs[specs["rank"] == spec_nr]
    es = spec_data["mean"].item()
    ub = spec_data["ub"].item()
    lb = spec_data["lb"].item()
    ci = ub - lb
    p = spec_data["p"].item()
    kc = spec_data["kc"].item()
    k = spec_data["k"].item()
    f = [f"**{k}**: {spec_data[k].item()}" for k in factor_lists.keys()]
    set = spec_data["set"].item()
    set_es = spec_data["set_es"].item()
    set_c_ids = np.array(set.split(",")).astype(int)
    set_e_ids = np.array(set_es.split(",")).astype(int)
    set_data = data[data[key_c_id].isin(set_c_ids)]
    clusters = {cluster: [f"*{e_id}*" for e_id in group[key_e_id]
                          if e_id in set_e_ids] for cluster, group in set_data.groupby(key_c)}
    cluster_infos = []
    for c, e_ids in clusters.items():
        c_index = np.where(np.array(cluster_fill_data["labels"]) == c)[0][0]
        c_fill = cluster_fill_data[f"{spec_nr}"][-(c_index+1)]
        str_e_ids = (", ").join(e_ids)
        info = f"**{c}**, Effect ID{'s' if len(e_ids) > 1 else ''}: {str_e_ids}, {c_fill:.2f}%"
        cluster_infos.append(info)

    spec_info = [
        f"{es:.4f}",
        f"{lb:.4f}, {ub:.4f} (width: {ci:.4f})",
        f"{kc}",
        f"{k}",
        f"{p:.4f}",
        ("  \n").join(f),
        ("  \n").join(cluster_infos)
    ]
    return (f"Specification Nr.: {spec_nr}", *spec_info)


@app.callback(
    Output("multiverse", "figure"),
    Output("outSpecPercent", "children"),
    Output("outSpecPercentP", "children"),
    Output("outSpecPercentESA", "children"),
    Output("outSpecPercentESB", "children"),
    Input("inRefresh", "n_clicks"),
    State("memory", "data"),
    State("inSpecNr", "value"),
    State("inCISwitch", "value"),
    State("inCICases", "value"),
    State("inPFilterSwitch", "value"),
    State("inPMarkerSwitch", "value"),
    State("inPValues", "value"),
    State("inRangeKC", "value"),
    State("inRangeK", "value"),
    State("inEffectSizes", "value"),
    State("inStudyChecklist", "value"),
    State("inESChecklist", "value"),
    State({"type": "outFactor", "index": ALL}, "children"),
    State({"type": "inSelect", "index": ALL}, "value"),
    prevent_initial_call=True
)
def update_multiverse(n_clicks, memory, spec_nr, ci_switch, ci_case, p_filter_switch,
                      p_marker_switch, p_value, range_kc, range_k, es_value,
                      study_list, es_list, factor_keys, factor_values):
    specs = pd.DataFrame(memory["specs"])
    cluster_fill_data = memory["cluster_fill_data"]
    spec_fill_data = memory["spec_fill_data"]
    fill_levels = len(np.unique([v for v in spec_fill_data.values()]))
    colors = memory["colors"]
    k_range = memory["k_range"]
    n_total_specs = memory["n_total_specs"]
    level = memory["level"]
    labels = memory["config"]["labels"]
    # title = memory["config"]["title"]
    title = ""

    y_l_limit = min(specs["lb"])
    y_u_limit = max(specs["ub"])
    y_range_diff = y_u_limit - y_l_limit
    y_limits = [y_l_limit - (y_range_diff * 0.1),
                y_u_limit + (y_range_diff * 0.1)]
    y_ticks = np.arange(
        round(y_limits[0], 1),
        round(y_limits[1], 1),
        round((y_limits[1] - y_limits[0]) / 5, 1)
    ).round(1)

    specs_f = specs.copy()
    if ci_switch != []:
        if ci_case == 0:
            specs_f = specs_f[specs_f["ub"] < 0]
        elif ci_case == 1:
            specs_f = specs_f[specs_f["lb"] > 0]
        elif ci_case == 2:
            specs_f = specs_f[(specs_f["ub"] > 0) & (specs_f["lb"] < 0)]

    if len(specs_f) != 0:
        specs_f = specs_f[specs_f["kc"] >= range_kc[0]]
    if len(specs_f) != 0:
        specs_f = specs_f[specs_f["kc"] <= range_kc[1]]

    if len(specs_f) != 0:
        specs_f = specs_f[specs_f["k"] >= range_k[0]]
    if len(specs_f) != 0:
        specs_f = specs_f[specs_f["k"] <= range_k[1]]

    if p_filter_switch != []:
        if len(specs_f) != 0:
            specs_f = specs_f[specs_f["p"] < p_value]

    if es_value != 0:
        # cutoff_rank = specs_f[specs_f["mean"] >= 0].iloc[0]["rank"]
        if len(specs_f) != 0:
            if es_value < 0:
                specs_f = specs_f[specs_f["mean"] < 0]
            else:
                specs_f = specs_f[specs_f["mean"] >= 0]

    if len(specs_f) != 0:
        specs_f = specs_f[specs_f["set"].apply(lambda set: all(
            c_id in study_list for c_id in set.split(",")))]
    if len(specs_f) != 0:
        specs_f = specs_f[specs_f["set_es"].apply(
            lambda set_es: all(e_id in es_list for e_id in set_es.split(",")))]

    factors = zip(factor_keys, factor_values)

    for f_key, f_val in factors:
        if f_val is not None:
            if len(specs_f) != 0:
                specs_f = specs_f[specs_f[f_key] == f_val]

    n_specs_f = len(specs_f)
    sfp = n_specs_f * 100 / n_total_specs

    if n_specs_f == 0:
        n_specs_p = n_specs_esa = n_specs_esb = sfpp = sfpesa = sfpesb = 0
    else:
        n_specs_p = len(specs_f[specs_f["p"] < 0.05])
        n_specs_esa = len(specs_f[specs_f["mean"] >= 0])
        n_specs_esb = len(specs_f[specs_f["mean"] < 0])
        sfpp = n_specs_p * 100 / n_specs_f
        sfpesa = n_specs_esa * 100 / n_specs_f
        sfpesb = n_specs_esb * 100 / n_specs_f

    sfp_info = f"Showing **{sfp:.2f}%** of specifications ({n_specs_f} / {n_total_specs})"
    sfpp_info = f"**{sfpp:5.2f}%** of shown effect sizes are *significant* (p < 0.05) ({n_specs_p} / {n_specs_f})"
    sfpesa_info = f"**{sfpesa:5.2f}%** of shown effect sizes are **≥ 0** ({n_specs_esa} / {n_specs_f})"
    sfpesb_info = f"**{sfpesb:5.2f}%** of shown effect sizes are **< 0** ({n_specs_esb} / {n_specs_f})"

    if n_specs_f == 0:
        return _get_empty_figure(), sfp_info, sfpp_info, sfpesa_info, sfpesb_info

    fig = plot_multiverse(
        specs_f,
        n_total_specs,
        k_range,
        cluster_fill_data,
        spec_fill_data,
        labels,
        colors,
        level,
        title,
        fill_levels,
        y_ticks,
        y_limits
    )

    if spec_nr is not None:
        fig.update_xaxes(
            range=[spec_nr-10, spec_nr+10],
            tickvals=[spec_nr]
        )
        fig.add_vline(x=spec_nr-0.5, line_color="red")
        fig.add_vline(x=spec_nr+0.5, line_color="red")

    customdata = specs_f[specs_f["p"] < p_value]["p"]
    if p_marker_switch != []:
        fig.add_trace(
            go.Scatter(
                x=specs_f[specs_f["p"] < p_value]["rank"],
                y=specs_f[specs_f["p"] < p_value]["mean"],
                marker=dict(color="blue", symbol="diamond", size=10),
                mode="markers", hovertemplate="p-Value: %{customdata:.4f}<extra></extra>", customdata=customdata
            ), row=1 if level == 2 else 2, col=1
        )

    # if es_value != 0:
    #     if es_value > 0:
    #         limits = [cutoff_rank, n_total_specs]
    #     else:
    #         limits = [1, cutoff_rank-1]
    #     fig.update_xaxes(
    #         range=limits
    #     )

    return fig, sfp_info, sfpp_info, sfpesa_info, sfpesb_info


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
