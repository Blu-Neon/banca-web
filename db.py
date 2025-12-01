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

    # attivo le foreign key
    cur.execute("PRAGMA foreign_keys = ON;")

    # tabella utenti
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );
    """)

    # tabella saldo (UNO per utente)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        user_id INTEGER PRIMARY KEY,
        saldo REAL NOT NULL DEFAULT 0,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # tabella movimenti (spese + entrate)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # indici per performance
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trans_user ON transactions(user_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trans_user_date ON transactions(user_id, created_at);")

    conn.commit()
    conn.close()


def get_saldo(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT saldo FROM accounts WHERE user_id = ?;", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row["saldo"] if row else 0.0


def add_expense(user_id: int, amount: float, category: str) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transactions (user_id, amount, category, type)
        VALUES (?, ?, ?, 'expense')
    """, (user_id, amount, category))

    cur.execute("""
        UPDATE accounts
        SET saldo = saldo - ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?;
    """, (amount, user_id))

    conn.commit()
    conn.close()

def add_income(user_id: int, amount: float) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transactions (user_id, amount, category, type)
        VALUES (?, ?, 'entrata', 'income')
    """, (user_id, amount))

    cur.execute("""
        UPDATE accounts
        SET saldo = saldo + ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?;
    """, (amount, user_id))

    conn.commit()
    conn.close()









