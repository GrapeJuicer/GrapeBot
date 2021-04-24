import sqlite3

class SqliteAccessor:
    def __init__(self, file: str):
        self.connection: sqlite3.Connection = sqlite3.connect(file, isolation_level=None)
        self.cursor = self.connection.cursor()
        self.isConnect = True
    
    def disconnect(self):
        self.cursor.close()
        self.connection.close()
        self.isConnect = False

    def execute(self, sql: str, param = None):
        if not self.isConnect:
            return 
        if (param == None):
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, param)
    
    def executemany(self, sql: str, params: list):
        self.cursor.executemany(sql, params)
    
    def fetchone(self):
        return self.cursor.fetchone()

    def fetchmany(self, size: int):
        return self.cursor.fetchmany(size)
    
    def fetchall(self):
        return self.cursor.fetchall()
    