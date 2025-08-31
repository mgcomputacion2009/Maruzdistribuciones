from flask import Blueprint, render_template

# Blueprint para Maruz Distributions Corp (migrado de app/rutas.py)
bp = Blueprint("main", __name__)

@bp.route("/")
def home():
    return render_template("base.html", mensaje="¡Maruz Distributions Corp - Tienda conectada!")

@bp.route("/login")
def login():
    return render_template("login.html")
