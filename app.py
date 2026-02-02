from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        usuario = request.form["user"]
        password = request.form["password"]

        print("Usuario ingresado:", usuario)
        print("Password ingresado:", password)

        return f"Usuario {usuario} ha intentado iniciar sesión."



    return render_template("login.html")

