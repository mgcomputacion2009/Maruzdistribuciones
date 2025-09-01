# 🚀 ENDPOINT CARGAR PRODUCTOS - MARUZ DISTRIBUCIONES
# Endpoint para recibir productos desde Windows y cargarlos en MySQL

from flask import Blueprint, request, jsonify, current_app
import json
import logging
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import traceback
import os

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
            host='127.0.0.1',
            user='miguel',
            password='Mg645418037$$',
            database='maruz_distribuciones',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
    except Error as e:
        logger.error(f"❌ Error conectando a base de datos: {e}")
        raise

def crear_tabla_productos():
    """Crear tabla productos si no existe"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS productos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            
            -- Campos de identificación
            codigo_producto VARCHAR(100) NOT NULL UNIQUE,
            descripcion TEXT NOT NULL,
            alterno VARCHAR(100),
            
            -- Campos de imágenes
            imagen1 VARCHAR(255),
            imagen2 VARCHAR(255),
            imagen3 VARCHAR(255),
            imagen1_editada VARCHAR(255),
            imagen2_editada VARCHAR(255),
            imagen3_editada VARCHAR(255),
            
            -- Campos de información
            metadata TEXT,
            nota TEXT,
            web VARCHAR(500),
            categoria VARCHAR(100),
            descripcion_producto TEXT,
            
            -- Campos técnicos
            propiedades TEXT,
            datos_tecnicos TEXT,
            especificaciones TEXT,
            campos_aplicacion TEXT,
            envases_disponibles TEXT,
            
            -- Campos adicionales
            pdf VARCHAR(255),
            recomendaciones TEXT,
            cont VARCHAR(100),
            pr VARCHAR(100),
            id_drive VARCHAR(100),
            qrt VARCHAR(100),
            
            -- Campos de sistema
            empresa_id INT DEFAULT 2,
            ambiente VARCHAR(20) DEFAULT 'desarrollo',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE,
            
            -- Índices para búsquedas rápidas
            INDEX idx_codigo (codigo_producto),
            INDEX idx_categoria (categoria),
            INDEX idx_empresa (empresa_id),
            INDEX idx_activo (activo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        logger.info("✅ Tabla productos creada/verificada exitosamente")
        
    except Error as e:
        logger.error(f"❌ Error creando tabla productos: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def validar_producto(producto):
    """Validar datos del producto antes de insertar/actualizar"""
    errores = []
    
    # Campos obligatorios
    if not producto.get('CODIGO'):
        errores.append("CODIGO es obligatorio")
    if not producto.get('DESCRIPCION'):
        errores.append("DESCRIPCION es obligatoria")
    
    # Validar longitud de campos
    if producto.get('CODIGO') and len(str(producto['CODIGO'])) > 100:
        errores.append("CODIGO no puede exceder 100 caracteres")
    
    if producto.get('DESCRIPCION') and len(str(producto['DESCRIPCION'])) > 65535:
        errores.append("DESCRIPCION es demasiado larga")
    
    # Validar URLs
    web = producto.get('WEB')
    if web and len(str(web)) > 500:
        errores.append("WEB no puede exceder 500 caracteres")
    
    return errores

def procesar_producto(producto):
    """Procesar un producto individual (insertar o actualizar)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
                web = %s,
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
                pr = %s,
                id_drive = %s,
                qrt = %s,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE codigo_producto = %s
            """
            
            update_values = (
                producto.get('DESCRIPCION'),
                producto.get('ALTERNO'),
                producto.get('IMAGEN1'),
                producto.get('IMAGEN2'),
                producto.get('IMAGEN3'),
                producto.get('IMAGEN1(EDITADA)'),
                producto.get('IMAGEN2(EDITADA)'),
                producto.get('IMAGEN3(EDITADA)'),
                producto.get('METADATA'),
                producto.get('NOTA'),
                producto.get('WEB'),
                producto.get('CATEGORIA'),
                producto.get('Descripción Producto'),
                producto.get('Propiedades'),
                producto.get('Datos técnicos'),
                producto.get('Especificaciones'),
                producto.get('Campos de aplicación'),
                producto.get('Envases disponibles'),
                producto.get('pdf'),
                producto.get('RECOMENDACIONES'),
                producto.get('cont'),
                producto.get('PR'),
                producto.get('IDdrive'),
                producto.get('qrt'),
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
                imagen1, imagen2, imagen3,
                imagen1_editada, imagen2_editada, imagen3_editada,
                metadata, nota, web, categoria, descripcion_producto,
                propiedades, datos_tecnicos, especificaciones,
                campos_aplicacion, envases_disponibles,
                pdf, recomendaciones, cont, pr, id_drive, qrt,
                empresa_id, ambiente
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            insert_values = (
                producto['CODIGO'],
                producto.get('DESCRIPCION'),
                producto.get('ALTERNO'),
                producto.get('IMAGEN1'),
                producto.get('IMAGEN2'),
                producto.get('IMAGEN3'),
                producto.get('IMAGEN1(EDITADA)'),
                producto.get('IMAGEN2(EDITADA)'),
                producto.get('IMAGEN3(EDITADA)'),
                producto.get('METADATA'),
                producto.get('NOTA'),
                producto.get('WEB'),
                producto.get('CATEGORIA'),
                producto.get('Descripción Producto'),
                producto.get('Propiedades'),
                producto.get('Datos técnicos'),
                producto.get('Especificaciones'),
                producto.get('Campos de aplicación'),
                producto.get('Envases disponibles'),
                producto.get('pdf'),
                producto.get('RECOMENDACIONES'),
                producto.get('cont'),
                producto.get('PR'),
                producto.get('IDdrive'),
                producto.get('qrt'),
                2,  # empresa_id para Maruz Distribuciones
                'desarrollo'
            )
            
            cursor.execute(insert_query, insert_values)
            conn.commit()
            logger.info(f"✅ Producto insertado: {producto['CODIGO']}")
            return 'inserted'
            
    except Error as e:
        logger.error(f"❌ Error procesando producto {producto.get('CODIGO', 'N/A')}: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@cargar_bp.route('/cargar', methods=['POST'])
def cargar_productos():
    """Endpoint principal para cargar productos desde Windows"""
    start_time = datetime.now()
    
    try:
        # Verificar que la tabla existe
        crear_tabla_productos()
        
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
                resultado = procesar_producto(producto)
                
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

@cargar_bp.route('/status', methods=['GET'])
def status_productos():
    """Endpoint para verificar estado de la tabla productos"""
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
        if conn.is_connected():
            cursor.close()
            conn.close()
