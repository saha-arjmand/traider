import mysql.connector as sql
from traider.database.kucoin_db import kucoin_tables
from sqlalchemy import exc


class DataBase:

    myDb = sql.connect(
        host="localhost",
        user="root",
        passwd="adminadmin")

    def isExist_db(self):

        myCursor = DataBase.myDb.cursor()

        # databases Names
        myCursor.execute("show databases")
        listDb = []
        for anyDb in myCursor:
            listDb.append(anyDb[0])

        # our database name is traiderdb
        if 'traiderdb' in listDb:
            return True
        else:
            return False

    def connect_and_create_db(self):

        if not self.isExist_db():
            myCursor = DataBase.myDb.cursor()
            myCursor.execute("CREATE DATABASE traiderdb")
            print("The database with name traiderdb created")
        else:
            print("The database already exist")

        myDb = sql.connect(
            host="localhost",
            user="root",
            passwd="adminadmin",
            database="traiderdb")

    def show_dbs(self):
        myCursor = DataBase.myDb.cursor()
        myCursor.execute("show databases")
        listDb = []
        for anyDb in myCursor:
            listDb.append(anyDb[0])

        print(listDb)

    '''done'''
    idSet = set()

    def saveSingleDF(self, singleData, tableName):

        # first i must to check the database is exist then start start save progress
        if self.isExist_db():

            errorNumber = 0
            # if db is exist i define a loop than save dataframe id to a list
            for i in range(len(singleData)):

                # get id from dataframe for each row of table
                dataID = int(singleData.iloc[i:i + 1, 0])

                # If the id dont in setID then add id to the set (idSet)
                if dataID not in self.idSet:
                    self.idSet.add(dataID)

                    # i calculate any row of data to save to db
                    anyItemData = singleData[i:i + 1]

                    # then next : i request to db and save data to db
                    try:
                        anyItemData.to_sql(name=tableName, if_exists='append', con=kucoin_tables.my_conn, index=False)
                        print(f"save data {i} to database")

                    # and if the request to db dont success i print Exception
                    except Exception as e:
                        print(f"\nerror number : {errorNumber}")
                        print(f"error text : {e}")
                        errorNumber += 1
                else:
                    print(" the id is duplicated ")
        else:
            print("database not found !")


    def saveMultiDF(self, multiData, tableName)
        pass