import sqlite3

class Database(object):
    conn = None
    cursor = None

    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()

    def writeChanges(self):
        self.conn.commit()

    def closeDB(self):
        self.cursor.close()
        self.conn.close()

    def getAllDBUsers(self):
        self.cursor.execute("SELECT * FROM Users")
        return self.cursor.fetchall()

    def getDBUserAliasesByID(self, userID):
        self.cursor.execute("select Aliases from Users where DiscordID = '" + (str)(userID) + "'")
        return self.cursor.fetchone()

    def getExistsUserID(self, userID):
        self.cursor.execute("select exists (select 1 from users where DiscordID='" + (str)(userID) + "')")
        return self.cursor.fetchone()[0]

    def addKamiUserToDB(self, kUser):
        self.cursor.execute("insert or replace into Users (DiscordID, Aliases) values ('" + (str)(
            kUser.getUserID()) + "','" + kUser.getAliasesAsString() + "')")
        self.writeChanges()



