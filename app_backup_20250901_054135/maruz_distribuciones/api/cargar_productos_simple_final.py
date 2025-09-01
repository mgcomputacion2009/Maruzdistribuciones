# 🚀 ENDPOINT SIMPLIFICADO - CARGAR PRODUCTOS - MARUZ DISTRIBUCIONES
# Versión simplificada que funciona con la base de datos existente

import os
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('/var/www/maruz/.env')
import json
import logging
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import traceback

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/www/maruz/app/maruz_distribuciones/storage/logs/cargar_productos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Crear Blueprint
cargar_bp = Blueprint('cargar', __name__, url_prefix='/api/productos')

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        return mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'miguel'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME', 'maruz_db'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
    except Error as e:
        logger.error(f"❌ Error conectando a base de datos: {e}")
        raise

def validar_producto(producto):
    """Validar datos del producto antes de insertar/actualizar"""
    errores = []
    
    # Campos obligatorios
    if not producto.get('CODIGO'):
        errores.append("CODIGO es obligatorio")
    if not producto.get('DESCRIPCION'):
        errores.append("DESCRIPCION es obligatoria")
    
    return errores

def _get_any(dct, keys):
    """Devuelve el primer valor no vacío para cualquiera de las claves dadas."""
    for key in keys:
        if key in dct and dct.get(key) not in [None, ""]:
            return dct.get(key)
    return None

def procesar_producto_simple(producto):
    """Procesar un producto con TODOS los campos del CSV"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Logging de diagnóstico de campos clave (no datos sensibles)
        img1 = producto.get('IMAGEN1')
        img2 = producto.get('IMAGEN2')
        # Aceptar clave con espacio final: "IMAGEN3 "
        img3 = producto.get('IMAGEN3') if 'IMAGEN3' in producto else producto.get('IMAGEN3 ', None)
        img1_edit = producto.get('IMAGEN1(EDITADA)')
        img2_edit = producto.get('IMAGEN2(EDITADA)')
        img3_edit = producto.get('IMAGEN3(EDITADA)')
        logger.info(f"🔍 {producto.get('CODIGO','N/A')} IMGs -> i1:{bool(img1)} i2:{bool(img2)} i3:{bool(img3)} i1e:{bool(img1_edit)} i2e:{bool(img2_edit)} i3e:{bool(img3_edit)}")

        # Otros campos del CSV
        alterno = producto.get('ALTERNO')
        metadata = producto.get('METADATA')
        nota = producto.get('NOTA')
        web = producto.get('WEB')
        categoria = producto.get('CATEGORIA')
        descripcion_producto = _get_any(producto, ['Descripción Producto', 'Descripcion Producto'])
        propiedades = producto.get('Propiedades')
        datos_tecnicos = _get_any(producto, ['Datos técnicos', 'Datos tecnicos'])
        especificaciones = producto.get('Especificaciones')
        campos_aplicacion = _get_any(producto, ['Campos de aplicación', 'Campos de aplicacion'])
        envases_disponibles = producto.get('Envases disponibles')
        pdf = producto.get('pdf')
        recomendaciones = producto.get('RECOMENDACIONES')
        cont = producto.get('cont')
        pr_field = _get_any(producto, ['PR', 'pr'])
        id_drive = _get_any(producto, ['IDdrive', 'id_drive'])
        qr_code = producto.get('qrt')

        # Verificar si el producto existe
        check_query = "SELECT id FROM productos WHERE codigo_producto = %s"
        cursor.execute(check_query, (producto['CODIGO'],))
        existing_product = cursor.fetchone()
        
        if existing_product:
            # UPDATE - Producto existe
            update_query = """
            UPDATE productos SET
                descripcion = %s,
                alterno = %s,
                imagen1 = %s,
                imagen2 = %s,
                imagen3 = %s,
                imagen1_editada = %s,
                imagen2_editada = %s,
                imagen3_editada = %s,
                metadata = %s,
                nota = %s,
                web_url = %s,
                categoria = %s,
                descripcion_producto = %s,
                propiedades = %s,
                datos_tecnicos = %s,
                especificaciones = %s,
                campos_aplicacion = %s,
                envases_disponibles = %s,
                pdf = %s,
                recomendaciones = %s,
                cont = %s,
                pr_field = %s,
                id_drive = %s,
                qr_code = %s,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE codigo_producto = %s
            """
            
            update_values = (
                producto.get('DESCRIPCION'),
                alterno,
                img1,
                img2,
                img3,
                img1_edit,
                img2_edit,
                img3_edit,
                metadata,
                nota,
                web,
                categoria,
                descripcion_producto,
                propiedades,
                datos_tecnicos,
                especificaciones,
                campos_aplicacion,
                envases_disponibles,
                pdf,
                recomendaciones,
                cont,
                pr_field,
                id_drive,
                qr_code,
                producto['CODIGO']
            )
            
            cursor.execute(update_query, update_values)
            conn.commit()
            logger.info(f"✅ Producto actualizado: {producto['CODIGO']}")
            return 'updated'
            
        else:
            # INSERT - Producto nuevo
            insert_query = """
            INSERT INTO productos (
                codigo_producto, descripcion, alterno,
                imagen1, imagen2, imagen3, imagen1_editada, imagen2_editada, imagen3_editada,
                metadata, nota, web_url, categoria, descripcion_producto,
                propiedades, datos_tecnicos, especificaciones, campos_aplicacion, envases_disponibles,
                pdf, recomendaciones, cont, pr_field, id_drive, qr_code,
                empresa_id, ambiente
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s
            )
            """
            
            insert_values = (
                producto['CODIGO'],
                producto.get('DESCRIPCION'),
                alterno,
                img1,
                img2,
                img3,
                img1_edit,
                img2_edit,
                img3_edit,
                metadata,
                nota,
                web,
                categoria,
                descripcion_producto,
                propiedades,
                datos_tecnicos,
                especificaciones,
                campos_aplicacion,
                envases_disponibles,
                pdf,
                recomendaciones,
                cont,
                pr_field,
                id_drive,
                qr_code,
                2,  # empresa_id para Maruz Distribuciones
                'desarrollo'
            )
            
            cursor.execute(insert_query, insert_values)
            conn.commit()
            logger.info(f"✅ Producto insertado: {producto['CODIGO']}")
            return 'inserted'
            
    except Error as e:
        logger.error(f"❌ Error procesando producto {producto.get('CODIGO', 'N/A')}: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@cargar_bp.route('/status', methods=['GET'])
def status_productos():
    """Endpoint para verificar estado de la tabla productos"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Contar productos
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = cursor.fetchone()[0]
        
        # Contar por empresa
        cursor.execute("SELECT empresa_id, COUNT(*) FROM productos GROUP BY empresa_id")
        productos_por_empresa = dict(cursor.fetchall())
        
        # Últimos productos agregados
        cursor.execute("""
            SELECT codigo_producto, descripcion, fecha_creacion 
            FROM productos 
            ORDER BY fecha_creacion DESC 
            LIMIT 5
        """)
        ultimos_productos = [
            {
                'codigo': row[0],
                'descripcion': row[1][:100] + '...' if len(row[1]) > 100 else row[1],
                'fecha': row[2].isoformat() if row[2] else None
            }
            for row in cursor.fetchall()
        ]
        
        response = {
            'success': True,
            'status': 'operativo',
            'tabla_productos': {
                'total_productos': total_productos,
                'productos_por_empresa': productos_por_empresa,
                'ultimos_productos': ultimos_productos
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"❌ Error en status_productos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@cargar_bp.route('/cargar', methods=['POST'])
def cargar_productos():
    """Endpoint principal para cargar productos desde Windows"""
    start_time = datetime.now()
    
    try:
        # Obtener datos del request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos JSON'
            }), 400
        
        # Verificar estructura de datos
        if 'productos' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo "productos" es obligatorio'
            }), 400
        
        productos = data['productos']
        
        if not isinstance(productos, list):
            return jsonify({
                'success': False,
                'error': 'Campo "productos" debe ser un array'
            }), 400
        
        if len(productos) == 0:
            return jsonify({
                'success': False,
                'error': 'Array de productos está vacío'
            }), 400
        
        # Contadores para el resumen
        total_productos = len(productos)
        insertados = 0
        actualizados = 0
        errores = 0
        productos_con_errores = []
        
        # Procesar cada producto
        for i, producto in enumerate(productos):
            try:
                # Validar producto
                errores_validacion = validar_producto(producto)
                
                if errores_validacion:
                    errores += 1
                    productos_con_errores.append({
                        'indice': i,
                        'codigo': producto.get('CODIGO', 'N/A'),
                        'errores': errores_validacion
                    })
                    continue
                
                # Procesar producto
                resultado = procesar_producto_simple(producto)
                
                if resultado == 'inserted':
                    insertados += 1
                elif resultado == 'updated':
                    actualizados += 1
                    
            except Exception as e:
                errores += 1
                productos_con_errores.append({
                    'indice': i,
                    'codigo': producto.get('CODIGO', 'N/A'),
                    'error': str(e)
                })
                logger.error(f"❌ Error procesando producto {i}: {e}")
        
        # Calcular tiempo de procesamiento
        end_time = datetime.now()
        tiempo_procesamiento = (end_time - start_time).total_seconds()
        
        # Preparar respuesta
        response = {
            'success': True,
            'resumen': {
                'total_productos': total_productos,
                'insertados': insertados,
                'actualizados': actualizados,
                'errores': errores,
                'tiempo_procesamiento_segundos': round(tiempo_procesamiento, 2)
            },
            'detalles': {
                'productos_con_errores': productos_con_errores
            },
            'timestamp': datetime.now().isoformat(),
            'empresa': 'Maruz Distribuciones',
            'ambiente': 'desarrollo'
        }
        
        # Log del resumen
        logger.info(f"🎯 CARGA COMPLETADA - Total: {total_productos}, Insertados: {insertados}, Actualizados: {actualizados}, Errores: {errores}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"❌ ERROR CRÍTICO en endpoint cargar_productos: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'detalles': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
