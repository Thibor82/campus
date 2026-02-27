from flask import Blueprint, render_template, request, redirect, url_for, session
from helpers import conectarCampus, login_requerido

admin_bp = Blueprint("admin_bp", __name__)


@admin_bp.route("/app-admin", methods=["GET", "POST"])
def login_admin():
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
                stored_password, email = resultado[0], resultado[1]
                # Aquí el admin puede comparar de la forma que desee (por ahora igual que antes)
                if password == stored_password:
                    session["usuario"] = usuario
                    session["email"] = email
                    return redirect(url_for("admin_bp.perfil_admin"))
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


@admin_bp.route("/perfil_admin", methods=["GET"])
@login_requerido
def perfil_admin():
    usuario = session.get("usuario")
    email = session.get("email")
    return render_template("perfil_admin.html", usuario=usuario, email=email)


@admin_bp.route("/mod_usuarios", methods=["GET", "POST"])
@login_requerido
def mod_usuarios():
    if request.method == "POST":
        usuario = request.form.get("user")
        email = request.form.get("email")
        creado_en = request.form.get("date")

        try:
            conn = conectarCampus()
            cursor = conn.cursor()
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


@admin_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    # volver a pantalla de login administrador
    return redirect(url_for("admin_bp.login_admin"))
@admin_bp.route("/mod_usuarios/<usuario>", methods=["GET", "POST"])
@login_requerido
def modificar_usuario(usuario):
    if request.method == "POST":
        nuevo_usuario = request.form.get("user")
        nuevo_email = request.form.get("email")
        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET usuario = %s, usuario_email = %s WHERE usuario = %s", (nuevo_usuario, nuevo_email, usuario))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for("admin_bp.mod_usuarios"))
        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            return render_template("mod_usuarios.html", error=f"Error al actualizar: {e}")

    # GET: obtener datos del usuario y mostrar formulario en la misma plantilla
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        cursor.execute("SELECT usuario, usuario_email, creado_en FROM usuarios WHERE usuario = %s", (usuario,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            usuario_data = {"usuario": row[0], "email": row[1], "creado_en": row[2]}
            return render_template("mod_usuarios.html", usuario_a_modificar=usuario_data)
        else:
            return render_template("mod_usuarios.html", error="Usuario no encontrado")
    except Exception as e:
        print(f"Error: {e}")
        return render_template("mod_usuarios.html", error=f"Error en el servidor: {e}")
