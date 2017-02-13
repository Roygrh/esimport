# ######################################################################################################################
#
# Python2.7 Script: elevenmssql.py
#
#
# Author: Sean P. Parker
# Date: January 2017
#
# Copyright @ 2017 Eleven Wireless Inc.
#
# ######################################################################################################################
import pyodbc


class ElevenMsSqlConnector:
    def __init__(self, connection):
        self.conn = pyodbc.connect(connection)
        self.cursor = self.conn.cursor()

    def maxId(self):
        return self.cursor.execute("select max(id) from Member").fetchone()[0]
