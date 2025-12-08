import os
import psycopg2
import psycopg2.extras
from datetime import date

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

    cur.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS email TEXT UNIQUE;
    """)
    cur.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS reset_token TEXT;
    """)
    cur.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS reset_token_expires_at TIMESTAMP;
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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS travels (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES accounts(user_id) ON DELETE CASCADE,
        name TEXT,                                -- es: "Madrid", "Weekend Roma"
        budget NUMERIC(10,2) NOT NULL,           -- budget iniziale
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        closed_at TIMESTAMP,                      -- quando lo chiudi
        is_active BOOLEAN NOT NULL DEFAULT TRUE   -- viaggio attivo/sospeso
    );
    """)

    cur.execute(""" 
    CREATE TABLE IF NOT EXISTS travel_transactions (
        id SERIAL PRIMARY KEY,
        travel_id INTEGER NOT NULL REFERENCES travels(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES accounts(user_id) ON DELETE CASCADE,
        amount NUMERIC(10,2) NOT NULL,
        category TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    ); 
    """)

    # Aggiungo le colonne per ricordare la valuta originale (se non ci sono già)
    cur.execute("""
        ALTER TABLE travel_transactions
        ADD COLUMN IF NOT EXISTS original_amount NUMERIC(10,2),
        ADD COLUMN IF NOT EXISTS original_currency TEXT;
    """)

    #abbonamenti 

    cur.execute("""
    CREATE TABLE IF NOT EXISTS abbonamenti(
        abb_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        created_at DATE NOT NULL DEFAULT CURRENT_DATE,
        name TEXT NOT NULL,
        amount NUMERIC(12,2) NOT NULL,
        tipo TEXT NOT NULL CHECK (tipo IN ('mensile','annuale')),
        last_charge_date DATE
    );
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

def get_active_travel(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT *
        FROM travels
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY created_at DESC
        LIMIT 1;
        """,
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row  # dict oppure None

def start_travel(user_id: int, budget: float) -> int:
    """
    Chiude eventuale viaggio attivo e apre un nuovo viaggio con il budget dato.
    Ritorna l'id del nuovo viaggio.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Chiudi eventuale viaggio ancora attivo
    cur.execute(
        """
        UPDATE travels
        SET is_active = FALSE, closed_at = CURRENT_TIMESTAMP
        WHERE user_id = %s AND is_active = TRUE;
        """,
        (user_id,),
    )

    # Crea nuovo viaggio
    cur.execute(
        """
        INSERT INTO travels (user_id, budget)
        VALUES (%s, %s)
        RETURNING id;
        """,
        (user_id, budget),
    )
    travel_id = cur.fetchone()["id"]

    conn.commit()
    conn.close()
    return travel_id


def add_travel_expense(
    user_id: int,
    amount_eur: float,
    category: str,
    original_amount=None,
    original_currency=None,
) -> None:
    """
    Aggiunge una spesa al viaggio attivo dell'utente.
    amount_eur è già convertito in EUR.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Prendo il viaggio attivo
    cur.execute(
        """
        SELECT id
        FROM travels
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY created_at DESC
        LIMIT 1;
        """,
        (user_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        raise RuntimeError("Nessun viaggio attivo per questo utente")

    travel_id = row["id"]

    # Inserisco la spesa
    cur.execute(
        """
        INSERT INTO travel_transactions
            (travel_id, user_id, amount, category, original_amount, original_currency)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        (travel_id, user_id, amount_eur, category, original_amount, original_currency),
    )

    conn.commit()
    conn.close()


def get_travel_summary(user_id: int):
    """
    Restituisce (travel, total_spent, per_category) per il viaggio attivo.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Viaggio attivo
    cur.execute(
        """
        SELECT *
        FROM travels
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY created_at DESC
        LIMIT 1;
        """,
        (user_id,),
    )
    travel = cur.fetchone()
    if not travel:
        conn.close()
        return None, 0.0, []

    travel_id = travel["id"]

    # Totale speso
    cur.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total_spent
        FROM travel_transactions
        WHERE travel_id = %s;
        """,
        (travel_id,),
    )
    row = cur.fetchone()
    total_spent = float(row["total_spent"]) if row and row["total_spent"] is not None else 0.0

    # Totale per categoria
    cur.execute(
        """
        SELECT category, SUM(amount) AS total
        FROM travel_transactions
        WHERE travel_id = %s
        GROUP BY category
        ORDER BY total DESC;
        """,
        (travel_id,),
    )
    per_category = cur.fetchall()

    conn.close()
    return travel, total_spent, per_category

def close_active_travel(user_id: int, name: str | None = None):
    """
    Chiude il viaggio attivo:
    - calcola quanto è stato speso
    - calcola quanto resta del budget (può essere negativo se hai sforato)
    - aggiorna il saldo dell'utente (+resto)
    - salva nome, closed_at, is_active = FALSE
    Ritorna (travel, total_spent, remaining)
    """
    conn = get_connection()
    cur = conn.cursor()

    # Prendo viaggio attivo
    cur.execute(
        """
        SELECT *
        FROM travels
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY created_at DESC
        LIMIT 1;
        """,
        (user_id,),
    )
    travel = cur.fetchone()
    if not travel:
        conn.close()
        return None, 0.0, 0.0

    travel_id = travel["id"]
    budget = float(travel["budget"])

    # Totale speso
    cur.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total_spent
        FROM travel_transactions
        WHERE travel_id = %s;
        """,
        (travel_id,),
    )
    row = cur.fetchone()
    total_spent = float(row["total_spent"]) if row and row["total_spent"] is not None else 0.0

    remaining = budget - total_spent  # se >0 hai risparmiato; se <0 hai sforato

    # Aggiorno il viaggio (nome + chiusura)
    cur.execute(
        """
        UPDATE travels
        SET name = %s,
            is_active = FALSE,
            closed_at = CURRENT_TIMESTAMP
        WHERE id = %s;
        """,
        (name, travel_id),
    )

    # Aggiorno il saldo dell'utente
    cur.execute(
        """
        UPDATE accounts
        SET saldo = saldo + %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s;
        """,
        (remaining, user_id),
    )

    conn.commit()
    conn.close()
    return travel, total_spent, remaining

def get_travel_history(user_id: int):
    """
    Tutti i viaggi chiusi con totale speso e mese.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            t.id,
            t.name,
            t.budget,
            t.created_at,
            t.closed_at,
            TO_CHAR(t.created_at, 'YYYY-MM') AS month,
            COALESCE(SUM(tr.amount), 0) AS total_spent
        FROM travels t
        LEFT JOIN travel_transactions tr ON tr.travel_id = t.id
        WHERE t.user_id = %s AND t.is_active = FALSE
        GROUP BY t.id
        ORDER BY t.created_at DESC;
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# Abbonamenti 
def add_abbonamento(user_id: int, name: str, amount: float, tipo: str, created_at: date) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO abbonamenti (user_id, name, amount, tipo, created_at)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (user_id, name, amount, tipo, created_at),
    )
    conn.commit()
    conn.close()


def get_abbonamenti(user_id: int):
    """
    Ritorna una lista di dict:
    [{ 'abb_id': ..., 'name': ..., 'amount': ..., 'tipo': ..., 'created_at': ..., 'last_charge_date': ...}, ...]
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """
        SELECT abb_id, name, amount, tipo, created_at, last_charge_date
        FROM abbonamenti
        WHERE user_id = %s
        ORDER BY created_at;
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def check_abbonamenti_oggi(user_id: int):
    today_str = date.today().isoformat()
    last_check = session.get("last_abb_check")

    if last_check != today_str:
        # primo accesso di oggi → applico abbonamenti
        applica_abbonamenti(user_id)
        session["last_abb_check"] = today_str


def applica_abbonamenti(user_id: int) -> None:
    """
    Scala dal saldo gli abbonamenti dovuti "oggi" e aggiorna last_charge_date.
    - mensile: ogni 1° del mese
    - annuale: una volta all'anno nel giorno/mese di created_at
    """
    oggi = date.today()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT abb_id, name, amount, tipo, created_at, last_charge_date
        FROM abbonamenti
        WHERE user_id = %s;
        """,
        (user_id,),
    )
    rows = cur.fetchall()

    for abb_id, name, amount, tipo, created_at, last_charge in rows:
        deve_addebitare = False

        if tipo == "mensile":
            # mai addebitato oppure mese diverso dall'ultimo addebito
            if (last_charge is None or
                last_charge.year != oggi.year or
                last_charge.month != oggi.month):


                deve_addebitare = True

        elif tipo == "annuale":
            # mai addebitato oppure anno diverso
            if (last_charge is None or last_charge.year != oggi.year):

                # stessa data (giorno e mese) di quando è stato creato
                if oggi.month == created_at.month:
                    deve_addebitare = True

        if deve_addebitare:
            # scala dal saldo
            cur.execute(
                """
                UPDATE accounts
                SET saldo = saldo - %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s;
                """,
                (amount, user_id),
            )

            # aggiorna la data dell'ultimo addebito
            cur.execute(
                """
                UPDATE abbonamenti
                SET last_charge_date = %s
                WHERE abb_id = %s;
                """,
                (oggi, abb_id),
            )

    conn.commit()
    conn.close()
