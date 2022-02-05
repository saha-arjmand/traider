from traider.utils.time.time import Calculate_time
from traider.get_data.kucoin.spot.url import CreateUrl
from traider.database import database
from traider.get_data.kucoin.spot.symbol.symbols import Symbols
import requests
import pandas as pd
import numpy as np
import time

# Option to display
pd.set_option('display.max_columns', None)


# Get Data From API
class OneMinuteSpotData:

    Log = "\n"

    """ In this Class Constructor if we set firstTime & lastTime Parameter then the
        number_of_candles parameters dont use in this Class                         """
    def __init__(self, symbol, number_of_candles=1, firstTime=0, lastTime=0):

        # check type of integer values is int
        if (type(number_of_candles) | type(firstTime) | type(lastTime)) is int:
            self.number_of_candles = number_of_candles
            self.firstTime = firstTime
            self.lastTime = lastTime

        # check type of string values is str
        if type(symbol) is str:
            self.symbol = symbol

    '''done'''
    def get_data(self):

        # Create stopWatch for Calculate how many time elapsed for this function
        stopwatch_start = time.perf_counter()

        firstTime = self.firstTime
        lastTime = self.lastTime
        symbol = self.symbol

        # we Create urlObj for Create and use Url
        urlObj = CreateUrl()

        # Create obj from Symbol Class to check symbol is correct
        symbolObj = Symbols()
        # if check symbol is true then start create the url for request
        # if symbolObj.check_symbol(symbol):

        if firstTime == 0 and lastTime == 0:

            # this parameter send from constructor init method
            number_of_candles = self.number_of_candles

            first_time = Calculate_time.firstTime - (number_of_candles - 1) * 60
            last_time = Calculate_time.lastTime

            # use from urlObj to create url
            url = urlObj.URL(last_time, first_time, symbol, "1min")

        else:
            '''
            in this part of if statement we dont need to candlesNumber and we create link with
            first and last time parameters
            '''
            first_Time = self.firstTime
            last_Time = self.lastTime
            # use from urlObj to create url
            url = urlObj.URL(last_Time, first_Time, symbol, "1min")

        try:
            response = requests.get(url=url)
            return response.json()['data']
        except requests.ConnectionError as e:
            return "\nConnection Error: DNS failure or refused connection"
        except requests.HTTPError as e:
            return "\nHTTP Error: event of the rare invalid HTTP response", e
        except requests.Timeout as e:
            return "\nTimeout Error: i must write loop code here per 5 time per 5 second", e
        except requests.TooManyRedirects as e:
            return "\nTimeout Error: i must write loop code here per 5 time per 5 second", e
        except Exception as e:
            return "\nUnhandled Exception occurred : ", e
        finally:
            stopwatch_stop = time.perf_counter()

            self.Log += "get data:\n"
            self.Log += f"Time passed : {stopwatch_stop - stopwatch_start} s\n"
            self.Log += f"Response request staus code : {response.status_code}\n"

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
            fullData3 = np.insert(fullData2, 2, timeInfo, axis=0)

            # 6 : add symbol to our dataframe
            fullData4 = tuple(np.insert(fullData3, 3, self.symbol, axis=0))

            # 7 : we must add fullData2 to a 2D array
            finalList.append(fullData4)

            i += 1

        final = np.array(finalList)

        return final

    '''done'''
    def data_sorting(self):
        data = self.convert_std_datetime()

        df = pd.DataFrame()
        df["id"], df["date"], df["time"], df["symbol"], df["open"], df["close"], \
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

    ''' working '''
    def next_one_min_data(self):
        pass


# n, m = map(int, input().split())
#
# stopwatch_start = time.perf_counter()
#
# for i in range(n):
#     t = int(input())
#     if t % m == 0:
#         print(t)
#
# stopwatch_stop = time.perf_counter()
#
# print("Elapsed time:", t1_stop, t1_start)
# print("Elapsed time during the whole program in seconds: ", t1_stop - t1_start)

getDataObj = OneMinuteSpotData("BTC-USDT")
data = getDataObj.get_data()
print(data)
print(getDataObj.Log)