from traider.utils.time.time import Calculate_time
from traider.get_data.kucoin.spot.url import CreateUrl
from traider.database import database
from traider.database import secrets
from sqlalchemy import create_engine
import requests
import pandas as pd
import numpy as np
import pymysql

# Option to display
pd.set_option('display.max_columns', None)


# Get Data From API
class OneMinuteSpotData:

    def __init__(self, number_of_candles=1):
        self.number_of_candles = number_of_candles

    '''done'''
    def get_data(self):
        # this parameter send from constructor init method
        number_of_candles = self.number_of_candles
        first_time = Calculate_time.firstTime - (number_of_candles - 1) * 60
        second_time = Calculate_time.lastTime
        url = CreateUrl.URL(second_time, first_time, "BTC-USDT", "1min")
        response = requests.get(url=url)

        ''' in this part of code we sure that the response from KUCOIN API get back
         if this code we dont back status code 200 the code repeat again'''
        if response.status_code == 200:
            return response.json()['data']
        else:
            while response.status_code != 200:
                response = requests.get(url=url)
                return response.json()['data']

    '''done'''
    def convert_std_datetime(self):

        # Convert list obj to numpy array 2D obj
        data = np.array(self.get_data())

        finalList = list()
        i = 0
        calcobj = Calculate_time()

        # i must iterate the items in the array and change time column
        for anyItem in data:
            # 1 : delete first column time
            dataInfo = np.delete(anyItem, 0)

            # DateTime
            # 2 : i want a uniq field for create primary key in our database and it's datetime seconds
            id = int(data[i, 0])

            # Date
            # 3 : Gain date from convert first column (seconds) to std uts date
            dateInfo = calcobj.convert_second_to_utc_time(int(data[i, 0])).date()

            # Time
            # 4 : Gain time from convert first column (seconds) to std uts time
            timeInfo = calcobj.convert_second_to_utc_time(int(data[i, 0])).time()

            # 5 : add datetime that extract in step 2 to final array
            fullData1 = np.insert(dataInfo, 0, id, axis=0)

            # 6 : add date that extract in step 2 to final array
            fullData2 = np.insert(fullData1, 1, dateInfo, axis=0)

            # 5 : add time that extract in step 3 to final array
            # for add to a numpy array the data must be a tuple so we casting data to tuple
            fullData3 = tuple(np.insert(fullData2, 2, timeInfo, axis=0))

            # 6 : we must add fullData2 to a 2D array
            finalList.append(fullData3)

            i += 1

        final = np.array(finalList)


        return final

    '''done'''
    def data_sorting(self):
        data = self.convert_std_datetime()

        df = pd.DataFrame()
        df["id"], df["date"], df["time"], df["open"], df["close"], \
            df["high"], df["Low"], df["volume"], df["amount"] = data.T

        # this code set time column to our index dataframe
        # df.set_index('time', inplace=True)
        return df

    '''done'''
    def save_data_db(self, data):

        db = database.DataBase()

        if db.isExist_db():
            my_conn = create_engine(
            f"mysql+pymysql://{secrets.dbuser}:{secrets.dbpass}@{secrets.dbhost}/{secrets.dbname}")
            data.to_sql(con=my_conn, name='1mindata', if_exists='replace', index=True)
            print("save data to databases")
        else:
            print("database not found !")

    '''working'''
    def one_min_past_24h_data(self):

        candleNumber = 1





s = OneMinuteSpotData(10)
data1 = s.data_sorting()
print(data1)
s.save_data_db(data1)






