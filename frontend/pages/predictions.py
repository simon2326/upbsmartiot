from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc  # Asegúrate de importar dbc
import plotly.graph_objs as go
from db_utils import get_predictions  # Cambia el import para usar db_utils


layout = html.Div([
    html.H3("Predicciones de Temperatura y Humedad para las Próximas 24 Horas", className="text-center mt-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="pred-temp-graph"), width=6),
        dbc.Col(dcc.Graph(id="pred-humidity-graph"), width=6),
    ]),
    html.Div(id='recommendations', className="text-center mt-4")
])

@callback(
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
