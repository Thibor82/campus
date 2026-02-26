import os
import psycopg2
from functools import wraps
from flask import session, redirect, url_for

def conectarCampus():
    conexion = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conexion

def login_requerido(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        if "usuario" not in session:
            # default redirigir al login de alumno (puede cambiarse según necesidad)
            return redirect(url_for("alumno_bp.hello_world"))
        return f(*args, **kwargs)
    return decorado
