#!/usr/bin/env python
# coding: utf-8

# Import packages
from dash import Dash, html, dash_table, dcc, Output, Input, State
import pandas as pd
import plotly.graph_objs as go
import base64
import io
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])
server = app.server
# Navbar setup
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Sankey Chart Tool", href="#", style={"color": "white", "font-weight": "bold", "font-family": "Poppins Medium"}))
    ],
    brand="Sankey Chart Tool",
    color="#F76B73",
    dark=True,
)

# App layout
app.layout = html.Div([
    navbar,
    html.Br(),
    html.H1('Sankey Chart Generator', style={'textAlign': 'center'}),
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed',
            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
        },
        multiple=False
    ),
    dcc.Store(id='stored-data'),
    html.Div(id='output-data-upload'),
    dbc.Button('Generate Sankey Chart', id='generate-chart', n_clicks=0, className="mb-3", style={'margin': '10px'}),
    dcc.Graph(id='sankey-chart'),
])

# Parse uploaded data
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename or 'xlsx' in filename:
            # Assume that the user uploaded an Excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])
    return df

# Callback to store uploaded data
@app.callback(Output('stored-data', 'data'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(contents, filename):
    if contents is not None:
        df = parse_contents(contents, filename)
        return df.to_dict('records')
    else:
        return []

# Callback for generating and displaying the Sankey chart
@app.callback(
    Output('sankey-chart', 'figure'),
    [Input('generate-chart', 'n_clicks')],
    [State('stored-data', 'data')]
)
def display_sankey(n_clicks, data):
    if n_clicks < 1 or data is None:
        raise PreventUpdate
    df = pd.DataFrame(data)
    # Here, you would call your function to generate the Sankey chart
    # For demonstration, I'm generating a simple figure. Replace this with your generate_graph function
    figure = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["A1", "A2", "B1", "B2", "C1", "C2"],
            color="blue"
        ),
        link=dict(
            source=[0, 1, 0, 2, 3, 3],  # indices correspond to labels, eg A1, A2, A1, B1, ...
            target=[2, 3, 3, 4, 4, 5],
            value=[8, 4, 2, 8, 4, 2]
        )))
    figure.update_layout(title_text="Sankey Chart Example", font_size=10)
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
