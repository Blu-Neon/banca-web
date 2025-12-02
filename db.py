import os
import psycopg2
import psycopg2.extras

# Prende la stringa di connessione dall'env (Render)
DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    """
    Apre una connessione a PostgreSQL.
    Usa RealDictCursor così le righe sono accessibili come dizionario: row["id"], row["saldo"], ecc.
    """
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL non impostata nelle variabili d'ambiente")

    conn = psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    return conn


def init_db():
    """
    Crea le tabelle se non esistono:
    - users
    - accounts
    - transactions
    + indici
    """
    conn = get_connection()
    cur = conn.cursor()

    # users: solo login
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );
    """)

    # accounts: saldo per utente
    cur.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        saldo NUMERIC(12,2) NOT NULL DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # transactions: spese + entrate
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        amount NUMERIC(12,2) NOT NULL,
        category TEXT NOT NULL,
        type TEXT NOT NULL CHECK (type IN ('expense', 'income')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # indici
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_trans_user
    ON transactions(user_id);
    """)

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_trans_user_date
    ON transactions(user_id, created_at);
    """)

    conn.commit()
    conn.close()


def get_saldo(user_id: int) -> float:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT saldo FROM accounts WHERE user_id = %s;", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return 0.0
    return float(row["saldo"])


def add_expense(user_id: int, amount: float, category: str) -> None:
    """
    Registra una spesa (type='expense') e aggiorna il saldo (saldo - amount).
    """
    conn = get_connection()
    cur = conn.cursor()

    # transazione
    cur.execute(
        """
        INSERT INTO transactions (user_id, amount, category, type)
        VALUES (%s, %s, %s, 'expense');
        """,
        (user_id, amount, category),
    )

    # aggiorno il saldo
    cur.execute(
        """
        UPDATE accounts
        SET saldo = saldo - %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s;
        """,
        (amount, user_id),
    )

    conn.commit()
    conn.close()


def add_income(user_id: int, amount: float) -> None:
    """
    Registra un'entrata (type='income') e aggiorna il saldo (saldo + amount).
    category la fisso a 'entrata' per coerenza con il tuo codice.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO transactions (user_id, amount, category, type)
        VALUES (%s, %s, 'entrata', 'income');
        """,
        (user_id, amount),
    )

    cur.execute(
        """
        UPDATE accounts
        SET saldo = saldo + %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s;
        """,
        (amount, user_id),
    )

    conn.commit()
    conn.close()
