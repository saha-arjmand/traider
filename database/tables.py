# import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, Time, Float, Integer, String, Sequence, BIGINT
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

# import secrets for connect to db
from traider.database import secrets

# import table Models
import traider.database.models as md

Base = declarative_base()

my_conn = create_engine(
    f"mysql+pymysql://{secrets.dbuser}:{secrets.dbpass}@{secrets.dbhost}/{secrets.dbname}")


class CreateTable:
    """ with this method we get the table name """

    def __init__(self, table_name, table_model, exchange):
        self.table_name = table_name.lower()

        '''in this part we highlighting the model of our table to create it'''
        if table_model.lower() == 'spot':
            self.table_model = md.spot.Model
            self.table_model_name = table_model.lower()

        self.exchange = exchange.lower()

    """ with this method we replace our name with table name """

    def build_table(self):
        classname = self.table_name
        ticket = type(classname, (Base, self.table_model), {'__tablename__': self.exchange + '.' +
                                                                             self.table_name + '-' +
                                                                             self.table_model_name})
        return ticket

    """ with this method we create the table with our name """

    def create(self):
        self.build_table().__table__.create(bind=my_conn)


# obj = CreateTable('BTCUSDT', 'spot', 'kucoin')
# obj.create()
