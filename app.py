#!/usr/bin/env python
# coding: utf-8

# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import pandas as pd
import plotly.graph_objs as go
import base64
import io
import dash_bootstrap_components as dbc
import os


# Initialize the app
app = Dash(__name__,external_stylesheets=[dbc.themes.LITERA],suppress_callback_exceptions=True)
server = app.server
port = int(os.environ.get("PORT", 5000))
# Barre de navigation supérieure : choix du logo à gauche, de la couleur de fond, et des 4 menus
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink(
                "Sankey chart tool",
                href="/Sankey-chart-tool",
                style={"color": "white", "font-weight": "bold",
                       "font-family": "Poppins Medium"},
            )
        )
    ],
    
    brand_href="/Sankey chart tool", # cliquer sur le logo Pickme renvoie vers la page Sales Tools
    color="#F76B73", # couleur de la barre de navigation
    dark=True,
)

# App layout
app.layout = html.Div([

    navbar,
    html.Br(),
    # Title of the dash
    html.H1(children='Sankey Chart App', style={'textAlign': 'center'}),
    html.Br(),
    
    # Field for uploading Excel file
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px auto'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    
    # Text above the data table
    html.Div(children='Tableau de données'),

    # Display a data table
    dash_table.DataTable(id='data-table', page_size=5),
    
    # Dropdown menus
    html.Div(id="dropdowns"),
    
    html.Br(),
    # Display a button
    dbc.Button('Générer le graph', id='submit-val', n_clicks=0),
    html.Br(),
    html.Br(),
    
    html.Div(children='Sankey chart :'),
    # Display a graph
    dcc.Graph(
        id='example-graph',
        figure={}
    ), 
])

# Read uploaded Excel file and update DataFrame
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # Check if the file is a CSV or Excel file
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename or 'xlsx' in filename:
        # Assume that the user uploaded an Excel file
        df = pd.read_excel(io.BytesIO(decoded), index_col=0)
    else:
        raise ValueError('Unsupported file format')
    return df

# Define function to generate Sankey graph
def generate_graph(df, column_level_1, column_level_2, column_level_3, column_values):
    # Dataframe creation
    df_sankey = pd.DataFrame(columns=['source', 'target', 'value'])
    lab0 = ['Total']

    # Creation of the first step attributes (count & list)
    Niveau_1_values = df.groupby(column_level_1)[column_values].sum()
    Listing_labels_Niveau_1 = Niveau_1_values.index.drop_duplicates()
    lab1 = Listing_labels_Niveau_1.to_list()
    Nb_Distinct_Niveau_1 = df[column_level_1].nunique()

    # Creation of the second step attributes (count & list)
    Listing_labels_Niveau_2 = df[column_level_2].drop_duplicates()
    lab2 = Listing_labels_Niveau_2.to_list()
    Listing_labels_Niveau_2 = Listing_labels_Niveau_2.reset_index()
    Niveau_2_values = df.groupby([column_level_1, column_level_2])[column_values].sum().reset_index()
    Nb_Distinct_Niveau_2 = df[column_level_2].nunique()

    # Creation of the third step attributes (count & list)
    Listing_labels_Niveau_3 = df[column_level_3].drop_duplicates()
    lab3 = Listing_labels_Niveau_3.to_list()
    Listing_labels_Niveau_3 = Listing_labels_Niveau_3.reset_index()
    Niveau_3_values = df.groupby([column_level_3, column_level_1, column_level_2])[column_values].sum().reset_index()
    Nb_Distinct_Niveau_3 = df[column_level_3].nunique()

    # Label attibution to each steps
    lab = lab0 + lab1 + lab2 + lab3

    # Colors attibution to each steps
    colors = ["rgba(214, 39, 40, 0.8)"]
    for a in range(0, len(lab1)):
        colors = colors + ["rgba(31, 119, 180, 0.8)"]
    for b in range(0, len(lab2)):
        colors = colors + ["rgba(255, 127, 14, 0.8)"]
    for c in range(0, len(lab3)):
        colors = colors + ["rgba(44, 160, 44, 0.8)"]

    # Initialize an empty list to hold the rows
    rows_to_append = []

    # Flows calculation
    for x in range(0, Nb_Distinct_Niveau_1):
        new_row = [0, x + 1, Niveau_1_values[x]]
        rows_to_append.append(new_row)
        for y in range(0, Nb_Distinct_Niveau_2):
            new_row = [x + 1, y + Nb_Distinct_Niveau_1 + 1, Niveau_2_values[(Niveau_2_values[column_level_2] == Listing_labels_Niveau_2[column_level_2][y]) & (Niveau_2_values[column_level_1] == Niveau_1_values.index[x])][column_values].sum()]
            rows_to_append.append(new_row)

    for z in range(0, Nb_Distinct_Niveau_3):
        for w in range(0, Nb_Distinct_Niveau_2):
            new_row = [w + Nb_Distinct_Niveau_1 + 1, z + Nb_Distinct_Niveau_2 + Nb_Distinct_Niveau_1 + 1, df[(df[column_level_2] == Listing_labels_Niveau_2[column_level_2][w]) & (df[column_level_3] == Listing_labels_Niveau_3[column_level_3][z])][column_values].sum()]
            rows_to_append.append(new_row)

    # Convert the list of rows to a DataFrame
    df_to_append = pd.DataFrame(rows_to_append, columns=['source', 'target', 'value'])

    # Concatenate the new DataFrame with df_sankey
    df_sankey = pd.concat([df_sankey, df_to_append], ignore_index=True)

    df_sankey = df_sankey.sort_values(['source', 'target'])

    df_sankey = df_sankey[df_sankey['value'] != 0]

    # Load data from Excel file
    data_excel = df_sankey

    # Create Sankey diagram with Excel file data
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=350,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=lab,  # Use the 'label' column for labels
            color=colors  # Use the 'color' column for colors
        ),
        link=dict(
            source=data_excel['source'],
            target=data_excel['target'],
            value=data_excel['value']
        ))])

    fig.update_layout(title_text="Sankey Chart", font_size=10, width=2000, height=1000)

    return fig

# Define function to update data and dropdown menus
@app.callback(
    [Output('data-table', 'data'),
     Output('dropdowns', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_data(contents, filename):
    if contents is None:
        return [], []

    df = parse_contents(contents, filename)
    if df is None:
        return [], []

    # Convert DataFrame to dict for dash_table.DataTable
    data = df.to_dict('records')

    # Filter columns containing numeric data
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

    # Update dropdown menus with column names containing numeric data
    dropdowns = [
        html.Div([
            html.Label("Niveau 1: "),
            dcc.Dropdown(
                options=[{'label': col, 'value': col} for col in df.columns],
                value=df.columns[0],
                id='column_level_1'
            ),
        ], style={'width': '21%', 'display': 'inline-block', 'margin-left': '40px','margin-right': '40px'}),
        
        html.Div([
            html.Label("Niveau 2: "),
            dcc.Dropdown(
                options=[{'label': col, 'value': col} for col in df.columns],
                value=df.columns[1],
                id='column_level_2'
            ),
        ], style={'width': '21%', 'display': 'inline-block', 'margin-right': '40px'}),
        
        html.Div([
            html.Label("Niveau 3: "),
            dcc.Dropdown(
                options=[{'label': col, 'value': col} for col in df.columns],
                value=df.columns[2],
                id='column_level_3'
            ),
        ], style={'width': '21%', 'display': 'inline-block', 'margin-right': '40px'}),
        
        html.Div([
            html.Label("Tickets : "),
            dcc.Dropdown(
                options=[{'label': col, 'value': col} for col in numeric_columns],
                value=numeric_columns[0] if numeric_columns else None,  # Select the first numeric column by default if available
                id='column_values'
            ),
        ], style={'width': '21%', 'display': 'inline-block'}),
    ]

    return data, dropdowns

# Define function to generate graph
@app.callback(
    Output('example-graph', 'figure'),
    [Input('submit-val', 'n_clicks')],
    [State('data-table', 'data'),
     State('column_level_1', 'value'),
     State('column_level_2', 'value'),
     State('column_level_3', 'value'),
     State('column_values', 'value')]
)
def update_graph(n_clicks, data, column_level_1, column_level_2, column_level_3, column_values):
    if n_clicks > 0:
        df = pd.DataFrame(data)
        return generate_graph(df, column_level_1, column_level_2, column_level_3, column_values)
    else:
        # Return an empty figure if the button has not been clicked
        return {}

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

