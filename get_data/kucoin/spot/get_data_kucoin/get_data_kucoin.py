from traider.utils.time.time import Calculate_time
from traider.get_data.kucoin.spot.url import CreateUrl
import requests



# Get Data From API
class OneMinuteSpotData():

    def single_One_Minute_Last_Data(self):
        first_time = Calculate_time.firstTime
        second_time = Calculate_time.lastTime
        url = CreateUrl.URL(second_time, first_time, "BTC-USDT", "1min")
        response = requests.get(url=url).json()
        try:
            response['code'] == 200000
            return response['data'][0]
        except:
            while(response['code'] != 200000):
                response = requests.get(url=url).json()
                return response['data'][0]

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



# candle = OneMinuteSpotData()
# for anyItem in candle.multi_One_Minute_Data(3):
#     print(anyItem)
