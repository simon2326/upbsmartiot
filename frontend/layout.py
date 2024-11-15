from dash import html, dcc
from pages import plant_info, historical_data, predictions

def get_layout():
    return html.Div([
        dcc.Tabs(id="tabs", children=[
            dcc.Tab(label='Información de la Planta', children=plant_info.layout, className="tab-content"),
            dcc.Tab(label='Datos Históricos', children=historical_data.layout, className="tab-content"),
            dcc.Tab(label='Predicciones', children=predictions.layout, className="tab-content")
        ], className="tabs-container")
    ], className="app-container")

