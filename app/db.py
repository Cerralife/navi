from contextlib import closing
import os
import sqlite3

from pandas import read_sql

RELATIVE_DB_PATH = '../data/naviDB.db'


cwd = os.path.abspath(os.path.dirname(__file__))
default_db_path = os.path.abspath(os.path.join(cwd, RELATIVE_DB_PATH))

class NaviDB:
    def __init__(self, db_path=default_db_path):
        self.db_path = db_path

    def _get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            return conn

        except Error:
            print(Error)

    def read_from_db(self, sql):
        with closing(self._get_connection()) as conn:
            return read_sql(sql=sql, con=conn)

    def write_to_db(self, sql):
        with closing(self._get_connection()) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute(sql)
                conn.commit()
