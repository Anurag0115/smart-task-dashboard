import sqlite3

def authenticate(username, password):
    conn = sqlite3.connect("tasks.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cur.fetchone()
    conn.close()
    return result
