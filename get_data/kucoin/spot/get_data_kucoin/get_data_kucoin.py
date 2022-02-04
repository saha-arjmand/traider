from traider.utils.time.time import Calculate_time
from traider.get_data.kucoin.spot.url import CreateUrl
from traider.database import database
import requests
import pandas as pd
import numpy as np


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

        tableName = "spotdata"
        db = database.DataBase()
        db.savedb(data, tableName)


    '''working'''
    def one_min_past_24h_data(self, daysNumber=0):
        pass
    #     calctime = Calculate_time()
    #
    #     i = 0
    #     if daysNumber == 0:
    #         # Today data
    #         lastTime = calctime.convert_second_to_utc_time(calctime.lastTime)
    #         lastTime_hour = lastTime.hour
    #         lastTim_minute = lastTime.minute
    #         totalTimePast = ((lastTime_hour * 60) + lastTim_minute)
    #         self.number_of_candles = totalTimePast
    #         print(f"{lastTime} and the time to end day is {24 - lastTime_hour}:{60 - lastTim_minute}"
    #               f" = {((24 - lastTime_hour - 1) * 60) + (60 - lastTim_minute)}")
    #         print(f"left over of time : {24 - lastTime_hour - 1}:{60 - lastTim_minute}")
    #
    #         return self.data_sorting()
    #     else:
    #         i = 0
    #         while i < daysNumber:
    #             first_hoar = calctime.firstTime
    #             yield data

        # print(f"total minutes is : {totalTimePast}")



obj = OneMinuteSpotData(5)
data = obj.data_sorting()
print(data)

