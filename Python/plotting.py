import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_spec_fill_data(n_which, which_lists, n_how, how_lists, specs):
    """Get spec fill data for each specification.

    The spec fill data is a vector that indicate the which- and how-
    factors that comprise a specification. The size of the number corresponds
    to the number of samples that contribute (i.e. the value of k).

    Arguments:
        n_which -- The number of which-factors.
        which_lists -- The which-factors.
        n_how -- The number of how-factors.
        how_lists -- The how-factors.
        specs -- The specification data.

    Returns:
        A dictionary containing the spec fill data for each specification.
    """
    # Combine which- and how- factors into a single dictionary
    group_factors = dict(which_lists, **how_lists)

    # Get complete list of values
    group_factor_values = [v for vals in group_factors.values() for v in vals]
    group_factor_values.reverse()
    n_factors = n_which + n_how

    spec_fill_data = {}

    # Get fill data for each specification
    for rank in specs["rank"]:
        spec = specs[specs["rank"] == rank]

        # The first columns in the specification data are factors
        spec_id = [
            int(l in spec.iloc[:, 0:n_factors].values)
            for l in group_factor_values
        ]

        # Key should be string, not number, for interoperability with R
        # Multiply binary vector with k
        spec_fill_data[f"{rank}"] = np.array(spec_id) * spec["k"].item()

    return spec_fill_data


def get_cluster_fill_data(data, specs, colmap):
    """Get cluster fill data for each specification.

    The cluster fill data is a vector that indicate the percentage of 
    available samples from each cluster that belongs to the specification.

    Arguments:
        data -- The meta-analytic dataset.
        specs -- The specification data.
        colmap -- The column-map from the configuration.

    Returns:
        A dictionary containing the cluster fill data for each specification.
    """
    # Get relevant keys from colmap
    key_c_id = colmap["key_c_id"]
    key_e_id = colmap["key_e_id"]
    key_c = colmap["key_c"]

    cluster_fill_data = {}

    # Get fill data for each specification
    for rank in specs["rank"]:
        spec = specs[specs["rank"] == rank]
        # Get the sets of cluster- and effect- IDs that contribute
        set_c_ids = [int(c_id) for c_id in spec["set"].item().split(",")]
        set_e_ids = [int(e_id) for e_id in spec["set_es"].item().split(",")]

        # For each cluster ID in the set, compute the percentage and set
        # the value at the corresponding index of the vector
        fills = np.zeros(len(data[key_c_id].unique()))
        for c_id in set_c_ids:
            # Get all effect IDs in cluster
            c_data = data[data[key_c_id] == c_id]
            c_e_ids = c_data[key_e_id].tolist()

            # Filter for effect IDs that are in the specification
            spec_c_e_ids = [e_id for e_id in c_e_ids if e_id in set_e_ids]

            # Compute percentage and set value at corresponding index
            c_fill = len(spec_c_e_ids) * 100 / len(c_e_ids)
            fills[c_id-1] = c_fill

        # Key should be string, not number, for interoperability with R
        # Reverse the vector for correct plotting
        cluster_fill_data[f"{rank}"] = np.flip(fills)

    # Prepare list of cluster names as labels
    c_ids = sorted(data[key_c_id].unique())
    cluster_fill_data["labels"] = [
        data[data[key_c_id] == c_id].iloc[0][key_c]
        for c_id in c_ids
    ]

    return cluster_fill_data


def get_colors(fill_levels):
    """Get list of colors for plotting, from warm to cold.

    The maximum amount of colors is 11. If the amount of fill_levels is less,
    the list of colors is reduced.

    Arguments:
        fill_levels -- The amount of different fill values
                       (unique values of k).

    Returns:
        A list of colors.
    """
    colors = ["#9E0142", "#D53E4F", "#F46D43",
              "#FDAE61", "#FEE08B", "#FFFFBF",
              "#E6F598", "#ABDDA4", "#66C2A5",
              "#3288BD", "#5E4FA2"]
    if 11 <= (fill_levels-1):
        return colors

    # Remove some values from color list at equal distances
    n_remove = 11 - (fill_levels-1)
    step = 1 / (n_remove + 1)
    steps = np.arange(step, step=step, stop=1)
    remove_indices = np.round(11 * steps).astype(int)
    colors = np.delete(colors, remove_indices)
    return colors


def _get_color_scale(colors, fill_levels):
    """Get color scale, consisting of repeated colors.

    Arguments:
        colors -- The list of colors.
        fill_levels -- The amount of different fill values
                       (unique values of k).

    Returns:
        A list of repeated colors of length fill_levels-1.
    """
    color_indices = np.linspace(1, len(colors), fill_levels - 1, dtype=int)
    color_indices = color_indices - 1
    color_scale = [colors[ci] for ci in color_indices]
    return color_scale


def _get_common_args(n_total_specs, title):
    """Get common plotting arguments.

    Arguments:
        n_total_specs -- The total number of specifications.
        title -- The analysis title.

    Returns:
        A dictionary of common plotting arguments.
    """
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


def _caterpillar(specs, n_total_specs, color_scale, k_range, y_ticks,
                 y_limits):
    """Get caterpillar figure data.

    Arguments:
        specs -- The specification data.
        n_total_specs -- The total number of specifications.
        color_scale -- The color scale.
        k_range -- The range of sample sizes.
        y_ticks -- The ticks for y-axis.
        y_limits -- The limits for y-axis.

    Returns:
        A dictionary with caterpillar figure data.
    """
    # Line of effect sizes
    go_line = go.Scatter(
        x=specs["rank"],
        y=specs["mean"],
        marker=dict(color="black"),
        mode="lines" if len(specs) == n_total_specs else "markers",
        hovertemplate="Effect Size: %{y:.4f}<extra></extra>"
    )
    # CI error bars
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
    # Horizontal line at y = 0
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


def _get_y_limits(specs):
    """Compute y-axis limits for caterpillar plot.

    Arguments:
        specs -- The specification data.

    Returns:
        The y-axis limits.
    """
    y_l_limit = min(specs["lb"])
    y_u_limit = max(specs["ub"])
    y_range_diff = y_u_limit - y_l_limit
    y_limits = [y_l_limit - (y_range_diff * 0.1),
                y_u_limit + (y_range_diff * 0.1)]
    return y_limits


def _get_y_ticks(y_limits):
    """Compute y-axis ticks.

    Arguments:
        y_limits -- The y-axis limits

    Returns:
        The y-axis ticks.
    """
    y_ticks = np.arange(
        round(y_limits[0], 1),
        round(y_limits[1], 1),
        round((y_limits[1] - y_limits[0]) / 5, 1)
    ).round(1)
    return y_ticks


def plot_caterpillar(specs, n_total_specs, colors, k_range, title, fill_levels):
    """Plot caterpillar.

    Arguments:
        specs -- The specification data.
        n_total_specs -- The total number of specifications.
        colors -- The list of colors.
        k_range -- The range of sample sizes.
        title -- The analysis title.
        fill_levels -- The amount of fill levels.

    Returns:
        Plotly figure.
    """
    y_limits = _get_y_limits(specs)
    y_ticks = _get_y_ticks(y_limits)
    color_scale = _get_color_scale(colors, fill_levels)

    # Get figure data
    caterpillar = _caterpillar(
        specs,
        n_total_specs,
        color_scale,
        k_range,
        y_ticks,
        y_limits
    )

    # Plot figure
    fig = go.Figure()
    for g_obj in caterpillar["go"]:
        fig.add_trace(g_obj)
    fig.add_hline(**caterpillar["hline_args"])
    fig.update_yaxes(**caterpillar["yaxes_args"])

    # Update layout with common values
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(
        **common_args["x"],
        ticks="outside",
        title="Specification Number"
    )
    fig.update_layout(common_args["layout"], width=1000, height=300)
    return fig


def _cluster_tiles(specs, cluster_fill_data, n_total_specs):
    """Get cluster tilemap figure data.

    Arguments:
        specs -- The specification data.
        cluster_fill_data -- See get_cluster_fill_data().
        n_total_specs -- The total number of specifications.

    Returns:
        A dictionary with cluster tilemap figure data.
    """
    # Construct tilemap
    n_clusters = len(cluster_fill_data["labels"])
    c_tiles = np.zeros((n_clusters, n_total_specs))
    for rank in specs["rank"]:
        fill = cluster_fill_data[f"{rank}"]
        c_tiles[:, rank-1] = fill

    # Reverse labels for correct plotting
    cluster_fill_data["labels"].reverse()

    # Construct hover information
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

    # Colorscale is single color with different opacity levels
    color_scale = [
        f"rgba(9, 175, 0, {round(i, 1)})"
        for i in np.arange(0, 1.2, 0.2)
    ]

    # Tilemap
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

    # Horizontal lines for each cluster
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


def plot_cluster_tiles(specs, cluster_fill_data, n_total_specs, title):
    """Plot cluster tilemap.

    Arguments:
        specs -- The specification data.
        cluster_fill_data -- See get_cluster_fill_data().
        n_total_specs -- The total number of specifications.
        title -- The analysis title.

    Returns:
        Plotly figure.
    """
    # Get figure data
    cluster_tiles = _cluster_tiles(specs, cluster_fill_data, n_total_specs)

    # Plot figure
    fig = go.Figure()
    fig.add_trace(cluster_tiles["go"])
    for hline_args in cluster_tiles["hline_args"]:
        fig.add_hline(**hline_args)
    fig.update_yaxes(**cluster_tiles["yaxes_args"])

    # Update layout with common values
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(
        **common_args["x"], ticks="outside", title="Specification Number")
    fig.update_layout(common_args["layout"], width=1000, height=600)
    return fig


def _get_y_intercepts(y_labels):
    """Get intercept points for each factor.

    Arguments:
        y_labels -- The list of factor labels.

    Returns:
        List of intercept points.
    """
    # Split each label and retain key
    group_labels = [l.split(":")[0] for l in y_labels]

    # Check how many values are present for each factor
    cumulative_n_groups = []
    prev_gl = group_labels[0]
    for i, gl in enumerate(group_labels):
        if gl != prev_gl:
            cumulative_n_groups.append(i-1)
        prev_gl = gl

    # Shift by 0.5 for correct plotting
    y_intercepts = np.array(cumulative_n_groups) + 0.5
    return y_intercepts


def _spec_tiles(specs, spec_fill_data, labels, n_total_specs,
                color_scale, k_range):
    """Get specification tilemap figure data.

    Arguments:
        specs -- The specification data.
        spec_fill_data -- See get_spec_fill_data().
        labels -- The factor labels.
        n_total_specs -- The total number of specifications.
        color_scale -- The color scale.
        k_range -- The range of sample sizes.

    Returns:
        A dictionary with specification tilemap figure data.
    """
    # Reverse labels for correct plotting
    y_labels = labels.copy()
    y_labels.reverse()
    n_factors = len(y_labels)

    # Construct tilemap
    tiles = np.zeros((n_factors, n_total_specs))
    for rank in specs["rank"]:
        fill = spec_fill_data[f"{rank}"]
        tiles[:, rank-1] = fill

    # Construct hover information
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

    # Ensure white "background"
    color_scale.insert(0, "white")

    # Tilemap
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

    # Horizontal lines for each factor
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


def plot_spec_tiles(specs, n_total_specs, spec_fill_data, labels, colors,
                    k_range, title, fill_levels):
    """Plot specification tilemap.

    Arguments:
        specs -- The specification data.
        n_total_specs -- The total number of specifications.
        spec_fill_data -- See get_spec_fill_data().
        labels -- The factor labels.
        colors -- The list of colors.
        k_range -- The range of sample sizes.
        title -- The analysis title.
        fill_levels -- The amount of fill levels.

    Returns:
        Plotly figure.
    """
    color_scale = _get_color_scale(colors, fill_levels)

    # Get figure data
    spec_tiles = _spec_tiles(specs, spec_fill_data, labels, n_total_specs,
                             color_scale, k_range)

    # Plot Figure
    fig = go.Figure()
    fig.add_trace(spec_tiles["go"])
    for hline_args in spec_tiles["hline_args"]:
        fig.add_hline(**hline_args)
    fig.update_yaxes(**spec_tiles["yaxes_args"])

    # Update layout with common values
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(
        **common_args["x"], ticks="outside", title="Specification Number")
    fig.update_layout(common_args["layout"], width=1000, height=600)
    return fig


def _cluster_size(specs, k_range):
    """Get cluster size barplot figure data.

    Arguments:
        specs -- The specification data.
        k_range -- The range of sample sizes.

    Returns:
        A dictionary with cluster size barplot figure data.
    """
    # Barplot
    graph_object = go.Bar(
        x=specs["rank"],
        y=specs["kc"],
        marker=dict(color="slategray", line_width=0),
        width=1,
        hovertemplate="Cluster Size: %{y}<extra></extra>"
    )

    # Ticksteps
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


def plot_cluster_size(specs, k_range, n_total_specs, title):
    """Plot cluster size barplot.

    Arguments:
        specs -- The specification data.
        k_range -- The range of sample sizes.
        n_total_specs -- The total number of specifications.
        title -- The analysis title.

    Returns:
        Plotly figure.
    """
    # Get figure data
    cluster_size = _cluster_size(specs, k_range)

    # Plot Figure
    fig = go.Figure()
    fig.add_trace(cluster_size["go"])
    fig.update_yaxes(**cluster_size["yaxes_args"])

    # Update layout with common values
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(
        **common_args["x"], ticks="outside", title="Specification Number")
    fig.update_layout(common_args["layout"], width=1000, height=200)
    return fig


def _sample_size(specs, k_range):
    """Get sample size barplot figure data.

    Arguments:
        specs -- The specification data.
        k_range -- The range of sample sizes.

    Returns:
        A dictionary with sample size barplot figure data.
    """
    # Barplot
    graph_object = go.Bar(
        x=specs["rank"],
        y=specs["k"],
        marker=dict(color="grey", line_width=0),
        width=1,
        hovertemplate="Sample Size: %{y}<extra></extra>"
    )

    # Ticksteps
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


def plot_sample_size(specs, k_range, n_total_specs, title):
    """Plot sample size barplot.

    Arguments:
        specs -- The specification data.
        k_range -- The range of sample sizes.
        n_total_specs -- The total number of specifications.
        title -- The analysis title.

    Returns:
        Plotly figure.
    """
    # Get figure data
    sample_size = _sample_size(specs, k_range)

    # Plot Figure
    fig = go.Figure()
    fig.add_trace(sample_size["go"])
    fig.update_yaxes(**sample_size["yaxes_args"])

    # Update layout with common values
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(
        **common_args["x"], ticks="outside", title="Specification Number")
    fig.update_layout(common_args["layout"], width=1000, height=200)
    return fig


def plot_multiverse(specs, n_total_specs, k_range, cluster_fill_data,
                    spec_fill_data, labels, colors, level, title, fill_levels,
                    y_ticks=None, y_limits=None):
    """Plot the multiverse summary figure.

    Arguments:
        specs -- The specification data.
        n_total_specs -- The total number of specifications.
        k_range -- The range of sample sizes.
        cluster_fill_data -- See get_cluster_fill_data().
        spec_fill_data -- See get_spec_fill_data().
        labels -- The factor labels.
        colors -- The list of colors.
        level -- The level of the meta-analysis (2 or 3).
        title -- The analysis title.
        fill_levels -- The amount of fill levels.

    Keyword Arguments:
        y_ticks -- y-axis ticks (default: {None})
        y_limits -- y-axis limits (default: {None})

    Returns:
        Plotly figure.
    """
    # Specify relative heights of each panel
    if level == 2:
        rows = 3
        row_heights = [0.3, 0.1, 0.6]
    elif level == 3:
        rows = 5
        row_heights = [0.35, 0.18, 0.06, 0.06, 0.35]

    # Prepare subplot figure
    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        row_heights=row_heights,
        vertical_spacing=0.02
    )
    row_counter = 1

    color_scale = _get_color_scale(colors, fill_levels)

    # If y-axis limits and/or ticks are not None, use the argument values
    # Otherwise, compute them
    if y_limits is None:
        y_limits = _get_y_limits(specs)
    if y_ticks is None:
        y_ticks = _get_y_ticks(y_limits)

    if level == 3:
        # Cluster tilemap
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
        # Cluster sample Size
        cluster_size = _cluster_size(specs, k_range)
        fig.add_trace(cluster_size["go"], row=row_counter, col=1)
        fig.update_yaxes(**cluster_size["yaxes_args"], row=row_counter, col=1)
        row_counter += 1

    # Sample size
    sample_size = _sample_size(specs, k_range)
    fig.add_trace(sample_size["go"], row=row_counter, col=1)
    fig.update_yaxes(**sample_size["yaxes_args"], row=row_counter, col=1)
    row_counter += 1

    # Specification tilemap
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

    # Update layout with common values
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(**common_args["x"])
    fig.update_layout(common_args["layout"], width=1500,
                      height=1000 if level == 2 else 1667)

    return fig


def plot_treemap(data, title, colmap):
    """Plot treemap of meta-analytic data.

    Arguments:
        data -- The meta-analytic data.
        title -- The analysis title.
        colmap -- The column-map from the configuration.

    Returns:
        Plotly figure.
    """
    # Get relevant keys from colmap
    key_c = colmap["key_c"]
    key_e_id = colmap["key_e_id"]
    key_main_es = colmap["key_main_es"]
    key_main_es_se = colmap["key_main_es_se"]
    key_n = colmap["key_n"]

    # Construct treemap data
    c_names = data[key_c].unique().tolist()
    labels = c_names.copy()
    info = c_names.copy()
    colors = [np.mean(data[data[key_c] == l][key_n]) for l in labels]
    labels.extend(data[key_e_id])
    parents = [title] * len(c_names)
    parents.extend(data[key_c])
    colors.extend(data[key_n])

    # Construct hover information text
    infotext = "ES ID: <b>" + data[key_e_id].astype(str) + "</b><br><br>" + \
        "ES = " + round(data[key_main_es], 3).astype(str) + "<br>" + \
        " +/- " + round(data[key_main_es_se], 3).astype(str) + "<br>" + \
        "N = " + data[key_n].astype(str) + "<br>"

    info.extend(infotext.tolist())

    # Plot treemap figure
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
    """Get inferential specification figure data.

    Arguments:
        boot_data -- The bootstrap sampling data.

    Returns:
        A dictionary with figure data.
    """
    # Draw mean line
    go_mean = go.Scatter(
        x=boot_data["rank"],
        y=boot_data["obs"],
        marker=dict(color="red"),
        mode="lines",
        hovertemplate="Effect Size: %{y:.4f}<extra></extra>"
    )
    # Draw lower bound line
    go_lb = go.Scatter(
        x=boot_data["rank"],
        y=boot_data["boot_lb"],
        marker=dict(color="gray"),
        mode="lines",
        line=dict(dash="dot", width=1),
        hovertemplate="Lower Bound: %{y:.4f}<extra></extra>"
    )
    # Draw upper bound line, set fill argument to 'tonexty' to shade area
    # between upper and lower bound
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
    """Plot inferential specification plot.

    Arguments:
        boot_data -- The bootstrap sampling data.
        title -- The analysis title.
        n_total_specs -- The total number of specifications

    Returns:
        Plotly figure.
    """
    # Get figure data
    inferential = _inferential(boot_data)

    # Plot figure
    fig = go.Figure()
    for g_obj in inferential["go"]:
        fig.add_trace(g_obj)
    fig.update_yaxes(**inferential["yaxes_args"])

    # Update layout with common values
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    fig.update_xaxes(
        **common_args["x"], ticks="outside", title="Specification Number")
    fig.update_layout(common_args["layout"], width=1000, height=300)

    return fig


def _p_hist(specs):
    """Get p-value histogram figure data.

    Arguments:
        specs -- The specification data.

    Returns:
        A dictionary with figure data.
    """
    # Histogram
    # 20 bins ensures that first bin covers all significant values
    go_hist = go.Histogram(
        x=specs["p"],
        nbinsx=20,
        histnorm="probability",
        marker=dict(line=dict(width=2, color="black")),
        hovertemplate="Proportion: %{x:.2f}<extra></extra>"
    )
    # Change color of first bin (significant values)
    colors = ["lightgray"]
    colors.extend(["gray"] * 19)
    go_hist.marker.color = colors

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
    """Plot p-value histogram.

    Arguments:
        specs -- The specification data.
        title -- The analysis title.
        n_total_specs -- The total number of specifications.

    Returns:
        Plotly figure
    """
    # Get figure data
    p_hist = _p_hist(specs)

    # Plot figure
    fig = go.Figure()
    fig.add_trace(p_hist["go"])
    fig.update_yaxes(**p_hist["yaxes_args"])

    # Update layout with common values
    common_args = _get_common_args(n_total_specs, title)
    fig.update_yaxes(**common_args["y"])
    del common_args["x"]["range"]
    fig.update_xaxes(
        **common_args["x"], ticks="outside", title="Specification p-Values")
    fig.update_layout(common_args["layout"], width=300, height=500)

    return fig
