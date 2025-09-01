#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blueprint para el sistema de pedido abierto
Sistema de Carrito Avanzado - Maruz Distribuciones
"""

from flask import Blueprint, request, jsonify, session, current_app
from mysql.connector import Error
import mysql.connector
import json
import logging
import hashlib
import time
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint
pedido_bp = Blueprint('pedido', __name__, url_prefix='/api/pedido')

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

def generar_pedido_token(pedido_id, session_id=None, cliente_id=None):
    """Generar token opaco y firmado para el pedido"""
    timestamp = str(int(time.time()))
    data = f"{pedido_id}:{session_id or ''}:{cliente_id or ''}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]

def validar_pedido_token(pedido_token, pedido_id, session_id=None, cliente_id=None):
    """Validar que el token pertenece al pedido"""
    # Por simplicidad, validamos que el token existe
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT id, cliente_id, session_id, estado 
        FROM historial_pedidos 
        WHERE id = %s AND estado = 'abierto'
        """
        cursor.execute(query, (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido:
            return False
            
        # Verificar propiedad
        if cliente_id and pedido['cliente_id'] == cliente_id:
            return True
        if session_id and pedido['session_id'] == session_id:
            return True
            
        return False
        
    except Error as e:
        logger.error(f"Error validando token: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def obtener_usuario_actual():
    """Obtener información del usuario actual"""
    try:
        if 'user_id' in session:
            return {'tipo': 'cliente', 'id': session['user_id']}
        else:
            session_id = session.get('carrito_session_id')
            if not session_id:
                # Crear un session_id único si no existe
                import uuid
                session_id = str(uuid.uuid4())
                session['carrito_session_id'] = session_id
            return {'tipo': 'session', 'id': session_id}
    except Exception as e:
        logger.error(f"Error en obtener_usuario_actual: {e}")
        # Fallback: crear session_id
        import uuid
        session_id = str(uuid.uuid4())
        session['carrito_session_id'] = session_id
        return {'tipo': 'session', 'id': session_id}

@pedido_bp.route('/ensure', methods=['POST'])
def ensure_pedido():
    """Crear o recuperar pedido abierto"""
    conn = None
    try:
        logger.info("🔍 Iniciando ensure_pedido...")
        usuario = obtener_usuario_actual()
        logger.info(f"👤 Usuario obtenido: {usuario}")
        
        if not usuario:
            return jsonify({'error': 'Usuario no identificado'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        logger.info("✅ Conexión a BD establecida")
        
        # Buscar pedido abierto existente
        logger.info(f"🔍 Buscando pedido existente para usuario tipo: {usuario['tipo']}, ID: {usuario['id']}")
        
        if usuario['tipo'] == 'cliente':
            query = """
            SELECT id, subtotal, iva, total_pedido, 
                   DATE_FORMAT(fecha_creacion, '%Y-%m-%d %H:%i:%s') as fecha_creacion
            FROM historial_pedidos 
            WHERE cliente_id = %s AND estado = 'abierto'
            ORDER BY fecha_creacion DESC LIMIT 1
            """
            logger.info(f"🔍 Ejecutando consulta cliente: {query}")
            logger.info(f"🔍 Parámetros: {usuario['id']}")
            cursor.execute(query, (usuario['id'],))
        else:
            query = """
            SELECT id, subtotal, iva, total_pedido,
                   DATE_FORMAT(fecha_creacion, '%Y-%m-%d %H:%i:%s') as fecha_creacion
            FROM historial_pedidos 
            WHERE session_id = %s AND estado = 'abierto'
            ORDER BY fecha_creacion DESC LIMIT 1
            """
            logger.info(f"🔍 Ejecutando consulta session: {query}")
            logger.info(f"🔍 Parámetros: {usuario['id']}")
            cursor.execute(query, (usuario['id'],))
            
        pedido_existente = cursor.fetchone()
        logger.info(f"🔍 Pedido existente encontrado: {pedido_existente}")
        
        if pedido_existente:
            # Recuperar pedido existente
            pedido_id = pedido_existente['id']
            
            # Contar unidades y calcular resumen
            cursor.execute("""
                SELECT COUNT(*) as unidades, SUM(total_linea) as subtotal
                FROM pedidos_activos 
                WHERE pedido_id = %s AND estado = 'abierto'
            """, (pedido_id,))
            resumen = cursor.fetchone()
            
            unidades = resumen['unidades'] or 0
            subtotal = float(resumen['subtotal'] or 0)
            total = float(pedido_existente['total_pedido'] or 0)
            
        else:
            # Crear nuevo pedido
            if usuario['tipo'] == 'cliente':
                cursor.execute("""
                    INSERT INTO historial_pedidos 
                    (cliente_id, estado, subtotal, iva, total_pedido, fecha_creacion)
                    VALUES (%s, 'abierto', 0.00, 0.00, 0.00, NOW())
                """, (usuario['id'],))
            else:
                cursor.execute("""
                    INSERT INTO historial_pedidos 
                    (session_id, estado, subtotal, iva, total_pedido, fecha_creacion)
                    VALUES (%s, 'abierto', 0.00, 0.00, 0.00, NOW())
                """, (usuario['id'],))
                
            conn.commit()
            pedido_id = cursor.lastrowid
            unidades = 0
            subtotal = 0.00
            total = 0.00
            
        # Generar token
        pedido_token = generar_pedido_token(pedido_id, 
                                         usuario['id'] if usuario['tipo'] == 'session' else None,
                                         usuario['id'] if usuario['tipo'] == 'cliente' else None)
        
        # Guardar token en sesión para validación
        session['pedido_token'] = pedido_token
        session['pedido_id'] = pedido_id
        
        return jsonify({
            'pedido_id': str(pedido_id),
            'pedido_token': pedido_token,
            'estado': 'abierto',
            'version': int(time.time()),  # Versión simple basada en timestamp
            'resumen': {
                'unidades': unidades,
                'subtotal': round(subtotal, 2),
                'total': round(total, 2)
            }
        })
        
    except Error as e:
        logger.error(f"Error en ensure_pedido: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@pedido_bp.route('/resumen', methods=['GET'])
def obtener_resumen():
    """Obtener resumen del pedido abierto"""
    conn = None
    try:
        pedido_token = request.headers.get('X-Pedido-Token')
        pedido_id = session.get('pedido_id')
        
        if not pedido_token or not pedido_id:
            return jsonify({'error': 'Token de pedido requerido'}), 400
            
        usuario = obtener_usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no identificado'}), 400
            
        # Validar token
        if not validar_pedido_token(pedido_token, pedido_id, 
                                  usuario['id'] if usuario['tipo'] == 'session' else None,
                                  usuario['id'] if usuario['tipo'] == 'cliente' else None):
            return jsonify({'error': 'Token inválido'}), 403
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener resumen del pedido
        cursor.execute("""
            SELECT subtotal, iva, total_pedido
            FROM historial_pedidos 
            WHERE id = %s
        """, (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404
            
        # Contar unidades
        cursor.execute("""
            SELECT COUNT(*) as unidades
            FROM pedidos_activos 
            WHERE pedido_id = %s AND estado = 'abierto'
        """, (pedido_id,))
        unidades = cursor.fetchone()['unidades']
        
        return jsonify({
            'version': int(time.time()),
            'unidades': unidades,
            'subtotal': float(pedido['subtotal']),
            'total': float(pedido['total_pedido'])
        })
        
    except Error as e:
        logger.error(f"Error obteniendo resumen: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@pedido_bp.route('/items/query', methods=['POST'])
def consultar_items():
    """Consultar items del pedido por códigos de producto"""
    conn = None
    try:
        pedido_token = request.headers.get('X-Pedido-Token')
        pedido_id = session.get('pedido_id')
        
        if not pedido_token or not pedido_id:
            return jsonify({'error': 'Token de pedido requerido'}), 400
            
        data = request.get_json()
        if not data or 'codigos' not in data:
            return jsonify({'error': 'Códigos de producto requeridos'}), 400
            
        codigos = data['codigos']
        if not isinstance(codigos, list) or len(codigos) > 200:
            return jsonify({'error': 'Máximo 200 códigos permitidos'}), 400
            
        usuario = obtener_usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no identificado'}), 400
            
        # Validar token
        if not validar_pedido_token(pedido_token, pedido_id, 
                                  usuario['id'] if usuario['tipo'] == 'session' else None,
                                  usuario['id'] if usuario['tipo'] == 'cliente' else None):
            return jsonify({'error': 'Token inválido'}), 403
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Consultar items del pedido para los códigos especificados
        placeholders = ','.join(['%s'] * len(codigos))
        query = f"""
            SELECT producto_codigo, cantidad, descuento
            FROM pedidos_activos 
            WHERE pedido_id = %s AND producto_codigo IN ({placeholders}) AND estado = 'abierto'
        """
        cursor.execute(query, [pedido_id] + codigos)
        
        items = {}
        for row in cursor.fetchall():
            items[row['producto_codigo']] = {
                'cantidad': row['cantidad'],
                'descuento_monto': float(row['descuento'])
            }
            
        return jsonify({'items': items})
        
    except Error as e:
        logger.error(f"Error consultando items: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@pedido_bp.route('/items/batch', methods=['POST'])
def actualizar_items_batch():
    """Actualizar items del pedido en lote (idempotente)"""
    conn = None
    try:
        pedido_token = request.headers.get('X-Pedido-Token')
        pedido_id = session.get('pedido_id')
        
        if not pedido_token or not pedido_id:
            return jsonify({'error': 'Token de pedido requerido'}), 400
            
        data = request.get_json()
        if not data or 'cambios' not in data:
            return jsonify({'error': 'Cambios requeridos'}), 400
            
        cambios = data['cambios']
        if not isinstance(cambios, list) or len(cambios) > 200:
            return jsonify({'error': 'Máximo 200 cambios permitidos'}), 400
            
        usuario = obtener_usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no identificado'}), 400
            
        # Validar token
        if not validar_pedido_token(pedido_token, pedido_id, 
                                  usuario['id'] if usuario['tipo'] == 'session' else None,
                                  usuario['id'] if usuario['tipo'] == 'cliente' else None):
            return jsonify({'error': 'Token inválido'}), 403
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el pedido esté abierto
        cursor.execute("""
            SELECT estado FROM historial_pedidos WHERE id = %s
        """, (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido or pedido['estado'] != 'abierto':
            return jsonify({'error': 'Pedido no está abierto'}), 403
            
        aplicados = []
        
        for cambio in cambios:
            producto_codigo = cambio.get('producto_codigo')
            cantidad = cambio.get('cantidad', 0)
            precio_unitario = cambio.get('precio_unitario')
            descuento_monto = cambio.get('descuento_monto', 0)
            
            if not producto_codigo:
                continue
                
            if cantidad == 0:
                # Eliminar línea
                cursor.execute("""
                    DELETE FROM pedidos_activos 
                    WHERE pedido_id = %s AND producto_codigo = %s
                """, (pedido_id, producto_codigo))
                aplicados.append(producto_codigo)
            else:
                # Verificar si el producto existe
                cursor.execute("""
                    SELECT codigo, precio FROM productos WHERE codigo = %s
                """, (producto_codigo,))
                producto = cursor.fetchone()
                
                if not producto:
                    continue
                    
                precio = precio_unitario or float(producto['precio'])
                total_linea = (precio * cantidad) - descuento_monto
                
                # Upsert idempotente
                cursor.execute("""
                    INSERT INTO pedidos_activos 
                    (pedido_id, producto_codigo, cantidad, precio_unitario, descuento, total_linea, estado, fecha_agregado, fecha_actualizado)
                    VALUES (%s, %s, %s, %s, %s, %s, 'abierto', NOW(), NOW())
                    ON DUPLICATE KEY UPDATE
                    cantidad = VALUES(cantidad),
                    precio_unitario = VALUES(precio_unitario),
                    descuento = VALUES(descuento),
                    total_linea = VALUES(total_linea),
                    fecha_actualizado = NOW()
                """, (pedido_id, producto_codigo, cantidad, precio, descuento_monto, total_linea))
                
                aplicados.append(producto_codigo)
        
        # Recalcular totales del pedido
        cursor.execute("""
            SELECT SUM(total_linea) as subtotal
            FROM pedidos_activos 
            WHERE pedido_id = %s AND estado = 'abierto'
        """, (pedido_id,))
        resumen = cursor.fetchone()
        
        subtotal = float(resumen['subtotal'] or 0)
        iva = subtotal * 0.16
        total = subtotal + iva
        
        # Actualizar totales del pedido
        cursor.execute("""
            UPDATE historial_pedidos 
            SET subtotal = %s, iva = %s, total_pedido = %s, fecha_actualizacion = NOW()
            WHERE id = %s
        """, (subtotal, iva, total, pedido_id))
        
        conn.commit()
        
        # Contar unidades
        cursor.execute("""
            SELECT COUNT(*) as unidades
            FROM pedidos_activos 
            WHERE pedido_id = %s AND estado = 'abierto'
        """, (pedido_id,))
        unidades = cursor.fetchone()['unidades']
        
        return jsonify({
            'version': int(time.time()),
            'resumen': {
                'unidades': unidades,
                'subtotal': round(subtotal, 2),
                'total': round(total, 2)
            },
            'aplicados': aplicados
        })
        
    except Error as e:
        logger.error(f"Error actualizando items batch: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@pedido_bp.route('/item/remove', methods=['POST'])
def quitar_item():
    """Quitar un item específico del pedido"""
    conn = None
    try:
        pedido_token = request.headers.get('X-Pedido-Token')
        pedido_id = session.get('pedido_id')
        
        if not pedido_token or not pedido_id:
            return jsonify({'error': 'Token de pedido requerido'}), 400
            
        data = request.get_json()
        if not data or 'producto_codigo' not in data:
            return jsonify({'error': 'Código de producto requerido'}), 400
            
        producto_codigo = data['producto_codigo']
        
        usuario = obtener_usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no identificado'}), 400
            
        # Validar token
        if not validar_pedido_token(pedido_token, pedido_id, 
                                  usuario['id'] if usuario['tipo'] == 'session' else None,
                                  usuario['id'] if usuario['tipo'] == 'cliente' else None):
            return jsonify({'error': 'Token inválido'}), 403
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el pedido esté abierto
        cursor.execute("""
            SELECT estado FROM historial_pedidos WHERE id = %s
        """, (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido or pedido['estado'] != 'abierto':
            return jsonify({'error': 'Pedido no está abierto'}), 403
            
        # Eliminar item
        cursor.execute("""
            DELETE FROM pedidos_activos 
            WHERE pedido_id = %s AND producto_codigo = %s
        """, (pedido_id, producto_codigo))
        
        # Recalcular totales
        cursor.execute("""
            SELECT SUM(total_linea) as subtotal
            FROM pedidos_activos 
            WHERE pedido_id = %s AND estado = 'abierto'
        """, (pedido_id,))
        resumen = cursor.fetchone()
        
        subtotal = float(resumen['subtotal'] or 0)
        iva = subtotal * 0.16
        total = subtotal + iva
        
        cursor.execute("""
            UPDATE historial_pedidos 
            SET subtotal = %s, iva = %s, total_pedido = %s, fecha_actualizacion = NOW()
            WHERE id = %s
        """, (subtotal, iva, total, pedido_id))
        
        conn.commit()
        
        # Contar unidades
        cursor.execute("""
            SELECT COUNT(*) as unidades
            FROM pedidos_activos 
            WHERE pedido_id = %s AND estado = 'abierto'
        """, (pedido_id,))
        unidades = cursor.fetchone()['unidades']
        
        return jsonify({
            'version': int(time.time()),
            'resumen': {
                'unidades': unidades,
                'subtotal': round(subtotal, 2),
                'total': round(total, 2)
            }
        })
        
    except Error as e:
        logger.error(f"Error quitando item: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@pedido_bp.route('/finalizar', methods=['POST'])
def finalizar_pedido():
    """Finalizar el pedido abierto"""
    conn = None
    try:
        pedido_token = request.headers.get('X-Pedido-Token')
        pedido_id = session.get('pedido_id')
        
        if not pedido_token or not pedido_id:
            return jsonify({'error': 'Token de pedido requerido'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
            
        # Validar campos obligatorios
        campos_requeridos = ['cliente_nombre', 'cliente_telefono', 'cliente_email', 'direccion_entrega']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({'error': f'Campo {campo} es requerido'}), 400
                
        usuario = obtener_usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no identificado'}), 400
            
        # Validar token
        if not validar_pedido_token(pedido_token, pedido_id, 
                                  usuario['id'] if usuario['tipo'] == 'session' else None,
                                  usuario['id'] if usuario['tipo'] == 'cliente' else None):
            return jsonify({'error': 'Token inválido'}), 403
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el pedido esté abierto
        cursor.execute("""
            SELECT estado FROM historial_pedidos WHERE id = %s
        """, (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido or pedido['estado'] != 'abierto':
            return jsonify({'error': 'Pedido no está abierto'}), 403
            
        # Verificar que hay productos
        cursor.execute("""
            SELECT COUNT(*) as total FROM pedidos_activos WHERE pedido_id = %s AND estado = 'abierto'
        """, (pedido_id,))
        if cursor.fetchone()['total'] == 0:
            return jsonify({'error': 'El pedido está vacío'}), 400
            
        # Generar número de pedido único
        fecha_actual = datetime.now()
        numero_pedido = f"PED-{fecha_actual.strftime('%Y%m%d')}-{pedido_id:08d}"
        
        # Preparar notas con datos del cliente
        notas = f"Cliente: {data['cliente_nombre']}\n"
        notas += f"Teléfono: {data['cliente_telefono']}\n"
        notas += f"Email: {data['cliente_email']}\n"
        notas += f"Dirección: {data['direccion_entrega']}\n"
        if data.get('metodo_pago'):
            notas += f"Método de pago: {data['metodo_pago']}\n"
        if data.get('notas'):
            notas += f"Notas adicionales: {data['notas']}"
            
        # Actualizar pedido con datos del cliente y cerrarlo
        cursor.execute("""
            UPDATE historial_pedidos 
            SET numero_pedido = %s, estado_pedido = 'pendiente', estado = 'cerrado',
                cliente_nombre = %s, cliente_telefono = %s, cliente_email = %s,
                direccion_entrega = %s, notas = %s, fecha_pedido = NOW(),
                fecha_actualizacion = NOW()
            WHERE id = %s
        """, (numero_pedido, data['cliente_nombre'], data['cliente_telefono'],
               data['cliente_email'], data['direccion_entrega'], notas, pedido_id))
        
        # Marcar items como cerrados
        cursor.execute("""
            UPDATE pedidos_activos 
            SET estado = 'cerrado' WHERE pedido_id = %s
        """, (pedido_id,))
        
        conn.commit()
        
        # Limpiar sesión
        if 'pedido_token' in session:
            del session['pedido_token']
        if 'pedido_id' in session:
            del session['pedido_id']
        if 'carrito_session_id' in session:
            del session['carrito_session_id']
            
        return jsonify({
            'numero_pedido': numero_pedido,
            'total': float(pedido.get('total_pedido', 0))
        })
        
    except Error as e:
        logger.error(f"Error finalizando pedido: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@pedido_bp.route('/migrar', methods=['POST'])
def migrar_sesion():
    """Migrar pedido de session_id a cliente_id"""
    conn = None
    try:
        pedido_token = request.headers.get('X-Pedido-Token')
        pedido_id = session.get('pedido_id')
        
        if not pedido_token or not pedido_id:
            return jsonify({'error': 'Token de pedido requerido'}), 400
            
        if 'user_id' not in session:
            return jsonify({'error': 'Usuario no autenticado'}), 401
            
        usuario = obtener_usuario_actual()
        if usuario['tipo'] != 'cliente':
            return jsonify({'error': 'Usuario no autenticado'}), 401
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el pedido esté abierto
        cursor.execute("""
            SELECT estado, session_id FROM historial_pedidos WHERE id = %s
        """, (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido or pedido['estado'] != 'abierto':
            return jsonify({'error': 'Pedido no está abierto'}), 403
            
        if not pedido['session_id']:
            return jsonify({'error': 'Pedido ya tiene cliente_id'}), 400
            
        # Migrar pedido
        cursor.execute("""
            UPDATE historial_pedidos 
            SET cliente_id = %s, session_id = NULL, fecha_actualizacion = NOW()
            WHERE id = %s
        """, (usuario['id'], pedido_id))
        
        conn.commit()
        
        return jsonify({'mensaje': 'Pedido migrado exitosamente'})
        
    except Error as e:
        logger.error(f"Error migrando sesión: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@pedido_bp.route('/stream')
def stream_pedido():
    """Stream de eventos SSE para sincronización en tiempo real"""
    try:
        pedido_token = request.headers.get('X-Pedido-Token')
        pedido_id = session.get('pedido_id')
        
        if not pedido_token or not pedido_id:
            return jsonify({'error': 'Token de pedido requerido'}), 400
            
        usuario = obtener_usuario_actual()
        if not usuario:
            return jsonify({'error': 'Usuario no identificado'}), 400
            
        # Validar token
        if not validar_pedido_token(pedido_token, pedido_id, 
                                  usuario['id'] if usuario['tipo'] == 'session' else None,
                                  usuario['id'] if usuario['tipo'] == 'cliente' else None):
            return jsonify({'error': 'Token inválido'}), 403
            
        def generate():
            """Generar eventos SSE"""
            conn = None
            try:
                # Enviar resumen inicial
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                while True:
                    # Obtener resumen actual
                    cursor.execute("""
                        SELECT subtotal, iva, total_pedido
                        FROM historial_pedidos WHERE id = %s
                    """, (pedido_id,))
                    pedido = cursor.fetchone()
                    
                    if pedido:
                        cursor.execute("""
                            SELECT COUNT(*) as unidades
                            FROM pedidos_activos 
                            WHERE pedido_id = %s AND estado = 'abierto'
                        """, (pedido_id,))
                        unidades = cursor.fetchone()['unidades']
                        
                        yield f"data: {json.dumps({'event': 'resumen', 'data': {'version': int(time.time()), 'unidades': unidades, 'subtotal': float(pedido['subtotal']), 'total': float(pedido['total_pedido'])}})}\n\n"
                    
                    # Heartbeat cada 25 segundos
                    time.sleep(25)
                    
            except Exception as e:
                logger.error(f"Error en stream SSE: {e}")
                yield f"data: {json.dumps({'event': 'sync_hint', 'data': {'reason': 'reconnect'}})}\n\n"
            finally:
                if conn and conn.is_connected():
                    cursor.close()
                    conn.close()
                    
        return current_app.response_class(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'X-Pedido-Token'
            }
        )
        
    except Exception as e:
        logger.error(f"Error en stream: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
