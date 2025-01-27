import mysql.connector
import config
import mysql.connector

class Model:
    def __init__(self):
        
        self.db = mysql.connector.connect(
            host="localhost",
            user=config.db['user'],
            password=config.db['password'],
            database="incubate"
        )

    def writeData(self,
                    ts,
                    temps,
                    fruitMedian,
                    fruitMax,
                    spawnMedian,
                    spawnMax,
                    heaterTemp,
                    humidity,
                    heaterOnPercent
                ):
        
        cursor = self.db.cursor()

        sql = "INSERT INTO temps (ts, `0`, `1`, `2`, `3`, `4`, `5`, `6`,"
        sql += "fruitMedian, fruitMax, spawnMedian, spawnMax, heaterTemp, humidity, heaterOnPercent"
        sql += ") VALUES "
        sql += "(%s,"
        sql += "%s, %s, %s, %s, %s, %s, %s, "
        sql += "%s, %s, %s, %s, %s,"
        sql += "%s, %s)"
        values = [ts] + temps + [
            fruitMedian, fruitMax, spawnMedian, spawnMax, heaterTemp,
            humidity, heaterOnPercent]
        cursor.execute(sql, values)
        self.db.commit()