from dash import html

layout = html.Div([
    html.H1("Suculenta Echeveria Pulvinata", className="plant-info-title"),
    html.Div([
        html.Div([
            html.Img(src="/assets/plantita.jpeg", className="plant-info-image"),
        ], className="image-container"),
        html.Div([
            html.Div([
                html.H5("Origen", className="info-header"),
                html.P("La Suculenta Echeveria Pulvinata es originaria de las zonas áridas de México. Es conocida por su resistencia a condiciones extremas de sequía y su facilidad de adaptación a interiores.", className="info-text"),
            ], className="info-card"),  # Nueva tarjeta para "Origen"
            
            html.Div([
                html.H5("Características y Cuidados", className="info-header"),
                html.P("Esta planta tiene hojas aterciopeladas que pueden almacenar agua, lo cual la hace ideal para ambientes secos. Prefiere luz indirecta y temperaturas moderadas. Debe regarse cuando el sustrato esté completamente seco para evitar problemas de humedad en sus raíces.", className="info-text"),
            ], className="info-card"),  # Nueva tarjeta para "Características y Cuidados"
            
            html.Div([
                html.H5("Recomendaciones de Mantenimiento", className="info-header"),
                html.P("Para evitar el estrés, es fundamental mantener la Echeveria entre 15°C y 25°C, y alejada de corrientes de aire frío. El exceso de humedad en las hojas puede propiciar hongos, por lo que es recomendable no rociarla directamente con agua.", className="info-text"),
            ], className="info-card"),  # Nueva tarjeta para "Recomendaciones de Mantenimiento"
            
            html.Div([
                html.H5("Beneficios de la Suculenta en Casa", className="info-header"),
                html.P("Además de ser una planta decorativa, la Suculenta Echeveria Pulvinata contribuye a la purificación del aire, mejorando la calidad ambiental en interiores. Su bajo mantenimiento la convierte en una opción ideal para personas con poco tiempo para el cuidado de plantas.", className="info-text"),
            ], className="info-card"),  # Nueva tarjeta para "Beneficios"
            
        ], className="info-container")
    ], className="content-layout"),
], className="plant-info-container")
