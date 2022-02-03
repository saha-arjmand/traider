from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, Time, Float, Integer
import os
from traider.database import secrets
import pymysql
from sqlalchemy import create_engine

Base = declarative_base()

my_conn = create_engine(
    f"mysql+pymysql://{secrets.dbuser}:{secrets.dbpass}@{secrets.dbhost}/{secrets.dbname}")


"""
    Class kucoin.spot.data.one_min
    id int
    date date
    time time
    open float
    close float
    low float
    volume float
    amount float
"""

class kucoinSpotDataOneMin(Base):
    __tablename__ = 'spotdata'
    id = Column(Integer(), primary_key=True)
    date = Column(Date(), nullable=False)
    time = Column(Time(), nullable=False)
    open = Column(Float(), nullable=False)
    close = Column(Float(), nullable=False)
    high = Column(Float(), nullable=False)
    low = Column(Float(), nullable=False)
    volume = Column(Float(), nullable=False)
    amount = Column(Float(), nullable=False)

    def __repr__(self):
        return f"<kucoinSpotDataOneMin date={self.date} time={self.time} close={self.close}>"


Base.metadata.create_all(my_conn)