from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).with_name("banca.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        saldo REAL NOT NULL
    );
    """)

    # controlla se l'utente esiste
    cur.execute("SELECT COUNT(*) AS c FROM users;")
    count = cur.fetchone()["c"]

    # se non c'è nessun utente, crea l'utente con saldo iniziale
    if count == 0:
        cur.execute(
            "INSERT INTO users (id, saldo) VALUES (?, ?);",
            (1, 1000.0)
        )

    conn.commit()
    conn.close()

def get_saldo(user_id: int) -> float:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT saldo FROM users WHERE id = ?;", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row["saldo"] if row else 0.0
