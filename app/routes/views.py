from flask import Blueprint, render_template, session, redirect, url_for, g
from app.maruz_distribuciones.decorators import oauth_login_required

bp = Blueprint("oauth_views", __name__)

@bp.route("/")
def home():
    # Si el usuario está autenticado, mostrar página principal personalizada
    if "user" in session:
        return render_template("home_authenticated.html", user=session["user"])
    # Si no está autenticado, redirigir al login
    return redirect(url_for("oauth_views.login"))

@bp.route("/login")
def login():
    return render_template("login.html")

@bp.route("/dashboard")
@oauth_login_required
def dashboard():
    return render_template("dashboard.html", user=g.current_user)

@bp.route("/home")
def home_authenticated():
    if "user" not in session:
        return redirect(url_for("oauth_views.login"))
    return render_template("home_authenticated.html", user=session["user"])

@bp.route("/complete-profile")
def complete_profile():
    if "user" not in session:
        return redirect(url_for("oauth_views.login"))
    return render_template("complete_profile.html", user=session["user"])
