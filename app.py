#!/usr/bin/env python
# Using one of the example in https://dash.plotly.com/sharing-data-between-callbacks
# as a base.

import os
import copy
import time
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output


external_stylesheets = [
    # Dash CSS
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    # Loading screen CSS
    "https://codepen.io/chriddyp/pen/brPBPO.css",
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

N = 100

df = pd.DataFrame(
    {
        "category": (
            (["apples"] * 5 * N)
            + (["oranges"] * 10 * N)
            + (["figs"] * 20 * N)
            + (["pineapples"] * 15 * N)
        )
    }
)
df["x"] = np.random.randn(len(df["category"]))
df["y"] = np.random.randn(len(df["category"]))

app.layout = html.Div(
    [
        dcc.Dropdown(
            id="dropdown",
            options=[{"label": i, "value": i} for i in df["category"].unique()],
            value="apples",
        ),
        html.Div(
            [
                html.Div(dcc.Graph(id="graph-1"), className="six columns"),
                html.Div(dcc.Graph(id="graph-2"), className="six columns"),
            ],
            className="row",
        ),
        html.Div(
            [
                html.Div(dcc.Graph(id="graph-3"), className="six columns"),
                html.Div(dcc.Graph(id="graph-4"), className="six columns"),
            ],
            className="row",
        ),
        # signal value to trigger callbacks
        dcc.Store(id="signal"),
    ]
)


def global_store(value):
    # simulate expensive query
    print("Computing value with {}".format(value))
    time.sleep(5)
    return df[df["category"] == value]


def generate_figure(value, figure):
    fig = copy.deepcopy(figure)
    filtered_dataframe = global_store(value)
    fig["data"][0]["x"] = filtered_dataframe["x"]
    fig["data"][0]["y"] = filtered_dataframe["y"]
    fig["layout"] = {"margin": {"l": 20, "r": 10, "b": 20, "t": 10}}
    return fig


@app.callback(Output("signal", "data"), Input("dropdown", "value"))
def compute_value(value):
    # compute value and send a signal when done
    global_store(value)
    return value


@app.callback(Output("graph-1", "figure"), Input("signal", "data"))
def update_graph_1(value):
    # generate_figure gets data from `global_store`.
    # the data in `global_store` has already been computed
    # by the `compute_value` callback and the result is stored
    # in the global redis cached
    return generate_figure(
        value,
        {
            "data": [
                {
                    "type": "scatter",
                    "mode": "markers",
                    "marker": {
                        "opacity": 0.5,
                        "size": 14,
                        "line": {"border": "thin darkgrey solid"},
                    },
                }
            ]
        },
    )


@app.callback(Output("graph-2", "figure"), Input("signal", "data"))
def update_graph_2(value):
    return generate_figure(
        value,
        {
            "data": [
                {
                    "type": "scatter",
                    "mode": "lines",
                    "line": {"shape": "spline", "width": 0.5},
                }
            ]
        },
    )


@app.callback(Output("graph-3", "figure"), Input("signal", "data"))
def update_graph_3(value):
    return generate_figure(
        value,
        {
            "data": [
                {
                    "type": "histogram2d",
                }
            ]
        },
    )


@app.callback(Output("graph-4", "figure"), Input("signal", "data"))
def update_graph_4(value):
    return generate_figure(
        value,
        {
            "data": [
                {
                    "type": "histogram2dcontour",
                }
            ]
        },
    )


if __name__ == "__main__":
    app.run_server(debug=True)
