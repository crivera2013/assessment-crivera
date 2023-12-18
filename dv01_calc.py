import math

import numpy as np
import numpy_financial as npf
import pandas as pd

from database_creation import DATABASE_URL


def num_payments_left(date: pd.Timestamp, mat_date: pd.Timestamp, freq: int = 1) -> int:
    """determines the number of payments left which is necessary for calculating DV01"""
    if date > mat_date:
        raise ValueError("date must be before maturity date")
    
    days = (mat_date - date).days
    years = days / 365
    num_payments = int(math.ceil(years) * freq)
    return num_payments


def calc_dv01(yield_close: float, coupon: float, num_payments: int, range: float=0.01, fv=1000) -> float:
    """DV01 is a linear approximation of duration (the derivative of the present value function).
    DV01 is thus calculated by observing the change in present value of a bond
    if the yield is changed +/-0.01.  The slope of the line is the duration.
    """
    price = -1 * npf.pv(rate=yield_close, nper=num_payments, pmt=coupon, fv=fv)
    lower = -1 * npf.pv(rate=yield_close - range, nper=num_payments, pmt=coupon, fv=fv)
    higher = -1 * npf.pv(rate=yield_close + range, nper=num_payments, pmt=coupon, fv=fv)
    dv01 = (lower - higher) / (2 * price * range)
    return dv01


def main():
    yield_df = pd.read_sql("tick_history", DATABASE_URL).set_index("id")
    coupon_df = pd.read_sql("cusip_info", DATABASE_URL).set_index("cusip")

    yield_df["yield_close"] = yield_df["yield_close"] / 100

    dv01_df = yield_df[["cusip", "trade_date"]].copy()
    dv01_df["dv01"] = np.nan

    for id in yield_df.index:
        cusip = yield_df.loc[id, "cusip"]
        yield_close = yield_df.loc[id, "yield_close"]
        trade_date = yield_df.loc[id, "trade_date"]
        coupon = coupon_df.loc[cusip, "coupon"]
        maturity_date = coupon_df.loc[cusip, "maturity_date"]
        num_payments = num_payments_left(trade_date, maturity_date)
        dv01_df.loc[id, "dv01"] = calc_dv01(yield_close, coupon, num_payments)

    dv01_df.to_sql("dv01_info", DATABASE_URL, if_exists="replace", index=True)


if __name__ == "__main__":
    main()