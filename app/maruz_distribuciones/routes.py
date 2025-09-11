from flask import Blueprint, render_template, request, current_app, send_from_directory, abort, url_for, make_response, g, jsonify, session
import os
import re
from sqlalchemy import text
from time import time
from app.maruz_distribuciones.app import db
from app.maruz_distribuciones.decorators import login_required

# Importar OpenAI para corrección de consultas
try:
    import openai
    from dotenv import load_dotenv
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    current_app.logger.warning("OpenAI no disponible - funcionalidad de corrección deshabilitada")

# Blueprint para Maruz Distribuciones (Desarrollo)
bp = Blueprint("main", __name__)

def normalize_query(query):
    """Normaliza la consulta para búsqueda consistente"""
    if not query:
        return ""
    
    # Quitar acentos y normalizar
    query = query.strip().lower()
    query = re.sub(r'[áàäâ]', 'a', query)
    query = re.sub(r'[éèëê]', 'e', query)
    query = re.sub(r'[íìïî]', 'i', query)
    query = re.sub(r'[óòöô]', 'o', query)
    query = re.sub(r'[úùüû]', 'u', query)
    query = re.sub(r'[ñ]', 'n', query)
    
    # Normalizar separadores
    query = re.sub(r'[–—―]', '-', query)
    query = re.sub(r'\s+', ' ', query)
    
    return query.strip()

def looks_like_code(query):
    """Determina si la consulta parece un código de producto"""
    if not query:
        return False
    
    # Patrones comunes de códigos: letras + números con guiones
    code_patterns = [
        r'^[a-z]{1,3}-?\d{3,6}$',  # MF8547, ML-3387
        r'^\d{3,8}$',              # 8547, 123456
        r'^[a-z]{2,4}\d{2,6}$',    # OEM1234, SKU5678
    ]
    
    for pattern in code_patterns:
        if re.match(pattern, query, re.IGNORECASE):
            return True
    
    return False

def correct_query_with_openai(original_query, mode='text'):
    """Corrige la consulta usando OpenAI"""
    if not OPENAI_AVAILABLE or not original_query:
        return original_query
    
    try:
        # Determinar el contexto según el modo
        if mode == 'code':
            system_prompt = """Eres un asistente especializado en códigos de productos automotrices. 
            Corrige errores tipográficos en códigos de productos manteniendo el formato original.
            Si el código parece válido, devuélvelo tal como está.
            Ejemplos: 'mf 8547' -> 'MF8547', 'ml-3387' -> 'ML-3387'"""
        else:
            system_prompt = """Eres un experto en el parque automotor venezolano. Tu trabajo es corregir errores tipográficos en marcas y modelos de vehículos que se distribuyen en Venezuela.

MARCAS PRINCIPALES EN VENEZUELA:
- CHEVROLET: Corsa, Aveo, Optra, Spark, Cruze, Malibu, Trailblazer, Tahoe, Silverado
- FORD: Mustang, Fiesta, Focus, Escape, Explorer, Ranger, F-150
- TOYOTA: Corolla, Camry, RAV4, Hilux, Prado, Yaris
- HONDA: Civic, Accord, CR-V, Pilot
- NISSAN: Sentra, Versa, March, X-Trail, Pathfinder
- VOLKSWAGEN: Gol, Polo, Jetta, Passat, Tiguan, Amarok
- BMW, MERCEDES, AUDI, HYUNDAI, KIA, MAZDA, SUZUKI, MITSUBISHI

REGLAS DE CORRECCIÓN:
1. Corrige errores tipográficos en marcas: 'chebrolet' -> 'chevrolet', 'toyta' -> 'toyota'
2. Corrige errores en modelos: 'corza' -> 'corsa', 'mustam' -> 'mustang'
3. Si no hay coincidencia exacta, sugiere la marca/modelo más similar del parque venezolano
4. Para repuestos genéricos, hazlos específicos: 'filtro' -> 'filtro de aceite'

EJEMPLOS ESPECÍFICOS:
- 'chebrolet' -> 'chevrolet'
- 'chevrolete' -> 'chevrolet' 
- 'chevroet' -> 'chevrolet'
- 'corza' -> 'corsa'
- 'vrisa' -> 'corsa'
- 'mustam' -> 'mustang'
- 'toyta' -> 'toyota'
- 'honda' -> 'honda'
- 'nissan' -> 'nissan'
- 'volks' -> 'volkswagen'
- 'vw' -> 'volkswagen'
- 'bujia' -> 'bujía'
- 'filtro' -> 'filtro de aceite'

Responde SOLO con la corrección, sin explicaciones adicionales."""
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Corrige esta consulta: '{original_query}'"}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        corrected = response.choices[0].message.content.strip()
        
        # Validar que la corrección sea razonable
        if len(corrected) > len(original_query) * 2:
            return original_query  # Corrección demasiado larga
        
        return corrected
        
    except Exception as e:
        current_app.logger.error(f"Error en corrección OpenAI: {e}")
        return original_query

def correct_vehicle_brand(query):
    """Corrección específica para marcas de vehículos comunes en Venezuela"""
    brand_corrections = {
        # Chevrolet (más común en Venezuela)
        'corza': 'corsa',
        'vrisa': 'corsa',
        'chevrolete': 'chevrolet',
        'chevroet': 'chevrolet',
        'chevrolet': 'chevrolet',
        'chevy': 'chevrolet',
        'aveo': 'aveo',
        'optra': 'optra',
        'spark': 'spark',
        'cruze': 'cruze',
        'malibu': 'malibu',
        'trailblazer': 'trailblazer',
        'tahoe': 'tahoe',
        'silverado': 'silverado',
        
        # Ford (muy popular en Venezuela)
        'ford': 'ford',
        'mustam': 'mustang',
        'mustang': 'mustang',
        'fiesta': 'fiesta',
        'focus': 'focus',
        'escape': 'escape',
        'explorer': 'explorer',
        'ranger': 'ranger',
        'f-150': 'f-150',
        
        # Toyota (muy confiable en Venezuela)
        'toyta': 'toyota',
        'toyota': 'toyota',
        'corolla': 'corolla',
        'camry': 'camry',
        'rav4': 'rav4',
        'hilux': 'hilux',
        'prado': 'prado',
        'yaris': 'yaris',
        
        # Honda (muy popular)
        'honda': 'honda',
        'civic': 'civic',
        'accord': 'accord',
        'cr-v': 'cr-v',
        'pilot': 'pilot',
        
        # Nissan
        'nissan': 'nissan',
        'sentra': 'sentra',
        'versa': 'versa',
        'march': 'march',
        'xtrail': 'xtrail',
        'pathfinder': 'pathfinder',
        
        # Volkswagen (muy común)
        'volkswagen': 'volkswagen',
        'volks': 'volkswagen',
        'vw': 'volkswagen',
        'gol': 'gol',
        'polo': 'polo',
        'jetta': 'jetta',
        'passat': 'passat',
        'tiguan': 'tiguan',
        'amarok': 'amarok',
        
        # Otras marcas populares en Venezuela
        'bmw': 'bmw',
        'mercedes': 'mercedes',
        'audi': 'audi',
        'hyundai': 'hyundai',
        'kia': 'kia',
        'mazda': 'mazda',
        'suzuki': 'suzuki',
        'mitsubishi': 'mitsubishi',
        'subaru': 'subaru',
        'peugeot': 'peugeot',
        'renault': 'renault',
        'fiat': 'fiat',
        'seat': 'seat',
        'skoda': 'skoda',
        
        # Repuestos comunes
        'bujia': 'bujía',
        'bujias': 'bujías',
        'filtro': 'filtro de aceite',
        'filtros': 'filtros de aceite',
        'frenos': 'pastillas de freno',
        'aceite': 'aceite de motor',
        'llantas': 'llantas',
        'bateria': 'batería',
        'baterias': 'baterías'
    }
    
    query_lower = query.lower().strip()
    return brand_corrections.get(query_lower, query)

def get_venezuelan_similar_terms(query):
    """Obtiene términos similares populares en el mercado automotriz venezolano"""
    query_lower = query.lower().strip()
    
    # Mapeo de términos similares basado en el mercado venezolano
    similar_mappings = {
        # Chevrolet (más común en Venezuela)
        'corza': ['corsa', 'chevrolet corsa', 'chevy corsa'],
        'vrisa': ['corsa', 'chevrolet corsa', 'chevy corsa'],
        'mustam': ['mustang', 'ford mustang'],
        'toyta': ['toyota', 'corolla', 'camry'],
        'chevrolete': ['chevrolet', 'chevy', 'corsa', 'aveo'],
        'chevroet': ['chevrolet', 'chevy', 'corsa', 'aveo'],
        
        # Repuestos genéricos
        'filtro': ['filtro de aceite', 'filtro aire', 'filtro combustible'],
        'frenos': ['pastillas de freno', 'discos de freno', 'frenos delanteros'],
        'bujia': ['bujía', 'bujías', 'bujía de encendido'],
        'aceite': ['aceite de motor', 'aceite 10w30', 'aceite 5w30'],
        'llantas': ['llantas', 'neumáticos', 'gomas'],
        'bateria': ['batería', 'baterías', 'batería de carro'],
        
        # Marcas populares en Venezuela
        'ford': ['ford', 'mustang', 'fiesta', 'focus'],
        'toyota': ['toyota', 'corolla', 'camry', 'hilux'],
        'honda': ['honda', 'civic', 'accord', 'cr-v'],
        'nissan': ['nissan', 'sentra', 'versa', 'march'],
        'volkswagen': ['volkswagen', 'vw', 'gol', 'polo'],
        'chevrolet': ['chevrolet', 'chevy', 'corsa', 'aveo', 'optra'],
        
        # Términos generales
        'carro': ['vehículo', 'automóvil', 'auto'],
        'moto': ['motocicleta', 'moto', 'scooter'],
        'camion': ['camión', 'pickup', 'ranger', 'hilux'],
        'bus': ['autobús', 'bus', 'ómnibus'],
    }
    
    # Buscar coincidencias exactas
    if query_lower in similar_mappings:
        return similar_mappings[query_lower]
    
    # Buscar coincidencias parciales
    similar_terms = []
    for key, terms in similar_mappings.items():
        if key in query_lower or query_lower in key:
            similar_terms.extend(terms)
    
    # Si no hay coincidencias, sugerir términos generales populares en Venezuela
    if not similar_terms:
        popular_terms = [
            'chevrolet', 'ford', 'toyota', 'honda', 'nissan', 'volkswagen',
            'filtro de aceite', 'pastillas de freno', 'bujía', 'aceite de motor',
            'corsa', 'aveo', 'optra', 'mustang', 'corolla', 'civic'
        ]
        similar_terms = popular_terms[:5]  # Limitar a 5 términos
    
    return similar_terms[:3]  # Devolver máximo 3 términos para probar

def normalize_query_for_canonical(query):
    """Normaliza query para crear canonical_query consistente"""
    if not query:
        return ""
    
    # Normalización básica
    normalized = query.strip().lower()
    # Quitar acentos
    normalized = normalized.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    normalized = normalized.replace('ñ', 'n')
    # Normalizar espacios y guiones
    normalized = ' '.join(normalized.split())
    normalized = normalized.replace(' - ', '-').replace(' -', '-').replace('- ', '-')
    
    return normalized

def register_search_event(original_query, normalized_query, corrected_query, suggestions, 
                         user_id=None, llm_used=False, latency_ms=0):
    """Registra un evento de búsqueda en la base de datos"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Generar UUID para el evento
        import uuid
        event_id = str(uuid.uuid4())
        
        # Determinar si hubo resultados
        had_results = len(suggestions) > 0
        result_count = len(suggestions)
        
        # Insertar evento de búsqueda
        cursor.execute("""
            INSERT INTO search_events (
                id, user_id, raw_query, normalized_query, 
                had_results, result_count, llm_used, corrected_query, 
                latency_ms_total, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            event_id, user_id, original_query, normalized_query,
            had_results, result_count, llm_used, corrected_query,
            latency_ms
        ))
        
        # Si se usó LLM y hubo corrección, registrar en query_corrections
        if llm_used and corrected_query and corrected_query != original_query:
            cursor.execute("""
                INSERT INTO query_corrections (
                    search_event_id, corrected_query, intent, 
                    model, latency_ms_llm, created_at
                ) VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                event_id, corrected_query, 'product', 
                'gpt-3.5-turbo', latency_ms
            ))
        
        # Actualizar query_aliases si hubo corrección exitosa
        if corrected_query and corrected_query != original_query and had_results:
            canonical_query = normalize_query_for_canonical(corrected_query)
            raw_term = normalize_query_for_canonical(original_query)
            
            # Buscar si ya existe el alias
            cursor.execute("""
                SELECT id, samples, confidence FROM query_aliases 
                WHERE raw_term = %s
            """, (raw_term,))
            
            alias = cursor.fetchone()
            if alias:
                # Actualizar alias existente
                new_samples = alias[1] + 1
                new_confidence = min(1.0, alias[2] + 0.1)  # Incrementar confianza
                cursor.execute("""
                    UPDATE query_aliases 
                    SET samples = %s, confidence = %s, last_seen_at = NOW()
                    WHERE id = %s
                """, (new_samples, new_confidence, alias[0]))
            else:
                # Crear nuevo alias
                cursor.execute("""
                    INSERT INTO query_aliases (
                        raw_term, canonical_term, confidence, samples, 
                        approved, created_at
                    ) VALUES (%s, %s, %s, %s, %s, NOW())
                """, (raw_term, canonical_query, 0.1, 1, False))
        
        connection.commit()
        current_app.logger.info(f"Evento de búsqueda registrado: {event_id}")
        
        return event_id
        
    except Exception as e:
        current_app.logger.error(f"Error registrando evento de búsqueda: {e}")
        if connection:
            connection.rollback()
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def update_search_event_interaction(event_id, interaction_type, product_code):
    """Actualiza un evento de búsqueda con interacciones del usuario"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        if interaction_type == 'click':
            cursor.execute("""
                UPDATE search_events 
                SET first_click_product_code = %s 
                WHERE id = %s AND first_click_product_code IS NULL
            """, (product_code, event_id))
        elif interaction_type == 'cart':
            cursor.execute("""
                UPDATE search_events 
                SET added_to_cart_product_code = %s 
                WHERE id = %s
            """, (product_code, event_id))
        elif interaction_type == 'purchase':
            cursor.execute("""
                UPDATE search_events 
                SET purchased_product_code = %s 
                WHERE id = %s
            """, (product_code, event_id))
        
        connection.commit()
        current_app.logger.info(f"Interacción {interaction_type} registrada para evento {event_id}")
        
    except Exception as e:
        current_app.logger.error(f"Error actualizando interacción: {e}")
        if connection:
            connection.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_search_suggestions(query, mode='text', limit=12):
    """Obtiene sugerencias de búsqueda con lógica mejorada"""
    if not query or len(query) < 2:
        return []
    
    try:
        # Normalizar consulta
        normalized_query = normalize_query(query)
        is_code_like = looks_like_code(normalized_query)
        
        # Determinar modo de búsqueda
        search_mode = 'code' if is_code_like else mode
        
        # Construir consulta SQL según el modo
        if search_mode == 'code':
            # Búsqueda por código - más estricta
            sql = text("""
                SELECT DISTINCT 
                    id,
                    codigo_producto,
                    descripcion,
                    categoria,
                    precio,
                    stock,
                    'code' as tipo
                FROM productos_v2 
                WHERE codigo_producto LIKE :like
                ORDER BY 
                    CASE 
                        WHEN codigo_producto = :exact THEN 1
                        WHEN codigo_producto LIKE :start THEN 2
                        ELSE 3
                    END,
                    codigo_producto
                LIMIT :limit
            """)
            like_pattern = f"%{normalized_query}%"
            exact_match = normalized_query.upper()
            start_match = f"{normalized_query.upper()}%"
            params = {
                'like': like_pattern,
                'exact': exact_match,
                'start': start_match,
                'limit': limit
            }
        else:
            # Búsqueda por texto - más amplia
            sql = text("""
                SELECT DISTINCT 
                    id,
                    codigo_producto,
                    descripcion,
                    categoria,
                    precio,
                    stock,
                    CASE 
                        WHEN codigo_producto LIKE :like THEN 'code'
                        WHEN categoria LIKE :like THEN 'categoria'
                        ELSE 'producto'
                    END as tipo
                FROM productos_v2 
                WHERE codigo_producto LIKE :like 
                   OR descripcion LIKE :like 
                   OR categoria LIKE :like
                ORDER BY 
                    CASE 
                        WHEN codigo_producto LIKE :exact THEN 1
                        WHEN codigo_producto LIKE :start THEN 2
                        WHEN descripcion LIKE :start THEN 3
                        ELSE 4
                    END,
                    codigo_producto
                LIMIT :limit
            """)
            like_pattern = f"%{normalized_query}%"
            exact_match = f"{normalized_query.upper()}%"
            start_match = f"{normalized_query}%"
            params = {
                'like': like_pattern,
                'exact': exact_match,
                'start': start_match,
                'limit': limit
            }
        
        # Ejecutar consulta
        result = db.session.execute(sql, params)
        suggestions = []
        
        for row in result:
            suggestions.append({
                'id': row.id,
                'codigo': row.codigo_producto,
                'descripcion': row.descripcion or '',
                'categoria': row.categoria or '',
                'precio': float(row.precio) if row.precio else None,
                'stock': int(row.stock) if row.stock else 0,
                'tipo': row.tipo
            })
        
        return suggestions
        
    except Exception as e:
        current_app.logger.error(f"Error en búsqueda: {e}")
        return []

@bp.route("/")
def home():
    # Si el usuario ya está logueado, redirigir a productos
    if 'user' in session:
        from flask import redirect, url_for
        return redirect(url_for('main.productos'))
    
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
    original_q = (request.args.get("q", "") or "").strip()
    categorias_filtro = request.args.getlist("categorias")  # Lista de categorías seleccionadas
    
    # Aplicar corrección de búsqueda
    corrected_q = original_q
    if original_q:
        # Corrección local de marcas
        corrected_q = correct_vehicle_brand(original_q)
        if corrected_q != original_q:
            current_app.logger.info(f"Búsqueda corregida: '{original_q}' -> '{corrected_q}'")
        
        # Corrección con OpenAI si está disponible
        if OPENAI_AVAILABLE and len(original_q) > 2:
            openai_corrected = correct_query_with_openai(corrected_q, 'text')
            if openai_corrected != corrected_q:
                current_app.logger.info(f"OpenAI corrigió búsqueda: '{corrected_q}' -> '{openai_corrected}'")
                corrected_q = openai_corrected
    
    q = corrected_q
    
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
    where_conditions = []
    params = {"limit": limit, "offset": offset}
    
    # Filtro de texto de búsqueda
    if q:
        where_conditions.append("(codigo_producto LIKE :like OR descripcion LIKE :like OR categoria LIKE :like)")
        params["like"] = f"%{q}%"
    
    # Filtro de categorías
    if categorias_filtro:
        # Crear placeholders para cada categoría
        categoria_placeholders = []
        for i, categoria in enumerate(categorias_filtro):
            placeholder = f"categoria_{i}"
            categoria_placeholders.append(f":{placeholder}")
            params[placeholder] = categoria
        
        where_conditions.append(f"categoria IN ({', '.join(categoria_placeholders)})")
    
    # Construir WHERE final
    where_sql = ""
    if where_conditions:
        where_sql = " AND " + " AND ".join(where_conditions)

    # Obtener cliente_id del usuario autenticado (si existe)
    cliente_id = None
    from flask import session
    if 'user' in session and 'id' in session['user']:
        cliente_id = session['user']['id']
    
    # Consulta con ranking personalizado si hay cliente autenticado
    if cliente_id:
        sql = text(
            """
            SELECT p.codigo_producto, p.descripcion, p.pdf,
                   p.imagen1, p.imagen2, p.imagen3,
                   p.imagen1_editada, p.imagen2_editada, p.imagen3_editada,
                   p.categoria, p.descripcion_producto, p.campos_aplicacion, p.propiedades, p.datos_tecnicos, p.especificaciones,
                   p.pre_precio,
                   COALESCE(r.score_ranking, 0) as score_ranking
            FROM productos_v2 p
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
            SELECT codigo_producto, descripcion, pdf,
                   imagen1, imagen2, imagen3,
                   imagen1_editada, imagen2_editada, imagen3_editada,
                   categoria, descripcion_producto, campos_aplicacion, propiedades, datos_tecnicos, especificaciones,
                   pre_precio
            FROM productos_v2
            WHERE 1=1
            """ + where_sql + " ORDER BY fecha_actualizacion DESC LIMIT :limit OFFSET :offset"
        )

    rows = db.session.execute(sql, params).fetchall()

    # Total para posibles paginaciones futuras
    count_sql = text("SELECT COUNT(*) AS total FROM productos_v2 WHERE 1=1" + where_sql)
    # Filtrar solo los parámetros que no son de paginación para el count
    count_params = {k: v for k, v in params.items() if k not in ["limit", "offset"]}
    total = db.session.execute(count_sql, count_params).scalar() or 0

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
            "web_url": data.get("pdf"),
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
        q=original_q,  # Mostrar la consulta original en el input
        corrected_query=corrected_q,  # Para mostrar la corrección
        productos=productos_list,
        page=page,
        total=total,
        limit=limit,
        v=version,
        categorias_filtro=categorias_filtro,
        has_ranking=cliente_id is not None,
        cliente_id=cliente_id,
    ))
    # Evitar cacheo del HTML en clientes intermedios
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@bp.route("/api/categorias")
def obtener_categorias():
    """Obtener lista de categorías únicas para el filtro"""
    try:
        # Obtener categorías únicas ordenadas alfabéticamente
        sql = text("""
            SELECT DISTINCT categoria 
            FROM productos_v2 
            WHERE categoria IS NOT NULL AND categoria != '' 
            ORDER BY categoria ASC
        """)
        
        rows = db.session.execute(sql).fetchall()
        categorias = [row[0] for row in rows if row[0]]
        
        return jsonify({
            "success": True,
            "categorias": categorias,
            "total": len(categorias)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo categorías: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor",
            "categorias": []
        }), 500

@bp.route("/api/productos/cargar_mas")
def cargar_mas_productos():
    """Cargar más productos para scroll infinito"""
    try:
        # Parámetros básicos
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 40))
        
        # Consulta completa con todas las imágenes
        sql = text("""
            SELECT codigo_producto, descripcion, pdf, categoria, pre_precio,
                   imagen1, imagen2, imagen3, imagen1_editada, imagen2_editada, imagen3_editada,
                   descripcion_producto, campos_aplicacion, propiedades, datos_tecnicos, especificaciones
            FROM productos_v2
            ORDER BY fecha_actualizacion DESC 
            LIMIT :limit OFFSET :offset
        """)
        
        rows = db.session.execute(sql, {"limit": limit, "offset": offset}).fetchall()
        
        # Preparar respuesta completa
        productos_list = []
        storage_placeholder = url_for("static", filename="images/maruz-logo-distribuciones.png")
        from time import time
        version = str(int(time()))
        
        for row in rows:
            data = dict(row._mapping)
            
            # Procesar imagen principal (simplificado por ahora)
            img_path = data.get("imagen1_editada") or data.get("imagen1")
            if img_path:
                img_url = f"/media/productos/{os.path.basename(img_path)}?v={version}"
            else:
                img_url = storage_placeholder
            
            # URLs de imágenes adicionales (simplificado)
            imagenes_urls = []
            for i in range(1, 4):
                img_key = f"imagen{i}_editada" if f"imagen{i}_editada" in data else f"imagen{i}"
                if data.get(img_key):
                    imagenes_urls.append(f"/media/productos/{os.path.basename(data[img_key])}?v={version}")
                else:
                    imagenes_urls.append("")
            
            productos_list.append({
                "codigo": data.get("codigo_producto") or "",
                "descripcion": data.get("descripcion") or "",
                "web": data.get("pdf") or "",
                "categoria": data.get("categoria") or "",
                "descripcion_producto": data.get("descripcion_producto") or "",
                "campos_aplicacion": data.get("campos_aplicacion") or "",
                "propiedades": data.get("propiedades") or "",
                "datos_tecnicos": data.get("datos_tecnicos") or "",
                "especificaciones": data.get("especificaciones") or "",
                "precio": float(data.get("pre_precio") or 0),
                "imagenes": imagenes_urls,
                "imagen_principal": img_url
            })
        
        return jsonify({
            "success": True,
            "productos": productos_list,
            "total_cargados": len(productos_list),
            "offset": offset,
            "has_more": len(productos_list) == limit
        })
        
    except Exception as e:
        current_app.logger.error(f"Error cargando más productos: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error: {str(e)}",
            "productos": []
        }), 500

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
    """Endpoint mejorado para autocompletado con OpenAI y registro de eventos"""
    import time
    start_time = time.time()
    
    # Obtener parámetros
    original_query = request.args.get('q', '').strip()
    mode = request.args.get('mode', 'text')  # 'code' o 'text'
    cliente_id = request.args.get('cliente_id', None)
    
    # Fallback: si no vino por query, intentar desde la sesión
    if not cliente_id and 'user' in session and 'id' in session['user']:
        cliente_id = session['user']['id']
    
    current_app.logger.info(f"Autocompletado - Query: '{original_query}', Mode: {mode}, Cliente ID: {cliente_id}")
    
    if not original_query or len(original_query) < 2:
        return jsonify([])
    
    try:
        # Normalizar query
        normalized_query = normalize_query_for_canonical(original_query)
        
        # Paso 1: SIEMPRE usar OpenAI para corrección inteligente de marcas venezolanas
        corrected_query = original_query
        llm_used = False
        if OPENAI_AVAILABLE and len(original_query) > 2:
            corrected_query = correct_query_with_openai(original_query, mode)
            if corrected_query != original_query:
                llm_used = True
                current_app.logger.info(f"OpenAI corrigió: '{original_query}' -> '{corrected_query}'")
        
        # Paso 2: Si OpenAI no está disponible, usar corrección local como fallback
        if not OPENAI_AVAILABLE:
            corrected_query = correct_vehicle_brand(original_query)
            if corrected_query != original_query:
                current_app.logger.info(f"Marca corregida (local): '{original_query}' -> '{corrected_query}'")
        
        # Paso 3: Buscar con la consulta original primero
        suggestions = get_search_suggestions(original_query, mode, limit=12)
        
        # Paso 4: Si no hay resultados, intentar con la versión corregida
        if not suggestions and corrected_query != original_query:
            current_app.logger.info(f"No hay resultados para '{original_query}', intentando con '{corrected_query}'")
            suggestions = get_search_suggestions(corrected_query, mode, limit=12)
        
        # Paso 5: Si aún no hay resultados, buscar términos similares venezolanos
        if not suggestions:
            similar_terms = get_venezuelan_similar_terms(original_query)
            for term in similar_terms:
                current_app.logger.info(f"Intentando búsqueda similar: '{term}'")
                suggestions = get_search_suggestions(term, mode, limit=12)
                if suggestions:
                    corrected_query = term  # Actualizar la corrección mostrada
                    break
        
        # Calcular latencia
        latency_ms = int((time.time() - start_time) * 1000)
        
        # REGISTRAR EVENTO DE BÚSQUEDA
        event_id = register_search_event(
            original_query=original_query,
            normalized_query=normalized_query,
            corrected_query=corrected_query if corrected_query != original_query else None,
            suggestions=suggestions,
            user_id=cliente_id,
            llm_used=llm_used,
            latency_ms=latency_ms
        )
        
        # Paso 6: Preparar respuesta con metadatos adicionales
        response_data = {
            'suggestions': suggestions,
            'original_query': original_query,
            'corrected_query': corrected_query if corrected_query != original_query else None,
            'mode': mode,
            'openai_available': OPENAI_AVAILABLE,
            'total': len(suggestions),
            'event_id': event_id,  # Para tracking de interacciones
            'latency_ms': latency_ms
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error en autocomplete: {e}")
        return jsonify({
            'suggestions': [],
            'error': 'Error interno del servidor',
            'original_query': original_query
        }), 500

@bp.route("/api/autocomplete/legacy")
def autocomplete_legacy():
    """Endpoint legacy para compatibilidad con el frontend actual"""
    query = request.args.get('q', '').strip()
    cliente_id = request.args.get('cliente_id', None)
    
    if not cliente_id and 'user' in session and 'id' in session['user']:
        cliente_id = session['user']['id']
    
    if not query or len(query) < 2:
        return jsonify([])
    
    try:
        # Usar la nueva lógica pero devolver formato legacy
        suggestions = get_search_suggestions(query, 'text', limit=10)
        
        # Formato legacy para compatibilidad
        legacy_suggestions = []
        for sugg in suggestions:
            legacy_suggestions.append({
                "id": sugg.get("id"),
                "codigo": sugg.get("codigo"),
                "descripcion": sugg.get("descripcion"),
                "categoria": sugg.get("categoria"),
                "precio": sugg.get("precio"),
                "display": f"{sugg.get('codigo')} - {sugg.get('descripcion') or ''}"
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
        if not suggestions or len(suggestions) == 0:
            return
            
        current_app.logger.info(f"Procesando ranking - Cliente: {cliente_id}, Query: '{query}', Total productos encontrados: {len(suggestions)}")
        
        # Registrar SOLO los primeros 5 productos de la búsqueda (optimización)
        productos_a_registrar = suggestions[:5]  # Solo los primeros 5
        current_app.logger.info(f"Productos a registrar en ranking: {len(productos_a_registrar)}")
        
        for suggestion in productos_a_registrar:
            producto_id = suggestion.get('id')
            if not producto_id:
                continue
                
            current_app.logger.info(f"Registrando producto ID: {producto_id} en ranking")
            
            # Calcular nuevo score para este producto
            nuevo_score = calcular_score_ranking(cliente_id, producto_id)
            
            # Insertar o actualizar ranking para este producto
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
                "producto_id": producto_id,
                "score": nuevo_score
            }
            
            db.session.execute(sql_upsert, params)
        
        # Commit de todos los cambios
        db.session.commit()
        current_app.logger.info(f"Ranking registrado exitosamente para {len(productos_a_registrar)} productos (de {len(suggestions)} encontrados) del cliente {cliente_id}")
        
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
        
        # Calcular nuevo score mejorado
        # Fórmula: (Frecuencia × 0.6) + (Recencia × 0.3) + (Bonus por búsquedas recientes × 0.1)
        from datetime import datetime, timedelta
        
        # Recencia: días desde la última búsqueda (máximo 30 días)
        if ultima_busqueda:
            dias_desde_ultima = (datetime.now() - ultima_busqueda).days
            recencia_score = max(0, 30 - dias_desde_ultima) / 30  # 0 a 1
        else:
            recencia_score = 1.0  # Primera búsqueda
        
        # Bonus por búsquedas recientes (últimas 24 horas)
        bonus_reciente = 0
        if ultima_busqueda:
            horas_desde_ultima = (datetime.now() - ultima_busqueda).total_seconds() / 3600
            if horas_desde_ultima < 24:
                bonus_reciente = 1.0  # Bonus máximo si fue en las últimas 24h
            elif horas_desde_ultima < 48:
                bonus_reciente = 0.5  # Bonus medio si fue en las últimas 48h
        
        # Score final mejorado
        nuevo_score = (frecuencia * 0.6) + (recencia_score * 0.3) + (bonus_reciente * 0.1)
        
        # Log para debugging
        current_app.logger.info(f"Score calculado - Frecuencia: {frecuencia}, Recencia: {recencia_score:.3f}, Bonus: {bonus_reciente:.3f}, Total: {nuevo_score:.4f}")
        
        return round(nuevo_score, 4)
        
    except Exception as e:
        current_app.logger.error(f"Error calculando score: {e}")
        return 1.0  # Score por defecto

@bp.route("/api/productos/get/<codigo>")
def get_producto_completo(codigo):
    """
    Endpoint para obtener TODOS los campos de un producto específico
    Uso: /api/productos/get/{codigo}?full=1&all_fields=1
    """
    try:
        # Verificar parámetros
        full = request.args.get('full', '0') == '1'
        all_fields = request.args.get('all_fields', '0') == '1'
        
        if not full and not all_fields:
            return jsonify({
                'success': False,
                'error': 'Debe especificar full=1 o all_fields=1 para obtener todos los campos'
            }), 400
        
        # Consulta para obtener TODOS los campos del producto
        sql = text("""
            SELECT * FROM productos_v2 
            WHERE codigo_producto = :codigo 
            LIMIT 1
        """)
        
        result = db.session.execute(sql, {'codigo': codigo}).fetchone()
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'Producto con código {codigo} no encontrado'
            }), 404
        
        # Convertir resultado a diccionario con TODOS los campos
        producto_data = dict(result._mapping)
        
        # Agregar URLs de imágenes si existen
        base_url = request.host_url.rstrip('/')
        for img_field in ['imagen1', 'imagen2', 'imagen3', 'imagen1_editada', 'imagen2_editada', 'imagen3_editada']:
            if producto_data.get(img_field):
                filename = os.path.basename(producto_data[img_field])
                producto_data[f'{img_field}_url'] = f"{base_url}/media/productos/{filename}"
        
        return jsonify({
            'success': True,
            'data': producto_data,
            'total_fields': len(producto_data),
            'codigo': codigo
        })
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo producto completo: {e}")
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

@bp.route("/api/voice/transcribe", methods=['POST'])
def transcribe_voice():
    """
    Endpoint para transcribir audio usando OpenAI Whisper
    """
    try:
        if not request.files or 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se recibió archivo de audio'
            }), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Archivo de audio vacío'
            }), 400
        
        # Verificar que OpenAI esté disponible
        if not OPENAI_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'OpenAI no está disponible'
            }), 500
        
        # Transcribir audio con Whisper
        try:
            # Configurar el cliente de OpenAI
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Leer el archivo de audio como bytes
            audio_file.seek(0)  # Asegurar que estamos al inicio del archivo
            audio_bytes = audio_file.read()
            
            # Crear un objeto de archivo temporal para OpenAI
            import io
            audio_file_obj = io.BytesIO(audio_bytes)
            audio_file_obj.name = "recording.wav"  # Asignar nombre para OpenAI
            
            # Transcribir el audio
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file_obj,
                language="es"  # Español
            )
            
            text = transcript.text.strip()
            
            if not text:
                return jsonify({
                    'success': False,
                    'error': 'No se pudo transcribir el audio'
                }), 400
            
            # Log de la transcripción
            current_app.logger.info(f"Transcripción de voz: '{text}'")
            
            return jsonify({
                'success': True,
                'text': text,
                'language': 'es'
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error en transcripción Whisper: {e}")
            return jsonify({
                'success': False,
                'error': f'Error en transcripción: {str(e)}'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de voz: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@bp.route("/api/productos/fields")
def get_producto_fields():
    """
    Endpoint para obtener la lista de todos los campos disponibles en la tabla productos_v2
    """
    try:
        sql = text("DESCRIBE productos_v2")
        result = db.session.execute(sql).fetchall()
        
        fields = []
        for row in result:
            fields.append({
                'name': row[0],
                'type': row[1],
                'null': row[2],
                'key': row[3],
                'default': row[4],
                'extra': row[5]
            })
        
        return jsonify({
            'success': True,
            'total_fields': len(fields),
            'fields': fields
        })
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo campos: {e}")
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500
