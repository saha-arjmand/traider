from traider.getdata.kucoin.spot.url import CreateUrl
from traider.utils.time.time import Calculate_time
import requests

timeObj = Calculate_time()
urlObj = CreateUrl()

lastTime = timeObj.lastTime
print(f"last time is : {timeObj.convert_second_to_utc_time(lastTime)}")

firstTime = lastTime - (24*60*60)
print(f"first time is : {timeObj.convert_second_to_utc_time(firstTime)}")


url = urlObj.URL(lastTime, firstTime, 'BTC-USDT', '1day')
print(f"url is : {url}\n")

response = requests.get(url=url)
data = response.json()['data'][0]
print(data)

print(f"time of json is : {timeObj.convert_second_to_utc_time(int(data[0]))}")