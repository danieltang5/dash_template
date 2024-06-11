# Import packages
import re
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from bs4 import BeautifulSoup
import os

from capture import Capture

class FuelMixDownloader(Capture):
    def __init__(self, max_retries=3):
        super().__init__(max_retries=max_retries)
        self.download_dir = "ercot_fuel_mix_reports"
        self.url = "https://www.ercot.com/gridinfo/generation"

    def run(self):
        os.makedirs(self.download_dir, exist_ok=True)
        response = self.session.get(self.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all(
            "a", href=True, title=lambda title: title and "Fuel Mix Report" in title
        )
        for link in links:
            full_url = link["href"]
            if not full_url.startswith("http"):
                full_url = "https://www.ercot.com" + full_url
            self.download_file(full_url)


# Example usage
# downloader = FuelMixDownloader(max_retries=5)
# downloader.run()


class ExcelProcessor:
    def __init__(self, download_dir):
        self.download_dir = download_dir

    def process_excel_file(self, filename):
        print(f"Processing file: {filename}")
        year = int(re.search(r"(\d{4})", filename).group(1))
        file_path = os.path.join(self.download_dir, filename)
        df = pd.read_excel(file_path, sheet_name="Summary", skiprows=7).dropna(
            how="all"
        )
        df = df.dropna(how="all", subset=df.columns[1:])
        df.columns = df.columns.str.replace("*", "", regex=False)
        df["Year"] = year
        # print(df.head())
        return df

    def process_excel_files(self):
        df = pd.concat(
            self.process_excel_file(filename)
            for filename in os.listdir(self.download_dir)
            if filename.endswith(".xlsx")
        )
        # print(df.head())
        return df


# Example usage
processor = ExcelProcessor(download_dir="ercot_fuel_mix_reports")
df = processor.process_excel_files()

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
# Initialize the app
app = Dash(external_stylesheets=external_stylesheets)
years = df["Year"].unique().tolist()
months = df.columns.drop(["Year", "Energy, GWh"]).tolist()

# App layout
app.layout = [
    html.Div(
        className="row",
        children="ERCOT Generation Fuel Mix",
        style={"textAlign": "center", "color": "blue", "fontSize": 30},
    ),
    html.Hr(),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="row",
                children=[
                    html.H3("Select Year:"),
                    dcc.RadioItems(
                        options=years,
                        value=max(years),
                        id="controls-and-radio-item-year",
                        inline=True,
                    ),
                ],
                style={"margin-bottom": "20px"},
            ),
            html.Div(
                className="row",
                children=[
                    html.H3("Select Month:"),
                    dcc.RadioItems(
                        options=months,
                        value=months[-1],
                        id="controls-and-radio-item-month",
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
                        data=[],
                        page_size=30,
                        style_table={"overflowX": "auto"},
                        id= "controls-and-table"
                    )
                ],
            ),
            html.Div(
                className="six columns",
                children=[dcc.Graph(figure={}, id="controls-and-graph")],
            ),
        ],
    ),
    dcc.Store(id='stored-data', data=df.to_dict("records"))
]


@callback(
    Output(component_id="controls-and-table", component_property="data"),
    Output(component_id="controls-and-graph", component_property="figure"),
    Input(component_id="controls-and-radio-item-year", component_property="value"),
    Input(component_id="controls-and-radio-item-month", component_property="value"),
    Input(component_id='stored-data', component_property='data')
)
def update_graph(year, month, data):
    fm_df = pd.DataFrame(data)
    fm_df = fm_df[fm_df["Year"] == year]
    fm_df = fm_df[["Energy, GWh", month]]
    fm_df = fm_df[fm_df["Energy, GWh"] != "Total"]
    fig = px.pie(fm_df, names="Energy, GWh", values=month, title=f"ERCOT Fuel Mix for {year} - {month}")
    return fm_df.to_dict("records"), fig
# Run the app
if __name__ == "__main__":
    app.run(debug=True)

