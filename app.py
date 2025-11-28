from flask import Flask, request, redirect, url_for
from db import init_db, get_saldo, add_expense

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
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="addChar('1')">1</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="addChar('2')">2</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="addChar('3')">3</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="addChar('4')">4</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="addChar('5')">5</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="addChar('6')">6</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="addChar('7')">7</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="addChar('8')">8</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="addChar('9')">9</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="addChar(',')">,</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="addChar('0')">0</button>
<button style=" background-color:#F0FFF0; width:60px; height:60px; border-radius:999px; font-size:25px; font-weight: bold" type="button" onclick="backspace()">C</button>
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

if __name__ == "__main__":
	app.run()

























