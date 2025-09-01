#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear las tablas necesarias para el historial de pedidos
Sistema de Carrito Avanzado - Maruz Distribuciones
"""

import mysql.connector
from mysql.connector import Error
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def crear_tabla_historial_pedidos():
    """Crear tabla para historial de pedidos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS historial_pedidos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            
            -- Información del pedido
            numero_pedido VARCHAR(50) NOT NULL UNIQUE,
            estado_pedido ENUM('pendiente', 'confirmado', 'en_proceso', 'enviado', 'entregado', 'cancelado') DEFAULT 'pendiente',
            
            -- Identificación del cliente
            cliente_id INT NULL,
            session_id VARCHAR(100) NULL,
            
            -- Datos del cliente
            cliente_nombre VARCHAR(200) NOT NULL,
            cliente_telefono VARCHAR(20) NOT NULL,
            cliente_email VARCHAR(200) NOT NULL,
            direccion_entrega TEXT NOT NULL,
            
            -- Totales del pedido
            subtotal DECIMAL(15,2) DEFAULT 0.00,
            iva DECIMAL(15,2) DEFAULT 0.00,
            total_pedido DECIMAL(15,2) DEFAULT 0.00,
            
            -- Fechas
            fecha_pedido TIMESTAMP NULL,
            fecha_confirmacion TIMESTAMP NULL,
            fecha_envio TIMESTAMP NULL,
            fecha_entrega TIMESTAMP NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            -- Notas adicionales
            notas TEXT,
            metodo_pago VARCHAR(100),
            
            -- Índices para búsquedas rápidas
            INDEX idx_numero_pedido (numero_pedido),
            INDEX idx_cliente_id (cliente_id),
            INDEX idx_session_id (session_id),
            INDEX idx_estado (estado_pedido),
            INDEX idx_fecha_pedido (fecha_pedido),
            INDEX idx_fecha_creacion (fecha_creacion)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        logger.info("✅ Tabla 'historial_pedidos' creada/verificada exitosamente")
        
    except Error as e:
        logger.error(f"❌ Error creando tabla historial_pedidos: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def crear_tabla_historial_productos_pedido():
    """Crear tabla para productos de cada pedido"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS historial_productos_pedido (
            id INT AUTO_INCREMENT PRIMARY KEY,
            
            -- Referencia al pedido
            pedido_id INT NOT NULL,
            
            -- Información del producto
            producto_codigo VARCHAR(100) NOT NULL,
            cantidad INT NOT NULL,
            precio_unitario DECIMAL(15,2) NOT NULL,
            descuento DECIMAL(15,2) DEFAULT 0.00,
            total_linea DECIMAL(15,2) NOT NULL,
            
            -- Fecha de creación
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Claves foráneas
            FOREIGN KEY (pedido_id) REFERENCES historial_pedidos(id) ON DELETE CASCADE,
            
            -- Índices para búsquedas rápidas
            INDEX idx_pedido_id (pedido_id),
            INDEX idx_producto_codigo (producto_codigo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        logger.info("✅ Tabla 'historial_productos_pedido' creada/verificada exitosamente")
        
    except Error as e:
        logger.error(f"❌ Error creando tabla historial_productos_pedido: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def verificar_tablas():
    """Verificar que las tablas se crearon correctamente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar historial_pedidos
        cursor.execute("DESCRIBE historial_pedidos")
        columnas_pedidos = cursor.fetchall()
        logger.info(f"✅ Tabla 'historial_pedidos' tiene {len(columnas_pedidos)} columnas")
        
        # Verificar historial_productos_pedido
        cursor.execute("DESCRIBE historial_productos_pedido")
        columnas_productos = cursor.fetchall()
        logger.info(f"✅ Tabla 'historial_productos_pedido' tiene {len(columnas_productos)} columnas")
        
        # Verificar pedidos_activos (debe existir)
        cursor.execute("DESCRIBE pedidos_activos")
        columnas_activos = cursor.fetchall()
        logger.info(f"✅ Tabla 'pedidos_activos' tiene {len(columnas_activos)} columnas")
        
    except Error as e:
        logger.error(f"❌ Error verificando tablas: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def main():
    """Función principal"""
    try:
        logger.info("🚀 Iniciando creación de tablas para historial de pedidos...")
        
        # Crear tablas
        crear_tabla_historial_pedidos()
        crear_tabla_historial_productos_pedido()
        
        # Verificar tablas
        verificar_tablas()
        
        logger.info("🎉 Todas las tablas creadas exitosamente!")
        logger.info("📋 Tablas disponibles:")
        logger.info("   - historial_pedidos")
        logger.info("   - historial_productos_pedido")
        logger.info("   - pedidos_activos (ya existía)")
        
    except Exception as e:
        logger.error(f"❌ Error en la ejecución: {e}")
        raise

if __name__ == "__main__":
    main()
