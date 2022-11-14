
import sqlite3


class SQL3(object):

    def __init__(self, file_path):
        self.conn = sqlite3.connect(file_path)

    def query(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)
        values = cur.fetchall()
        cur.close()
        return values

    def __del__(self):
        self.conn.close()
