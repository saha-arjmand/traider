from traider.get_data.kucoin.spot.get_data_kucoin import pastData

# get next data and save in db

getDataObj = pastData("BTC-USDT")

# 1: create first next data and add to db
firstNextData = getDataObj.firstNextData()
print(firstNextData)
# getDataObj.saveData(firstNextData)