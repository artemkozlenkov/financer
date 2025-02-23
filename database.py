import sqlite3

class Database:
    def __init__(self, db_name="assets.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                value REAL NOT NULL,
                currency TEXT NOT NULL,
                location TEXT,
                notes TEXT
            )
        ''')
        self.conn.commit()

    def load_assets(self):
        self.cursor.execute("SELECT name, type, value, currency, location, notes FROM assets")
        rows = self.cursor.fetchall()
        return [{"Asset Name": row[0], "Type": row[1], "Value": row[2], "Currency": row[3], "Location": row[4], "Notes": row[5]} for row in rows]

    def save_asset(self, asset):
        self.cursor.execute('''
            INSERT INTO assets (name, type, value, currency, location, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (asset["Asset Name"], asset["Type"], asset["Value"], asset["Currency"], asset["Location"], asset["Notes"]))
        self.conn.commit()

    def delete_asset(self, asset):
        self.cursor.execute('''
            DELETE FROM assets
            WHERE name = ? AND type = ? AND value = ? AND currency = ? AND location = ? AND notes = ?
        ''', (asset["Asset Name"], asset["Type"], asset["Value"], asset["Currency"], asset["Location"], asset["Notes"]))
        self.conn.commit()

    def update_asset(self, old_asset, new_asset):
        self.cursor.execute('''
            UPDATE assets
            SET name = ?, type = ?, value = ?, currency = ?, location = ?, notes = ?
            WHERE name = ? AND type = ? AND value = ? AND currency = ? AND location = ? AND notes = ?
        ''', (new_asset["Asset Name"], new_asset["Type"], new_asset["Value"], new_asset["Currency"], new_asset["Location"], new_asset["Notes"],
              old_asset["Asset Name"], old_asset["Type"], old_asset["Value"], old_asset["Currency"], old_asset["Location"], old_asset["Notes"]))
        self.conn.commit()

    def close(self):
        self.conn.close()