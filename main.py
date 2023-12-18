"""Contains the intial app layout and the main function for running the Dash app"""

from dash import Dash, dcc, html  # pylint: disable=import-error

from webpage import callbacks
from webpage import frontend

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

callbacks.get_callbacks(app)

app.layout = html.Div(
    [
        html.Div(
            [html.H2("Pharo Assessment, Software Developer: Christian Rivera")],
            style={
                "color": "grey",
                "textAlign": "center",
                "font-family": "Georgia",
            },
        ),
        html.Div(id="hidden-port-data", style={"display": "none"}),
        html.Div(id="hidden-dv01-data", style={"display": "none"}),
        html.Div(id="hidden-weights-data",style={"display": "none"}),

        dcc.Tabs(
            id="tabs",
            children=[
                dcc.Tab(
                    label="Bond Portfolio",
                    children=[frontend.load_html()],
                ),
                dcc.Tab(
                    label="README",
                    children=[dcc.Markdown("""## To Whom it May Concern""")],
                ),
            ],
        ),
    ]
)

# Only for running on development mode
if __name__ == "__main__":
    app.run(debug=True)
