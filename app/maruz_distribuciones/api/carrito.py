# 🛒 API DEL CARRITO DE COMPRAS - MARUZ DISTRIBUCIONES
# API para manejar carrito persistente entre páginas

from flask import Blueprint, request, jsonify, session, current_app
import json
import logging
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import uuid

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear Blueprint
carrito_bp = Blueprint('carrito', __name__, url_prefix='/api/carrito')

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        return mysql.connector.connect(
            host='127.0.0.1',
            user='miguel',
            password='Mg645418037$$',
            database='maruz_db',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
    except Error as e:
        logger.error(f"❌ Error conectando a base de datos: {e}")
        raise

def get_session_or_user_id():
    """Obtener ID de cliente o generar session_id"""
    if 'user' in session and 'id' in session['user']:
        return {'cliente_id': session['user']['id'], 'session_id': None}
    else:
        # Generar session_id único si no hay usuario logueado
        if 'carrito_session_id' not in session:
            session['carrito_session_id'] = str(uuid.uuid4())
        return {'cliente_id': None, 'session_id': session['carrito_session_id']}

@carrito_bp.route('/agregar', methods=['POST'])
def agregar_producto():
    """Agregar producto al carrito"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['producto_codigo', 'cantidad', 'precio_unitario']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Campo {field} es requerido'}), 400
        
        producto_codigo = data['producto_codigo']
        cantidad = int(data['cantidad'])
        precio_unitario = float(data['precio_unitario'])
        descuento = float(data.get('descuento', 0))
        
        # Calcular total de línea
        total_linea = (precio_unitario * cantidad) - descuento
        
        # Obtener identificador del cliente/sesión
        ids = get_session_or_user_id()
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar si el producto ya existe en el carrito
        if ids['cliente_id']:
            check_sql = """
                SELECT id, cantidad FROM pedidos_activos 
                WHERE cliente_id = %s AND producto_codigo = %s AND estado = 'activo'
            """
            cursor.execute(check_sql, (ids['cliente_id'], producto_codigo))
        else:
            check_sql = """
                SELECT id, cantidad FROM pedidos_activos 
                WHERE session_id = %s AND producto_codigo = %s AND estado = 'activo'
            """
            cursor.execute(check_sql, (ids['session_id'], producto_codigo))
        
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Actualizar cantidad existente
            nueva_cantidad = existing_item['cantidad'] + cantidad
            nuevo_total = (precio_unitario * nueva_cantidad) - descuento
            
            update_sql = """
                UPDATE pedidos_activos 
                SET cantidad = %s, precio_unitario = %s, descuento = %s, 
                    total_linea = %s, fecha_actualizado = NOW()
                WHERE id = %s
            """
            cursor.execute(update_sql, (nueva_cantidad, precio_unitario, descuento, nuevo_total, existing_item['id']))
            
            message = f"Producto actualizado: {nueva_cantidad} unidades"
        else:
            # Insertar nuevo producto
            insert_sql = """
                INSERT INTO pedidos_activos 
                (cliente_id, session_id, producto_codigo, cantidad, precio_unitario, descuento, total_linea)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                ids['cliente_id'], ids['session_id'], producto_codigo, 
                cantidad, precio_unitario, descuento, total_linea
            ))
            
            message = f"Producto agregado al carrito: {cantidad} unidades"
        
        connection.commit()
        
        # Obtener resumen actualizado del carrito
        resumen = obtener_resumen_carrito_interno(ids)
        
        logger.info(f"✅ Producto agregado al carrito: {producto_codigo} - {message}")
        
        return jsonify({
            'success': True,
            'message': message,
            'resumen': resumen
        })
        
    except Exception as e:
        logger.error(f"❌ Error agregando producto al carrito: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@carrito_bp.route('/actualizar', methods=['POST'])
def actualizar_producto():
    """Actualizar cantidad/descuento de producto en carrito"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['producto_codigo', 'cantidad', 'precio_unitario']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Campo {field} es requerido'}), 400
        
        producto_codigo = data['producto_codigo']
        cantidad = int(data['cantidad'])
        precio_unitario = float(data['precio_unitario'])
        descuento = float(data.get('descuento', 0))
        
        # Calcular total de línea
        total_linea = (precio_unitario * cantidad) - descuento
        
        # Obtener identificador del cliente/sesión
        ids = get_session_or_user_id()
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Actualizar producto en carrito
        if ids['cliente_id']:
            update_sql = """
                UPDATE pedidos_activos 
                SET cantidad = %s, precio_unitario = %s, descuento = %s, 
                    total_linea = %s, fecha_actualizado = NOW()
                WHERE cliente_id = %s AND producto_codigo = %s AND estado = 'activo'
            """
            cursor.execute(update_sql, (cantidad, precio_unitario, descuento, total_linea, ids['cliente_id'], producto_codigo))
        else:
            update_sql = """
                UPDATE pedidos_activos 
                SET cantidad = %s, precio_unitario = %s, descuento = %s, 
                    total_linea = %s, fecha_actualizado = NOW()
                WHERE session_id = %s AND producto_codigo = %s AND estado = 'activo'
            """
            cursor.execute(update_sql, (cantidad, precio_unitario, descuento, total_linea, ids['session_id'], producto_codigo))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Producto no encontrado en carrito'}), 404
        
        connection.commit()
        
        # Obtener resumen actualizado del carrito
        resumen = obtener_resumen_carrito_interno(ids)
        
        logger.info(f"✅ Producto actualizado en carrito: {producto_codigo}")
        
        return jsonify({
            'success': True,
            'message': 'Producto actualizado correctamente',
            'resumen': resumen
        })
        
    except Exception as e:
        logger.error(f"❌ Error actualizando producto en carrito: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@carrito_bp.route('/quitar', methods=['POST'])
def quitar_producto():
    """Quitar producto del carrito"""
    try:
        data = request.get_json()
        
        if 'producto_codigo' not in data:
            return jsonify({'success': False, 'error': 'Campo producto_codigo es requerido'}), 400
        
        producto_codigo = data['producto_codigo']
        ids = get_session_or_user_id()
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Eliminar producto del carrito
        if ids['cliente_id']:
            delete_sql = """
                DELETE FROM pedidos_activos 
                WHERE cliente_id = %s AND producto_codigo = %s AND estado = 'activo'
            """
            cursor.execute(delete_sql, (ids['cliente_id'], producto_codigo))
        else:
            delete_sql = """
                DELETE FROM pedidos_activos 
                WHERE session_id = %s AND producto_codigo = %s AND estado = 'activo'
            """
            cursor.execute(delete_sql, (ids['session_id'], producto_codigo))
        
        connection.commit()
        
        # Obtener resumen actualizado del carrito
        resumen = obtener_resumen_carrito_interno(ids)
        
        logger.info(f"✅ Producto quitado del carrito: {producto_codigo}")
        
        return jsonify({
            'success': True,
            'message': 'Producto quitado del carrito',
            'resumen': resumen
        })
        
    except Exception as e:
        logger.error(f"❌ Error quitando producto del carrito: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@carrito_bp.route('/limpiar', methods=['POST'])
def limpiar_carrito():
    """Limpiar todo el carrito (botón papelera)"""
    try:
        ids = get_session_or_user_id()
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Marcar todos los productos como cerrados
        if ids['cliente_id']:
            update_sql = """
                UPDATE pedidos_activos 
                SET estado = 'cerrado', fecha_actualizado = NOW()
                WHERE cliente_id = %s AND estado = 'activo'
            """
            cursor.execute(update_sql, (ids['cliente_id'],))
        else:
            update_sql = """
                UPDATE pedidos_activos 
                SET estado = 'cerrado', fecha_actualizado = NOW()
                WHERE session_id = %s AND estado = 'activo'
            """
            cursor.execute(update_sql, (ids['session_id'],))
        
        connection.commit()
        
        logger.info(f"✅ Carrito limpiado para {'cliente ' + str(ids['cliente_id']) if ids['cliente_id'] else 'sesión ' + ids['session_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Carrito limpiado correctamente',
            'resumen': {'total_unidades': 0, 'total_monto': 0.00, 'cantidad_productos': 0}
        })
        
    except Exception as e:
        logger.error(f"❌ Error limpiando carrito: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@carrito_bp.route('/resumen', methods=['GET'])
def obtener_resumen_carrito(ids=None):
    """Obtener resumen del carrito actual"""
    try:
        if ids is None:
            ids = get_session_or_user_id()
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Obtener productos del carrito
        if ids['cliente_id']:
            select_sql = """
                SELECT producto_codigo, cantidad, precio_unitario, descuento, total_linea
                FROM pedidos_activos 
                WHERE cliente_id = %s AND estado = 'activo'
                ORDER BY fecha_agregado DESC
            """
            cursor.execute(select_sql, (ids['cliente_id'],))
        else:
            select_sql = """
                SELECT producto_codigo, cantidad, precio_unitario, descuento, total_linea
                FROM pedidos_activos 
                WHERE session_id = %s AND estado = 'activo'
                ORDER BY fecha_agregado DESC
            """
            cursor.execute(select_sql, (ids['session_id'],))
        
        productos = cursor.fetchall()
        
        # Calcular resumen
        total_unidades = sum(p['cantidad'] for p in productos)
        total_monto = sum(p['total_linea'] for p in productos)
        cantidad_productos = len(productos)
        
        resumen = {
            'total_unidades': total_unidades,
            'total_monto': round(total_monto, 2),
            'cantidad_productos': cantidad_productos,
            'productos': productos
        }
        
        return jsonify(resumen)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen del carrito: {e}")
        return jsonify({'total_unidades': 0, 'total_monto': 0.00, 'cantidad_productos': 0, 'productos': []})
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

def obtener_resumen_carrito_interno(ids=None):
    """Función interna para obtener resumen del carrito (devuelve diccionario)"""
    try:
        if ids is None:
            ids = get_session_or_user_id()
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Obtener productos del carrito
        if ids['cliente_id']:
            select_sql = """
                SELECT producto_codigo, cantidad, precio_unitario, descuento, total_linea
                FROM pedidos_activos 
                WHERE cliente_id = %s AND estado = 'activo'
                ORDER BY fecha_agregado DESC
            """
            cursor.execute(select_sql, (ids['cliente_id'],))
        else:
            select_sql = """
                SELECT producto_codigo, cantidad, precio_unitario, descuento, total_linea
                FROM pedidos_activos 
                WHERE session_id = %s AND estado = 'activo'
                ORDER BY fecha_agregado DESC
            """
            cursor.execute(select_sql, (ids['session_id'],))
        
        productos = cursor.fetchall()
        
        # Calcular resumen
        total_unidades = sum(p['cantidad'] for p in productos)
        total_monto = sum(p['total_linea'] for p in productos)
        cantidad_productos = len(productos)
        
        resumen = {
            'total_unidades': total_unidades,
            'total_monto': round(total_monto, 2),
            'cantidad_productos': cantidad_productos,
            'productos': productos
        }
        
        return resumen
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen del carrito: {e}")
        return {'total_unidades': 0, 'total_monto': 0.00, 'cantidad_productos': 0, 'productos': []}
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@carrito_bp.route('/productos', methods=['GET'])
def obtener_productos_carrito():
    """Obtener lista de productos en el carrito"""
    try:
        ids = get_session_or_user_id()
        resumen = obtener_resumen_carrito_interno(ids)
        
        return jsonify({
            'success': True,
            'resumen': resumen
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo productos del carrito: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@carrito_bp.route('/finalizar-compra', methods=['POST'])
def finalizar_compra():
    """Finalizar compra y procesar pedido"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos para finalizar compra
        required_fields = ['cliente_nombre', 'cliente_telefono', 'cliente_email', 'direccion_entrega']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Campo {field} es requerido'}), 400
        
        # Obtener identificador del cliente/sesión
        ids = get_session_or_user_id()
        
        if not ids['cliente_id'] and not ids['session_id']:
            return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar que hay productos en el carrito
        if ids['cliente_id']:
            check_carrito_sql = """
                SELECT COUNT(*) as total FROM pedidos_activos 
                WHERE cliente_id = %s AND estado = 'activo'
            """
            cursor.execute(check_carrito_sql, (ids['cliente_id'],))
        else:
            check_carrito_sql = """
                SELECT COUNT(*) as total FROM pedidos_activos 
                WHERE session_id = %s AND estado = 'activo'
            """
            cursor.execute(check_carrito_sql, (ids['session_id'],))
        
        carrito_vacio = cursor.fetchone()['total'] == 0
        if carrito_vacio:
            return jsonify({'success': False, 'error': 'El carrito está vacío'}), 400
        
        # Generar número de pedido único
        numero_pedido = f"PED-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Obtener productos del carrito
        if ids['cliente_id']:
            productos_sql = """
                SELECT * FROM pedidos_activos 
                WHERE cliente_id = %s AND estado = 'activo'
            """
            cursor.execute(productos_sql, (ids['cliente_id'],))
        else:
            productos_sql = """
                SELECT * FROM pedidos_activos 
                WHERE session_id = %s AND estado = 'activo'
            """
            cursor.execute(productos_sql, (ids['session_id'],))
        
        productos_carrito = cursor.fetchall()
        
        # Calcular totales
        subtotal = float(sum(p['total_linea'] for p in productos_carrito))
        iva = subtotal * 0.16  # 16% IVA
        total_pedido = subtotal + iva
        
        # Crear pedido en historial
        insert_pedido_sql = """
            INSERT INTO historial_pedidos 
            (pedido_id, cliente_id, session_id, total_pedido, cantidad_productos, 
             estado, notas, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, 'pendiente', %s, NOW())
        """
        
        # Crear nota con información del cliente
        nota_cliente = f"Cliente: {data['cliente_nombre']}\nTeléfono: {data['cliente_telefono']}\nEmail: {data['cliente_email']}\nDirección: {data['direccion_entrega']}\nMétodo de pago: {data.get('metodo_pago', 'No especificado')}\nNotas: {data.get('notas', 'Ninguna')}"
        
        cursor.execute(insert_pedido_sql, (
            numero_pedido, ids['cliente_id'], ids['session_id'],
            total_pedido, len(productos_carrito), nota_cliente
        ))
        
        pedido_id = cursor.lastrowid
        
        # Insertar productos del pedido
        for producto in productos_carrito:
            insert_producto_sql = """
                INSERT INTO historial_productos_pedido 
                (pedido_id, producto_codigo, cantidad, precio_unitario, 
                 descuento, total_linea)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_producto_sql, (
                pedido_id, producto['producto_codigo'], producto['cantidad'],
                producto['precio_unitario'], producto['descuento'], producto['total_linea']
            ))
        
        # Marcar productos del carrito como procesados
        if ids['cliente_id']:
            update_carrito_sql = """
                UPDATE pedidos_activos 
                SET estado = 'cerrado', fecha_actualizado = NOW()
                WHERE cliente_id = %s AND estado = 'activo'
            """
            cursor.execute(update_carrito_sql, (ids['cliente_id'],))
        else:
            update_carrito_sql = """
                UPDATE pedidos_activos 
                SET estado = 'cerrado', fecha_actualizado = NOW()
                WHERE session_id = %s AND estado = 'activo'
            """
            cursor.execute(update_carrito_sql, (ids['session_id'],))
        
        connection.commit()
        
        # Limpiar sesión del carrito si es usuario anónimo
        if not ids['cliente_id'] and 'carrito_session_id' in session:
            session.pop('carrito_session_id', None)
        
        return jsonify({
            'success': True,
            'message': 'Pedido procesado exitosamente',
            'pedido': {
                'numero_pedido': numero_pedido,
                'pedido_id': pedido_id,
                'cliente_nombre': data['cliente_nombre'],
                'subtotal': round(subtotal, 2),
                'iva': round(iva, 2),
                'total_pedido': round(total_pedido, 2),
                'fecha_pedido': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'productos': len(productos_carrito)
            }
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': 'Datos inválidos en la solicitud'}), 400
    except Error as e:
        logger.error(f"❌ Error en base de datos: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return jsonify({'success': False, 'error': 'Error inesperado del servidor'}), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
