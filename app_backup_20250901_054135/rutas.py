from flask import Blueprint, render_template

bp = Blueprint("main", __name__)

@bp.route("/")
def home():
    return render_template("base.html", mensaje="¡Tienda conectada!")

@bp.route("/login")
def login():
    return render_template("login.html")
