import sqlite3
import os

# Toggle this to True when you want to apply changes and reset the DB
RESET_DB = True

def init_db():
    if RESET_DB and os.path.exists("tasks.db"):
        os.remove("tasks.db")

    if not os.path.exists("tasks.db"):
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                project TEXT,
                employee TEXT,
                status TEXT,
                start_date TEXT,
                due_date TEXT,
                completed_date TEXT,
                priority TEXT
            )
        ''')

        sample_data = [
            (1, 'Alpha', 'Anurag', 'Completed', '2024-06-01', '2024-06-05', '2024-06-04', 'High'),
            (2, 'Beta', 'Ravi', 'Pending', '2024-06-03', '2024-06-10', '', 'Medium'),
            (3, 'Alpha', 'Anurag', 'In Progress', '2024-06-05', '2024-06-12', '', 'High'),
            (4, 'Gamma', 'Astha', 'Pending', '2024-06-01', '2024-06-07', '', 'Low'),
            (5, 'Beta', 'Anurag', 'Completed', '2024-06-08', '2024-06-15', '2024-06-13', 'Medium'),
            (6, 'Gamma', 'Ravi', 'In Progress', '2024-06-06', '2024-06-14', '', 'High')
        ]

        cursor.executemany('''
            INSERT INTO tasks (id, project, employee, status, start_date, due_date, completed_date, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_data)

        conn.commit()
        conn.close()
