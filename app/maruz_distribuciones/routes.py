from flask import Blueprint, render_template, request, current_app, send_from_directory, abort, url_for, make_response
import os
from sqlalchemy import text
from time import time
from app.maruz_distribuciones.app import db

# Blueprint para Maruz Distribuciones (Desarrollo)
bp = Blueprint("main", __name__)

@bp.route("/")
def home():
    return render_template("base.html", mensaje="¡Maruz Distribuciones - Tienda en desarrollo!")

@bp.route("/login")
def login():
    return render_template("login.html")

@bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@bp.route("/productos")
def productos():
    # Parámetros de búsqueda y paginación
    q = (request.args.get("q", "") or "").strip()
    try:
        page = int(request.args.get("page", 1) or 1)
    except ValueError:
        page = 1
    try:
        limit = int(request.args.get("limit", 50) or 50)
    except ValueError:
        limit = 50
    if limit <= 0:
        limit = 50
    if page <= 0:
        page = 1
    offset = (page - 1) * limit

    # Consulta eficiente a MySQL (campos mínimos necesarios)
    where_sql = ""
    params = {"limit": limit, "offset": offset}
    if q:
        where_sql = " AND (codigo_producto LIKE :like OR descripcion LIKE :like OR categoria LIKE :like)"
        params["like"] = f"%{q}%"

    sql = text(
        """
        SELECT codigo_producto, descripcion, web,
               imagen1, imagen2, imagen3,
               imagen1_editada, imagen2_editada, imagen3_editada,
               categoria, descripcion_producto, campos_aplicacion, propiedades, datos_tecnicos, especificaciones
        FROM productos
        WHERE 1=1
        """ + where_sql + " ORDER BY fecha_actualizacion DESC LIMIT :limit OFFSET :offset"
    )

    rows = db.session.execute(sql, params).fetchall()

    # Total para posibles paginaciones futuras
    count_sql = text("SELECT COUNT(*) AS total FROM productos WHERE 1=1" + where_sql)
    total = db.session.execute(count_sql, {k: v for k, v in params.items() if k == "like"}).scalar() or 0

    # Preparar datos para la vista (resolviendo URL de imagen segura)
    productos_list = []
    storage_placeholder = url_for("static", filename="images/maruz-logo-distribuciones.png")
    version = str(int(time()))
    for row in rows:
        data = dict(row._mapping)
        img_path = data.get("imagen1_editada") or data.get("imagen1")
        if img_path:
            filename = os.path.basename(img_path)
            img_url = url_for("main.media_productos", filename=filename)
        else:
            img_url = storage_placeholder
        # Construir galería de imágenes
        gallery_raw = [
            data.get("imagen1_editada"), data.get("imagen1"),
            data.get("imagen2_editada"), data.get("imagen2"),
            data.get("imagen3_editada"), data.get("imagen3"),
        ]
        imagenes_urls = []
        for pth in gallery_raw:
            if not pth:
                continue
            fn = os.path.basename(pth)
            imagenes_urls.append(url_for("main.media_productos", filename=fn) + f"?v={version}")
        productos_list.append({
            "codigo": data.get("codigo_producto"),
            "descripcion": data.get("descripcion") or "",
            "web_url": data.get("web"),
            "img_url": img_url + f"?v={version}",
            "categoria": data.get("categoria"),
            "descripcion_producto": data.get("descripcion_producto") or "",
            "campos_aplicacion": data.get("campos_aplicacion") or "",
            "propiedades": data.get("propiedades") or "",
            "datos_tecnicos": data.get("datos_tecnicos") or "",
            "especificaciones": data.get("especificaciones") or "",
            "imagenes": imagenes_urls,
            "precio": 0.0,
        })

    resp = make_response(render_template(
        "productos.html",
        q=q,
        productos=productos_list,
        page=page,
        total=total,
        limit=limit,
        v=version,
    ))
    # Evitar cacheo del HTML en clientes intermedios
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@bp.route("/media/productos/<path:filename>")
def media_productos(filename):
    """Servir imágenes de productos de forma segura desde storage permitido."""
    base_storage = current_app.config.get(
        "STORAGE_PATH", "/var/www/maruz/app/maruz_distribuciones/storage"
    )
    allowed_dirs = [
        os.path.join(base_storage, "productos_global"),
        os.path.join(base_storage, "productos"),
    ]
    for directory in allowed_dirs:
        candidate = os.path.join(directory, filename)
        if os.path.isfile(candidate):
            return send_from_directory(directory, filename)
    return abort(404)
