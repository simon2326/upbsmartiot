from dash import html, dcc, callback, Input, Output
import plotly.graph_objs as go
import pandas as pd
from db_utils import get_data_from_postgres  # Cambia el import para usar db_utils


layout = html.Div([
    html.H3("Últimos Datos de Temperatura y Humedad", className="text-center mt-4"),
    dcc.DatePickerSingle(
        id='date-picker',
        date=pd.to_datetime("today").date(),
        display_format='YYYY-MM-DD'
    ),
    dcc.Tabs([
        dcc.Tab(label='Temperatura', children=dcc.Graph(id="temp-graph")),
        dcc.Tab(label='Humedad', children=dcc.Graph(id="humidity-graph")),
        dcc.Tab(label='Posición', children=dcc.Graph(id="map-graph"))
    ])
])

@callback(
    [Output("temp-graph", "figure"),
     Output("humidity-graph", "figure"),
     Output("map-graph", "figure")],
    [Input("date-picker", "date")]
)
def update_visualization(date):
    date = pd.to_datetime(date)
    
    # Obtener datos
    temperature_data = get_data_from_postgres("temperature")
    humidity_data = get_data_from_postgres("humidity")
    position_data = get_data_from_postgres("position")
    
    # Crear figuras vacías en caso de error
    empty_fig = go.Figure()
    empty_fig.update_layout(title="No hay datos disponibles")
    
    # Verificar si hay datos
    if temperature_data.empty or humidity_data.empty or position_data.empty:
        return empty_fig, empty_fig, empty_fig
    
    # Filtrar datos por fecha
    temperature_data = temperature_data[temperature_data['timestamp'].dt.date == date.date()]
    humidity_data = humidity_data[humidity_data['timestamp'].dt.date == date.date()]
    position_data = position_data[position_data['timestamp'].dt.date == date.date()]
    
    # Gráfico de temperatura
    temp_fig = go.Figure(go.Scatter(x=temperature_data['timestamp'], y=temperature_data['temperature'], mode='lines+markers'))
    temp_fig.update_layout(
    title="Temperatura (°C)", 
    xaxis=dict(title="Hora", showgrid=False, zeroline=False, color='#556b2f'),
    yaxis=dict(title="Temperatura", showgrid=True, gridcolor='#dcdcdc', color='#556b2f'),
    plot_bgcolor='white'
)


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
