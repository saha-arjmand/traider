from traider.utils.time.time import Calculate_time
from traider.get_data.kucoin.spot.url import CreateUrl
import requests
import pandas as pd
import numpy as np

# Option to display
pd.set_option('display.max_columns', None)


# Get Data From API
class OneMinuteSpotData:

    def __init__(self, number_of_candles=1):
        self.number_of_candles = number_of_candles

    '''done'''
    def __get_data(self):
        # this parameter send from constructor init method
        number_of_candles = self.number_of_candles
        first_time = Calculate_time.firstTime - (number_of_candles - 1) * 60
        second_time = Calculate_time.lastTime
        url = CreateUrl.URL(second_time, first_time, "BTC-USDT", "1min")
        response = requests.get(url=url)

        ''' in this part of code we sure that the response from KUCOIN API get back
         if this code we dont back status code 200 the code repeat again'''
        if response.status_code == 200:
            return response.json()['data']
        else:
            while response.status_code != 200:
                response = requests.get(url=url)
                return response.json()['data']

    '''done'''
    def past_data_stdTime(self):

        # Convert list obj to numpy array 2D obj
        data = np.array(self.__get_data())

        # data.shape[0] this command give us number of rows of our matrix
        i = 0
        # with calcobj.convert_second_to_utc_time we convert seconds to std time
        calcobj = Calculate_time()
        while i < data.shape[0]:
            # data[i,0] give us the index0 (time) of our matrix
            data[i, 0] = calcobj.convert_second_to_utc_time(int(data[i, 0]))
            i += 1

        return data

    '''done'''
    def data_sorting(self):
        data = self.past_data_stdTime()

        df = pd.DataFrame()
        df["time"], df["open"], df["close"], \
        df["high"], df["Low"], df["volume"], df["amount"] = data.T

        return df


s = OneMinuteSpotData(5)
d = s.data_sorting()
print(d)
