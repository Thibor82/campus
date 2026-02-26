from flask import Blueprint, render_template

profesor_bp = Blueprint("profesor_bp", __name__)


@profesor_bp.route("/profesor", endpoint="index_profesor")
def index_profesor():
    # Punto de partida para rutas y vistas específicas de profesor
    return render_template("base.html")
