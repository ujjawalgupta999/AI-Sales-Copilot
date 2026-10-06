import sqlite3

def get_user_record(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Use a parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    return cursor.fetchall()

def get_user_record(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 🚨 DANGER: Raw f-string used for a SQL query (SQL Injection!)
    query = f"SELECT * FROM users WHERE username = '{username}'"
    
    cursor.execute(query)
    return cursor.fetchall()