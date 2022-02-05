from traider.utils.time.time import Calculate_time
from traider.get_data.kucoin.spot.url import CreateUrl
from traider.database import database
from traider.get_data.kucoin.spot.symbol.symbols import Symbols
import requests
import pandas as pd
import numpy as np


# Option to display
pd.set_option('display.max_columns', None)


# Get Data From API
class OneMinuteSpotData:

    """ In this Class Constructor if we set firstTime & lastTime Parameter then the
    number_of_candles parameters dont use in this Class"""
    def __init__(self, symbol, number_of_candles=1, firstTime=0, lastTime=0):
        self.number_of_candles = number_of_candles
        self.symbol = symbol
        self.firstTime = firstTime
        self.lastTime = lastTime

    '''done'''
    def get_data(self):

        firstTime = self.firstTime
        lastTime = self.lastTime
        symbol = self.symbol

        # Create obj from Symbol Class to check symbol is correct
        symbolObj = Symbols()
        # if check symbol is true then start create the url for request
        if symbolObj.check_symbol(symbol):

            if firstTime == 0 and lastTime == 0:

                # this parameter send from constructor init method
                number_of_candles = self.number_of_candles

                first_time = Calculate_time.firstTime - (number_of_candles - 1) * 60
                last_time = Calculate_time.lastTime
                url = CreateUrl.URL(last_time, first_time, symbol, "1min")
                response = requests.get(url=url)

            else:
                '''
                in this part of if statement we dont need to candlesNumber and we create link with
                first and last time parameters
                '''
                first_Time = self.firstTime
                last_Time = self.lastTime
                url = CreateUrl.URL(last_Time, firstTime, "BTC-USDT", "1min")
                response = requests.get(url=url)

        # else if the symbol not correct
        else:
            print("the symbol not correct !")



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

    '''done'''
    def allDay_candles(self):

        # first we create a object from time Class for convert time
        calctime = Calculate_time()

        # Today data : in below code we calculate today code
        todayLastTime = calctime.convert_second_to_utc_time(calctime.lastTime)
        TodayLastTime_hour = todayLastTime.hour
        TodayLastTime_minute = todayLastTime.minute
        # total past minute in today is totalTimePastToday
        totalTimePast = ((TodayLastTime_hour * 60) + TodayLastTime_minute)
        # So just we equal number_of_candles to this totalTimePastToday obj
        # base totalTimePast is number of Today minutes
        self.number_of_candles = totalTimePast
        print("this is today data")
        return self.data_sorting()

    '''this function one_min_past_24h_data has 2 yield and one yield is for today data
        and second yield is for other days yield data and show data to dataframe model'''
    def one_min_past_24h_data(self, daysNumber=1):
        # Today data
        yield self.allDay_candles()

        # first we create a object from time Class for convert time
        calctime = Calculate_time()

        timespan = calctime.pastDay_datetime(daysNumber)

        for anyItem in timespan:
            # first we calculate lastTime
            last_Time = anyItem[1]
            # then we minus a day's seconds from last time to calculate firstTime
            first_Time = last_Time - (24 * 60 * 60)

            # then we replace it with first & last time in our getData
            self.firstTime = first_Time
            self.lastTime = last_Time
            print("this is next day data")
            yield self.data_sorting()


dataObj = OneMinuteSpotData("BTC-USDT")
data = dataObj.get_data()
print(data)



