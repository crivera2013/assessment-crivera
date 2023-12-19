"""
This module contains functions for:
- calculating the portfolio yield and duration values from the constituents and weights
- calcuating the daily yield change
- computing historical simulation VaR
- computing variance-covariance VaR
"""
import json

import numpy as np
import pandas as pd
from scipy.stats import norm


def create_portfolio(
    input_df: pd.DataFrame, table_data: dict, column: str = "ytm"
) -> pd.DataFrame:
    """convert yield or DV01 data into a columnar dataframe and use that to compute the historical portfolio values"""

    port_df = pd.pivot_table(
        input_df, index="trade_date", columns="cusip", values=column
    ).ffill()
    weights: pd.DataFrame = pd.DataFrame(table_data).set_index("cusip")
    weights["weight"] = weights["weight"].astype(float)

    weights_df = port_df.copy()
    for cusip in weights_df.columns:
        weights_df[cusip] = weights.loc[cusip, "weight"]

    port_df["Portfolio"] = (port_df * weights_df).sum(axis=1)

    return port_df


def create_yield_change_df(
    yield_df: pd.DataFrame, table_data: list[dict]
) -> pd.DataFrame:
    """compute the historical portfolio yield change"""

    port_df = create_portfolio(yield_df, table_data, "ytm")
    delta_df = port_df - port_df.shift(1)

    return delta_df


def value_at_risk_historical_simulation(
    yield_df: pd.DataFrame, table_data: list[dict], confidence_level=0.99
) -> float:
    """compute the historical simulation VaR of the portfolio"""
    port_df = create_portfolio(yield_df, table_data)
    returns = port_df["Portfolio"].pct_change()
    value_at_risk = returns.quantile(1 - confidence_level)
    return value_at_risk


def value_at_risk_var_covar(
    yield_df: pd.DataFrame, table_data: list[dict], confidence_level=0.99
) -> float:
    """compute the variance-covariance VaR of the portfolio"""
    port_df = create_portfolio(yield_df, table_data)
    returns = port_df["Portfolio"].pct_change()
    value_at_risk = norm.ppf(1 - confidence_level, returns.mean(), returns.std())
    return value_at_risk


def check_weights(table_data: list[dict]) -> bool:
    "checks if the user inputted weights sum up to 1"
    table_df = pd.DataFrame(table_data)
    table_df["weight"] = table_df["weight"].astype(float)
    if np.isclose(table_df["weight"].sum(), 1.0, atol=1e-04):
        return True
    return False


def convert_to_port_df(port_data: str, column: str = "ytm") -> pd.DataFrame:
    """converts json string to pandas dataframe"""
    port_df = pd.DataFrame(json.loads(port_data))
    port_df["trade_date"] = pd.to_datetime(port_df["trade_date"])
    port_df[column] = port_df[column].astype(float)
    return port_df
