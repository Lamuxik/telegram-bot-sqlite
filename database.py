import sqlite3

db = sqlite3.connect("bot.db")
cursor = db.cursor()


def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        client_name TEXT NOT NULL,
        client_username TEXT,
        problem TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'new'
    )
    """)

    db.commit()


def add_application(client_id, client_name, client_username, problem):
    cursor.execute("""
    INSERT INTO applications
    (client_id, client_name, client_username, problem)
    VALUES (?, ?, ?, ?)
    """, (client_id, client_name, client_username, problem))

    db.commit()

    return cursor.lastrowid


def get_application(application_id):
    cursor.execute("""
    SELECT client_id, client_name, client_username, status
    FROM applications
    WHERE id = ?
    """, (application_id,))

    return cursor.fetchone()


def update_application_status(application_id, status):
    cursor.execute("""
    UPDATE applications
    SET status = ?
    WHERE id = ? AND status = 'new'
    """, (status, application_id))

    db.commit()

    return cursor.rowcount


def get_new_applications():
    cursor.execute("""
    SELECT id, client_name, problem
    FROM applications
    WHERE status = ?
    ORDER BY id ASC
    """, ("new",))

    return cursor.fetchall()