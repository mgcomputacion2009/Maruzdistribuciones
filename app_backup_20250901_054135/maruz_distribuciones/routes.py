from flask import Blueprint, render_template, request, current_app, send_from_directory, abort, url_for, make_response, g
import os
from sqlalchemy import text
from time import time
from app.maruz_distribuciones.app import db
from app.maruz_distribuciones.decorators import login_required

# Blueprint para Maruz Distribuciones (Desarrollo)
bp = Blueprint("main", __name__)

@bp.route("/")
def home():
    return render_template("base.html", mensaje="¡Maruz Distribuciones - Tienda en desarrollo!")

@bp.route("/login")
def login():
    return render_template("login.html")

@bp.route("/dashboard")
@login_required
def dashboard():
    # Si hay usuario en g (del decorador), usarlo
    if hasattr(g, 'current_user'):
        return render_template("dashboard.html", user=g.current_user)
    # Si no hay usuario, mostrar error o redirigir
    return render_template("dashboard.html", user=None)

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

    # Obtener cliente_id del usuario autenticado (si existe)
    cliente_id = None
    from flask import session
    if 'user' in session and 'id' in session['user']:
        cliente_id = session['user']['id']
    
    # Consulta con ranking personalizado si hay cliente autenticado
    if cliente_id:
        sql = text(
            """
            SELECT p.codigo_producto, p.descripcion, p.web,
                   p.imagen1, p.imagen2, p.imagen3,
                   p.imagen1_editada, p.imagen2_editada, p.imagen3_editada,
                   p.categoria, p.descripcion_producto, p.campos_aplicacion, p.propiedades, p.datos_tecnicos, p.especificaciones,
                   p.pre_precio,
                   COALESCE(r.score_ranking, 0) as score_ranking
            FROM productos p
            LEFT JOIN ranking_productos_cliente r ON p.id = r.producto_id AND r.cliente_id = :cliente_id
            WHERE 1=1
            """ + where_sql + """
            ORDER BY 
                CASE WHEN r.score_ranking > 0 THEN 0 ELSE 1 END,
                r.score_ranking DESC,
                p.fecha_actualizacion DESC 
            LIMIT :limit OFFSET :offset
            """
        )
        params["cliente_id"] = cliente_id
    else:
        # Consulta normal sin ranking para usuarios no autenticados
        sql = text(
            """
            SELECT codigo_producto, descripcion, web,
                   imagen1, imagen2, imagen3,
                   imagen1_editada, imagen2_editada, imagen3_editada,
                   categoria, descripcion_producto, campos_aplicacion, propiedades, datos_tecnicos, especificaciones,
                   pre_precio
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
            "precio": data.get("pre_precio") or 0.0,
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

@bp.route("/api/autocomplete")
def autocomplete():
    """Endpoint para autocompletado de búsqueda de productos con registro de ranking"""
    query = request.args.get('q', '').strip()
    cliente_id = request.args.get('cliente_id', None)
    
    # Debug log para verificar si llega el cliente_id
    current_app.logger.info(f"Autocompletado - Query: '{query}', Cliente ID: {cliente_id}")
    
    if not query or len(query) < 2:
        return jsonify([])
    
    try:
        # Consulta optimizada para autocompletado
        sql = text("""
            SELECT DISTINCT 
                id,
                codigo_producto,
                descripcion,
                categoria,
                pre_precio
            FROM productos 
            WHERE codigo_producto LIKE :query 
               OR descripcion LIKE :query 
               OR categoria LIKE :query
            ORDER BY 
                CASE 
                    WHEN codigo_producto LIKE :query THEN 1
                    WHEN descripcion LIKE :query THEN 2
                    WHEN categoria LIKE :query THEN 3
                END,
                descripcion
            LIMIT 10
        """)
        
        params = {"query": f"%{query}%"}
        rows = db.session.execute(sql, params).fetchall()
        
        # Preparar resultados para autocompletado
        suggestions = []
        for row in rows:
            data = dict(row._mapping)
            suggestions.append({
                "id": data.get("id"),
                "codigo": data.get("codigo_producto"),
                "descripcion": data.get("descripcion") or "",
                "categoria": data.get("categoria") or "",
                "precio": float(data.get("pre_precio") or 0),
                "display": f"{data.get('codigo_producto')} - {data.get('descripcion') or ''}"
            })
        
        # Registrar búsqueda en ranking si hay cliente_id
        if cliente_id and suggestions:
            try:
                current_app.logger.info(f"Registrando búsqueda en ranking - Cliente: {cliente_id}, Query: '{query}', Productos encontrados: {len(suggestions)}")
                registrar_busqueda_ranking(cliente_id, query, suggestions)
            except Exception as e:
                current_app.logger.error(f"Error registrando búsqueda en ranking: {e}")
        
        return jsonify(suggestions)
        
    except Exception as e:
        current_app.logger.error(f"Error en autocompletado: {e}")
        return jsonify([])

def registrar_busqueda_ranking(cliente_id, query, suggestions):
    """Registra la búsqueda en el sistema de ranking personalizado"""
    try:
        # Obtener el primer producto de los resultados
        if suggestions and len(suggestions) > 0:
            primer_producto_id = suggestions[0].get('id')
            current_app.logger.info(f"Procesando ranking - Cliente: {cliente_id}, Producto ID: {primer_producto_id}")
            
            # Calcular nuevo score
            nuevo_score = calcular_score_ranking(cliente_id, primer_producto_id)
            current_app.logger.info(f"Score calculado: {nuevo_score}")
            
            # Insertar o actualizar ranking
            sql_upsert = text("""
                INSERT INTO ranking_productos_cliente 
                    (cliente_id, producto_id, score_ranking, ultima_busqueda, frecuencia_busqueda)
                VALUES (:cliente_id, :producto_id, :score, NOW(), 1)
                ON DUPLICATE KEY UPDATE 
                    score_ranking = :score,
                    ultima_busqueda = NOW(),
                    frecuencia_busqueda = frecuencia_busqueda + 1
            """)
            
            params = {
                "cliente_id": cliente_id,
                "producto_id": primer_producto_id,
                "score": nuevo_score
            }
            
            db.session.execute(sql_upsert, params)
            db.session.commit()
            current_app.logger.info(f"Ranking registrado exitosamente para cliente {cliente_id}")
            
    except Exception as e:
        current_app.logger.error(f"Error en registro de ranking: {e}")
        db.session.rollback()

def calcular_score_ranking(cliente_id, producto_id):
    """Calcula el score de ranking para un producto del cliente"""
    try:
        # Obtener datos actuales del ranking
        sql_select = text("""
            SELECT score_ranking, frecuencia_busqueda, ultima_busqueda
            FROM ranking_productos_cliente 
            WHERE cliente_id = :cliente_id AND producto_id = :producto_id
        """)
        
        params = {"cliente_id": cliente_id, "producto_id": producto_id}
        result = db.session.execute(sql_select, params).fetchone()
        
        if result:
            score_actual = float(result[0] or 0)
            frecuencia = int(result[1] or 0)
            ultima_busqueda = result[2]
        else:
            score_actual = 0
            frecuencia = 0
            ultima_busqueda = None
        
        # Calcular nuevo score: (Frecuencia × 0.7) + (Recencia × 0.3)
        # Recencia: días desde la última búsqueda (máximo 30 días)
        from datetime import datetime, timedelta
        
        if ultima_busqueda:
            dias_desde_ultima = (datetime.now() - ultima_busqueda).days
            recencia_score = max(0, 30 - dias_desde_ultima) / 30  # 0 a 1
        else:
            recencia_score = 1.0  # Primera búsqueda
        
        nuevo_score = (frecuencia * 0.7) + (recencia_score * 0.3)
        
        return round(nuevo_score, 4)
        
    except Exception as e:
        current_app.logger.error(f"Error calculando score: {e}")
        return 1.0  # Score por defecto
