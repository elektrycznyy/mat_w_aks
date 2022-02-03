from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def witaj():
	return "Witajcie!"
	
@app.route("/czesc")
@app.route("/czesc/<name>")
def czesc(name=None):
	return render_template("index.html", name=name)
	
if __name__ == "__main__":
	app.run(host="0.0.0.0")
