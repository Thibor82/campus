from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from helpers import conectarCampus, login_requerido
from datetime import datetime

profesor_bp = Blueprint("profesor_bp", __name__)


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


@profesor_bp.route("/profesor", endpoint="index_profesor")
@login_requerido
def index_profesor():
    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM asignaturas WHERE id_profesor = %s
        """, (user_id,))
        num_asignaturas = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT m.id_usuario) FROM matriculaciones m
            JOIN asignaturas a ON m.id_asignatura = a.id_asignatura
            WHERE a.id_profesor = %s
        """, (user_id,))
        num_alumnos = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return render_template("profesor.html", 
                             usuario=usuario,
                             num_asignaturas=num_asignaturas,
                             num_alumnos=num_alumnos)
    except Exception as e:
        print(f"Error: {e}")
        return render_template("profesor.html", usuario=usuario, 
                             num_asignaturas=0, num_alumnos=0)


@profesor_bp.route("/profesor/asignaturas", methods=["GET"])
@login_requerido
def mis_asignaturas():
    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_asignatura, nombre, descripcion, creado_en
            FROM asignaturas
            WHERE id_profesor = %s
            ORDER BY nombre
        """, (user_id,))
        asignaturas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template("profesor_asignaturas.html",
                             asignaturas=asignaturas,
                             usuario=usuario)
    except Exception as e:
        print(f"Error: {e}")
        return render_template("profesor_asignaturas.html", asignaturas=[])


@profesor_bp.route("/profesor/asignatura/<int:id_asignatura>", methods=["GET"])
@login_requerido
def detalle_asignatura(id_asignatura):
    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        
        # Verificar que sea el profesor de la asignatura
        cursor.execute("""
            SELECT id_asignatura, nombre, descripcion FROM asignaturas
            WHERE id_asignatura = %s AND id_profesor = %s
        """, (id_asignatura, user_id))
        asignatura = cursor.fetchone()
        
        if not asignatura:
            return redirect(url_for("profesor_bp.mis_asignaturas"))
        
        # Obtener alumnos matriculados
        cursor.execute("""
            SELECT DISTINCT u.id_usuarios, u.usuario, u.usuario_email
            FROM matriculaciones m
            JOIN usuarios u ON m.id_usuario = u.id_usuarios
            WHERE m.id_asignatura = %s
            ORDER BY u.usuario
        """, (id_asignatura,))
        alumnos = cursor.fetchall()
        
        # Obtener eventos de la asignatura
        cursor.execute("""
            SELECT id_evento_asign, fecha, titulo, descripcion
            FROM eventos_asignatura
            WHERE id_asignatura = %s
            ORDER BY fecha DESC
        """, (id_asignatura,))
        eventos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template("profesor_detalle_asignatura.html",
                             asignatura=asignatura,
                             alumnos=alumnos,
                             eventos=eventos,
                             usuario=usuario)
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for("profesor_bp.mis_asignaturas"))


@profesor_bp.route("/profesor/asignatura/<int:id_asignatura>/evento", methods=["POST"])
@login_requerido
def crear_evento(id_asignatura):
    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    
    fecha_str = request.form.get("fecha")
    titulo = request.form.get("titulo")
    descripcion = request.form.get("descripcion")
    
    if not fecha_str or not titulo:
        return redirect(url_for("profesor_bp.detalle_asignatura", 
                               id_asignatura=id_asignatura))
    
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        
        conn = conectarCampus()
        cursor = conn.cursor()
        
        # Verificar que sea el profesor
        cursor.execute("""
            SELECT 1 FROM asignaturas
            WHERE id_asignatura = %s AND id_profesor = %s
        """, (id_asignatura, user_id))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return redirect(url_for("profesor_bp.mis_asignaturas"))
        
        cursor.execute("""
            INSERT INTO eventos_asignatura 
            (id_asignatura, id_profesor, fecha, titulo, descripcion)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_asignatura, user_id, fecha, titulo, descripcion))
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creando evento: {e}")
    
    return redirect(url_for("profesor_bp.detalle_asignatura", 
                           id_asignatura=id_asignatura))


@profesor_bp.route("/profesor/evento/<int:id_evento>/eliminar", methods=["POST"])
@login_requerido
def eliminar_evento(id_evento):
    usuario = session.get("usuario")
    user_id = _get_user_id(usuario)
    
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        
        # Obtener id_asignatura para redirect
        cursor.execute("""
            SELECT id_asignatura FROM eventos_asignatura
            WHERE id_evento_asign = %s AND id_profesor = %s
        """, (id_evento, user_id))
        result = cursor.fetchone()
        
        if result:
            id_asignatura = result[0]
            cursor.execute("""
                DELETE FROM eventos_asignatura
                WHERE id_evento_asign = %s
            """, (id_evento,))
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return redirect(url_for("profesor_bp.detalle_asignatura",
                               id_asignatura=id_asignatura))
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for("profesor_bp.mis_asignaturas"))
