import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta
import psycopg2
from sqlalchemy import create_engine

# Configuración de conexión a PostgreSQL
POSTGRES_HOST = "middleware-db"
POSTGRES_PORT = "5432"
POSTGRES_DB = "iotplant"
POSTGRES_USER = "simon"
POSTGRES_PASSWORD = "simon123"

# Conexión a PostgreSQL usando SQLAlchemy
engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

# Inicializar la aplicación Dash con Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Planta - Suculenta Echeveria Pulvinata"

# Función para obtener datos de temperatura y humedad
def get_data_from_postgres(table, limit=1000):
    query = f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT {limit}"
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    print(data.head())  # Imprime los primeros registros para verificar
    return data

# Función para obtener datos de predicción
def get_predictions():
    return get_data_from_postgres("prediction", limit=24)

# Layout de la aplicación
app.layout = dbc.Container([
    html.H1("Dashboard Planta - Suculenta Echeveria Pulvinata", className="text-center mt-4 mb-4"),

    # Tabs para las tres secciones
    dbc.Tabs([
        # Pestaña 1: Información de la planta
        dbc.Tab(label="Información de la Planta", children=[
            html.H3("Información de la Planta - Suculenta Echeveria Pulvinata", className="text-center mt-4"),
            dbc.Row([
                dbc.Col(html.Img(src="/assets/suculenta.jpg", style={"width": "100%", "max-width": "400px"}), width=4),
                dbc.Col([
                    html.H5("Origen: "),
                    html.P("La Suculenta Echeveria Pulvinata es originaria de zonas áridas de México."),
                    html.H5("Cuidados:"),
                    html.P("Prefiere luz indirecta, riego moderado solo cuando el sustrato esté seco."),
                    html.H5("Recomendaciones especiales:"),
                    html.P("Mantener en temperaturas entre 15°C y 25°C, evita exceso de humedad en sus hojas.")
                ])
            ], justify="center")
        ]),

        # Pestaña 2: Visualización de Datos
        dbc.Tab(label="Visualización de Datos", children=[
            html.H3("Últimos Datos de Temperatura y Humedad", className="text-center mt-4"),
            dcc.DatePickerSingle(
                id='date-picker',
                date=datetime.now().date(),
                display_format='YYYY-MM-DD'
            ),
            dbc.Row([
                dbc.Col(dcc.Graph(id="temp-graph"), width=6),
                dbc.Col(dcc.Graph(id="humidity-graph"), width=6),
            ], justify="center"),
            dbc.Row([
                html.H4("Datos de Posición en el Mapa"),
                dcc.Graph(id="map-graph")
            ], justify="center")
        ]),

        # Pestaña 3: Predicciones
        dbc.Tab(label="Predicciones", children=[
            html.H3("Predicciones de Temperatura y Humedad para las Próximas 24 Horas", className="text-center mt-4"),
            dbc.Row([
                dbc.Col(dcc.Graph(id="pred-temp-graph"), width=6),
                dbc.Col(dcc.Graph(id="pred-humidity-graph"), width=6),
            ], justify="center"),
            html.Div(id='recommendations', className="text-center mt-4")
        ]),
    ])
], fluid=True)

# Callback para actualizar los gráficos de la pestaña de visualización de datos
@app.callback(
    [Output("temp-graph", "figure"),
     Output("humidity-graph", "figure"),
     Output("map-graph", "figure")],
    [Input("date-picker", "date")]
)
def update_visualization(date):
    date = pd.to_datetime(date)
    
    # Obtener datos de temperatura y humedad
    temperature_data = get_data_from_postgres("temperature")
    humidity_data = get_data_from_postgres("humidity")
    position_data = get_data_from_postgres("position")

    # Filtrar datos por fecha
    temperature_data = temperature_data[temperature_data['timestamp'].dt.date == date.date()]
    humidity_data = humidity_data[humidity_data['timestamp'].dt.date == date.date()]
    position_data = position_data[position_data['timestamp'].dt.date == date.date()]

    # Gráfico de temperatura
    temp_fig = go.Figure(go.Scatter(x=temperature_data['timestamp'], y=temperature_data['temperature'], mode='lines+markers'))
    temp_fig.update_layout(title="Temperatura (°C)", xaxis_title="Hora", yaxis_title="Temperatura")

    # Gráfico de humedad
    humidity_fig = go.Figure(go.Scatter(x=humidity_data['timestamp'], y=humidity_data['humidity'], mode='lines+markers'))
    humidity_fig.update_layout(title="Humedad (%)", xaxis_title="Hora", yaxis_title="Humedad")

    # Mapa de posición
    map_fig = go.Figure(go.Scattermapbox(
        lat=position_data['lat'], lon=position_data['lon'],
        mode='markers', marker=go.scattermapbox.Marker(size=14),
        text=position_data['timestamp'].astype(str)
    ))
    map_fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=10,
        mapbox_center={"lat": position_data['lat'].mean(), "lon": position_data['lon'].mean()},
        title="Posición"
    )

    return temp_fig, humidity_fig, map_fig

# Callback para actualizar los gráficos de predicciones y recomendaciones
@app.callback(
    [Output("pred-temp-graph", "figure"),
     Output("pred-humidity-graph", "figure"),
     Output("recommendations", "children")],
    [Input("date-picker", "date")]
)
def update_predictions(date):
    prediction_data = get_predictions()

    # Gráfico de predicción de temperatura
    pred_temp_fig = go.Figure(go.Scatter(x=prediction_data['timestamp'], y=prediction_data['temperature_prediction'], mode='lines+markers'))
    pred_temp_fig.update_layout(title="Predicción de Temperatura (°C)", xaxis_title="Hora", yaxis_title="Temperatura")

    # Gráfico de predicción de humedad
    pred_humidity_fig = go.Figure(go.Scatter(x=prediction_data['timestamp'], y=prediction_data['humidity_prediction'], mode='lines+markers'))
    pred_humidity_fig.update_layout(title="Predicción de Humedad (%)", xaxis_title="Hora", yaxis_title="Humedad")

    # Generar recomendaciones
    max_temp = prediction_data['temperature_prediction'].max()
    min_temp = prediction_data['temperature_prediction'].min()
    avg_humidity = prediction_data['humidity_prediction'].mean()

    recommendations = "Recomendaciones: "
    if max_temp > 28 and (avg_humidity < 50 or avg_humidity > 70):
        recommendations += "Ajustar humedad para evitar estrés por exceso de temperatura. "
    if min_temp < 10 and (avg_humidity < 10 or avg_humidity > 50):
        recommendations += "Proteger la planta del frío y ajustar humedad para evitar daño por bajas temperaturas."

    return pred_temp_fig, pred_humidity_fig, recommendations

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8050)
