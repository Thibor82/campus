from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import conectarCampus, login_requerido
import calendar as _calendar
from datetime import date, datetime

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


# ---------- calendario personal ----------

def _get_user_id(usuario):
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuarios FROM usuarios WHERE usuario = %s", (usuario,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"Error obteniendo id_usuarios: {e}")
        return None


@alumno_bp.route("/perfil/calendario")
@login_requerido
def calendario():
    usuario = session.get("usuario")
    year = request.args.get("year", type=int) or date.today().year
    month = request.args.get("month", type=int) or date.today().month

    # compute calendar weeks
    cal = _calendar.Calendar(firstweekday=6)  # week starts domingo
    weeks = cal.monthdayscalendar(year, month)

    # fetch events for the month to mark days with events
    events_by_day = {}
    user_id = _get_user_id(usuario)
    if user_id:
        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT fecha, titulo FROM eventos WHERE id_usuario = %s AND date_part('year', fecha) = %s AND date_part('month', fecha) = %s",
                (user_id, year, month),
            )
            for fecha, titulo in cursor.fetchall():
                day = fecha.day
                events_by_day.setdefault(day, []).append(titulo)
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error cargando eventos: {e}")

    # calcula mes anterior y siguiente para los controles
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    return render_template(
        "calendario.html",
        usuario=usuario,
        year=year,
        month=month,
        weeks=weeks,
        events_by_day=events_by_day,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
    )


@alumno_bp.route("/perfil/calendario/dia")
@login_requerido
def dia_detalle():
    date_str = request.args.get("date")
    try:
        fecha = datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return jsonify({"error": "fecha inválida"}), 400

    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    eventos = []

    if user_id:
        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT titulo, descripcion FROM eventos WHERE id_usuario = %s AND fecha = %s",
                (user_id, fecha),
            )
            for titulo, descripcion in cursor.fetchall():
                eventos.append({"titulo": titulo, "descripcion": descripcion})
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error consultando eventos día: {e}")
            return jsonify({"error": "falló consulta"}), 500

    return jsonify({"date": fecha.isoformat(), "eventos": eventos})


@alumno_bp.route("/perfil/calendario/evento", methods=["POST"])
@login_requerido
def crear_evento():
    # recibe fecha, titulo, descripcion desde formulario
    fecha_str = request.form.get("fecha")
    titulo = request.form.get("titulo")
    descripcion = request.form.get("descripcion")
    if not fecha_str or not titulo:
        return redirect(url_for("alumno_bp.calendario"))
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except Exception:
        return redirect(url_for("alumno_bp.calendario"))

    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    if user_id:
        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO eventos (id_usuario, fecha, titulo, descripcion) VALUES (%s, %s, %s, %s)",
                (user_id, fecha, titulo, descripcion),
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error creando evento: {e}")
    return redirect(url_for("alumno_bp.calendario", year=fecha.year, month=fecha.month))




# ---------- asignaturas ----------

@alumno_bp.route("/asignaturas", methods=["GET"])
@login_requerido
def listar_asignaturas():
    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        
        # Obtener todas las asignaturas con info del profesor
        cursor.execute("""
            SELECT a.id_asignatura, a.nombre, a.descripcion, u.usuario
            FROM asignaturas a
            JOIN usuarios u ON a.id_profesor = u.id_usuarios
            ORDER BY a.nombre
        """)
        asignaturas = cursor.fetchall()
        
        # Obtener asignaturas donde está matriculado
        cursor.execute("""
            SELECT id_asignatura FROM matriculaciones WHERE id_usuario = %s
        """, (user_id,))
        matriculado = {row[0] for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        
        return render_template("asignaturas.html", 
                             asignaturas=asignaturas,
                             matriculado=matriculado,
                             usuario=usuario)
    except Exception as e:
        print(f"Error cargando asignaturas: {e}")
        return render_template("asignaturas.html", asignaturas=[], matriculado=set())


@alumno_bp.route("/mis-asignaturas", methods=["GET"])
@login_requerido
def mis_asignaturas():
    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id_asignatura, a.nombre, a.descripcion, u.usuario
            FROM asignaturas a
            JOIN matriculaciones m ON a.id_asignatura = m.id_asignatura
            JOIN usuarios u ON a.id_profesor = u.id_usuarios
            WHERE m.id_usuario = %s
            ORDER BY a.nombre
        """, (user_id,))
        asignaturas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template("mis_asignaturas.html", 
                             asignaturas=asignaturas,
                             usuario=usuario)
    except Exception as e:
        print(f"Error cargando mis asignaturas: {e}")
        return render_template("mis_asignaturas.html", asignaturas=[])


@alumno_bp.route("/asignatura/<int:id_asignatura>", methods=["GET"])
@login_requerido
def detalle_asignatura(id_asignatura):
    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        
        # Obtener info de asignatura
        cursor.execute("""
            SELECT a.id_asignatura, a.nombre, a.descripcion, u.usuario, u.id_usuarios
            FROM asignaturas a
            JOIN usuarios u ON a.id_profesor = u.id_usuarios
            WHERE a.id_asignatura = %s
        """, (id_asignatura,))
        asignatura = cursor.fetchone()
        
        if not asignatura:
            return redirect(url_for("alumno_bp.listar_asignaturas"))
        
        # Verificar si está matriculado
        cursor.execute("""
            SELECT 1 FROM matriculaciones 
            WHERE id_usuario = %s AND id_asignatura = %s
        """, (user_id, id_asignatura))
        matriculado = cursor.fetchone() is not None
        
        # Obtener eventos de la asignatura
        cursor.execute("""
            SELECT fecha, titulo, descripcion
            FROM eventos_asignatura
            WHERE id_asignatura = %s
            ORDER BY fecha DESC
        """, (id_asignatura,))
        eventos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template("detalle_asignatura.html",
                             asignatura=asignatura,
                             matriculado=matriculado,
                             eventos=eventos,
                             usuario=usuario)
    except Exception as e:
        print(f"Error cargando detalle asignatura: {e}")
        return redirect(url_for("alumno_bp.listar_asignaturas"))


@alumno_bp.route("/asignatura/<int:id_asignatura>/inscribirse", methods=["POST"])
@login_requerido
def inscribirse_asignatura(id_asignatura):
    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO matriculaciones (id_usuario, id_asignatura)
            VALUES (%s, %s)
        """, (user_id, id_asignatura))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error inscribiendo: {e}")
    
    return redirect(url_for("alumno_bp.detalle_asignatura", id_asignatura=id_asignatura))


@alumno_bp.route("/asignatura/<int:id_asignatura>/darse-baja", methods=["POST"])
@login_requerido
def baja_asignatura(id_asignatura):
    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM matriculaciones
            WHERE id_usuario = %s AND id_asignatura = %s
        """, (user_id, id_asignatura))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error dando de baja: {e}")
    
    return redirect(url_for("alumno_bp.listar_asignaturas"))


@alumno_bp.route("/logout", methods=["GET"])

def logout():
    session.clear()
    return redirect(url_for("alumno_bp.hello_world"))
