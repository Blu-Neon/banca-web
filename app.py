from flask import Flask

app= Flask(__name__)

@app.route("/")
def home():
	return"<h1> Ciao banca!</h1><p>Prima prova online</p>"
if __name__ == "__main__":
	app.run()
