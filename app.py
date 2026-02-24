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
                    return redirect(url_for("f_registro"))
            else:
                return redirect(url_for("f_registro"))
        except Exception as e:
            print(f"Error: {e}")
            return redirect(url_for("f_registro"))
    
    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def f_registro():
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
            # Comprobar si el email ya está registrado
            cursor.execute("SELECT 1 FROM usuarios WHERE usuario_email = %s", (email,))
            existe = cursor.fetchone()
            if existe:
                cursor.close()
                conn.close()
                return render_template("registro.html", error="El email ya está registrado")

            # Insertar nuevo usuario
            cursor.execute("INSERT INTO usuarios (usuario, password, usuario_email, creado_en, actualizado_en, rol) VALUES (%s, %s, %s, %s, %s, %s)", (usuario, password_hash, email, creado_en, actualizado_en, rol_defecto))
        
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
@app.route("/perfil_admin", methods=["GET"])
@login_requerido
def perfil_admin():
    """Página de perfil del administrador protegida"""
    usuario = session.get("usuario")
    email = session.get("email")
    return render_template("perfil_admin.html", usuario=usuario, email=email)

@app.route("/logout", methods=["GET"])
def logout():
    """Cerrar sesión del usuario"""
    session.clear()
    return redirect(url_for("hello_world"))



@app.route("/app-admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        usuario = request.form["user"]
        password = request.form["password"]
        
        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            # Obtener el password y email para el usuario admin
            cursor.execute("SELECT password, usuario_email FROM usuarios WHERE usuario = %s", (usuario,))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()

            if resultado:
                stored_password, email = resultado[0], resultado[1]
                if password == stored_password:
                    session["usuario"] = usuario
                    session["email"] = email
                    return redirect(url_for("perfil_admin"))
                else:
                    print("Contraseña incorrecta")
                    return render_template("admin.html", error="Usuario o contraseña incorrectos")
            else:
                print("Usuario no encontrado en la base de datos")
                return render_template("admin.html", error="Usuario o contraseña incorrectos")
        except Exception as e:
            print(f"Error: {e}")
            return render_template("admin.html", error=f"Error en el servidor: {e}")
    
    return render_template("admin.html")


@app.route("/mod_usuarios", methods=["GET", "POST"])
def mod_usuarios():
    if request.method == "POST":       
        usuario = request.form["user"]
        email = request.form["email"]
        creado_en = request.form["date"]

        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            # Obtener el password y email para el usuario admin
            cursor.execute("SELECT usuario, usuario_email, creado_en FROM usuarios WHERE usuario = %s OR usuario_email = %s OR creado_en = %s", (usuario, email, creado_en))
            resultados = cursor.fetchall()
            cursor.close()
            conn.close()

            usuarios = []
            for r in resultados:
                usuarios.append({
                    "usuario": r[0],
                    "email": r[1],
                    "creado_en": r[2]
                })

            return render_template("mod_usuarios.html", usuarios=usuarios)
        except Exception as e:
            print(f"Error: {e}")
            return render_template("mod_usuarios.html", error=f"Error en el servidor: {e}")
        
    return render_template("mod_usuarios.html")