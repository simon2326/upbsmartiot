from dash import html

layout = html.Div([
    html.H1("Información de la Planta - Suculenta Echeveria Pulvinata", className="plant-info-title"),
    html.Div([
        html.Img(src="/assets/suculenta.jpg", className="plant-info-image"),
        html.Div([
            html.H5("Origen: "),
            html.P("La Suculenta Echeveria Pulvinata es originaria de zonas áridas de México."),
            html.H5("Cuidados:"),
            html.P("Prefiere luz indirecta, riego moderado solo cuando el sustrato esté seco."),
            html.H5("Recomendaciones especiales:"),
            html.P("Mantener en temperaturas entre 15°C y 25°C, evita exceso de humedad en sus hojas.")
        ])
    ], className="two-column-layout"),
], className="plant-info-container")
