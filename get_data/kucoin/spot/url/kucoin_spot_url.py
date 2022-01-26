
class CreateUrl:
    def URL(secondTime,firstTime,symbol,TimeFrame):
        # URL for CandleStick Kucoin API
        url = f"https://api.kucoin.com/api/v1/market/candles?symbol=" \
              f"{symbol}&type={TimeFrame}&startAt={firstTime}&endAt={secondTime}"
        return url