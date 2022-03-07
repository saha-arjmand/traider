from traider.getdata.kucoin.spot.get_data_kucoin import pastData

# Get past data and save in db

getDataObj = pastData("BTC-USDT")

""" Past Data"""
# 1: we give past data and save in db
past = getDataObj.daysData(10)
for anything in past:
    print(anything)
    getDataObj.saveData_speed(past)

""" Now Data """
# 2: Complete next today data to now
now = getDataObj.firstNextData()
print(now[0])
getDataObj.saveData(now[0])

""" Next Data """
nextData = getDataObj.nextData()
for anyNextData in nextData:
    print(anyNextData)
    getDataObj.saveData(anyNextData)

# end
