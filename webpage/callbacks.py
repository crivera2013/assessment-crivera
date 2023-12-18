import json

import pandas as pd
from dash import Input, Output
from plotly.graph_objs import Layout, Scatter

from database_creation import DATABASE_URL
from webpage import calculations as calcs


def get_callbacks(app):
    """wrapper functioon to assign all the callbacks for the Bond Portfolio tab
    to the app object"""

    @app.callback(
        Output("hidden-port-data", "children"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input(component_id="sec-picker", component_property="value"),
    )
    def query_yield_data(start_date: str, end_date: str, secs: list[str]) -> dict:
        """Callback function to query the SQL database for the yield data
        and return it as a json string"""
        query = f"""select cusip, yield_close, trade_date from tick_history where
        trade_date >= '{start_date}' and trade_date <= '{end_date}' and cusip in {tuple(secs)}"""
        yield_df = pd.read_sql(query, DATABASE_URL).to_dict("records")

        return json.dumps(yield_df)

    @app.callback(
        Output("hidden-dv01-data", "children"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input(component_id="sec-picker", component_property="value"),
    )
    def query_dv01_data(start_date: str, end_date: str, secs: list[str]) -> dict:
        """Callback function to query the SQL database for the dv01 data
        and return it as a json string"""
        query = f"""select cusip, dv01, trade_date from dv01_info where
        trade_date >= '{start_date}' and trade_date <= '{end_date}' and cusip in {tuple(secs)}"""
        dv01_df = pd.read_sql(query, DATABASE_URL).to_dict("records")
        return json.dumps(dv01_df)

    @app.callback(
        Output("constituents-table", "data"),
        Input(component_id="sec-picker", component_property="value"),
    )
    def create_cusip_table(secs: list[str]) -> dict:
        """Callback function to create the constituent table"""
        query = f"select * from cusip_info where cusip in {tuple(secs)}"
        cusip_df = pd.read_sql(query, DATABASE_URL)
        cusip_df["maturity_date"] = cusip_df["maturity_date"].str.split(" ").str[0]
        num_secs = len(secs)
        cusip_df["weight"] = 1 / num_secs
        cusip_df["weight"] = cusip_df["weight"].round(4)

        return cusip_df.to_dict("records")

    @app.callback(
        Output("weight-error", "children"),
        Input("constituents-table", "data"),
    )
    def check_weights(table_data: dict) -> str:
        """Callback function to check if the weights sum to 1"""
        calcs.check_weights(table_data)
        if calcs.check_weights(table_data):
            return "Weight column is editable: input value and press enter to re-weight"
        return "Weights do not add up to 1 (100%)"

    @app.callback(
        Output(component_id="yield-graph", component_property="figure"),
        Input("hidden-port-data", "children"),
        Input("constituents-table", "data"),
    )
    def create_yield_chart(port_data, table_data):
        sec_df = calcs.convert_to_port_df(port_data)
        port_df = calcs.create_portfolio(sec_df, table_data, "yield_close")
        traces = []
        for sec in port_df.columns:
            traces.append(
                Scatter(
                    x=port_df.index,
                    y=port_df[sec],
                    # text=df_by_continent['country'],
                    opacity=0.5 if sec != "Portfolio" else 1,
                    mode="lines",
                    name=sec,
                )
            )
        layout = Layout(
            title="Portfolio and Constituent Yields",
            yaxis={"title": "Yield"},
            hovermode="closest",
            legend=dict(x=0, y=1),
        )
        if calcs.check_weights(table_data):
            results = {"data": traces, "layout": layout}
        else:
            results = {"data": [], "layout": layout}
        return results

    @app.callback(
        Output(component_id="yield-change-graph", component_property="figure"),
        Input("hidden-port-data", "children"),
        Input("constituents-table", "data"),
    )
    def create_yield_change_chart(port_data, table_data):
        sec_df = calcs.convert_to_port_df(port_data)
        delta_df = calcs.create_yield_change_df(sec_df, table_data)
        traces = [
            Scatter(
                x=delta_df.index,
                y=delta_df["Portfolio"],
                # text=df_by_continent['country'],
                opacity=1,
                mode="lines",
                name="Portfolio",
            )
        ]
        layout = Layout(
            title="Portfolio Daily Yield Change",
            yaxis={"title": "Yield Delta"},
            hovermode="closest",
            legend=dict(x=0, y=1),
        )
        if calcs.check_weights(table_data):
            results = {"data": traces, "layout": layout}
        else:
            results = {"data": [], "layout": layout}
        return results

    @app.callback(
        Output(component_id="duration-graph", component_property="figure"),
        Input("hidden-dv01-data", "children"),
        Input("constituents-table", "data"),
    )
    def create_duration_chart(port_data, table_data):
        sec_df = calcs.convert_to_port_df(port_data, "dv01")
        duration_df = calcs.create_portfolio(sec_df, table_data, "dv01")
        traces = []
        for sec in duration_df.columns:
            traces.append(
                Scatter(
                    x=duration_df.index,
                    y=duration_df[sec],
                    # text=df_by_continent['country'],
                    opacity=0.5 if sec != "Portfolio" else 1,
                    mode="lines",
                    name=sec,
                )
            )
        layout = Layout(
            title="Portfolio and Constituent Duration",
            yaxis={"title": "Duration"},
            hovermode="closest",
            legend=dict(x=0, y=1),
        )
        if calcs.check_weights(table_data):
            results = {"data": traces, "layout": layout}
        else:
            results = {"data": [], "layout": layout}
        return results

    @app.callback(
        Output(component_id="sim-var", component_property="children"),
        Input("hidden-port-data", "children"),
        Input("constituents-table", "data"),
        Input("var-slider", "value"),
    )
    def create_sim_value_at_risk(port_data, table_data, confidence_level):
        sec_df = calcs.convert_to_port_df(port_data)
        var = calcs.value_at_risk_historical_simulation(
            sec_df, table_data, confidence_level / 100
        )
        if calcs.check_weights(table_data):
            return f"Historical Simulation VaR: {var:.2%}"
        return "Historical Simulation VaR:"

    @app.callback(
        Output(component_id="cov-var", component_property="children"),
        Input("hidden-port-data", "children"),
        Input("constituents-table", "data"),
        Input("var-slider", "value"),
    )
    def create_var_cov_value_at_risk(port_data, table_data, confidence_level):
        sec_df = calcs.convert_to_port_df(port_data)
        var = calcs.value_at_risk_var_covar(sec_df, table_data, confidence_level / 100)
        if calcs.check_weights(table_data):
            return f"Variance-Covariance VaR: {var:.2%}"
        return "Variance-Covariance VaR:"
