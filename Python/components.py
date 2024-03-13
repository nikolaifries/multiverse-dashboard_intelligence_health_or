from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import numpy as np
from plotting import plot_treemap, plot_inferential, plot_p_hist


def get_header():
    return dbc.Row([
        dbc.Col(dcc.Markdown(id="outHeaderTitle",
                children="# Meta-Analysis"), width=4),
        dbc.Col(dcc.Markdown(id="outHeaderLevel", children=""),
                width={"size": 2, "offset": 3}),
        dbc.Col(dcc.Upload(
            id="inUpload",
            children=html.Div([
                "Drag and Drop or ",
                html.A("Select Files")
            ]),
            multiple=True,
            className="upload"
        ), width=2),
        dbc.Col(
            dcc.Markdown(id="outUpload", children=""), width=1),
    ], className="header")


def get_data_tab(config, data):
    colmap = config["colmap"]
    key_c_id = colmap["key_c_id"]
    title = config["title"]
    return dbc.Col([
        dbc.Row([
            dbc.Col(html.H2("Dataset"), width=6),
            dbc.Col(dbc.Row([
                dbc.Col(html.H2("Treemap"), width=6)
            ], justify="between"), width=6),
        ]),
        dbc.Row([
            dbc.Col(id="outDatatable", children=get_datatable(
                data, key_c_id), width=6),
            dbc.Col(dcc.Graph(figure=plot_treemap(
                data, title, colmap), id="treemap"), width=6)
        ])
    ])


def get_multiverse_tab(data, factor_lists, kc_range, k_range, n_total_specs, colmap):
    return dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(html.H2("Multiverse Analysis"), width=4),
            ], justify="between"),
            dbc.Row([
                dcc.Graph(figure={}, id="multiverse")
            ]),
        ], width=9),
        dbc.Col([
            get_filter_info_card(),
            get_spec_info_card(),
            get_filter_card(data, factor_lists, kc_range,
                            k_range, n_total_specs, colmap),
        ], width=3, className="sidebar")
    ])


def get_other_tab(boot_data, specs, title, n_total_specs):
    return dbc.Col([
        dbc.Row([
            dbc.Col(html.H2("Inferential Plot"), width=9),
            dbc.Col(html.H2("p-Value Histogram"), width=3),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=plot_inferential(
                boot_data, title, n_total_specs), id="inferential"), width=9),
            dbc.Col(dcc.Graph(figure=plot_p_hist(specs, title,
                    n_total_specs), id="pValueHist"), width=3)
        ])
    ])


def get_datatable(df, key_c_id):
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=_get_datatable_formatting(df),
        page_action="none",
        sort_action="native",
        # fixed_rows={'headers': True},
        style_header={
            'backgroundColor': "dimgray",
            'color': 'white',
            'text-align': 'center',
            "fontWeight": "bold",
            "padding": 10,
        },
        style_cell={
            "border-left": "1px solid black",
            "border-left": "1px solid black",
            "border-top": "2px solid black",
            "border-bottom": "2px solid black",
            "padding": "5px",
            'padding-left': '10px',
            "text-align": "left",
            "fontWeight": 100,
            "minWidth": 100,
        },
        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'right'
            } for c in df.select_dtypes(include=np.number).columns
        ],
        style_table={
            "border": "5px solid black",
            "height": 750,
            "overflowY": "auto",
            "overflowX": "scroll",
            "margin": "10px",
        },
        style_data_conditional=[
            {
                'if': {"filter_query": f"{{c_id}} eq '{c_id}'"},
                'background-color': "lightgray"
            }
            for c_id in df[df[key_c_id] % 2 != 0][key_c_id]]
    )


def _get_datatable_formatting(df):
    columns = []
    for col in df.columns:
        if df[col].dtype == "float64":
            item = dict(id=col, name=col, type="numeric",
                        format=dict(specifier=".4f"),  selectable=True)
            columns.append(item)
        else:
            item = dict(id=col, name=col, selectable=True)
            columns.append(item)

    return columns


def get_filter_info_card():
    return dbc.Col([
        dbc.Card(dbc.CardBody(), className="card-header thin"),
        dbc.Card(dbc.CardBody(dbc.Col([
            dcc.Markdown(id="outSpecPercent", children="", className="mdp"),
            dcc.Markdown(id="outSpecPercentP", children="", className="mdp"),
            dcc.Markdown(id="outSpecPercentESA", children="", className="mdp"),
            dcc.Markdown(id="outSpecPercentESB", children="", className="mdp"),
        ])), className="card-main")
    ])


def get_spec_infos():
    spec_infos = [
        ("Effect Size: ", "es"),
        ("95%-CI: ", "ci"),
        ("Cluster Size: ", "cs"),
        ("Sample Size: ", "ss"),
        ("p-Value: ", "pv"),
        ("Factors: ", "f"),
        ("Studies: ", "st")
    ]
    return spec_infos


def get_spec_info_card():
    spec_infos = get_spec_infos()
    return dbc.Col([
        dbc.Card(dbc.CardBody(html.H4(id="outSpecInfoSN", children="",
                 className="card-title")), className="card-header"),
        dbc.Card(dbc.CardBody([
            *[dbc.Row([
                dbc.Col(dcc.Markdown(k, className="mdp"),
                        width=3, style={"margin": "unset"}),
                dbc.Col(dcc.Markdown(
                    id=f"outSpecInfo{v}", children="-", className="mdp"), width=9)
            ], className="spec-info-card-row") for (k, v) in spec_infos]
        ], className="spec-info"), className="card-main")
    ])


def get_filter_card(data, factor_lists, kc_range, k_range, n_total_specs, colmap):
    return dbc.Col([
        dbc.Card(dbc.CardBody(
            dbc.Row([
                dbc.Col(html.H4("Filters", className="card-title"), width=6),
                dbc.Col(dbc.Row([
                    dbc.Col(dbc.Button(id="inRefresh", children=html.I("Apply",
                        className="bi")), width=5, className="btn-col"),
                    dbc.Col(dbc.Button(id="inReset", children=html.I("Reset",
                        className="bi")), width=5, className="btn-col"),
                ], justify="start"), width=4)
            ], justify="between", className="filter-row")
        ), className="card-header"),
        dbc.Card(dbc.CardBody(
            get_filters(data, factor_lists, kc_range, k_range, n_total_specs, colmap), className="filters"
        ), className="card-main")
    ])


def get_filters(data, factor_lists, kc_range, k_range, n_total_specs, colmap):
    kc_min, kc_max = kc_range
    k_min, k_max = k_range
    key_c = colmap["key_c"]
    key_c_id = colmap["key_c_id"]
    key_e_id = colmap["key_e_id"]
    return [
        dbc.InputGroup([dbc.InputGroupText("Spec. Nr."),
                        dbc.Input(
            id="inSpecNr",
            placeholder="Spec. Nr.",
            type="number",
            min=1,
            max=n_total_specs,
            value=None
        ),
        ]),
        html.Hr(),
        dbc.Label("Confidence Intervals"),
        dbc.Row([
            dbc.Col(dbc.Checklist(
                options=[
                    {"label": "95%-CI", "value": 1},
                ],
                value=[],
                id="inCISwitch",
                switch=True,
            ), width=4),
            dbc.Col(dbc.RadioItems(
                options=[
                    {"label": "below 0", "value": 0, "disabled": True},
                    {"label": "above 0", "value": 1, "disabled": True},
                    {"label": "around 0", "value": 2, "disabled": True},
                ],
                value=0,
                id="inCICases",
            )),
        ]),
        html.Hr(),
        dbc.Label("p-Values"),
        dbc.Row([
            dbc.Col([
                dbc.Checklist(
                    options=[
                        {"label": "p: Markers", "value": 1},
                    ],
                    value=[],
                    id="inPMarkerSwitch",
                    switch=True,
                ),
                dbc.Checklist(
                    options=[
                        {"label": "p: Filter", "value": 1},
                    ],
                    value=[],
                    id="inPFilterSwitch",
                    switch=True,
                ),
            ], width=4),
            dbc.Col(dbc.RadioItems(
                options=[
                    {"label": "p < 0.05", "value": 0.05, "disabled": True},
                    {"label": "p < 0.01", "value": 0.01, "disabled": True},
                    {"label": "p < 0.001", "value": 0.001, "disabled": True}
                ],
                value=0.05,
                id="inPValues",
            )),
        ]),
        html.Hr(),
        dbc.Label("# Clusters", html_for="inRangeKC"),
        dcc.RangeSlider(id="inRangeKC", min=kc_min, max=kc_max, step=1, value=[kc_min, kc_max],
                        marks={**{i: str(i) for i in range(kc_min, kc_max+1, 2)}, kc_max: f"{kc_max}"}),
        html.Hr(),
        dbc.Label("# Samples", html_for="inRangeK"),
        dcc.RangeSlider(id="inRangeK", min=k_min, max=k_max, step=1, value=[k_min, k_max],
                        marks={**{i: str(i) for i in range(k_min, k_max+1, 2)}, k_max: f"{k_max}"}),
        html.Hr(),
        dbc.Label("Effect Sizes"),
        dbc.RadioItems(
            options=[
                {"label": "All Effect Sizes", "value": 0},
                {"label": "Effect Sizes < 0", "value": -1},
                {"label": "Effect Sizes ≥ 0", "value": 1},
            ],
            value=0,
            id="inEffectSizes",
        ),
        html.Hr(),
        dbc.Accordion([dbc.AccordionItem([
            dbc.Col([
                dbc.Row([
                    dbc.Col(dcc.Markdown(
                        id={"type": "outFactor", "index": i}, children=k)),
                    dbc.Col(dbc.Select(
                        factor_lists[k],
                        None,
                        id={"type": "inSelect", "index": i},
                    ))
                ])
                for i, k in enumerate(factor_lists.keys())
            ]),
        ], title="Factor Filters")], start_collapsed=True,),
        html.Hr(),
        dbc.Accordion([dbc.AccordionItem([
            dbc.Button(children=html.I("Select all",
                className="bi"), id="inToggleAll"),
            dbc.Checklist(
                options=[{"label": c, "value": str(c_id)}
                         for c_id, c in [(c_id, data[data[key_c_id] == c_id][key_c].iloc[0]) for c_id in sorted(data[key_c_id].unique())]],
                value=[str(c_id) for c_id in sorted(data[key_c_id].unique())],
                id="inStudyChecklist",
                className="study-checks"
            ),
        ], title="Study ID Filters")], start_collapsed=True,),
        html.Hr(),
        dbc.Accordion([dbc.AccordionItem([
            dbc.Button(children=html.I("Select all",
                className="bi"), id="inToggleAllES"),
            dbc.Checklist(
                options=[{"label": f"ES ID: {e_id}", "value": str(e_id)}
                         for e_id in sorted(data[key_e_id])],
                value=[str(e_id) for e_id in sorted(data[key_e_id])],
                id="inESChecklist",
                className="es-checks"
            ),
        ], title="ES ID Filters")], start_collapsed=True,),
    ]
