from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from functools import wraps

# Cargar variables de entorno desde archivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Decorador para proteger rutas que requieren autenticación
def login_requerido(f):
    @wraps(f)
    def decorado(*args, **kwargs):  
        if "usuario" not in session:
            return redirect(url_for("hello_world"))
        return f(*args, **kwargs)
    return decorado

def conectarCampus():
    conexion = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conexion

@app.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        usuario = request.form["user"]
        password = request.form["password"]
        print(password)
        

        
        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            # Obtener el hash de la contraseña y el email para el usuario
            cursor.execute("SELECT password, usuario_email FROM usuarios WHERE usuario = %s", (usuario,))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()

            if resultado:
                stored_hash, email = resultado[0], resultado[1]
                # Verificar el password con el hash almacenado
                if check_password_hash(stored_hash, password):
                    # Crear sesión activa
                    session["usuario"] = usuario
                    session["email"] = email
                    return redirect(url_for("perfil_usuario"))
                else:
                    return redirect(url_for("registro"))
            else:
                return redirect(url_for("registro"))
        except Exception as e:
            print(f"Error: {e}")
            return redirect(url_for("registro"))
    
    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form["user"]
        password = request.form["password"]
        email = request.form["email"]
        
        password_hash = generate_password_hash(password)

        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            # Comprobar si el email ya está registrado
            cursor.execute("SELECT 1 FROM usuarios WHERE usuario_email = %s", (email,))
            existe = cursor.fetchone()
            if existe:
                cursor.close()
                conn.close()
                return render_template("registro.html", error="El email ya está registrado")

            # Insertar nuevo usuario
            cursor.execute("INSERT INTO usuarios (usuario, password, usuario_email) VALUES (%s, %s, %s)", (usuario, password_hash, email))
            conn.commit()
            cursor.close()
            conn.close()

            # Crear sesión después del registro
            session["usuario"] = usuario
            session["email"] = email
            return redirect(url_for("perfil_usuario"))
        except Exception as e:
            print(f"Error al registrar: {e}")
            return render_template("registro.html", error="Error al registrar el usuario")
    
    return render_template("registro.html")

@app.route("/perfil", methods=["GET"])
@login_requerido
def perfil_usuario():
    """Página de perfil de usuario protegida"""
    usuario = session.get("usuario")
    email = session.get("email")
    return render_template("user.html", usuario=usuario, email=email)

@app.route("/logout", methods=["GET"])
def logout():
    """Cerrar sesión del usuario"""
    session.clear()
    return redirect(url_for("hello_world"))

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     # Ruta alternativa para login (puede usarse además de /)
#     if request.method == "POST":
#         usuario = request.form["user"]
#         password = request.form["password"]
        
#         try:
#             conn = conectarCampus()
#             cursor = conn.cursor()
#             cursor.execute("SELECT password, usuario_email FROM usuarios WHERE usuario = %s", (usuario,))
#             resultado = cursor.fetchone()
#             cursor.close()
#             conn.close()

#             if resultado:
#                 stored_hash, email = resultado[0], resultado[1]
#                 if check_password_hash(stored_hash, password):
#                     return render_template("user.html", usuario=usuario, email=email)
#                 else:
#                     return redirect(url_for("registro"))
#             else:
#                 return redirect(url_for("registro"))
#         except Exception as e:
#             print(f"Error: {e}")
#             return redirect(url_for("registro"))
    
#     return render_template("login.html")

