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

    def saveDb(self, df, tableName):

        if self.isExist_db():

            # this Prevents duplicate data storage in the database
            errorNumber = 0
            for i in range(len(df)):
                try:
                    df.iloc[i:i + 1].to_sql(name=tableName, if_exists='append', con=kucoin_tables.my_conn, index=False)
                    print(f"save data {i} to databases")
                except exc.IntegrityError as e:

                    # if the error of this prevents duplicate more than 5 Stop

                    print(f"Error {errorNumber} when save data : {e}")
                    if errorNumber > 4:
                        break
                    errorNumber += 1

        else:
            print("database not found !")
