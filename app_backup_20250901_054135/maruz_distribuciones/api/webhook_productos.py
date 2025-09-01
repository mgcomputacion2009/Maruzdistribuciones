# 🌐 WEBHOOK PRODUCTOS - MARUZ DISTRIBUCIONES
# Endpoint para recibir productos desde AppSheet

from flask import Blueprint, request, jsonify, current_app
import json
import logging
from datetime import datetime
import os
import mysql.connector
from app.maruz_distribuciones.models import Producto, ProductoImagen, ProductoDocumento, TipoDocumento

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/www/maruz/app/maruz_distribuciones/storage/logs/webhook_productos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Crear Blueprint
webhook_bp = Blueprint('webhook', __name__, url_prefix='/api/webhook')

def get_db_connection():
    """Obtener conexión a la base de datos"""
    return mysql.connector.connect(
        host='127.0.0.1',
        user='miguel',
        password='Mg645418037$$',
        database='maruz_db'
    )

def crear_estructura_carpetas(codigo_producto):
    """Crear estructura de carpetas para un producto"""
    base_path = f"/var/www/maruz/app/maruz_distribuciones/storage/productos/{codigo_producto}"
    
    # Crear directorios
    os.makedirs(f"{base_path}/imagenes", exist_ok=True)
    os.makedirs(f"{base_path}/documentos", exist_ok=True)
    
    # Asignar permisos
    os.chmod(base_path, 0o755)
    os.chmod(f"{base_path}/imagenes", 0o755)
    os.chmod(f"{base_path}/documentos", 0o755)
    
    logger.info(f"✅ Estructura de carpetas creada para: {codigo_producto}")
    return base_path

def procesar_producto_appsheet(data):
    """Procesa producto desde AppSheet y lo guarda en base de datos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Insertar producto principal
        producto_query = """
        INSERT INTO productos (
            codigo_producto, descripcion, nota, web_url, categoria,
            descripcion_producto, propiedades, datos_tecnicos, especificaciones,
            campos_aplicacion, envases_disponibles, recomendaciones,
            cont, pr_field, id_drive, qr_code, empresa_id, ambiente
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        producto_values = (
            data.get('codigo'),
            data.get('descripcion'),
            data.get('nota'),
            data.get('web'),
            data.get('categoria'),
            data.get('descripcion_producto'),
            data.get('propiedades'),
            data.get('datos_tecnicos'),
            data.get('especificaciones'),
            data.get('campos_aplicacion'),
            data.get('envases_disponibles'),
            data.get('recomendaciones'),
            data.get('cont'),
            data.get('pr'),
            data.get('id_drive'),
            data.get('qrt'),
            2,  # empresa_id para Maruz Distribuciones
            'desarrollo'
        )
        
        cursor.execute(producto_query, producto_values)
        producto_id = cursor.lastrowid
        
        # 2. Crear estructura de carpetas
        crear_estructura_carpetas(data.get('codigo'))
        
        # 3. Insertar registros de imágenes
        for i in range(1, 4):
            campo_imagen = f"IMAGEN{i}"
            if campo_imagen in data and data[campo_imagen]:
                nombre_archivo = data[campo_imagen]
                url_local = f"/storage/productos/{data.get('codigo')}/imagenes/{nombre_archivo}"
                
                imagen_query = """
                INSERT INTO producto_imagenes (
                    producto_id, numero_imagen, nombre_archivo, url_local
                ) VALUES (%s, %s, %s, %s)
                """
                
                cursor.execute(imagen_query, (producto_id, i, nombre_archivo, url_local))
                logger.info(f"📸 Imagen {i} registrada: {nombre_archivo}")
        
        # 4. Insertar registros de documentos
        documentos = [
            ('METADATA', 'metadata'),
            ('pdf', 'pdf'),
            ('PR', 'pr')
        ]
        
        for campo, tipo in documentos:
            if campo in data and data[campo]:
                nombre_archivo = data[campo]
                url_local = f"/storage/productos/{data.get('codigo')}/documentos/{nombre_archivo}"
                
                doc_query = """
                INSERT INTO producto_documentos (
                    producto_id, tipo_documento, nombre_archivo, url_local
                ) VALUES (%s, %s, %s, %s)
                """
                
                cursor.execute(doc_query, (producto_id, tipo, nombre_archivo, url_local))
                logger.info(f"📄 Documento {tipo} registrado: {nombre_archivo}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Producto procesado exitosamente: {data.get('codigo')}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error procesando producto: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

@webhook_bp.route('/productos', methods=['POST'])
def recibir_producto():
    """
    Endpoint para recibir productos desde AppSheet
    POST /api/webhook/productos
    """
    try:
        # Log de inicio
        logger.info("=== NUEVO PRODUCTO RECIBIDO ===")
        logger.info(f"Timestamp: {datetime.now()}")
        logger.info(f"IP Remota: {request.remote_addr}")
        logger.info(f"User-Agent: {request.headers.get('User-Agent', 'N/A')}")
        
        # Verificar contenido
        if not request.is_json:
            logger.error("Error: Content-Type no es application/json")
            return jsonify({
                'error': 'Content-Type debe ser application/json',
                'status': 'error'
            }), 400
        
        # Obtener datos JSON
        data = request.get_json()
        logger.info(f"Datos recibidos: {json.dumps(data, indent=2)}")
        
        # Validar campos requeridos
        campos_requeridos = ['codigo', 'descripcion']
        campos_faltantes = [campo for campo in campos_requeridos if campo not in data or not data[campo]]
        
        if campos_faltantes:
            logger.error(f"Campos requeridos faltantes: {campos_faltantes}")
            return jsonify({
                'error': f'Campos requeridos faltantes: {campos_faltantes}',
                'status': 'error'
            }), 400
        
        # Validar código único
        codigo = data.get('codigo')
        if not codigo or len(codigo.strip()) == 0:
            logger.error("Código de producto vacío o inválido")
            return jsonify({
                'error': 'Código de producto es requerido y no puede estar vacío',
                'status': 'error'
            }), 400
        
        # Log de validación exitosa
        logger.info(f"Validación exitosa para producto: {codigo}")
        
        # Procesar producto en base de datos
        if procesar_producto_appsheet(data):
            response_data = {
                'status': 'success',
                'message': 'Producto procesado y guardado correctamente',
                'codigo': codigo,
                'timestamp': datetime.now().isoformat(),
                'procesado': True,
                'estructura_carpetas': f'/storage/productos/{codigo}/',
                'nota': 'Producto listo para sincronización de imágenes'
            }
        else:
            response_data = {
                'status': 'error',
                'message': 'Error procesando producto en base de datos',
                'codigo': codigo,
                'timestamp': datetime.now().isoformat(),
                'procesado': False
            }
            return jsonify(response_data), 500
        
        logger.info(f"Respuesta enviada: {json.dumps(response_data, indent=2)}")
        logger.info("=== FIN PRODUCTO RECIBIDO ===\n")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error interno del servidor',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@webhook_bp.route('/productos/batch', methods=['POST'])
def recibir_productos_lote():
    """
    Endpoint para recibir múltiples productos desde AppSheet
    POST /api/webhook/productos/batch
    """
    try:
        logger.info("=== LOTE DE PRODUCTOS RECIBIDO ===")
        logger.info(f"Timestamp: {datetime.now()}")
        logger.info(f"IP Remota: {request.remote_addr}")
        
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type debe ser application/json',
                'status': 'error'
            }), 400
        
        data = request.get_json()
        
        # Verificar que sea una lista
        if not isinstance(data, list):
            return jsonify({
                'error': 'El body debe ser una lista de productos',
                'status': 'error'
            }), 400
        
        logger.info(f"Productos en lote: {len(data)}")
        
        # Validar cada producto
        productos_validos = []
        productos_invalidos = []
        productos_procesados = 0
        
        for i, producto in enumerate(data):
            try:
                # Validar campos requeridos
                if 'codigo' in producto and 'descripcion' in producto:
                    productos_validos.append(producto)
                    logger.info(f"Producto {i+1} válido: {producto.get('codigo')}")
                    
                    # Procesar producto
                    if procesar_producto_appsheet(producto):
                        productos_procesados += 1
                        logger.info(f"✅ Producto {i+1} procesado: {producto.get('codigo')}")
                    else:
                        logger.error(f"❌ Error procesando producto {i+1}: {producto.get('codigo')}")
                        
                else:
                    productos_invalidos.append({
                        'indice': i+1,
                        'error': 'Campos requeridos faltantes',
                        'producto': producto
                    })
                    logger.warning(f"Producto {i+1} inválido: campos requeridos faltantes")
            except Exception as e:
                productos_invalidos.append({
                    'indice': i+1,
                    'error': str(e),
                    'producto': producto
                })
                logger.error(f"Error validando producto {i+1}: {str(e)}")
        
        # Respuesta del lote
        response_data = {
            'status': 'success',
            'message': f'Lote procesado: {productos_procesados} exitosos, {len(productos_invalidos)} con errores',
            'total_recibidos': len(data),
            'productos_validos': len(productos_validos),
            'productos_procesados': productos_procesados,
            'productos_invalidos': len(productos_invalidos),
            'detalle_invalidos': productos_invalidos,
            'timestamp': datetime.now().isoformat(),
            'procesado': True,
            'nota': f'Lote procesado. {productos_procesados} productos listos para sincronización de imágenes'
        }
        
        logger.info(f"Respuesta del lote: {json.dumps(response_data, indent=2)}")
        logger.info("=== FIN LOTE DE PRODUCTOS ===\n")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error inesperado en lote: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error interno del servidor',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@webhook_bp.route('/productos/health', methods=['GET'])
def health_check():
    """
    Endpoint de verificación de salud del webhook
    GET /api/webhook/productos/health
    """
    return jsonify({
        'status': 'healthy',
        'service': 'webhook_productos',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'funcionalidad': 'Procesamiento completo de productos con nombres de archivos'
    }), 200
