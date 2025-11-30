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
        username TEXT UNIQUE,
        password_hash TEXT,
        saldo REAL NOT NULL DEFAULT 0
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2) MIGRAZIONE: se la tabella users esisteva con schema vecchio,
    #    aggiungo le colonne che mancano (senza cancellare nulla).

    cur.execute("PRAGMA table_info(users);")
    cols = [row["name"] for row in cur.fetchall()]

    if "username" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN username TEXT;")

    if "password_hash" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN password_hash TEXT;")

    if "saldo" not in cols:
        # se veniva da uno schema senza saldo (non è il tuo caso, ma per sicurezza)
        cur.execute("ALTER TABLE users ADD COLUMN saldo REAL NOT NULL DEFAULT 0;")

    conn.commit()
    conn.close()

def get_saldo(user_id: int) -> float:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT saldo FROM users WHERE id = ?;", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row["saldo"] if row else 0.0

def add_expense(user_id: int, amount: float, category: str) -> None:
    """Registra una spesa e aggiorna il saldo (saldo = saldo - amount)."""
    conn = get_connection()
    cur = conn.cursor()

    #inserico la spesa 
    cur.execute(
        "INSERT INTO expenses (user_id, amount, category) VALUES (?, ?, ?);",
        (user_id, amount, category)
    )

    #aggiorno il saldo 
    cur.execute(
        "UPDATE users SET saldo = saldo - ? WHERE id = ?;",
        (amount, user_id)
    )

    conn.commit()
    conn.close()

def add_income(user_id: int, amount: float) -> None:
    conn = get_connection()
    cur = conn.cursor()

    #salvo anche le entrate 

    cur.execute(
        "INSERT INTO expenses (user_id, amount, category) VALUES (?, ?, ?)",
        (user_id, amount, "entrata")
    )

    cur.execute(
        "UPDATE users SET saldo = saldo + ? WHERE id = ?;",
        (amount, user_id)
    )
    conn.commit()
    conn.close()








