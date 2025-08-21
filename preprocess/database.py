import os
import sqlite3

class GCJDatabase:
    def __init__(self, base_path, db_name='gcj_dataset.db'):
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        db_path = os.path.join(base_path, db_name)

        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS gcj_data
                          (md5_value TEXT PRIMARY KEY,
                           username TEXT NOT NULL,
                           file_name TEXT NOT NULL)''')
        self.conn.commit()

    def insert_data(self, md5_value, username, file_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO gcj_data (md5_value, username, file_name) VALUES (?, ?, ?)",
                           (md5_value, username, file_name))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_data_by_md5(self, md5_value):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM gcj_data WHERE md5_value=?", (md5_value,))
        return cursor.fetchone()

    def close(self):
        self.conn.close()
