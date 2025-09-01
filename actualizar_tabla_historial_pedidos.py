#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar la tabla historial_pedidos
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

def actualizar_tabla_historial_pedidos():
    """Actualizar tabla historial_pedidos con campos necesarios"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Agregar campos faltantes
        campos_agregar = [
            "ADD COLUMN IF NOT EXISTS subtotal DECIMAL(15,2) DEFAULT 0.00",
            "ADD COLUMN IF NOT EXISTS iva DECIMAL(15,2) DEFAULT 0.00",
            "ADD COLUMN IF NOT EXISTS estado_pedido ENUM('pendiente', 'confirmado', 'en_proceso', 'enviado', 'entregado', 'cancelado') DEFAULT 'pendiente'",
            "ADD COLUMN IF NOT EXISTS fecha_pedido TIMESTAMP NULL",
            "ADD COLUMN IF NOT EXISTS fecha_confirmacion TIMESTAMP NULL",
            "ADD COLUMN IF NOT EXISTS fecha_envio TIMESTAMP NULL",
            "ADD COLUMN IF NOT EXISTS fecha_entrega TIMESTAMP NULL",
            "ADD COLUMN IF NOT EXISTS fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            "ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(100)",
            "ADD COLUMN IF NOT EXISTS cliente_nombre VARCHAR(200)",
            "ADD COLUMN IF NOT EXISTS cliente_telefono VARCHAR(20)",
            "ADD COLUMN IF NOT EXISTS cliente_email VARCHAR(200)",
            "ADD COLUMN IF NOT EXISTS direccion_entrega TEXT"
        ]
        
        # Modificar campo estado para incluir 'abierto'
        logger.info("🔄 Modificando campo estado para incluir 'abierto'...")
        try:
            cursor.execute("""
                ALTER TABLE historial_pedidos 
                MODIFY COLUMN estado ENUM('abierto', 'pendiente', 'confirmado', 'en_proceso', 'enviado', 'entregado', 'cancelado', 'cerrado') DEFAULT 'abierto'
            """)
            logger.info("✅ Campo estado modificado exitosamente")
        except Error as e:
            logger.warning(f"⚠️ Campo estado ya modificado o error: {e}")
        
        # Agregar campos uno por uno
        for campo in campos_agregar:
            try:
                cursor.execute(f"ALTER TABLE historial_pedidos {campo}")
                logger.info(f"✅ Campo agregado: {campo}")
            except Error as e:
                logger.warning(f"⚠️ Campo ya existe o error: {e}")
        
        conn.commit()
        
        # Verificar estructura final
        cursor.execute("DESCRIBE historial_pedidos")
        columnas = cursor.fetchall()
        logger.info(f"✅ Tabla 'historial_pedidos' actualizada. Tiene {len(columnas)} columnas:")
        
        for columna in columnas:
            logger.info(f"   - {columna[0]}: {columna[1]}")
        
    except Error as e:
        logger.error(f"❌ Error actualizando tabla: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def verificar_tabla_pedidos_activos():
    """Verificar que la tabla pedidos_activos tenga los campos necesarios"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si existe el campo pedido_id
        cursor.execute("DESCRIBE pedidos_activos")
        columnas = cursor.fetchall()
        nombres_columnas = [col[0] for col in columnas]
        
        if 'pedido_id' not in nombres_columnas:
            logger.info("🔄 Agregando campo pedido_id a pedidos_activos...")
            cursor.execute("""
                ALTER TABLE pedidos_activos 
                ADD COLUMN pedido_id INT NULL,
                ADD INDEX idx_pedido_id (pedido_id)
            """)
            conn.commit()
            logger.info("✅ Campo pedido_id agregado a pedidos_activos")
        else:
            logger.info("✅ Campo pedido_id ya existe en pedidos_activos")
        
        # Verificar estructura final
        cursor.execute("DESCRIBE pedidos_activos")
        columnas = cursor.fetchall()
        logger.info(f"✅ Tabla 'pedidos_activos' verificada. Tiene {len(columnas)} columnas")
        
    except Error as e:
        logger.error(f"❌ Error verificando pedidos_activos: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def main():
    """Función principal"""
    try:
        logger.info("🚀 Iniciando actualización de tablas para sistema de pedido abierto...")
        
        # Actualizar historial_pedidos
        actualizar_tabla_historial_pedidos()
        
        # Verificar pedidos_activos
        verificar_tabla_pedidos_activos()
        
        logger.info("🎉 Todas las tablas actualizadas exitosamente!")
        logger.info("📋 Sistema listo para pedidos abiertos")
        
    except Exception as e:
        logger.error(f"❌ Error en la actualización: {e}")
        raise

if __name__ == "__main__":
    main()
