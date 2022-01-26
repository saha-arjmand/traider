import traider.utils.time.time as timeutc
import requests

print(timeutc.current_utc_time)

def URL(secondTime,firstTime,symbol,TimeFrame):
    # URL for CandleStick Kucoin API
    url = f"https://api.kucoin.com/api/v1/market/candles?symbol={symbol}&type={TimeFrame}&startAt={firstTime}&endAt={secondTime}"
    return url

# Get Data From API
first_time = timeutc.firstTime
second_time = timeutc.lastTime
url = URL(second_time,first_time,"BTC-USDT","1min")
response = requests.get(url=url).text

print(response)
