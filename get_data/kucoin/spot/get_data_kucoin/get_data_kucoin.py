from traider.utils.time.time import Calculate_time
from traider.get_data.kucoin.spot.url import CreateUrl
from traider.database import database
from traider.get_data.kucoin.spot.symbol.symbols import Symbols
import requests
import pandas as pd
import numpy as np
import time
import threading
import concurrent.futures

# Option to display
pd.set_option('display.max_columns', None)


# Get Data From API
class OneMinuteSpotData:

    Log = "\nLogfile: \n\n"

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

        # Log save
        self.Log += "get data:\n"

        firstTime = self.firstTime
        # anyWay i dont any Calculate for last Time item and it comes from CalcObj
        lastTime = Calculate_time.lastTime
        symbol = self.symbol

        # Create Objects from our classes
        # url object: Create and use Url
        urlObj = CreateUrl()
        # time object: for calculate time
        timeObj = Calculate_time()

        # use from urlObj to create url
        url = urlObj.URL(lastTime, firstTime, symbol, "1min")

        if firstTime == 0:
            number_of_candles = self.number_of_candles
            firstTime = Calculate_time.firstTime - (number_of_candles - 1) * 60
            url = urlObj.URL(lastTime, firstTime, symbol, "1min")

        # elif firstTime != 0:
        #     '''
        #     in this part of if statement we dont need to candlesNumber and we create link with
        #     first and last time parameters
        #     '''
        #     first_Time = self.firstTime

        # Log (start)
        print(f"\n-Log- init basic data in getData:\n")
        self.Log += f"- init basic data in getData:\n"
        logData = [[f"{timeObj.convert_second_to_utc_time(firstTime)} |",
                    f"{timeObj.convert_second_to_utc_time(lastTime)} |",
                    f"{symbol} |", f"{self.number_of_candles}"]]
        logData2 = np.array(logData)
        df = pd.DataFrame()
        df["lastTime        "], df["firstTime        "], \
            df["symbol   "], df["candle's number"] = logData2.T
        print(f"{df} \n")
        self.Log += f"{df} \n"
        # Log (end)

        while True:
            try:
                response = requests.get(url=url)

                # Log (start)
                # add status code to log file
                print(f"Response request status code : {response.status_code}\n")
                self.Log += f"Response request status code : {response.status_code}\n"
                # Log (end)

                return response.json()['data']

            except requests.ConnectionError as e:

                # Log (start)
                self.Log += "Connection Error: DNS failure or refused connection\n"
                self.Log += f"Error text : {e} \n"
                print("\nConnection Error: DNS failure or refused connection")
                # Log(end)

                print("\nTry Again After 30 Seconds")
                time.sleep(30)
                print("\nTry Again...")
                continue

            except requests.HTTPError as e:

                # Log (start)
                self.Log += "HTTP Error: event of the rare invalid HTTP response\n"
                self.Log += f"Error text : {e} \n"
                print("\nHTTP Error: event of the rare invalid HTTP response")
                # Log (end)

            except requests.Timeout as e:

                # Log (start)
                self.Log += "Timeout Error \n"
                self.Log += f"Error text : {e} \n"
                print("\nTimeout Error ")
                # Log (end)

                print("\nTry Again After 30 Seconds")
                time.sleep(30)
                print("\nTry Again...")
                continue

            except requests.TooManyRedirects as e:

                # Log (start)
                self.Log += "TooManyRedirects Error\n"
                self.Log += f"Error text : {e} \n"
                print("\nTooManyRedirects Error")
                # Log (end)

                time.sleep(30)
                print("\nTry Again...")
                continue

            except Exception as e:

                # Log (start)
                self.Log += "Unhandled Exception occurred \n"
                self.Log += f"Error text : {e} \n"
                print("\nUnhandled Exception occurred : ")
                # Log (end)

            finally:
                stopwatch_stop = time.perf_counter()
                timePassed = round((stopwatch_stop - stopwatch_start), 3)

                # Log (start)
                self.Log += f"Time passed GetData: {timePassed} s\n"
                print(f"Time passed getData: {timePassed} s\n")
                # Log (end)

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


'''
###########################_Run_Area_###########################
'''


obj = OneMinuteSpotData("BTC-USDT")
data = obj.get_data()
print(data)



