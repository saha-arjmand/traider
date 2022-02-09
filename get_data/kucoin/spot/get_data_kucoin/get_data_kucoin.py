import datetime

from traider.utils.time.time import Calculate_time
from traider.get_data.kucoin.spot.url import CreateUrl
from traider.database import database
from traider.get_data.kucoin.spot.symbol.symbols import Symbols
import requests
import pandas as pd
import numpy as np
import time
import concurrent.futures

# Option to display
pd.set_option('display.max_columns', None)


# Get Data From API
class pastData:

    Log = "\nLogfile: \n\n"

    # when create obj from cls we create startTime
    startTime = datetime.datetime.utcnow()

    """ In this Class Constructor if we set firstTime & lastTime Parameter then the
        number_of_candles parameters dont use in this Class                         """
    def __init__(self, symbol, firstTime=0, lastTime=0, number_of_candles=1):

        # check type of integer values is int
        if (type(number_of_candles | firstTime | lastTime)) is int:
            self.number_of_candles = number_of_candles
            self.firstTime = firstTime
            self.lastTime = lastTime

        # check type of string values is str
        if type(symbol) is str:
            self.symbol = symbol

    '''done'''
    def getData(self):

        # Create stopWatch for Calculate how many time elapsed for this function
        stopwatch_start = time.perf_counter()

        # Log save
        self.Log += "get data:\n"

        # anyWay i dont any Calculate for last Time item and it comes from CalcObj

        symbol = self.symbol

        # Create Objects from our classes
        # url object: Create and use Url
        urlObj = CreateUrl()
        # time object: for calculate time
        timeObj = Calculate_time()

        if self.firstTime == 0:
            number_of_candles = self.number_of_candles
            lastTime = Calculate_time.lastTime
            firstTime = Calculate_time.firstTime - (number_of_candles - 1) * 60
            url = urlObj.URL(lastTime, firstTime, symbol, "1min")
        else:
            firstTime = self.firstTime
            lastTime = self.lastTime
            # use from urlObj to create url
            url = urlObj.URL(lastTime, firstTime, symbol, "1min")

        # Log (start)
        print(f"this getData firs time : {timeObj.convert_second_to_utc_time(firstTime)}")
        print(f"this getData last time : {timeObj.convert_second_to_utc_time(lastTime)}")
        print(f"\n-Log- init basic data in getData:\n")
        self.Log += f"- init basic data in getData:\n"
        logData = [[f"{timeObj.convert_second_to_utc_time(firstTime)} |",
                    f"{timeObj.convert_second_to_utc_time(lastTime)} |",
                    f"{symbol} |", f"{self.number_of_candles}"]]
        logData2 = np.array(logData)
        df = pd.DataFrame()
        df["firstTime        "], df["lastTime        "], \
            df["symbol   "], df["candle's number"] = logData2.T
        print(f"{df} \n")
        self.Log += f"{df} \n"
        # Log (end)

        i = 0
        numberOfTry = 5
        while i <= numberOfTry:
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

                print(f"\nTry Again(number{i}) After 30 Seconds")
                time.sleep(5)
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

                # Log (start)
                stopwatch_stop = time.perf_counter()
                timePassed = round((stopwatch_stop - stopwatch_start), 3)
                self.Log += f"Time passed GetData: {timePassed} s\n"
                print(f"Time passed getData: {timePassed} s\n")
                # Log (end)

        i += 1

    '''done'''
    def organizeData(self):

        stopwatch_start = time.perf_counter()

        # Convert list obj to numpy array 2D obj
        data = np.array(self.getData())

        finalList = list()
        i = 0
        calcObj = Calculate_time()

        # i must iterate the items in the array and change time column
        for anyItem in data:
            # 1 : delete first column time
            dataInfo = np.delete(anyItem, 0)

            # DateTime
            # 2 : i want a uniq field for create primary key in our database and it's datetime seconds
            dataId = int(data[i, 0])

            # Date
            # 3 : Gain date from convert first column (seconds) to std uts date
            dateInfo = calcObj.convert_second_to_utc_time(int(data[i, 0])).date()

            # Time
            # 4 : Gain time from convert first column (seconds) to std uts time
            timeInfo = calcObj.convert_second_to_utc_time(int(data[i, 0])).time()

            # 5 : add datetime that extract in step 2 to final array
            fullData1 = np.insert(dataInfo, 0, dataId, axis=0)

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

        # Log (start)
        stopwatch_stop = time.perf_counter()
        timePassed = round((stopwatch_stop - stopwatch_start), 3)
        self.Log += f"Time passed organizeData: {timePassed} s\n"
        print(f"Time passed organizeData: {timePassed} s\n")
        # Log (end)

        return final

    '''done'''
    def frameData(self):

        stopwatch_start = time.perf_counter()

        data = self.organizeData()

        df = pd.DataFrame()
        df["id"], df["date"], df["time"], df["symbol"], df["open"], df["close"], \
            df["high"], df["Low"], df["volume"], df["amount"] = data.T

        # this code set time column to our index dataframe
        # df.set_index('time', inplace=True)

        # Log (start)
        stopwatch_stop = time.perf_counter()
        timePassed = round((stopwatch_stop - stopwatch_start), 3)
        self.Log += f"Time passed frameData: {timePassed} s\n"
        print(f"Time passed frameData: {timePassed} s\n")
        # Log (end)

        return df

    '''done'''
    def dayData(self):

        stopwatch_start = time.perf_counter()

        # first we create a object from time Class for convert time
        calcTime = Calculate_time()

        # Today data : in below code we calculate today code
        todayLastTime = calcTime.convert_second_to_utc_time(calcTime.lastTime)
        TodayLastTime_hour = todayLastTime.hour
        TodayLastTime_minute = todayLastTime.minute

        # Log (start)
        self.Log += f"- dayData lastTime :{todayLastTime}\n"
        print(f"\n- dayData lastTime :{todayLastTime}")
        # Log (end)

        # total past minute in today is totalTimePastToday
        totalTimePast = ((TodayLastTime_hour * 60) + TodayLastTime_minute)
        # So just we equal number_of_candles to this totalTimePastToday obj
        # base totalTimePast is number of Today minutes
        self.number_of_candles = totalTimePast

        # Log (start)
        self.Log += f"total candle's number in dayData is : {totalTimePast}\n"
        print(f"\ntotal candle's number in dayData is : {totalTimePast}")

        stopwatch_stop = time.perf_counter()
        timePassed = round((stopwatch_stop - stopwatch_start), 3)
        self.Log += f"Time passed dayData: {timePassed} s\n"
        print(f"Time passed dayData: {timePassed} s\n")
        # Log (end)

        return self.frameData()

    '''this function daysData has 2 yield and one yield is for today data
        and second yield is for other days yield data and show data to dataframe model'''
    def daysData(self, daysNumber=1):

        stopwatch_start = time.perf_counter()

        # Today data
        yield self.dayData()

        # first we create a object from time Class for convert time
        calcObj = Calculate_time()
        timespan = calcObj.pastDay(daysNumber)

        for anyItem in timespan:
            first_Time = anyItem[0]
            last_Time = anyItem[1]

            # replace it with first & last time in our getData
            self.firstTime = first_Time
            self.lastTime = last_Time

            # Log (start)
            print("this is next day data")
            print(f"this days firsttime: {calcObj.convert_second_to_utc_time(self.firstTime)}")
            print(f"this days lasttime: {calcObj.convert_second_to_utc_time(self.lastTime)}")
            # Log (end)

            yield self.frameData()

        # Log (start)
        stopwatch_stop = time.perf_counter()
        timePassed = round((stopwatch_stop - stopwatch_start), 3)
        self.Log += f"Time passed days data: {timePassed} s\n"
        print(f"Time passed days data: {timePassed} s\n")
        # Log (end)

    '''done'''
    @staticmethod
    def saveData(data):

        tableName = "spotdata"
        db = database.DataBase()
        db.saveDb(data, tableName)

    ''' this function get data collection and save their in db with open thread for each data'''
    def saveData_speed(self, dataList):

        stopwatch_start = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.saveData, dataList)

        # Log (start)
        stopwatch_stop = time.perf_counter()
        timePassed = round((stopwatch_stop - stopwatch_start), 3)
        self.Log += f"Time passed saveData_speed : {timePassed} s\n"
        print(f"Time passed saveData_speed: {timePassed} s\n")
        # Log (end)

    '''done'''
    def syncPastData(self):
        # first we sync today data again for sure that the today data is complete
        self.saveData_speed(self.daysData(0))

    '''working'''
    def firstNextData(self):

        """Create time object for calculate time"""
        timeObj = Calculate_time()

        """Calculate first time"""
        # first time is that time program run and get past data
        startTime = self.startTime.time()

        # for sure that we get all the time from api , we minus first time with 3 minutes
        if startTime.minute >= 3:
            firstTime_hour = startTime.hour
            firstTime_minute = startTime.minute - 3

        else:
            firstTime_hour = startTime.hour - 1
            firstTime_minute = (startTime.minute + 60) - 3

        # so i create new first Date Time with new minute and set seconds to zero
        firstDateTime = self.startTime.replace(self.startTime.year, self.startTime.month, self.startTime.day,
                                               firstTime_hour, firstTime_minute, 0, 0)

        # we need firstTime to second so use timeObj to convert this
        firstDateTime_seconds = timeObj.convert_date_to_seconds(firstDateTime)

        # Log (start)
        self.Log += "firstNextData log"

        print("Calculate firstTime")
        self.Log += "Calculate firstTime"

        print(f"startTime of request : {startTime}")
        self.Log += f"startTime of request : {startTime}"

        print(f"firstDateTime with minus 3 minute is : {firstDateTime}")
        self.Log += f"firstTime with minus 3 minute is : {firstDateTime}"

        print(f"Seconds of the firstDateTime is : {firstDateTime_seconds}")
        self.Log += f"Seconds of the firstDateTime is : {firstDateTime_seconds}"
        # Log (end)

        """Calculate last time"""
        # finish time is now when the method is started
        finishTime = datetime.datetime.utcnow().time()

        # i should wait to finish time goes next minute so i create remaining time
        finishTime_seconds = finishTime.second
        remainingTime = 60 - finishTime_seconds

        # Log (start)
        print("\nCalculate lastTime")
        self.Log += "\nCalculate lastTime"

        self.Log += f"finishTime of getData is {finishTime}"
        print(f"finishTime of getData is : {finishTime}")

        self.Log += f"seconds of the finishTime variable is : {finishTime_seconds} s"
        print(f"seconds of the finish time is : {finishTime_seconds} s")

        self.Log += f"remaining time to end of this minutes is : {remainingTime} s"
        print(f"remaining time to end of this minutes is : {remainingTime} s")

        self.Log += f"program sleep(wait) for {remainingTime} seconds"
        print(f"program sleep(wait) for {remainingTime} seconds")
        # Log (end)

        # then the program must sleep (wait) for remainingTime (seconds)
        time.sleep(remainingTime)

        # last time is next of sleep
        lastTime = datetime.datetime.utcnow()

        # we must set nanoSeconds to zero
        lastDateTime = lastTime.replace(lastTime.year, lastTime.month, lastTime.day,
                                        lastTime.hour, lastTime.minute, lastTime.second, 0)

        # we need firstTime to second so use timeObj to convert this
        lastDateTime_seconds = timeObj.convert_date_to_seconds(lastDateTime)

        # Log (start)
        self.Log += f"\nlastTime is : {lastTime} "
        print(f"\nlastTime is : {lastTime} ")

        self.Log += f"lastTime with zero nanoSecond : {lastDateTime}"
        print(f"lastTime with zero nanoSecond : {lastDateTime}")

        self.Log += f"Seconds of the lastDateTime is : {lastDateTime_seconds}"
        print(f"Seconds of the lastDateTime is : {lastDateTime_seconds}")

        # Log (end)

        """ Set firstTime & lastTime to the init class """
        # we must set firstTime and lastTime to the cls parameters
        self.firstTime = firstDateTime_seconds
        self.lastTime = lastDateTime_seconds

        """ yield df from our data"""
        return self.frameData(), lastDateTime

    '''working'''
    def nextData(self):
        # todo : i must read data from db and if the data is exist in there calc some thing
        pass

    def test(self):
        query="SELECT * FROM spotdata WHERE "








class NextData:
    pass










'''
###########################_Run_Area_###########################
'''


obj = pastData("BTC-USDT")
data1 = obj.firstNextData()
print(data1[1])

print("\n\n\nthis is next ")
print(data1[0])


# data2 = obj.daysData(0)
# for anyItem1 in data2:
#     print(anyItem1)




