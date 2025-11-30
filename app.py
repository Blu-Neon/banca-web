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

  <form method="GET" action="/">
    <button class="menu-btn" style="background:#8B4513;">NULL</button>
  </form>

  <form method="GET" action="/">
    <button class="menu-btn" style="background:#556B2F;">NULL</button>
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

  <form method="GET" action="/statistiche">
    <button class="menu-btn" style="background:#8B4513;">NULL</button>
  </form>

  <form method="GET" action="/">
    <button class="menu-btn" style="background:#556B2F;">NULL</button>
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

    # Spese del mese, in ordine di data
    cur.execute("""
        SELECT amount, category, date
        FROM expenses
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        ORDER BY date ASC
    """)
    dati = cur.fetchall()

    # Ultime 5 spese (in assoluto)
    cur.execute("""
        SELECT amount, category, date
        FROM expenses
        ORDER BY date DESC
        LIMIT 5
    """)
    ultime_cinque = cur.fetchall()

    # Etichette (date) per il grafico
    labels = [row[2] for row in dati]

    # Calcolo del saldo progressivo nel mese
    saldo_attuale = get_saldo(1)
    totale_spese_mese = sum(row[0] for row in dati)
    saldo_inizio_mese = saldo_attuale + totale_spese_mese

    valori_saldo = []
    saldo_prog = saldo_inizio_mese
    for amount, category, date in dati:
        saldo_prog -= amount
        valori_saldo.append(round(saldo_prog, 2))

    # Costruisco la lista delle ultime 5 spese in HTML
    spese_html = ""
    for amount, category, date in ultime_cinque:
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

          <form method="GET" action="/statistiche">
            <button class="menu-btn" style="background:#8B4513;">Statistiche</button>
          </form>

          <form method="GET" action="/grafico">
            <button class="menu-btn" style="background:#556B2F;">Grafico mese</button>
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

        <canvas id="mioGrafico" style="max-width:100%; background:rgba(0,0,0,0.3); background-color: white; border-radius:50px; padding:10px; width:430px; height:300px;margin-left:2px;opacity: 0.4"></canvas>

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



if __name__ == "__main__":
	app.run()

























