#!/usr/bin/env python
# Using one of the example in https://dash.plotly.com/sharing-data-between-callbacks
# as a base.
#
# Now we are adding an upload button https://dash.plotly.com/dash-core-components/upload
# and make sure that the dataframe we got is convert to dict, so
# we can store it in the browser using JSON format.
#
# During the parsing, we are also creating options for the dropdown button.
#
# And now we add a callback for the dropdown. It will use the value to
# retrive the correct dictionary and recreate the DataFrame.
#
# We will then plot the figure and return it back for the update
# of a `dcc.Graph`.
import base64
import os
import io
import copy
import time
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State


external_stylesheets = [
    # Dash CSS
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    # Loading screen CSS
    "https://codepen.io/chriddyp/pen/brPBPO.css",
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


app.layout = html.Div(
    [
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Allow multiple files to be uploaded
            multiple=True,
        ),
        dcc.Dropdown(
            id="dropdown",
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
        dcc.Store(id="uploaded-data"),
        dcc.Store(id="sheet-list"),
    ]
)


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        dfs = pd.read_excel(io.BytesIO(decoded), sheet_name=None)
        return dfs, None
    except Exception as e:
        print(e)
        return None, html.Div(["There was an error processing this file."])


@app.callback(
    Output("uploaded-data", "data"),
    Output("dropdown", "options"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        zipped_data = zip(list_of_contents, list_of_names, list_of_dates)
        # Only consider one file.
        c, n, d = next(zipped_data)
        dfs, element = parse_contents(c, n, d)
        if dfs is not None:
            # Extract list of sheet names.
            sheet_names = dfs.keys()
            options = []
            for name in sheet_names:
                options.append({"label": name, "value": name})

            # Process each sheet into dict.
            dicts = {}
            for sheet_name, df in dfs.items():
                dicts[sheet_name] = df.to_dict()
            return dicts, options
    return None, []


@app.callback(
    Output("graph-1", "figure"),
    Input("dropdown", "value"),
    State("uploaded-data", "data"),
    prevent_initial_call=True,
)
def generate_graph(value, dfs):
    # Get the correct dataframe.
    if dfs is not None:
        df_dict = dfs[value]
        df = pd.DataFrame.from_dict(df_dict)
        fig = px.line(df, x="x", y="y")
        return fig


if __name__ == "__main__":
    app.run_server(debug=True)
