import sqlite3

DB_NAME = "agent_memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_key TEXT UNIQUE,
            rule_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS action_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT,
            details TEXT,
            status TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_preference(key, value):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO preferences (rule_key, rule_value) VALUES (?, ?)
    ''', (key, value))
    conn.commit()
    conn.close()

def get_all_preferences():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT rule_key, rule_value FROM preferences')
    prefs = cursor.fetchall()
    conn.close()
    return {k: v for k, v in prefs}

def log_action(action_type, details, status="SUCCESS"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO action_logs (action_type, details, status) VALUES (?, ?, ?)
    ''', (action_type, details, status))
    conn.commit()
    conn.close()
