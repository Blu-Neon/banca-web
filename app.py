from flask import Flask, request, redirect, url_for
from db import init_db, get_saldo, add_expense

app= Flask(__name__)

init_db()

@app.route("/", methods=["GET"])
def home():
    saldo = get_saldo(1)
    return f"""
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

    background-image: url('https://images.unsplash.com/photo-1602292678572-16cb94ea0d88?            q=80&w=430&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;

    color: white;
    text-shadow: 0 0 5px black;
    ">

        <h1>
          <span style="color:#F0FFF0">Saldo: </span>
          <span style="color:#008000">{saldo:.2f} €</span>
        </h1>

        <p>Inserisci una nuova spesa:</p>
        <form method="POST" action="/add-expense" style="display:flex; flex-direction:column; gap:10px;">
          <input
            type="text"
            name="amount"
            placeholder="Importo (es. 12,50)"
            style="padding:10px; font-size:20px; font-family:Fantasy; color:#B22222; background-color:#F0FFF0; font-weight:bold"
            required
          />
          <select name="category" style="padding:10px; font-size:18px; background-color:#F0FFF0; font-family: time">
            <option value="spesa">Spesa</option>
            <option value="cibo">Cibo</option>
            <option value="altro">Altro</option>
            <option value="evitabile">Evitabile</option>
            <option value="eccezionale">Eccezionale</option>
          </select>
          <button type="submit" style="padding:10px; font-size:16px; font-family:time; background-color: #CD5C5C">
            Salva spesa
          </button>
        </form>
      </body>
    </html>
    """
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

























