
# import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, Time, Float, Integer, String, Sequence, BIGINT
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

# import secrets for connect to db
from traider.database import secrets

Base = declarative_base()

my_conn = create_engine(
    f"mysql+pymysql://{secrets.dbuser}:{secrets.dbpass}@{secrets.dbhost}/{secrets.dbname}")


"""Model Of Data
    In this part we create all models of anyType of our data"""


class KucoinSpotDataOneMin:

    id = Column(Integer, Sequence('id_seq'), primary_key=True)
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


class CreateTable:

    """ with this method we get the table name """
    def __init__(self, table_name):
        self.table_name = table_name

    """ with this method we replace our name with table name """
    def build_daily_history_table(self):
        classname = self.table_name
        ticket = type(classname, (Base, KucoinSpotDataOneMin), {'__tablename__': self.table_name})
        return ticket

    """ with this method we create the table with our name """
    def create(self):
        self.build_daily_history_table().__table__.create(bind=my_conn)


obj = CreateTable('BTCUSDT')
obj.create()

