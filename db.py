import sqlite3


class DataBase():

    def __init__(self, name):
        # Initial, connect with db.
        self.db = sqlite3.connect(str(name))
        self.cursor = self.db.cursor()

    def get_identifier(self, user_id):
        # Return all users identifier.
        return self.cursor.execute("SELECT * FROM records WHERE user_id=?", (user_id,))

    def add_identifier(self,user_id, indetifier, status):
        self.cursor.execute("""INSERT INTO records (user_id, identifier, status_id)
            VALUES (?, ?, ?);""",
            (user_id, indetifier, status)
            )
        self.db.commit()

    def delete_record(self, user_id):
        self.cursor.execute("DELETE FROM records WHERE user_id=?;", (user_id,))
        self.db.commit()

    def count(self):
        return self.cursor.execute("SELECT COUNT(*) AS LEN FROM records")
    
    def get_item(self, offset, limit):
        return self.cursor.execute("SELECT * FROM records LIMIT ? OFFSET ?;", (limit, offset))

    def update_record(self, user_id, status):
        self.cursor.execute("UPDATE records SET status_id = ? WHERE user_id = ?;", (status, user_id))
        self.db.commit()
