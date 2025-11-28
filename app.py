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
      <body style="font-family: sans-serif; padding: 20px; max-width: 480px; margin: auto;">
        <h1>Saldo: {saldo:.2f} €</h1>
        <p>Inserisci una nuova spesa:</p>
        <form method="POST" action="/add-expense" style="display:flex; flex-direction:column; gap:10px;">
          <input
            type="text"
            name="amount"
            placeholder="Importo (es. 12,50)"
            style="padding:10px; font-size:16px;"
            required
          />
          <select name="category" style="padding:10px; font-size:16px;">
            <option value="spesa">Spesa</option>
            <option value="cibo">Cibo</option>
            <option value="altro">Altro</option>
            <option value="evitabile">Evitabile</option>
            <option value="eccezionale">Eccezionale</option>
          </select>
          <button type="submit" style="padding:10px; font-size:16px;">
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

























