import datetime
from traider.utils.time.time import Calculate_time
from traider.getdata.url.kucoin import KucoinUrl
from traider.database import database
import requests
import pandas as pd
import numpy as np
import time

# Option to display
pd.set_option('display.max_columns', None)


# Get Data From API
class GetData:
    Log = "\nLogfile: \n\n"

    # when create obj from cls we create startTime
    startTime = datetime.datetime.utcnow()

    """ In this Class Constructor if we set firstTime & lastTime Parameter then the
        number_of_candles parameters dont use in this Class                         """
    def __init__(self, symbol, exchange, tradeType, timeFrame, firstTime=0, lastTime=0, number_of_candles=1):

        # check type of integer values is int
        if (type(number_of_candles | firstTime | lastTime)) is int:
            self.number_of_candles = number_of_candles
            self.firstTime = firstTime
            self.lastTime = lastTime
            self.exchange = exchange
            self.tradeType = tradeType
            self.timeFrame = timeFrame
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

        symbol = self.symbol

        # Create Objects from our classes
        # url object: Create and use Url
        urlObj = KucoinUrl()
        # time object: for calculate time
        timeObj = Calculate_time()

        if self.firstTime == 0:
            number_of_candles = self.number_of_candles
            lastTime = Calculate_time.lastTime
            firstTime = Calculate_time.firstTime - (number_of_candles - 1) * 60
            url = urlObj.spot_url(lastTime, firstTime, symbol, self.timeFrame)
        else:
            firstTime = self.firstTime
            lastTime = self.lastTime
            # use from urlObj to create url
            url = urlObj.spot_url(lastTime, firstTime, symbol, self.timeFrame)

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

                if response.ok:
                    return response.text
                else:
                    return 'Bad Response!'

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


# btcusdt = GetData('BTC-USDT', 'kucoin', 'spot', '1min')
# tt = btcusdt.getData()
#
# print(tt.status_code)
# print(tt.ok)
# print(tt.text)
