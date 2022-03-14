import unittest
from unittest.mock import patch
from traider.getdata.timeframe.oneMin_betha import GetData
from traider.utils.time.time import Calculate_time


class TestGetData(unittest.TestCase):

    def setUp(self):

        print('setUp')

        self.btcusdt = GetData('BTC-USDT', 'kucoin', 'spot', '1min')
        self.xbtcusdt = GetData('ATH-USDT', 'kucoin', 'spot', '1min')

    def tearDown(self):
        print('tearDown\n')

    def test_getData(self):

        print('test_getData')

        ''' with the mock we dont need to connect to web site for test api
            we can visualization the work with mock obj '''
        with patch('traider.getdata.timeframe.oneMin_betha.requests.get') as mocked_get:
            mocked_get.return_value.ok = True
            mocked_get.return_value.text = 'Success'

            schedule = self.btcusdt.getData()

            ''' first we must to create firstTime and lastTime for our test url '''

            lastTime = Calculate_time.lastTime
            firstTime = lastTime - 60
            TimeFrame = '1min'
            symbol = 'BTC-USDT'

            url = f"https://api.kucoin.com/api/v1/market/candles?symbol=" \
                  f"{symbol}&type={TimeFrame}&startAt={firstTime}&endAt={lastTime}"

            ''' with this code we sure about the api work with correct url
                with emp_1 object '''
            mocked_get.assert_called_with(url=url)

            ''' next that we sure about correct url go to check it returns the
                correct text which we set to success'''
            self.assertEqual(schedule, 'Success')

            '''False result'''
            ''' last thing is that we want to test a failed response '''
            mocked_get.return_value.ok = False

            schedule = self.xbtcusdt.getData()
            lastTime = Calculate_time.lastTime
            firstTime = lastTime - 60
            TimeFrame = '1min'
            symbol = 'ATH-USDT'

            url = f"https://api.kucoin.com/api/v1/market/candles?symbol=" \
                  f"{symbol}&type={TimeFrame}&startAt={firstTime}&endAt={lastTime}"
            mocked_get.assert_called_with(url=url)
            self.assertEqual(schedule, 'Bad Response!')


if __name__ == '__main__':
    unittest.main()

