import traider.utils.time.time as timeutc
from traider.get_data.kucoin.spot.url import CreateUrl
import requests



# Get Data From API
class OneMinuteSpotData():
    def singleOneMinuteData(self):
        first_time = timeutc.firstTime
        second_time = timeutc.lastTime
        url = CreateUrl.URL(second_time, first_time, "BTC-USDT", "1min")
        try:
            response = requests.get(url=url).json()
            return response['data'][0]
        except:
            while(response['code'] != 200000):
                response = requests.get(url=url).json()
            return response['data'][0]



candle = OneMinuteSpotData()
print(candle.singleOneMinuteData())