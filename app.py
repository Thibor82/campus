from flask import Flask
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Registrar blueprints de rutas separadas por rol
from routes.alumno import alumno_bp
from routes.admin import admin_bp
from routes.profesor import profesor_bp

app.register_blueprint(alumno_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(profesor_bp)


if __name__ == "__main__":
    app.run(debug=True)