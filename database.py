import sqlite3
import os

def connection_db():
    connection = None
    try:
        connection = sqlite3.connect(str(os.path.dirname(__file__)) + "/users.db")
        print("Connection successful")
    except sqlite3.Error as e:
        print("The error '{e}' occurred")
    return connection


async def query_db(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    i = 0
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()

        if (len(result) != 0):
            if (len(result[i]) == 1):
                for i in range(0, len(result)):
                    result[i] = result[i][0]
        return result
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")


table_users = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER NOT NULL UNIQUE,
        name TEXT NOT NULL
)
"""

table_state = """
    CREATE TABLE IF NOT EXISTS state (
        id INTEGER,
        date DATE NOT NULL,
        work TEXT NOT NULL,
        ves INTEGER NOT NULL,
        report TEXT NOT NULL,
        FOREIGN KEY (id) REFERENCES users(id)
)
"""

connection_users = connection_db()