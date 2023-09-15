import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_spec_fill_data(n_which, which_lists, n_how, how_lists, specs):
    group_factors = dict(which_lists, **how_lists)
    group_factor_values = [v for vals in group_factors.values() for v in vals]
    group_factor_values.reverse()
    n_factors = n_which + n_how

    spec_fill_data = {}

    for rank in specs["rank"]:
        spec = specs[specs["rank"] == rank]
        spec_id = [int(l in spec.iloc[:, 0:n_factors].values) for l in group_factor_values]
        spec_fill_data[f"{rank}"] = np.array(spec_id) * spec["k"].item()

    return spec_fill_data

def get_cluster_fill_data(data, specs, colmap):
    key_c_id = colmap["key_c_id"]
    key_e_id = colmap["key_e_id"]
    key_c = colmap["key_c"]

    cluster_fill_data = {}

    for rank in specs["rank"]:
        spec = specs[specs["rank"] == rank]
        set_c_ids = [int(c_id) for c_id in spec["set"].item().split(",")]
        set_e_ids = [int(e_id) for e_id in spec["set_es"].item().split(",")]
        fills = np.zeros(len(data[key_c_id].unique()))
        for c_id in set_c_ids:
            c_data = data[data[key_c_id] == c_id]
            c_e_ids = c_data[key_e_id].tolist()
            spec_c_e_ids = [e_id for e_id in c_e_ids if e_id in set_e_ids]
            c_fill = len(spec_c_e_ids) * 100 / len(c_e_ids)
            fills[c_id-1] = c_fill
        cluster_fill_data[f"{rank}"] = np.flip(fills)

    c_ids = sorted(data[key_c_id].unique())
    cluster_fill_data["labels"] = [data[data[key_c_id] == c_id].iloc[0][key_c] for c_id in c_ids]

    return cluster_fill_data

def get_colors(fill_levels):
    # TODO
    colors = ["#9E0142", "#D53E4F", "#F46D43", "#FDAE61", "#FEE08B",
              "#FFFFBF", "#E6F598", "#ABDDA4", "#66C2A5", "#3288BD", "#5E4FA2"]
    return colors

def _get_color_scale(colors, fill_levels):
    color_indices = np.linspace(1, len(colors), fill_levels - 1, dtype=int) - 1
    color_scale = [colors[ci] for ci in color_indices]
    return color_scale

def plot_cluster_tiles(specs, cluster_fill_data, n_total_specs, title):
    cluster_tiles = _cluster_tiles(specs, cluster_fill_data, n_total_specs)
    fig = go.Figure()
    fig.add_trace(cluster_tiles["go"])
    for hline_args in cluster_tiles["hline_args"]:
        fig.add_hline(**hline_args)
    fig.update_yaxes(**cluster_tiles["yaxes_args"])
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(**common_args["x"], ticks="outside", title="Specification Number")
    fig.update_layout(common_args["layout"], width=1000, height=600)
    return fig

def plot_spec_tiles(specs, n_total_specs, spec_fill_data, labels, colors,
                    k_range, title, fill_levels):
    color_scale = _get_color_scale(colors, fill_levels)
    spec_tiles = _spec_tiles(specs, spec_fill_data, labels, n_total_specs, color_scale, k_range)
    fig = go.Figure()
    fig.add_trace(spec_tiles["go"])
    for hline_args in spec_tiles["hline_args"]:
        fig.add_hline(**hline_args)
    fig.update_yaxes(**spec_tiles["yaxes_args"])
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(**common_args["x"], ticks="outside", title="Specification Number")
    fig.update_layout(common_args["layout"], width=1000, height=600)
    return fig

def plot_cluster_size(specs, k_range, n_total_specs, title):
    cluster_size = _cluster_size(specs, k_range)
    fig = go.Figure()
    fig.add_trace(cluster_size["go"])
    fig.update_yaxes(**cluster_size["yaxes_args"])
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(**common_args["x"], ticks="outside", title="Specification Number")
    fig.update_layout(common_args["layout"], width=1000, height=200)
    return fig

def plot_sample_size(specs, k_range, n_total_specs, title):
    sample_size = _sample_size(specs, k_range)
    fig = go.Figure()
    fig.add_trace(sample_size["go"])
    fig.update_yaxes(**sample_size["yaxes_args"])
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(**common_args["x"], ticks="outside", title="Specification Number")
    fig.update_layout(common_args["layout"], width=1000, height=200)
    return fig

def plot_caterpillar(specs, n_total_specs, colors, k_range, title, fill_levels):
    y_limits = _get_y_limits(specs)
    y_ticks = _get_y_ticks(y_limits)
    color_scale = _get_color_scale(colors, fill_levels)
    caterpillar = _caterpillar(
        specs,
        n_total_specs,
        color_scale,
        k_range,
        y_ticks,
        y_limits
    )
    fig = go.Figure()
    for g_obj in caterpillar["go"]:
        fig.add_trace(g_obj)
    fig.add_hline(**caterpillar["hline_args"])
    fig.update_yaxes(**caterpillar["yaxes_args"])
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(**common_args["x"], ticks="outside", title="Specification Number")
    fig.update_layout(common_args["layout"], width=1000, height=300)
    return fig

def plot_multiverse(specs, n_total_specs, k_range, cluster_fill_data, 
                    spec_fill_data, labels, colors, level, title, fill_levels,
                    y_ticks=None, y_limits=None):
    if level == 2:
        rows = 3
        row_heights = [0.3, 0.1, 0.6]
    elif level == 3:
        rows = 5
        row_heights = [0.35, 0.18, 0.06, 0.06, 0.35]

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        row_heights=row_heights,
        vertical_spacing=0.02
    )
    row_counter = 1

    color_scale = _get_color_scale(colors, fill_levels)

    if y_limits is None:
        y_limits = _get_y_limits(specs)
    if y_ticks is None:
        y_ticks = _get_y_ticks(y_limits)

    if level == 3:
        # Cluster Fill Tiles
        cluster_tiles = _cluster_tiles(
            specs,
            cluster_fill_data,
            n_total_specs
        )
        fig.add_trace(cluster_tiles["go"], row=row_counter, col=1)
        for hline_args in cluster_tiles["hline_args"]:
            fig.add_hline(**hline_args, row=row_counter, col=1)
        fig.update_yaxes(**cluster_tiles["yaxes_args"], row=row_counter, col=1)
        row_counter += 1

    # Caterpillar
    caterpillar = _caterpillar(
        specs,
        n_total_specs,
        color_scale,
        k_range,
        y_ticks,
        y_limits
    )
    for g_obj in caterpillar["go"]:
        fig.add_trace(g_obj, row=row_counter, col=1)
    fig.add_hline(**caterpillar["hline_args"], row=row_counter, col=1)
    fig.update_yaxes(**caterpillar["yaxes_args"], row=row_counter, col=1)
    row_counter += 1

    if level == 3:
        # Cluster Sample Size
        cluster_size = _cluster_size(specs, k_range)
        fig.add_trace(cluster_size["go"], row=row_counter, col=1)
        fig.update_yaxes(**cluster_size["yaxes_args"], row=row_counter, col=1)
        row_counter += 1

    # Sample Size
    sample_size = _sample_size(specs, k_range)
    fig.add_trace(sample_size["go"], row=row_counter, col=1)
    fig.update_yaxes(**sample_size["yaxes_args"], row=row_counter, col=1)
    row_counter += 1

    # Spec Tiles
    spec_tiles = _spec_tiles(
        specs,
        spec_fill_data,
        labels,
        n_total_specs,
        color_scale,
        k_range
    )
    fig.add_trace(spec_tiles["go"], row=row_counter, col=1)
    for hline_args in spec_tiles["hline_args"]:
        fig.add_hline(**hline_args, row=row_counter, col=1)
    fig.update_yaxes(**spec_tiles["yaxes_args"], row=row_counter, col=1)
    fig.update_xaxes(**spec_tiles["xaxes_args"], row=row_counter, col=1)

    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(**common_args["x"])
    fig.update_layout(common_args["layout"], width=1500, height=1000 if level == 2 else 1667)

    return fig

def _get_common_args(n_total_specs, title):
    yaxes_args = {
        "linecolor": "black",
        "mirror": True,
        "linewidth": 2,
        "ticks": "outside",
        "gridcolor": "lightgrey",
        "title_standoff": 15
    }
    xaxes_args = {
        "linecolor": "black",
        "mirror": True,
        "linewidth": 2,
        "range": [1 - 0.5, n_total_specs + 0.5]
    }
    layout_args = {
        "title": dict(text=title, font=dict(size=24)),
        "margin": dict(l=30, r=20, t=50, b=30),
        "coloraxis_showscale": False,
        "showlegend": False,
        "plot_bgcolor": "white",
        "hovermode": "x unified",
        "width": 1500
    }
    common_args = {
        "y": yaxes_args,
        "x": xaxes_args,
        "layout": layout_args
    }
    return common_args
    

def _cluster_tiles(specs, cluster_fill_data, n_total_specs):
    n_clusters = len(cluster_fill_data["labels"])
    c_tiles = np.zeros((n_clusters, n_total_specs))
    for rank in specs["rank"]:
        fill = cluster_fill_data[f"{rank}"]
        c_tiles[:, rank-1] = fill

    cluster_fill_data["labels"].reverse()
    c_labels = cluster_fill_data["labels"]
    tiles_bool = (c_tiles != 0)
    spec_infos = []
    for spec_nr in range(tiles_bool.shape[1]):
        spec_info = []
        for cluster in range(tiles_bool.shape[0]):
            if tiles_bool[cluster, spec_nr]:
                c_fill = c_tiles[cluster, spec_nr]
                spec_info.append(f"<b>{c_labels[cluster]}</b>: {c_fill:.2f}%")
        spec_info.reverse()
        spec_infos.append(("<br>").join(spec_info))

    customdata = np.tile(spec_infos, (n_clusters, 1))
    
    color_scale = [f"rgba(9, 175, 0, {round(i, 1)})" for i in np.arange(0, 1.2, 0.2)]
    graph_object = go.Heatmap(
        x=[rank for rank in range(1, n_total_specs + 1)],
        z=c_tiles,
        showscale=False,
        colorscale=color_scale,
        customdata=customdata,
        hovertemplate=("%{customdata}<extra></extra>"),
        hoverlabel=dict(
            bgcolor="white",
            font_size=16
        ),
        zmin=0,
        zmax=100
    )

    y_intercepts = np.arange(0, n_clusters - 1, 1) + 0.5
    hline_args = [{
        "y": y,
        "line_color": "black",
    } for y in y_intercepts]

    yaxes_args = {
        "tickvals": np.arange(0, n_clusters, 1),
        "ticktext": c_labels,
        "showgrid": False
    }

    return {
        "go": graph_object,
        "yaxes_args": yaxes_args,
        "hline_args": hline_args
    }

def _caterpillar(specs, n_total_specs, color_scale, k_range, y_ticks,
                 y_limits):
    go_line = go.Scatter(
        x=specs["rank"],
        y=specs["mean"],
        marker=dict(color="black"),
        mode="lines" if len(specs) == n_total_specs else "markers",
        hovertemplate="Effect Size: %{y:.4f}<extra></extra>"
    )
    go_ci = go.Bar(
        x=specs["rank"],
        y=specs["ci"],
        base=specs["lb"],
        marker=dict(
            color=specs["k"],
            line_width=0,
            colorscale=color_scale,
            cmin=k_range[0],
            cmax=k_range[1]
        ),
        width=1,
        hovertemplate="95%-CI: [%{base:.4f}, %{y:.4f}]<extra></extra>"
    )
    yaxes_args = {
        "title": "Summary Effect (r)",
        "tickvals": y_ticks,
        "range": y_limits
    }
    hline_args = {
        "y": 0,
        "line_dash": "dash",
        "line_color": "black",
        "line_width": 1
    }
    
    return {
        "go": [go_line, go_ci],
        "yaxes_args": yaxes_args,
        "hline_args": hline_args
    }

def _sample_size(specs, k_range):
    graph_object = go.Bar(
        x=specs["rank"],
        y=specs["k"],
        marker=dict(color="grey", line_width=0),
        width=1,
        hovertemplate="Sample Size: %{y}<extra></extra>"
    )
    k_step = round((k_range[1] - k_range[0]) / 4 / 2) * 2
    yaxes_args = {
        "title": "# Samples",
        "tickvals": [t for t in range(k_range[0], k_range[1] + 1, k_step)],
        "range": k_range
    }

    return {
        "go": graph_object,
        "yaxes_args": yaxes_args
    }

def _cluster_size(specs, k_range):
    graph_object = go.Bar(
        x=specs["rank"],
        y=specs["kc"],
        marker=dict(color="slategray", line_width=0),
        width=1,
        hovertemplate="Cluster Size: %{y}<extra></extra>"
    )
    k_step = round((k_range[1] - k_range[0]) / 4 / 2) * 2
    yaxes_args = {
        "title": "# Clusters",
        "tickvals": [t for t in range(k_range[0], k_range[1] + 1, k_step)],
        "range": k_range
    }

    return {
        "go": graph_object,
        "yaxes_args": yaxes_args
    }

def _spec_tiles(specs, spec_fill_data, labels, n_total_specs,
                color_scale, k_range):
    y_labels = labels.copy()
    y_labels.reverse()
    n_factors = len(y_labels)

    tiles = np.zeros((n_factors, n_total_specs))
    for rank in specs["rank"]:
        fill = spec_fill_data[f"{rank}"]
        tiles[:, rank-1] = fill

    tiles_bool = (tiles != 0)
    spec_infos = []
    for spec_nr in range(tiles_bool.shape[1]):
        spec_info = []
        for factor in range(tiles_bool.shape[0]):
            if tiles_bool[factor, spec_nr]:
                spec_info.append(f"{y_labels[factor]}")
        spec_info.reverse()
        spec_infos.append(("<br>").join(spec_info))

    customdata = np.tile(spec_infos, (n_factors, 1))

    color_scale.insert(0, "white")
    graph_object = go.Heatmap(
        x=[rank for rank in range(1, n_total_specs + 1)],
        z=tiles,
        showscale=False,
        colorscale=color_scale,
        customdata=customdata,
        hovertemplate=("%{customdata}<extra></extra>"),
        hoverlabel=dict(
            bgcolor="white",
            font_size=16
        ),
        zmin=0,
        zmax=k_range[1]
    )
    y_intercepts = _get_y_intercepts(y_labels)
    hline_args = [{
        "y": y,
        "line_color": "black",
    } for y in y_intercepts]

    yaxes_args = {
        "tickvals": np.arange(0, n_factors + 1),
        "ticktext": y_labels,
        "title": "Which/How Factors"
    }
    xaxes_args = {
        "ticks": "outside",
        "title": "Specification Number"
    }

    return {
        "go": graph_object,
        "hline_args": hline_args,
        "yaxes_args": yaxes_args,
        "xaxes_args": xaxes_args
    }

def _get_y_intercepts(y_labels):
    group_labels = [l.split(":")[0] for l in y_labels]
    cumulative_n_groups = []
    prev_gl = group_labels[0]
    for i, gl in enumerate(group_labels):
        if gl != prev_gl:
            cumulative_n_groups.append(i-1)
        prev_gl = gl

    y_intercepts = np.array(cumulative_n_groups) + 0.5
    return y_intercepts

def _get_y_limits(specs):
    y_l_limit = min(specs["lb"])
    y_u_limit = max(specs["ub"])
    y_range_diff = y_u_limit - y_l_limit
    y_limits = [y_l_limit - (y_range_diff * 0.1),
                y_u_limit + (y_range_diff * 0.1)]
    return y_limits

def _get_y_ticks(y_limits):
    y_ticks = np.arange(
        round(y_limits[0], 1),
        round(y_limits[1], 1), 
        round((y_limits[1] - y_limits[0]) / 5, 1)
    ).round(1)
    return y_ticks

def plot_treemap(data, title, colmap):
    key_c = colmap["key_c"]
    key_e_id = colmap["key_e_id"]
    key_main_es = colmap["key_main_es"]
    key_main_es_se = colmap["key_main_es_se"]
    key_n = colmap["key_n"]

    c_names = data[key_c].unique().tolist()
    labels = c_names.copy()
    info = c_names.copy()
    colors = [np.mean(data[data[key_c] == l][key_n]) for l in labels]
    labels.extend(data[key_e_id])
    parents = [title] * len(c_names)
    parents.extend(data[key_c])
    colors.extend(data[key_n])

    infotext="ES ID: <b>" + data[key_e_id].astype(str) + "</b><br><br>" + \
        "ES = " + round(data[key_main_es], 3).astype(str) + "<br>" + \
        " +/- " + round(data[key_main_es_se], 3).astype(str) + "<br>" + \
        "N = " + data[key_n].astype(str) + "<br>"

    info.extend(infotext.tolist())

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        marker=dict(
            colors=colors,
            colorscale="Spectral",
            colorbar=dict(
                title="N",
            ),
            line=dict(
                color="black"
            ),
        ),
        text=info,
        textinfo="text",
        hovertemplate="%{text}<extra></extra>",
        tiling=dict(
            pad=10
        ),
    ))
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=16
        ),
        margin=dict(t=25, l=25, r=25, b=25),
        width=1000,
        height=750
    )
    return fig

def _inferential(boot_data):
    go_mean = go.Scatter(
        x=boot_data["rank"],
        y=boot_data["obs"],
        marker=dict(color="red"),
        mode="lines",
        hovertemplate="Effect Size: %{y:.4f}<extra></extra>"
    )
    go_lb = go.Scatter(
        x=boot_data["rank"],
        y=boot_data["boot_lb"],
        marker=dict(color="gray"),
        mode="lines",
        line=dict(dash="dot", width=1),
        hovertemplate="Lower Bound: %{y:.4f}<extra></extra>"
    )
    go_ub = go.Scatter(
        x=boot_data["rank"],
        y=boot_data["boot_ub"],
        marker=dict(color="gray"),
        mode="lines",
        fill="tonexty",
        line=dict(dash="dot", width=1),
        hovertemplate="Upper Bound: %{y:.4f}<extra></extra>"
    )

    yaxes_args = {
        "title": "Summary Effect"
    }

    return {
        "go": [go_lb, go_ub, go_mean],
        "yaxes_args": yaxes_args
    }

def plot_inferential(boot_data, title, n_total_specs):
    inferential = _inferential(boot_data)
    fig = go.Figure()
    for g_obj in inferential["go"]:
        fig.add_trace(g_obj)

    fig.update_yaxes(**inferential["yaxes_args"])
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(**common_args["x"], ticks="outside", title="Specification Number")
    fig.update_layout(common_args["layout"], width=1000, height=300)

    return fig

def _p_hist(specs):
    significant = specs["p"] < 0.05
    go_hist = go.Histogram(
        x=specs["p"],
        nbinsx=20,
        histnorm="probability",
        marker=dict(
            color=significant,
            line=dict(width=2, color="black")
        ),
        hovertemplate="Proportion: %{x:.2f}<extra></extra>"
    )
    for i in range(20):
        if i == 0:
            go_hist.marker.color[i] = "lightgray"
        else:
            go_hist.marker.color[i] = "gray"

    yaxes_args = {
        "tickvals": np.arange(0, 0.2, 0.05),
        "range": [0, 0.15],
        "title": "Proportion"
    }

    return {
        "go": go_hist,
        "yaxes_args": yaxes_args
    }

def plot_p_hist(specs, title, n_total_specs):
    p_hist = _p_hist(specs)
    fig = go.Figure()
    fig.add_trace(p_hist["go"])

    fig.update_yaxes(**p_hist["yaxes_args"])
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    del common_args["x"]["range"]
    fig.update_xaxes(**common_args["x"], ticks="outside", title="Specification p-Values")
    fig.update_layout(common_args["layout"], width=300, height=500)

    return fig