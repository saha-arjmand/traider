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
        try:
            if response.status_code == 200:
                return response.json()['data'][0]
        except:
            if response.status_code != 200:
                while response.status_code == 200:
                    response = requests.get(url=url)
                    return response.json()['data'][0]

    def multi_One_Minute_Data(self,number_of_Candles):
        first_time = Calculate_time.firstTime - (number_of_Candles - 1) * 60
        second_time = Calculate_time.lastTime
        url = CreateUrl.URL(second_time, first_time, "BTC-USDT", "1min")
        response = requests.get(url=url).json()
        try:
            response['code'] == 200000
            return response['data']
        except:
            while(response['code'] != 200000):
                response = requests.get(url=url).json()
                return response['data']



candle = OneMinuteSpotData()
data = candle.single_One_Minute_Last_Data()
# print(len(data))
print(data)
