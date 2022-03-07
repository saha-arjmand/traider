
# import sqlalchemy
from sqlalchemy import Column, Date, Time, Float, Integer, String, Sequence

""" Model Of Data
    In this part we create Spot model data """


class Model:

    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    timeframe = Column(String(32), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    symbol = Column(String(32), nullable=False)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    def __repr__(self):
        return f"<kucoinSpotDataOneMin date={self.date} time={self.time} close={self.close}>"