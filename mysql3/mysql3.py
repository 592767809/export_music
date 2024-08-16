
import sqlite3


class SQL3(object):

    def __init__(self, file_path):
        self.conn = sqlite3.connect(file_path)
        # self.conn.execute('PRAGMA journal_mode = OFF')

    def query(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)
        values = cur.fetchall()
        cur.close()
        return values

    def search_text(self, text):
        table_list = set()
        cur = self.conn.cursor()
        cur.execute("select name from sqlite_master where type='table' order by name;")
        values = cur.fetchall()
        for table_name, *_ in values:
            cur.execute("select * from " + table_name + ';')
            values2 = cur.fetchall()
            for each in values2:
                for item in each:
                    if text in str(item):
                        table_list.add(table_name)
                        break
        cur.close()
        return table_list

    def __del__(self):
        self.conn.close()
