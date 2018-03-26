"""
Client caching
"""

import os
import json
import sqlite3
import time

_this_dir = os.path.abspath(os.path.dirname(__file__))

CACHE_FILE = os.path.join(_this_dir, 'cache.db')
UPDATE_DELAY = 900


def is_cache_file():
    return os.path.isfile(CACHE_FILE)


def _get_ts():
    return int(time.time())


class Cache:
    _connection = None
    _cursor = None

    def __init__(self):
        if is_cache_file():
            self.open()
        else:
            self.open()
            self._init_tables()

    def open(self):
        """
        Open internal connection and cursor
        :return:
        """
        self._connection = sqlite3.connect(CACHE_FILE)
        self._cursor = self._connection.cursor()

    def _init_tables(self):
        """
        Init cache tables
        :return:
        """
        self._connection.execute(
            'CREATE TABLE cache (id INTEGER PRIMARY KEY AUTOINCREMENT, lastUpdate INTEGER, cmdrName TEXT, cmdrData TEXT)')

    def check(self, cmdr_name):
        """
        Check for a cache entry
        :param cmdr_name:
        :return:
        """
        delay = _get_ts() - UPDATE_DELAY

        self._cursor.execute('SELECT cmdrData FROM cache WHERE cmdrName=? AND lastUpdate > ?',
                             (cmdr_name, delay))

        result = self._cursor.fetchone()

        return json.loads(result[0]) if result else result

    def _insert_cache(self, cmdr_name, cmdr_data):
        """
        DB insert
        :param cmdr_name:
        :param cmdr_data:
        :return:
        """
        self._cursor.execute('INSERT INTO cache (lastUpdate, cmdrName, cmdrData) VALUES (?, ?, ?)',
                             (_get_ts(), cmdr_name, json.dumps(cmdr_data),))

        self._connection.commit()

    def _update_cache(self, cmdr_name, cmdr_data):
        """
        DB update
        :param cmdr_name:
        :param cmdr_data:
        :return:
        """
        self._cursor.execute('UPDATE cache SET lastUpdate = ? , cmdrData = ? WHERE cmdrName = ?',
                             (_get_ts(), json.dumps(cmdr_data), cmdr_name,))

        self._connection.commit()

    def add_to_cache(self, cmdr_name, cmdr_data):
        """
        Add entry into cache
        :param cmdr_name:
        :param cmdr_data:
        :return:
        """
        self._cursor.execute('SELECT cmdrName, lastUpdate FROM cache WHERE cmdrName = ?',
                             (cmdr_name,))

        result = self._cursor.fetchone()

        if result:
            self._update_cache(cmdr_name, cmdr_data)
        else:
            self._insert_cache(cmdr_name, cmdr_data)

    def close(self):
        """
        Close connection
        :return:
        """
        self._cursor.close()
        self._connection.close()
