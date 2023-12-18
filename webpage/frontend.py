"""

"""

from datetime import date

import pandas as pd
from dash import dcc, html  # pylint: disable=import-error
from dash.dash_table import DataTable  # pylint: disable=import-error

styling = {
    "font-family": "Georgia",
    "font-size": "18px",
    "padding": "10px",
    "text-align": "center",
}

styling_table = {
    "font-family": "Georgia",
    "font-size": "12px",
    "padding": "4px",
    "text-align": "center",
}


DATABASE_URL = "sqlite:///pharo_assessment.db"

CUSIPS = pd.read_sql("cusip_info", DATABASE_URL)[["cusip"]]
CUSIPS["value"] = CUSIPS["cusip"]
CUSIPS = CUSIPS.rename(columns={"cusip": "label"})
CUSIPS = CUSIPS.to_dict("records")

DATES = pd.read_sql(
    f"select trade_date from tick_history where cusip='{CUSIPS[0]['label']}'",
    DATABASE_URL,
)
DATES["trade_date"] = pd.to_datetime(DATES["trade_date"])
MAX_DATE = DATES["trade_date"].max()
MAX_DATE = date(MAX_DATE.year, MAX_DATE.month, MAX_DATE.day)
MIN_DATE = DATES["trade_date"].min()
MIN_DATE = date(MIN_DATE.year, MIN_DATE.month, MIN_DATE.day)


def load_html() -> html.Div:
    """Returns the html layout for the bond portfolio tab"""
    return html.Div(
        [
            html.Div(
                [
                    dcc.Tabs(
                        id="graph-tabs",
                        children=[
                            dcc.Tab(
                                label="Yield Chart",
                                children=[
                                    dcc.Graph(
                                        id="yield-graph",
                                        config={
                                            "displayModeBar": False,
                                            "scrollZoom": True,
                                        },
                                    )
                                ],
                            ),
                            dcc.Tab(
                                label="Yield Delta Chart",
                                children=[
                                    dcc.Graph(
                                        id="yield-change-graph",
                                        config={
                                            "displayModeBar": False,
                                            "scrollZoom": True,
                                        },
                                    )
                                ],
                            ),
                            dcc.Tab(
                                label="Duration Chart",
                                children=[
                                    dcc.Graph(
                                        id="duration-graph",
                                        config={
                                            "displayModeBar": False,
                                            "scrollZoom": True,
                                        },
                                    )
                                ],
                            ),
                        ],
                    )
                ],
                style={
                    "textAlign": "center",
                    "align": "center",
                    "float": "left",
                    "width": "60%",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Select Securities", style=styling),
                            dcc.Dropdown(
                                options=CUSIPS,
                                value=["00751YAD8", "90131HAY1", "912810FG8"],
                                multi=True,
                                clearable=False,
                                id="sec-picker",
                                style={"textAlign": "center", "align": "center"},
                            ),
                        ]
                    ),
                    html.Label("Select Date Range", style=styling),
                    dcc.DatePickerRange(
                        id="date-range",
                        min_date_allowed=MIN_DATE,
                        max_date_allowed=MAX_DATE,
                        start_date=MIN_DATE,
                        end_date=MAX_DATE,
                    ),
                    html.Label("VaR Confidence Interval %", style=styling),
                    dcc.Slider(min=90, max=99, step=1, value=95, id="var-slider"),
                    html.Label("VaR Type", style=styling),
                    html.Label(
                        "Historical Simulation VaR:", style=styling, id="sim-var"
                    ),
                    html.Label("Variance-Covariance VaR:", style=styling, id="cov-var"),
                    DataTable(
                        id="constituents-table",
                        columns=(
                            [{"id": "weight", "name": "weight", "editable": True}]
                            + [
                                {
                                    "id": p,
                                    "name": p.replace("_", " "),
                                    "editable": False,
                                }
                                for p in [
                                    "cusip",
                                    "issuer",
                                    "coupon",
                                    "maturity_date",
                                    "payments_per_year",
                                ]
                            ]
                        ),
                        style_cell=styling_table,
                        style_cell_conditional=[
                            {
                                "if": {"column_id": "weight"},
                                "backgroundColor": "lightgreen",
                            }
                        ],
                    ),
                    html.Label(
                        "Weight column is editable: input number and press enter to re-weight",
                        style=styling,
                        id="weight-error",
                    ),
                ],
                style={
                    "textAlign": "center",
                    "align": "center",
                    "float": "left",
                    "width": "40%",
                },
            ),
        ]
    )
