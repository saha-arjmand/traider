import mysql.connector as sql

class DataBase:

    def connect_and_create_db(self):
        myDb0 = sql.connect(
            host="localhost",
            user="root",
            passwd="adminadmin")

        myCursor0 = myDb0.cursor()

        # databases Names
        myCursor0.execute("show databases")
        listDb = []
        for anyDb in myCursor0:
            listDb.append(anyDb[0])

        # create Database if it not exist
        # database name is traiderdb
        if 'traiderdb' not in listDb:
            myCursor0.execute("CREATE DATABASE traiderdb")

        myDb1 = sql.connect(
            host="localhost",
            user="root",
            passwd="adminadmin",
            database="traiderdb")

        myCursor = myDb1.cursor()
        myCursor.execute("show databases")
        listDb = []
        for anyDb in myCursor:
            listDb.append(anyDb[0])

        print(listDb)








    def showDb(self):
        pass

db = DataBase()
db.connect_and_create_db()