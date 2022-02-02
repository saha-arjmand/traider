import mysql.connector as sql

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
