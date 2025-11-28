from flask import Flask
from db import init_db, get_saldo

app= Flask(__name__)

init_db()

@app.route("/")
def home():
    saldo = get_saldo(1)
    return f"""
	<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Banca</title>
    </head>
    <body style="front-family: sans-serif; padding: 20px;">
        <h1>Saldo: {saldo:.2f} €</h1>
        <p>Prima versione con database</p>
    </body>
    </html>
    """


if __name__ == "__main__":
	app.run()
