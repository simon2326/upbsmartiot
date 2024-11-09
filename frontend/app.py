import dash
from flask import Flask
from layout import get_layout

# Crear instancias de Flask y Dash
server = Flask(__name__)
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/")
app.layout = get_layout()

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
