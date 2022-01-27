from traider.utils.time.time import Calculate_time
from traider.get_data.kucoin.spot.url import CreateUrl
import requests
import pandas as pd


# Get Data From API
class OneMinuteSpotData():

    def single_One_Minute_Last_Data(self):
        first_time = Calculate_time.firstTime
        second_time = Calculate_time.lastTime
        url = CreateUrl.URL(second_time, first_time, "BTC-USDT", "1min")
        response = requests.get(url=url)

        ''' in this part of code we sure that the response from KUCOIN API get back
         if this code if we dont back status code 200 the code repeat again'''
        timeObj = Calculate_time()
        if response.status_code == 200:
            '''this for is convert time second to standard format time'''
            for anyItem in response.json()['data']:
                anyItem[0] = str(timeObj.convert_second_to_utc_time(int(anyItem[0])))
                return anyItem
        else:
            while response.status_code != 200:
                response = requests.get(url=url)
        for anyItem in response.json()['data']:
            anyItem[0] = str(timeObj.convert_second_to_utc_time(int(anyItem[0])))
            return anyItem


    def multi_One_Minute_Data(self, number_of_Candles):
        first_time = Calculate_time.firstTime - (number_of_Candles - 1) * 60
        second_time = Calculate_time.lastTime
        url = CreateUrl.URL(second_time, first_time, "BTC-USDT", "1min")
        response = requests.get(url=url)

        ''' in this part of code we sure that the response from KUCOIN API get back
         if this code if we dont back status code 200 the code repeat again'''
        timeObj = Calculate_time()
        '''this for is convert time second to standard format time'''
        if response.status_code == 200:
            for anyItem in response.json()['data']:
                anyItem[0] = str(timeObj.convert_second_to_utc_time(int(anyItem[0])))
                print(anyItem)
        else:
            while response.status_code != 200:
                response = requests.get(url=url)
                for anyItem in response.json()['data']:
                    anyItem[0] = str(timeObj.convert_second_to_utc_time(int(anyItem[0])))
                    print(anyItem)


candle = OneMinuteSpotData()
data = candle.multi_One_Minute_Data(10)


# candle2 = OneMinuteSpotData()
# data2 = candle2.single_One_Minute_Last_Data()
# print(data2)




