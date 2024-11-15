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
    temp_fig = go.Figure(go.Scatter(
        x=temperature_data['timestamp'], 
        y=temperature_data['temperature'], 
        mode='lines+markers',
        marker=dict(color='#8fb596'),  # Color suave para los puntos
        line=dict(color='#556b2f', width=2)  # Color y grosor de la línea
    ))
    temp_fig.update_layout(
        title="Temperatura (°C)", 
        title_font=dict(size=16, color='#6c9a8b'),  # Título en color verde suave
        xaxis=dict(
            title="Hora", 
            showgrid=True,  # Mostrar cuadrícula en el eje x
            gridcolor='#dcdcdc',  # Color suave para la cuadrícula en el eje x
            zeroline=False,
            color='#556b2f', 
            showline=True,  # Mostrar línea del eje x
            linecolor='#dcdcdc'  # Color de la línea del eje x
        ),
        yaxis=dict(
            title="Temperatura", 
            showgrid=True,  # Cuadrícula en el eje y
            gridcolor='#dcdcdc',  # Color suave para la cuadrícula en el eje y
            color='#556b2f', 
            showline=True,  # Mostrar línea del eje y
            linecolor='#dcdcdc'  # Color de la línea del eje y
        ),
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=50, b=40)  # Reducir margen para hacer la gráfica más compacta
    )


    # Gráfico de humedad
    humidity_fig = go.Figure(go.Scatter(
        x=humidity_data['timestamp'], 
        y=humidity_data['humidity'], 
        mode='lines+markers',
        marker=dict(color='#8fb596'),  # Color suave para los puntos
        line=dict(color='#556b2f', width=2)  # Color y grosor de la línea
    ))
    humidity_fig.update_layout(
        title="Humedad (%)", 
        title_font=dict(size=16, color='#6c9a8b'),  # Título en color verde suave
        xaxis=dict(
            title="Hora", 
            showgrid=True,  # Mostrar cuadrícula en el eje x
            gridcolor='#dcdcdc',  # Color suave para la cuadrícula en el eje x
            zeroline=False,
            color='#556b2f', 
            showline=True,  # Mostrar línea del eje x
            linecolor='#dcdcdc'  # Color de la línea del eje x
        ),
        yaxis=dict(
            title="Humedad", 
            showgrid=True,  # Cuadrícula en el eje y
            gridcolor='#dcdcdc',  # Color suave para la cuadrícula en el eje y
            color='#556b2f', 
            showline=True,  # Mostrar línea del eje y
            linecolor='#dcdcdc'  # Color de la línea del eje y
        ),
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=50, b=40)  # Reducir margen para hacer la gráfica más compacta
    )


    # Mapa de posición con indicador de calor
    position_data = position_data.merge(
    temperature_data[['timestamp', 'temperature']],
    on='timestamp',  # Unir por timestamp
    how='left'  # 'left' mantiene las filas de position_data aunque no haya temperatura
)

    # Mapa de posición con indicador de calor
    map_fig = go.Figure(go.Scattermapbox(
        lat=position_data['lat'], 
        lon=position_data['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=position_data['temperature'] / 2,  # Escalar tamaño basado en temperatura
            color=position_data['temperature'],  # Color basado en temperatura
            colorscale='YlOrRd',  # Escala de colores (amarillo a rojo)
            colorbar=dict(
                title="Temperatura (°C)",
                titleside="right",
                ticks="outside"
            )
        ),
        text=position_data['timestamp'].astype(str) + "<br>Temperatura: " + position_data['temperature'].astype(str) + "°C",
    ))
    map_fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=18,  # Disminuir el nivel de zoom para ampliar la zona de cobertura
        mapbox_center={"lat": position_data['lat'].mean(), "lon": position_data['lon'].mean()},
        title="Posición y Calor de la Planta",
        title_font=dict(size=16, color='#6c9a8b'),  # Estilo del título
        margin=dict(l=10, r=10, t=50, b=40)  # Reducir márgenes
    )



    return temp_fig, humidity_fig, map_fig
