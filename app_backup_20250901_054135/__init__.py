from flask import Flask

app = Flask(
    __name__,
    template_folder="../paginas",
    static_folder="../public"
)

# Registrar el blueprint DESPUÉS de crear la app
from app.rutas import bp
app.register_blueprint(bp)
