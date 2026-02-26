from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import conectarCampus, login_requerido

alumno_bp = Blueprint("alumno_bp", __name__)


@alumno_bp.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        usuario = request.form["user"]
        password = request.form["password"]
        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            cursor.execute("SELECT password, usuario_email FROM usuarios WHERE usuario = %s", (usuario,))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            if resultado:
                stored_hash, email = resultado[0], resultado[1]
                if check_password_hash(stored_hash, password):
                    session["usuario"] = usuario
                    session["email"] = email
                    return redirect(url_for("alumno_bp.perfil_usuario"))
                else:
                    return redirect(url_for("alumno_bp.registro"))
            else:
                return redirect(url_for("alumno_bp.registro"))
        except Exception as e:
            print(f"Error: {e}")
            return redirect(url_for("alumno_bp.registro"))

    return render_template("login.html")


@alumno_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form["user"]
        password = request.form["password"]
        email = request.form["email"]
        creado_en = "NOW()"
        actualizado_en = "NOW()"
        rol_defecto = "alumno"

        password_hash = generate_password_hash(password)

        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM usuarios WHERE usuario_email = %s", (email,))
            existe = cursor.fetchone()
            if existe:
                cursor.close()
                conn.close()
                return render_template("registro.html", error="El email ya está registrado")

            cursor.execute("INSERT INTO usuarios (usuario, password, usuario_email, creado_en, actualizado_en, rol) VALUES (%s, %s, %s, %s, %s, %s)", (usuario, password_hash, email, creado_en, actualizado_en, rol_defecto))
            conn.commit()
            cursor.close()
            conn.close()

            session["usuario"] = usuario
            session["email"] = email
            return redirect(url_for("alumno_bp.perfil_usuario"))
        except Exception as e:
            print(f"Error al registrar: {e}")
            return render_template("registro.html", error="Error al registrar el usuario")

    return render_template("registro.html")


@alumno_bp.route("/perfil", methods=["GET"])

@login_requerido
def perfil_usuario():
    usuario = session.get("usuario")
    email = session.get("email")
    return render_template("user.html", usuario=usuario, email=email)


@alumno_bp.route("/logout", methods=["GET"])

def logout():
    session.clear()
    return redirect(url_for("alumno_bp.hello_world"))
