import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from mysql.connector import Error
from app.maruz_distribuciones.config import get_db_connection

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
bp = Blueprint('productos_v2', __name__, url_prefix='/api/productos')

def crear_tabla_productos_v2():
    """Verificar que la tabla productos tiene todos los campos necesarios"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que la tabla productos existe y tiene los campos necesarios
        cursor.execute("SHOW TABLES LIKE 'productos'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            raise Exception("La tabla productos no existe")
        
        # Verificar campos críticos
        cursor.execute("DESCRIBE productos")
        columnas = [row[0] for row in cursor.fetchall()]
        
        campos_requeridos = ['precio_a', 'precio_b', 'existencia', 'marca', 'codigo_barras']
        campos_faltantes = [campo for campo in campos_requeridos if campo not in columnas]
        
        if campos_faltantes:
            raise Exception(f"Campos faltantes en tabla productos: {', '.join(campos_faltantes)}")
        
        logger.info("✅ Tabla productos verificada exitosamente")
        
    except Error as e:
        logger.error(f"❌ Error verificando tabla productos: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def validar_producto_v2(producto):
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
    
    # Validar campos numéricos
    campos_numericos = ['PRE_PRECIO', 'PRECIOA', 'PRECIOB', 'PRECIOA + IVA', 'PRECIOB + IVA', 
                       'ULTIMO_COSTO', 'COSTO USD', 'UTIL', 'EXIS']
    
    for campo in campos_numericos:
        if producto.get(campo):
            try:
                float(str(producto[campo]).replace(',', ''))
            except ValueError:
                errores.append(f"{campo} debe ser un número válido")
    
    # Validar URLs
    web = producto.get('WEB')
    if web and len(str(web)) > 500:
        errores.append("WEB no puede exceder 500 caracteres")
    
    return errores

def procesar_producto_v2(producto):
    """Procesar un producto individual (insertar o actualizar)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si el producto existe
        check_query = "SELECT id FROM productos WHERE codigo_producto = %s"
        cursor.execute(check_query, (producto['CODIGO'],))
        existing_product = cursor.fetchone()
        
        # Preparar datos para inserción/actualización
        datos = {
            'codigo_producto': producto.get('CODIGO'),
            'descripcion': producto.get('DESCRIPCION'),
            'pre_precio': float(str(producto.get('PRE_PRECIO', 0)).replace(',', '')) if producto.get('PRE_PRECIO') else 0.00,
            'precio_a': float(str(producto.get('PRECIOA', 0)).replace(',', '')) if producto.get('PRECIOA') else 0.00,
            'precio_b': float(str(producto.get('PRECIOB', 0)).replace(',', '')) if producto.get('PRECIOB') else 0.00,
            'precio_a_iva': float(str(producto.get('PRECIOA + IVA', 0)).replace(',', '')) if producto.get('PRECIOA + IVA') else 0.00,
            'precio_b_iva': float(str(producto.get('PRECIOB + IVA', 0)).replace(',', '')) if producto.get('PRECIOB + IVA') else 0.00,
            'ultimo_costo': float(str(producto.get('ULTIMO_COSTO', 0)).replace(',', '')) if producto.get('ULTIMO_COSTO') else 0.00,
            'costo_usd': float(str(producto.get('COSTO USD', 0)).replace(',', '')) if producto.get('COSTO USD') else 0.00,
            'utilidad': float(str(producto.get('UTIL', 0)).replace(',', '')) if producto.get('UTIL') else 0.00,
            'existencia': int(float(str(producto.get('EXIS', 0)).replace(',', ''))) if producto.get('EXIS') else 0,
            'almacen': producto.get('ALMACEN'),
            'unidad_medida': producto.get('UND MED'),
            'tipo_iva': producto.get('TIPO IVA'),
            'marca': producto.get('MARCA'),
            'grupo': producto.get('GRUPO'),
            'sub_grupo': producto.get('SUB GRUPO'),
            'codigo_barras': producto.get('BARRAS'),
            'imagen1': producto.get('IMAGEN1'),
            'imagen2': producto.get('IMAGEN2'),
            'imagen3': producto.get('IMAGEN3'),
            'imagen1_editada': producto.get('IMAGEN1(EDITADA)'),
            'imagen2_editada': producto.get('IMAGEN2(EDITADA)'),
            'imagen3_editada': producto.get('IMAGEN3(EDITADA)'),
            'metadata': producto.get('METADATA'),
            'nota': producto.get('NOTA'),
            'web': producto.get('WEB'),
            'categoria': producto.get('CATEGORIA'),
            'descripcion_producto': producto.get('Descripción Producto'),
            'propiedades': producto.get('Propiedades'),
            'datos_tecnicos': producto.get('Datos técnicos'),
            'especificaciones': producto.get('Especificaciones'),
            'campos_aplicacion': producto.get('Campos de aplicación'),
            'envases_disponibles': producto.get('Envases disponibles'),
            'pdf': producto.get('pdf'),
            'recomendaciones': producto.get('RECOMENDACIONES'),
            'cont': producto.get('cont'),
            'pr': producto.get('PR'),
            'id_drive': producto.get('IDdrive'),
            'qrt': producto.get('qrt')
        }
        
        if existing_product:
            # Actualizar producto existente
            update_fields = []
            update_values = []
            
            for key, value in datos.items():
                if key != 'codigo_producto':  # No actualizar el código
                    update_fields.append(f"{key} = %s")
                    update_values.append(value)
            
            update_values.append(producto['CODIGO'])  # Para la condición WHERE
            
            update_query = f"""
                UPDATE productos 
                SET {', '.join(update_fields)}, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE codigo_producto = %s
            """
            
            cursor.execute(update_query, update_values)
            logger.info(f"✅ Producto actualizado: {producto['CODIGO']}")
            return "actualizado"
            
        else:
            # Insertar nuevo producto
            insert_query = """
                INSERT INTO productos (
                    codigo_producto, descripcion, pre_precio, precio_a, precio_b, 
                    precio_a_iva, precio_b_iva, ultimo_costo, costo_usd, utilidad,
                    existencia, almacen, unidad_medida, tipo_iva, marca, grupo, 
                    sub_grupo, codigo_barras, imagen1, imagen2, imagen3, 
                    imagen1_editada, imagen2_editada, imagen3_editada, metadata, 
                    nota, web, categoria, descripcion_producto, propiedades, 
                    datos_tecnicos, especificaciones, campos_aplicacion, 
                    envases_disponibles, pdf, recomendaciones, cont, pr, 
                    id_drive, qrt
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            insert_values = (
                datos['codigo_producto'], datos['descripcion'], datos['pre_precio'],
                datos['precio_a'], datos['precio_b'], datos['precio_a_iva'],
                datos['precio_b_iva'], datos['ultimo_costo'], datos['costo_usd'],
                datos['utilidad'], datos['existencia'], datos['almacen'],
                datos['unidad_medida'], datos['tipo_iva'], datos['marca'],
                datos['grupo'], datos['sub_grupo'], datos['codigo_barras'],
                datos['imagen1'], datos['imagen2'], datos['imagen3'],
                datos['imagen1_editada'], datos['imagen2_editada'],
                datos['imagen3_editada'], datos['metadata'], datos['nota'],
                datos['web'], datos['categoria'], datos['descripcion_producto'],
                datos['propiedades'], datos['datos_tecnicos'], datos['especificaciones'],
                datos['campos_aplicacion'], datos['envases_disponibles'],
                datos['pdf'], datos['recomendaciones'], datos['cont'], datos['pr'],
                datos['id_drive'], datos['qrt']
            )
            
            cursor.execute(insert_query, insert_values)
            logger.info(f"✅ Producto insertado: {producto['CODIGO']}")
            return "insertado"
            
    except Error as e:
        logger.error(f"❌ Error procesando producto {producto.get('CODIGO', 'N/A')}: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@bp.route('/cargar_v2', methods=['POST'])
def cargar_productos_v2():
    """Endpoint para cargar productos con campos actualizados"""
    start_time = datetime.now()
    
    try:
        # Crear tabla si no existe
        crear_tabla_productos_v2()
        
        # Obtener datos del request
        data = request.get_json()
        
        if not data or 'productos' not in data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON inválidos o faltantes',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        productos = data['productos']
        timestamp = data.get('timestamp', datetime.now().isoformat())
        origen = data.get('origen', 'API v2')
        
        if not isinstance(productos, list):
            return jsonify({
                'success': False,
                'error': 'El campo "productos" debe ser una lista',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Procesar productos
        insertados = 0
        actualizados = 0
        errores = 0
        productos_con_errores = []
        
        for producto in productos:
            try:
                # Validar producto
                errores_validacion = validar_producto_v2(producto)
                if errores_validacion:
                    errores += 1
                    productos_con_errores.append({
                        'codigo': producto.get('CODIGO', 'N/A'),
                        'errores': errores_validacion
                    })
                    continue
                
                # Procesar producto
                resultado = procesar_producto_v2(producto)
                if resultado == "insertado":
                    insertados += 1
                elif resultado == "actualizado":
                    actualizados += 1
                    
            except Exception as e:
                errores += 1
                productos_con_errores.append({
                    'codigo': producto.get('CODIGO', 'N/A'),
                    'errores': [str(e)]
                })
                logger.error(f"❌ Error procesando producto: {e}")
        
        # Calcular tiempo de procesamiento
        tiempo_procesamiento = (datetime.now() - start_time).total_seconds()
        
        # Respuesta exitosa
        return jsonify({
            'success': True,
            'resumen': {
                'total_productos': len(productos),
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
            'ambiente': 'desarrollo',
            'version': 'v2'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error general en endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'detalles': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/status_v2', methods=['GET'])
def status_productos_v2():
    """Endpoint para verificar estado de la tabla productos_v2"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'productos'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            return jsonify({
                'success': False,
                'error': 'Tabla productos no existe',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # Obtener estadísticas
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
        productos_activos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM productos WHERE existencia > 0")
        productos_con_stock = cursor.fetchone()[0]
        
        # Obtener últimas actualizaciones
        cursor.execute("""
            SELECT codigo_producto, descripcion, fecha_actualizacion 
            FROM productos 
            ORDER BY fecha_actualizacion DESC 
            LIMIT 5
        """)
        ultimas_actualizaciones = []
        for row in cursor.fetchall():
            ultimas_actualizaciones.append({
                'codigo': row[0],
                'descripcion': row[1][:50] + '...' if len(row[1]) > 50 else row[1],
                'fecha': row[2].isoformat() if row[2] else None
            })
        
        return jsonify({
            'success': True,
            'estado': {
                'tabla_existe': True,
                'total_productos': total_productos,
                'productos_activos': productos_activos,
                'productos_con_stock': productos_con_stock
            },
            'ultimas_actualizaciones': ultimas_actualizaciones,
            'timestamp': datetime.now().isoformat(),
            'empresa': 'Maruz Distribuciones',
            'ambiente': 'desarrollo',
            'version': 'v2'
        }), 200
        
    except Error as e:
        logger.error(f"❌ Error verificando estado: {e}")
        return jsonify({
            'success': False,
            'error': 'Error conectando a la base de datos',
            'detalles': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
