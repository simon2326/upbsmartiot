from dash import html, dcc, callback, Input, Output
import pandas as pd
import plotly.graph_objs as go
from db_utils import get_data_from_postgres

layout = html.Div([
    html.H3("Recomendaciones de Cuidado para la Planta", className="text-center mt-4"),
    html.Div(id="recommendations-content", className="recommendations-text"),
    
    # Gráficos de promedio y último dato
    html.Div([
        html.Div([
            html.H4("Temperatura Promedio", className="graph-title"),
            dcc.Graph(id="avg-temp-graph")
        ], className="graph-container"),
        
        html.Div([
            html.H4("Humedad Promedio", className="graph-title"),
            dcc.Graph(id="avg-humidity-graph")
        ], className="graph-container"),
        
        html.Div([
            html.H4("Última Temperatura Registrada", className="graph-title"),
            dcc.Graph(id="last-temp-graph")
        ], className="graph-container"),
        
        html.Div([
            html.H4("Última Humedad Registrada", className="graph-title"),
            dcc.Graph(id="last-humidity-graph")
        ], className="graph-container"),
    ], className="graphs-wrapper")
])

@callback(
    [Output("recommendations-content", "children"),
     Output("avg-temp-graph", "figure"),
     Output("avg-humidity-graph", "figure"),
     Output("last-temp-graph", "figure"),
     Output("last-humidity-graph", "figure")],
    [Input("date-picker", "date")]
)
def update_recommendations(date):
    # Obtener datos de temperatura y humedad
    temperature_data = get_data_from_postgres("temperature")
    humidity_data = get_data_from_postgres("humidity")
    
    # Filtrar datos por fecha seleccionada
    date = pd.to_datetime(date)
    temperature_data = temperature_data[temperature_data['timestamp'].dt.date == date.date()]
    humidity_data = humidity_data[humidity_data['timestamp'].dt.date == date.date()]

    # Verificar si hay datos
    if temperature_data.empty or humidity_data.empty:
        return ("No hay datos disponibles para generar recomendaciones.", 
                go.Figure(), go.Figure(), go.Figure(), go.Figure())

    # Calcular recomendaciones en función de los datos de temperatura y humedad
    max_temp = temperature_data['temperature'].max()
    min_temp = temperature_data['temperature'].min()
    avg_temp = temperature_data['temperature'].mean()
    avg_humidity = humidity_data['humidity'].mean()
    last_temp = temperature_data['temperature'].iloc[-1]
    last_humidity = humidity_data['humidity'].iloc[-1]

    recommendations = []
    # Recomendaciones basadas en requisitos específicos de temperatura y humedad
    if max_temp > 28:
        if avg_humidity > 70:
            recommendations.append(html.B("La planta está en riesgo de hongos debido a la alta humedad. Reduzca el riego."))
        elif avg_humidity < 50:
            recommendations.append(html.B("La planta está en riesgo de estrés por falta de agua debido a la baja humedad. Aumente el riego."))
    elif min_temp < 10:
        if avg_humidity > 50:
            recommendations.append(html.B("La planta está en riesgo de quemadura por frío debido a la alta humedad. Reduzca la humedad y proporcione una fuente de calor."))
        elif avg_humidity < 10:
            recommendations.append(html.B("La planta está en riesgo de destrucción de tejidos celulares por el frío y la baja humedad. Proporcione una fuente de calor y aumente la humedad."))

    # Adicional: estado general basado en promedio de humedad
    if avg_humidity < 20:
        recommendations.append(html.B("La planta necesita agua urgentemente."))
    elif avg_humidity > 80:
        recommendations.append(html.B("La planta tiene exceso de humedad; reducir riego."))

    # Crear los gráficos
    avg_temp_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_temp,
        title={"text": "Temperatura Promedio (°C)"},
        gauge={"axis": {"range": [0, 50], "tickwidth": 1, "tickcolor": "#6c9a8b"}}
    ))

    avg_humidity_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_humidity,
        title={"text": "Humedad Promedio (%)"},
        gauge={"axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#6c9a8b"}}
    ))

    last_temp_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=last_temp,
        title={"text": "Última Temperatura (°C)"},
        gauge={"axis": {"range": [0, 50], "tickwidth": 1, "tickcolor": "#6c9a8b"}}
    ))

    last_humidity_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=last_humidity,
        title={"text": "Última Humedad (%)"},
        gauge={"axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#6c9a8b"}}
    ))

    # Retornar recomendaciones y gráficos
    return (
        html.Ul([html.Li(rec) for rec in recommendations]) if recommendations else "La planta está en condiciones óptimas.",
        avg_temp_fig, avg_humidity_fig, last_temp_fig, last_humidity_fig
    )
