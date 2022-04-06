import sqlite3
import time
import hashlib
import json

class SimpleCache():
    
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.cursor = self.db.cursor()
        self.timestamp = int(time.time())
        self.cursor.execute('CREATE TABLE IF NOT EXISTS hash (timestamp INTEGER, hash TEXT, json TEXT)')
    
    def __del__(self):
        self._rotate()
        self.db.commit()
        self.db.close()
    
    def _serializer(self, data):
        return json.dumps(data)
    
    def _hash(self, data):
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    def lookup(self, data):
        value = self._serializer(data)
        hash = self._hash(value)
        self.cursor.execute('SELECT timestamp from hash WHERE hash = ?', (hash, ))
        if self.cursor.fetchone():
            return True
        return False

    def add(self, data):
        value = self._serializer(data)
        hash = self._hash(value)
        self.cursor.execute('INSERT INTO hash(timestamp, hash, json) VALUES (?, ?, ?)',(self.timestamp, hash, value))

    def update_last_access(self, data):
        value = self._serializer(data)
        hash = self._hash(value)
        self.cursor.execute('UPDATE hash SET timestamp=? WHERE hash=?', (self.timestamp, hash))

    def _rotate(self):
        self.cursor.execute('DELETE FROM hash WHERE timestamp<?', (self.timestamp, ))

    