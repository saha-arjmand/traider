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
import asyncio


# Option to display
pd.set_option('display.max_columns', None)


# Get Data From API
class GetData:

    Log = "\nLogfile: \n\n"

    # when create obj from cls we create startTime
    startTime = datetime.datetime.utcnow()

    """ In this Class Constructor if we set firstTime & lastTime Parameter then the
        number_of_candles parameters dont use in this Class                         """
    def __init__(self, symbol, exchange, tradeType, firstTime=0, lastTime=0, number_of_candles=1):

        # check type of integer values is int
        if (type(number_of_candles | firstTime | lastTime)) is int:
            self.number_of_candles = number_of_candles
            self.firstTime = firstTime
            self.lastTime = lastTime
            self.exchange = exchange
            self.tradeType = tradeType
            # check type of string values is str
            if type(symbol) is str:
                self.symbol = symbol

            # i must remove - from symbol to create table name with symbol without -
            newSymbol = self.symbol.replace("-", "").lower()
            self.tableName = f"{self.exchange}_{newSymbol}_{self.tradeType}"



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
        while i < numberOfTry:
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
        # df.set_index('id', inplace=True)

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
        timeObj = Calculate_time()

        """ calculate last Time"""

        # first calculate now time
        nowTime = datetime.datetime.utcnow()

        # then i must set minute to zero for calculate last time
        nowTime_zeroMin = nowTime.replace(nowTime.year, nowTime.month, nowTime.day,
                                          nowTime.hour, nowTime.minute, 0, 0)

        # calculate nowTime_zeroMin to seconds for calculate today last time

        lastTime_seconds = timeObj.convert_date_to_seconds(nowTime_zeroMin)

        """ calculate first Time"""

        # calculate first time with replace time hour and minute and second to zero
        firstTime = nowTime.replace(nowTime.year, nowTime.month, nowTime.day,
                                    0, 0, 0, 0)
        firstTime_seconds = timeObj.convert_date_to_seconds(firstTime)

        """ replace first time and last time with init parameter of the class """

        self.firstTime = firstTime_seconds
        self.lastTime = lastTime_seconds

        # Log (start)
        stopwatch_stop = time.perf_counter()
        timePassed = round((stopwatch_stop - stopwatch_start), 3)
        self.Log += f"Time passed dayData: {timePassed} s\n"
        print(f"Time passed dayData: {timePassed} s\n")
        # Log (end)

        return self.frameData()

    '''done'''
    @staticmethod
    def lastData_dayData(df):

        """get the last Datetime from dayData df"""
        lastTime = df.iloc[0, 2]
        lastDate = df.iloc[0, 1]
        fullTime = f"{lastDate} {lastTime}"
        date_time_obj = datetime.datetime.strptime(fullTime, '%Y-%m-%d %H:%M:%S')

        """Convert date_time_obj to seconds"""
        timeObj = Calculate_time()
        lastData = timeObj.convert_date_to_seconds(date_time_obj)

        return lastData

    '''this function daysData has 2 yield and one yield is for today data
        and second yield is for other days yield data and show data to dataframe model'''
    def daysData(self, daysNumber=1):

        stopwatch_start = time.perf_counter()

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

            # Today data
            # yield self.dayData()

        # Log (start)
        stopwatch_stop = time.perf_counter()
        timePassed = round((stopwatch_stop - stopwatch_start), 3)
        self.Log += f"Time passed days data: {timePassed} s\n"
        print(f"Time passed days data: {timePassed} s\n")
        # Log (end)

    '''done'''
    def syncPastData(self):
        # first we sync today data again for sure that the today data is complete
        self.saveData_speed(self.daysData(0))

    '''done'''
    def nowData(self, lastData_dayData):

        """Create time object for calculate time"""
        timeObj = Calculate_time()

        """Calculate first time"""
        firstTime_seconds = lastData_dayData

        # Log (start)
        print("\nfirstNextData")
        self.Log += "\nfirstNextData"
        print(f"firstTime is : {timeObj.convert_second_to_utc_time(firstTime_seconds)}")
        self.Log += f"firstTime is : {timeObj.convert_second_to_utc_time(firstTime_seconds)}"
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
        self.firstTime = firstTime_seconds
        self.lastTime = lastDateTime_seconds

        """ return df from our data"""
        return self.frameData()

    '''working'''
    def nextData(self, lastData_dayData):

        """ Create time object to calc time """
        timeObj = Calculate_time()

        """ Calculate first time to start get data """
        startTime = lastData_dayData

        # Log (start)
        print(f"\nnextData :")
        self.Log += f"\nnextData :"

        print(f"start time is : {timeObj.convert_second_to_utc_time(startTime)}")
        self.Log += f"start time is : {timeObj.convert_second_to_utc_time(startTime)}"
        # Log (end)

        while True:
            """ Calculate current time for check firstTime """
            currentTime = datetime.datetime.utcnow()

            """ i must set zero to second to calculate firstTime"""
            firstTime = currentTime.replace(currentTime.year, currentTime.month, currentTime.day,
                                            currentTime.hour, currentTime.minute, 0, 0)

            firstTime_seconds = timeObj.convert_date_to_seconds(firstTime)

            """ Calculate second to end of this minute and wait """
            seconds = 60 - currentTime.second

            # Log (start)
            print(f"current time is : {currentTime}")
            self.Log += f"current time is : {currentTime}"

            print(f"first time is : {firstTime}")
            self.Log += f"first time is : {firstTime}"

            print(f"sleep(wait) for {seconds} s")
            self.Log += f"sleep(wait) for {seconds} s"
            # Log (end)

            time.sleep(seconds)

            # when sleep is done we calculate last time
            lastTime = datetime.datetime.utcnow()
            lastTime_seconds = timeObj.convert_date_to_seconds(lastTime)

            """ replace the first and last time """

            self.firstTime = firstTime_seconds
            self.lastTime = lastTime_seconds

            yield self.frameData()

    '''working'''
    @staticmethod
    def main():

        """Create Objects """
        obj = GetData("BTC-USDT", 'kucoin', 'spot')
        dbObj = database.DataBase()

        """ Past Data """
        pastDays = 1
        pastData = obj.daysData(3)
        for anyData in pastData:
            print(anyData)
            dbObj.saveData_speed(pastData)

        # Log(start)
        print("\n---------------------------")
        print(f"save past data {pastDays} done")
        pastDays += 1
        print("---------------------------\n")
        # Log(end)

        """ Today Data """
        todayData = obj.dayData()
        print(todayData)
        dbObj.saveData(todayData, obj.tableName)

        # Log (start)
        print("\n---------------------------")
        print("save today data done")
        print("---------------------------\n")
        # Log (end)

        """ last time of todayData"""
        timeObj = Calculate_time()
        lastData_dayData = obj.lastData_dayData(todayData)
        lastData_dayData_show = timeObj.convert_second_to_utc_time(obj.lastData_dayData(todayData))
        print("\n---------------------------")
        print(f"\nlast today data is : {lastData_dayData_show}\n")
        print("---------------------------\n")

        """ now Data """
        nowData = obj.nowData(lastData_dayData)
        print(nowData)
        dbObj.saveData(nowData, obj.tableName)

        # Log (start)
        print("\n---------------------------")
        print("save now data done")
        print("---------------------------\n")
        # Log (end)

        """ Next Data """

        # Log (start)
        print("\n---------------------------")
        print("start to get next data")
        print("---------------------------\n")
        # Log (end)

        nextData = obj.nextData(lastData_dayData)
        for anyItem in nextData:
            print(anyItem)
            dbObj.saveData(anyItem, obj.tableName)




'''
###########################_Run_Area_###########################
'''

objGetData = GetData("BTC-USDT", 'kucoin', 'spot')
objGetData.main()










