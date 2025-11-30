from flask import Flask, request, redirect, url_for
from db import init_db, get_saldo, add_expense, add_income, get_connection
import json

app= Flask(__name__)

init_db()

@app.route("/", methods=["GET"])
def home():
    saldo = f"{get_saldo(1):.2f}"
    html="""
       <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Banca</title>
      </head>
      <body style="
    font-family: sans-serif;
    padding: 20px;
    max-width: 480px;
    margin: auto;

    background-image: url('https://images.unsplash.com/photo-1602292678572-16cb94ea0d88?q=80&w=430&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;

    color: white;
    text-shadow: 0 0 5px black;
    ">
    
    
<style>
  #menu-button {
    position: fixed;
    top: 20px;
    right: 20px;
    font-size: 30px;
    background: rgba(255,255,255,0.7);
    border-radius: 10px;
    padding: 5px 12px;
    border: none;
    cursor: pointer;
  }

  #dropdown-menu {
    position: fixed;
    top: 70px;
    right: 20px;
    background: rgba(255,255,255,0.9);
    padding: 15px;
    border-radius: 15px;
    display: flex;
    flex-direction: column;
    gap: 10px;

    opacity: 0;
    transform: translateY(-10px);
    pointer-events: none;

    /* animazione */
    transition: opacity 0.2s ease-out, transform 0.2s ease-out;
  }

  #dropdown-menu.open {
    opacity: 1;
    transform: translateY(0);
    pointer-events: auto;
  }

  .menu-btn {
    padding: 10px;
    border-radius: 10px;
    font-size: 16px;
    border: none;
    cursor: pointer;
    width: 160px;
  }
</style>

<button id="menu-button">☰</button>

<div id="dropdown-menu">
  <form method="GET" action="/update-saldo">
    <button class="menu-btn" style="background:#20B2AA;">Aggiorna saldo</button>
  </form>

  <form method="GET" action="/grafico">
    <button class="menu-btn" style="background:#CD5C5C;">Grafico del mese</button>
  </form>

  <form method="GET" action="/tipologia">
    <button class="menu-btn" style="background:#8B4513;">Spese per tipologia</button>
  </form>

  <form method="GET" action="/storico">
    <button class="menu-btn" style="background:#556B2F;">Storico</button>
  </form>
</div>

<script>
  const menuBtn = document.getElementById("menu-button");
  const drop = document.getElementById("dropdown-menu");

  menuBtn.onclick = () => {
    drop.classList.toggle("open");
  };
</script>


        <h1>
          <span style="color:#F0FFF0">Saldo: </span>
          <span style="color:#008000">__SALDO__ €</span>
        </h1>


        <p>Inserisci una nuova spesa:</p>
        <form method="POST" action="/add-expense" style="display:flex; flex-direction:column; gap:10px;">
         <input
            type="text"
            id="amount-input"
            name="amount"
            placeholder="Importo (es. 12,50)"
            style="padding:10px; font-size:20px; font-family:Fantasy; color:#B22222; background-color:#F0FFF0; font-weight:bold"
            required
            />

          <select name="category" style="padding:10px; font-size:18px; background-color:#F0FFF0; font-family: time; border-radius:34px">
            <option value="spesa">Spesa</option>
            <option value="cibo">Cibo</option>
            <option value="altro">Altro</option>
            <option value="evitabile">Evitabile</option>
            <option value="eccezionale">Eccezionale</option>
          </select>
          <button type="submit" style="padding:10px; font-size:16px; font-family:time; background-color: #CD5C5C; border-radius:34px; border-color:#F0FFF0">
            Salva spesa
          </button>
        </form>

        
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:40px; margin-top:50px; margin-left: 40px">
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="addChar('1')">1</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="addChar('2')">2</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="addChar('3')">3</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="addChar('4')">4</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="addChar('5')">5</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="addChar('6')">6</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="addChar('7')">7</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="addChar('8')">8</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="addChar('9')">9</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="addChar(',')">,</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="addChar('0')">0</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; color:black; font-weight: bold" type="button" onclick="backspace()">C</button>
<script>
function addChar(ch) {
const input = document.getElementById('amount-input');
if (ch === ',' && input.value.includes(',')) {
return; // evita due virgole
}
if (input.value === '0' && ch !== ',') {
input.value = ch; // sostituisce lo zero iniziale
} else {
input.value = input.value + ch;
}
}
function clearInput() {
const input = document.getElementById('amount-input');
input.value = '';
}
function backspace() {
const input = document.getElementById('amount-input');
input.value = input.value.slice(0, -1);
}
</script>
      </body>
    </html>
    """

    return html.replace("__SALDO__", saldo)
@app.route("/add-expense", methods=["POST"])
def add_expense_route():
    amount_str = request.form.get("amount", "").replace(",", ".")
    category = request.form.get("category", "altro")

    try:
        amount = float(amount_str)
    except ValueError:
        return redirect(url_for("home"))
    if amount <=0:
        return redirect(url_for("home"))
    add_expense(1, amount, category)
    return redirect(url_for("home"))


@app.route("/update-saldo", methods=["GET", "POST"])
def update_saldo():
    # Se arriva un POST → aggiorno il saldo e torno alla home
    if request.method == "POST":
        amount_str = request.form.get("amount", "").replace(",", ".")
        try:
            amount = float(amount_str)
        except ValueError:
            return redirect(url_for("update_saldo"))

        if amount <= 0:
            return redirect(url_for("update_saldo"))

        add_income(1, amount)
        return redirect(url_for("home"))

    # Se è un GET → mostro la pagina
    saldo = f"{get_saldo(1):.2f}"
    html = """
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Aggiorna saldo</title>
      </head>

      <body style="
        font-family: sans-serif;
        padding: 20px;
        max-width: 480px;
        margin: auto;

        background-image: url('https://images.unsplash.com/photo-1602292678572-16cb94ea0d88?q=80&w=430&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;

        color: white;
        text-shadow: 0 0 5px black;
      ">
      
         
    
<style>
  #menu-button {
    position: fixed;
    top: 20px;
    right: 20px;
    font-size: 30px;
    background: rgba(255,255,255,0.7);
    border-radius: 10px;
    padding: 5px 12px;
    border: none;
    cursor: pointer;
  }

  #dropdown-menu {
    position: fixed;
    top: 70px;
    right: 20px;
    background: rgba(255,255,255,0.9);
    padding: 15px;
    border-radius: 15px;
    display: flex;
    flex-direction: column;
    gap: 10px;

    opacity: 0;
    transform: translateY(-10px);
    pointer-events: none;

    /* animazione */
    transition: opacity 0.2s ease-out, transform 0.2s ease-out;
  }

  #dropdown-menu.open {
    opacity: 1;
    transform: translateY(0);
    pointer-events: auto;
  }

  .menu-btn {
    padding: 10px;
    border-radius: 10px;
    font-size: 16px;
    border: none;
    cursor: pointer;
    width: 160px;
  }
</style>

<button id="menu-button">☰</button>

<div id="dropdown-menu">
  <form method="GET" action="/">
    <button class="menu-btn" style="background:#20B2AA;">Home</button>
  </form>

  <form method="GET" action="/grafico">
    <button class="menu-btn" style="background:#CD5C5C;">Grafico del mese</button>
  </form>

  <form method="GET" action="/tipologia">
    <button class="menu-btn" style="background:#8B4513;">Spese per tipologia</button>
  </form>

  <form method="GET" action="/storico">
    <button class="menu-btn" style="background:#556B2F;">Storico</button>
  </form>
</div>

<script>
  const menuBtn = document.getElementById("menu-button");
  const drop = document.getElementById("dropdown-menu");

  menuBtn.onclick = () => {
    drop.classList.toggle("open");
  };
</script>


        <h1>Aggiorna saldo</h1>
        <p>Saldo attuale: <strong>__SALDO__ €</strong></p>

        <form method="POST" action="/update-saldo"
              style="display:flex; flex-direction:column; gap:15px; margin-top:25px;">

          <input type="text"
                 id="amount-input"
                 name="amount"
                 placeholder="Importo (es. 150,00)"
                 style="padding:12px; font-size:20px; background:#F0FFF0; color:#006400; border-radius:12px; font-weight:bold;"
                 required />

          <button type="submit"
                  style="padding:12px; font-size:18px; background:#32CD32; color:white; border-radius:25px;">
            Aggiungi al saldo
          </button>
        </form>

        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:40px; margin-top:50px; margin-left: 40px">
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="addChar('1')">1</button>
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="addChar('2')">2</button>
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="addChar('3')">3</button>
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="addChar('4')">4</button>
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="addChar('5')">5</button>
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="addChar('6')">6</button>
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="addChar('7')">7</button>
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="addChar('8')">8</button>
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="addChar('9')">9</button>
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="addChar(',')">,</button>
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="addChar('0')">0</button>
          <button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; color: black; font-size:25px; font-weight: bold" type="button" onclick="backspace()">C</button>
        </div>


        <script>
        function addChar(ch) {
          const input = document.getElementById('amount-input');
          if (ch === ',' && input.value.includes(',')) {
            return;
          }
          if (input.value === '0' && ch !== ',') {
            input.value = ch;
          } else {
            input.value = input.value + ch;
          }
        }

        function clearInput() {
          const input = document.getElementById('amount-input');
          input.value = '';
        }

        function backspace() {
          const input = document.getElementById('amount-input');
          input.value = input.value.slice(0, -1);
        }
        </script>

      </body>
    </html>
   
    """
    return html.replace("__SALDO__", saldo)

@app.route("/grafico", methods=["GET"])
def grafico():
    cur = get_connection().cursor()

    # Movimenti del mese (entrate + spese), in ordine di data
    cur.execute("""
        SELECT amount, category, date
        FROM expenses
        WHERE user_id = 1
          AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        ORDER BY date ASC
    """)
    dati = cur.fetchall()

    # Ultimi 5 movimenti in assoluto (spese + entrate)
    cur.execute("""
        SELECT amount, category, date
        FROM expenses
        WHERE user_id = 1
        ORDER BY date DESC
        LIMIT 5
    """)
    ultime_cinque = cur.fetchall()

    # Etichette (solo la data, senza orario)
    labels = [row["date"].split(" ")[0] for row in dati]

    # Costruisco i movimenti con il segno:
    # - spesa    -> movimento NEGATIVO
    # - entrata  -> movimento POSITIVO
    movimenti = []
    for row in dati:
        amount = float(row["amount"])
        category = row["category"]
        if category == "entrata":
            movimenti.append(amount)     # entrata: +amount
        else:
            movimenti.append(-amount)    # spesa:   -amount

    saldo_attuale = get_saldo(1)

    # saldo_finale = saldo_inizio_mese + somma(movimenti)
    # => saldo_inizio_mese = saldo_finale - somma(movimenti)
    saldo_inizio_mese = saldo_attuale - sum(movimenti)

    valori_saldo = []
    saldo_prog = saldo_inizio_mese
    for movimento in movimenti:
        saldo_prog += movimento
        valori_saldo.append(round(saldo_prog, 2))

    # Costruisco la lista delle ultime 5 spese/movimenti in HTML
    spese_html = ""
    for row in ultime_cinque:
        amount = float(row["amount"])
        category = row["category"]
        date = ["date"]
        spese_html += f"""
        <div class="spesa">
            <strong>{amount:.2f} €</strong> — {category}<br>
            <small>{date}</small>
        </div>
        """


    html = """
<!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Grafico saldo</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                font-family: sans-serif;
                padding: 20px;
                max-width: 480px;
                margin: auto;

                background-image: url('https://images.unsplash.com/photo-1602292678572-16cb94ea0d88?q=80&w=430&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;

                color: white;
                text-shadow: 0 0 5px black;
            }

            #menu-button {
                position: fixed;
                top: 20px;
                right: 20px;
                font-size: 30px;
                background: rgba(255,255,255,0.7);
                border-radius: 10px;
                padding: 5px 12px;
                border: none;
                cursor: pointer;
            }

            #dropdown-menu {
                position: fixed;
                top: 70px;
                right: 20px;
                background: rgba(255,255,255,0.9);
                padding: 15px;
                border-radius: 15px;
                display: flex;
                flex-direction: column;
                gap: 10px;

                opacity: 0;
                transform: translateY(-10px);
                pointer-events: none;
                transition: opacity 0.2s ease-out, transform 0.2s ease-out;
            }

            #dropdown-menu.open {
                opacity: 1;
                transform: translateY(0);
                pointer-events: auto;
            }

            .menu-btn {
                padding: 10px;
                border-radius: 10px;
                font-size: 16px;
                border: none;
                cursor: pointer;
                width: 160px;
            }

            .spesa {
                padding: 10px;
                margin: 8px 0;
                border-bottom: 1px solid rgba(255,255,255,0.4);
            }
        </style>
    </head>
    <body>

        <button id="menu-button">☰</button>

        <div id="dropdown-menu">
          <form method="GET" action="/">
            <button class="menu-btn" style="background:#20B2AA;">Home</button>
          </form>

          <form method="GET" action="/update-saldo">
            <button class="menu-btn" style="background:#CD5C5C;">Aggiorna saldo</button>
          </form>

          <form method="GET" action="/tipologia">
            <button class="menu-btn" style="background:#8B4513;">Spese per tipologia</button>
          </form>

          <form method="GET" action="/storico">
            <button class="menu-btn" style="background:#556B2F;">Storico</button>
          </form>
        </div>

        <script>
          const menuBtn = document.getElementById("menu-button");
          const drop = document.getElementById("dropdown-menu");

          menuBtn.onclick = () => {
            drop.classList.toggle("open");
          };
        </script>

        <h2>Andamento del saldo del mese</h2>

        <canvas id="mioGrafico" style="max-width:100%; background:rgba(0,0,0,0.3); background-color: white; border-radius:10px; padding:15px; width:430px; height:300px;margin-left:2px;opacity: 0.8;"></canvas>

        <script>
            const labels = __LABELS__;
            const dataValues = __VALUES__;

            const ctx = document.getElementById('mioGrafico');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Saldo',
                        data: dataValues,
                        fill: false,
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                }
            });
        </script>

        <h2>Ultime 5 spese</h2>

        __LISTA_SPESE__

        <br>

    </body>
    </html>
    """

    html = html.replace("__LABELS__", json.dumps(labels))
    html = html.replace("__VALUES__", json.dumps(valori_saldo))
    html = html.replace("__LISTA_SPESE__", spese_html)

    return html

@app.route("/tipologia", methods=["GET"])
def tipologia():
    conn = get_connection()
    cur = conn.cursor()

    # Totale spese per categoria nel mese corrente (escludo le entrate)
    cur.execute("""
        SELECT category, SUM(amount) AS totale
        FROM expenses
        WHERE user_id = 1
          AND category != 'entrata'
          AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        GROUP BY category
        ORDER BY totale DESC
    """)
    righe = cur.fetchall()
    conn.close()

    # Se non ci sono spese, niente grafico
    labels = [r["category"] for r in righe]
    values = [float(r["totale"]) for r in righe]

    # Colori per la torta (se ci sono più categorie li riciclo)
    base_colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"]
    if len(labels) == 0:
        colors = []
    elif len(labels) <= len(base_colors):
        colors = base_colors[:len(labels)]
    else:
        # ripete la lista finché basta
        ripetizioni = (len(labels) // len(base_colors)) + 1
        colors = (base_colors * ripetizioni)[:len(labels)]

    # Legenda sotto il grafico
    legenda_html = ""
    for cat, col, val in zip(labels, colors, values):
        legenda_html += f"""
        <div style="display:flex; align-items:center; margin-bottom:6px;">
            <span style="display:inline-block; width:16px; height:16px; border-radius:4px; margin-right:8px; background-color:{col};"></span>
            <span>{cat}: {val:.2f} €</span>
        </div>
        """

    html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Tipologia spese</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: sans-serif;
            padding: 20px;
            max-width: 480px;
            margin: auto;

            background-image: url('https://images.unsplash.com/photo-1602292678572-16cb94ea0d88?q=80&w=430&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;

            color: white;
            text-shadow: 0 0 5px black;
        }

        #menu-button {
            position: fixed;
            top: 20px;
            right: 20px;
            font-size: 30px;
            background: rgba(255,255,255,0.7);
            border-radius: 10px;
            padding: 5px 12px;
            border: none;
            cursor: pointer;
        }

        #dropdown-menu {
            position: fixed;
            top: 70px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            padding: 15px;
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;

            opacity: 0;
            transform: translateY(-10px);
            pointer-events: none;
            transition: opacity 0.2s ease-out, transform 0.2s ease-out;
        }

        #dropdown-menu.open {
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }

        .menu-btn {
            padding: 10px;
            border-radius: 10px;
            font-size: 16px;
            border: none;
            cursor: pointer;
            width: 160px;
        }

        .box-bianca {
            background: rgba(255,255,255,0.8);
            border-radius: 20px;
            padding: 15px;
            margin-top: 20px;
            color: #222;
            text-shadow: none;
        }
    </style>
</head>
<body>

    <button id="menu-button">☰</button>

    <div id="dropdown-menu">
      <form method="GET" action="/">
        <button class="menu-btn" style="background:#20B2AA;">Home</button>
      </form>

      <form method="GET" action="/update-saldo">
        <button class="menu-btn" style="background:#CD5C5C;">Aggiorna saldo</button>
      </form>

      <form method="GET" action="/grafico">
        <button class="menu-btn" style="background:#556B2F;">Grafico mese</button>
      </form>

      <form method="GET" action="/storico">
        <button class="menu-btn" style="background:#8B4513;">Storico</button>
      </form>
    </div>

    <script>
      const menuBtn = document.getElementById("menu-button");
      const drop = document.getElementById("dropdown-menu");

      menuBtn.onclick = () => {
        drop.classList.toggle("open");
      };
    </script>

    <h2>Tipologia spese del mese</h2>

    <div class="box-bianca">
        <canvas id="torta" style="max-width:100%;"></canvas>
    </div>

    <script>
        const labels = __LABELS__;
        const dataValues = __VALUES__;
        const colors = __COLORS__;

        const ctx = document.getElementById('torta');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: dataValues,
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false  // legenda la facciamo noi sotto
                    }
                }
            }
        });
    </script>

    <h3 style="margin-top:25px;">Legenda</h3>
    <div class="box-bianca">
        __LEGENDA__
    </div>

</body>
</html>
    """

    html = html.replace("__LABELS__", json.dumps(labels))
    html = html.replace("__VALUES__", json.dumps(values))
    html = html.replace("__COLORS__", json.dumps(colors))
    html = html.replace("__LEGENDA__", legenda_html)

    return html

@app.route("/storico", methods=["GET"])
def storico():
    conn = get_connection()
    cur = conn.cursor()

    # Totale spese (non entrate) per ogni mese dell'anno corrente
    cur.execute("""
        SELECT strftime('%Y-%m', date) AS ym,
               SUM(CASE WHEN category != 'entrata' THEN amount ELSE 0 END) AS totale
        FROM expenses
        WHERE user_id = 1
          AND strftime('%Y', date) = strftime('%Y', 'now')
        GROUP BY ym
        ORDER BY ym ASC;
    """)
    righe = cur.fetchall()
    conn.close()

    # Mappa numero mese -> nome mese in italiano
    nomi_mesi = {
        "01": "Gennaio",
        "02": "Febbraio",
        "03": "Marzo",
        "04": "Aprile",
        "05": "Maggio",
        "06": "Giugno",
        "07": "Luglio",
        "08": "Agosto",
        "09": "Settembre",
        "10": "Ottobre",
        "11": "Novembre",
        "12": "Dicembre",
    }

    storico_html = ""
    for row in righe:
        ym = row["ym"]          # tipo "2025-03"
        totale = row["totale"] or 0.0
        year, month_num = ym.split("-")
        nome_mese = nomi_mesi.get(month_num, month_num)

        storico_html += f"""
        <div class="riga-mese">
            <strong>{nome_mese}</strong>: {float(totale):.2f} €
        </div>
        """

    # Se nessuna spesa quest'anno
    if not storico_html:
        storico_html = """
        <p>Nessuna spesa registrata quest'anno.</p>
        """

    html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Storico spese annuale</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: sans-serif;
            padding: 20px;
            max-width: 480px;
            margin: auto;

            background-image: url('https://images.unsplash.com/photo-1602292678572-16cb94ea0d88?q=80&w=430&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;

            color: white;
            text-shadow: 0 0 5px black;
        }

        #menu-button {
            position: fixed;
            top: 20px;
            right: 20px;
            font-size: 30px;
            background: rgba(255,255,255,0.7);
            border-radius: 10px;
            padding: 5px 12px;
            border: none;
            cursor: pointer;
        }

        #dropdown-menu {
            position: fixed;
            top: 70px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            padding: 15px;
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;

            opacity: 0;
            transform: translateY(-10px);
            pointer-events: none;
            transition: opacity 0.2s ease-out, transform 0.2s ease-out;
        }

        #dropdown-menu.open {
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }

        .menu-btn {
            padding: 10px;
            border-radius: 10px;
            font-size: 16px;
            border: none;
            cursor: pointer;
            width: 160px;
        }

        .box-bianca {
            background: rgba(255,255,255,0.85);
            border-radius: 20px;
            padding: 15px;
            margin-top: 20px;
            color: #222;
            text-shadow: none;
        }

        .riga-mese {
            padding: 6px 0;
            border-bottom: 1px solid rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>

    <button id="menu-button">☰</button>

    <div id="dropdown-menu">
      <form method="GET" action="/">
        <button class="menu-btn" style="background:#20B2AA;">Home</button>
      </form>

      <form method="GET" action="/update-saldo">
        <button class="menu-btn" style="background:#CD5C5C;">Aggiorna saldo</button>
      </form>

      <form method="GET" action="/grafico">
        <button class="menu-btn" style="background:#556B2F;">Grafico mese</button>
      </form>

      <form method="GET" action="/tipologia">
        <button class="menu-btn" style="background:#8B4513;">Tipologia spese</button>
      </form>

      <form method="GET" action="/storico">
        <button class="menu-btn" style="background:#1E90FF;">Storico annuale</button>
      </form>
    </div>

    <script>
      const menuBtn = document.getElementById("menu-button");
      const drop = document.getElementById("dropdown-menu");

      menuBtn.onclick = () => {
        drop.classList.toggle("open");
      };
    </script>

    <h2>Storico spese dell'anno</h2>

    <div class="box-bianca">
        __STORICO__
    </div>

</body>
</html>
    """

    html = html.replace("__STORICO__", storico_html)
    return html


if __name__ == "__main__":
	app.run()

























