# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

# Incorporate data
df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
)
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
# Initialize the app
app = Dash(external_stylesheets=external_stylesheets)


# App layout
app.layout = [
    html.Div(
        className="row",
        children="Dash App Template with Data, Graph, and Controls",
        style={"textAlign": "center", "color": "blue", "fontSize": 30},
    ),
    html.Hr(),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="row",
                children=[
                    html.H3("Select X-axis:"),
                    dcc.RadioItems(
                        options=["continent", "country"],
                        value="continent",
                        id="controls-and-radio-item-x",
                        inline=True,
                    ),
                ],
                style={"margin-bottom": "20px"},
            ),
            html.Div(
                className="row",
                children=[
                    html.H3("Select Y-axis:"),
                    dcc.RadioItems(
                        options=["pop", "lifeExp", "gdpPercap"],
                        value="lifeExp",
                        id="controls-and-radio-item-y",
                        inline=True,
                    ),
                ],
                style={"margin-bottom": "20px"},
            ),
        ],
    ),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="six columns",
                children=[
                    dash_table.DataTable(
                        data=df.to_dict("records"),
                        page_size=11,
                        style_table={"overflowX": "auto"},
                    )
                ],
            ),
            html.Div(
                className="six columns",
                children=[dcc.Graph(figure={}, id="controls-and-graph")],
            ),
        ],
    ),
]


# Add controls to build the interaction
@callback(
    Output(component_id="controls-and-graph", component_property="figure"),
    Input(component_id="controls-and-radio-item-x", component_property="value"),
    Input(component_id="controls-and-radio-item-y", component_property="value"),
)
def update_graph(x_col_chosen, y_col_chosen):
    fig = px.histogram(df, x=x_col_chosen, y=y_col_chosen, histfunc="avg")
    return fig


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
