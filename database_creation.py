"""
This script creates the SQL database and insert yield and CUSIP data
gathered from Refinitiv Datascope jobs.

This code uses an Object Relational Mapper (ORM) called SQLAlchemy
to create the database schema and to insert the data.

While this project uses SQLite instead of Microsoft Express SQL, the difference
is only in the database URL. The code is the same for both databases as
the SQLAlchemy ORM abstractsaway the difference.
"""

import datetime

import pandas as pd
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import declarative_base

# this database URL can be changed to MS SQL server, MySQL,
# MariaDB, PostGresSQL, etc.
# it is a level of abstraction that allows for the same code
# to be used for different databases
DATABASE_URL = "sqlite:///pharo_assessment.db"

# if it was microsoft sql server/express, it would be this:
# "mssql+pyodbc://{network_user_name}:{network_pw}@{server_name}//{database_name}"

Base = declarative_base()


class TickHistory(Base):
    """tick_history SQL Table schema where the historical yield data is stored"""

    __tablename__ = "tick_history"
    id = Column(Integer, primary_key=True)
    cusip = Column(String(50), unique=False, nullable=False)
    ytm = Column(Float, unique=False, nullable=False)
    trade_date = Column(DateTime, default=datetime.datetime.utcnow)


class CusipInfo(Base):
    """cusip_info SQL Table schema where characteristics of bonds are stored

    Cusip is used as the primary key although I'm aware that CUSIP is not always unique.
    In municipal bonds, municipalities will recycle CUSIPs after a bond has matured"""

    __tablename__ = "cusip_info"
    cusip = Column(String(50), primary_key=True, unique=True, nullable=False)
    issuer = Column(String(50), unique=False, nullable=False)
    maturity_date = Column(DateTime, default=datetime.datetime.utcnow)
    coupon_freq = Column(Integer, unique=False, nullable=False)
    coupon = Column(Float, unique=False, nullable=False)


class DV01(Base):
    """
    dv01_info SQL Table schema where the daily DV01 of each bond is stored

    While this could just be another column in the Tick_history table,
    I've seperated it into a different table since it is computed data
    rather than input data
    """

    __tablename__ = "dv01_info"
    id = Column(Integer, primary_key=True)
    cusip = Column(String(50), unique=False, nullable=False)
    dv01 = Column(Float, unique=False, nullable=False)
    trade_date = Column(DateTime, default=datetime.datetime.utcnow)


def create_database() -> Engine:
    """instantiates a database with the SQL schema given above"""
    engine = create_engine(DATABASE_URL)

    Base.metadata.create_all(engine)
    return engine


def load_refinitiv_data() -> [pd.DataFrame, pd.DataFrame]:
    """Refinitiv Datascope jobs are downloaded as csv files.
    This loads the csv files as pandas dataframes in preparation for SQL ingestion"""

    tick_history = pd.read_csv(
        "refinitiv_data/tick_history.csv", parse_dates=["trade_date"]
    )
    tick_history.index.name = "id"
    cusip_info = pd.read_csv(
        "refinitiv_data/cusip_info.csv", parse_dates=["maturity_date"]
    )
    cusip_info = cusip_info.set_index("cusip")
    return tick_history, cusip_info


def insert_data(engine: Engine, df: pd.DataFrame, table_name: str) -> None:
    """inserts pandas dataframe into SQL database"""
    conn = engine.connect()
    df.to_sql(table_name, con=conn, if_exists="replace", index=True)


def main() -> None:
    """create SQL db, load data, and insert data into SQL db"""
    engine = create_database()
    tick_history, cusip_info = load_refinitiv_data()
    insert_data(engine, tick_history, "tick_history")
    insert_data(engine, cusip_info, "cusip_info")


if __name__ == "__main__":
    main()
