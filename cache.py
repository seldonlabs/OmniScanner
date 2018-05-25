"""
Client caching
"""

import os
import json
import sqlite3
import time

_this_dir = os.path.abspath(os.path.dirname(__file__))

CACHE_FILE = os.path.join(_this_dir, "cache.db")
UPDATE_DELAY = 900


class Cache:
    __connection = None
    __cursor = None

    def __init__(self):
        if self.__is_cache_file():
            self.open()
        else:
            self.open()
            self.__init_tables()

    def __get_ts(self):
        """
        Return timestamp
        :return:
        """
        return int(time.time())

    def __is_cache_file(self):
        """
        Check if the file is a valid cache database
        :return:
        """
        return os.path.isfile(CACHE_FILE)

    def open(self):
        """
        Open internal connection and cursor
        :return:
        """
        self.__connection = sqlite3.connect(CACHE_FILE)
        self.__cursor = self.__connection.cursor()

    def __init_tables(self):
        """
        Init cache tables
        :return:
        """
        self.__connection.execute(
            "CREATE TABLE cache (id INTEGER PRIMARY KEY AUTOINCREMENT, lastUpdate INTEGER, cmdrName TEXT, cmdrData TEXT)")

    def check(self, cmdr_name):
        """
        Check for a cache entry
        :param cmdr_name:
        :return:
        """
        delay = self.__get_ts() - UPDATE_DELAY

        self.__cursor.execute("SELECT cmdrData FROM cache WHERE cmdrName=? AND lastUpdate > ?",
                              (cmdr_name, delay))

        result = self.__cursor.fetchone()

        return json.loads(result[0]) if result else result

    def get_scans(self, limit):
        """
        Get all the scanned commanders in cache
        :return:
        """
        self.__cursor.execute("SELECT cmdrName, cmdrData FROM cache ORDER BY lastUpdate DESC LIMIT ?", (limit,))

        results = self.__cursor.fetchall()

        return {
            'history': [t[0] for t in results],
            'log': {
                t[0]: json.loads(t[1])
                for t in results
            }
        }

    def __insert_cache(self, cmdr_name, cmdr_data):
        """
        DB insert
        :param cmdr_name:
        :param cmdr_data:
        :return:
        """
        self.__cursor.execute("INSERT INTO cache (lastUpdate, cmdrName, cmdrData) VALUES (?, ?, ?)",
                              (self.__get_ts(), cmdr_name, json.dumps(cmdr_data),))

        self.__connection.commit()

    def __update_cache(self, cmdr_name, cmdr_data):
        """
        DB update
        :param cmdr_name:
        :param cmdr_data:
        :return:
        """
        self.__cursor.execute("UPDATE cache SET lastUpdate = ? , cmdrData = ? WHERE cmdrName = ?",
                              (self.__get_ts(), json.dumps(cmdr_data), cmdr_name,))

        self.__connection.commit()

    def add_to_cache(self, cmdr_name, cmdr_data):
        """
        Add entry into cache
        :param cmdr_name:
        :param cmdr_data:
        :return:
        """
        self.__cursor.execute("SELECT cmdrName, lastUpdate FROM cache WHERE cmdrName = ?", (cmdr_name,))

        result = self.__cursor.fetchone()

        if result:
            self.__update_cache(cmdr_name, cmdr_data)
        else:
            self.__insert_cache(cmdr_name, cmdr_data)

    def close(self):
        """
        Close connection
        :return:
        """
        self.__cursor.close()
        self.__connection.close()


cacheDatabase = Cache()
