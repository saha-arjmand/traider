from traider.get_data.kucoin.spot.get_data_kucoin import pastData

# Get past data and save in db

getDataObj = pastData("BTC-USDT")

# 1: we give past data and save in db
past = getDataObj.daysData(10)
for anything in past:
    print(anything)
    getDataObj.saveData_speed(past)

# 2: we sync today data for miss today data
getDataObj.syncPastData()

# end
