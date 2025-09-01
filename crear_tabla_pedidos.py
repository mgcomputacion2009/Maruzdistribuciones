#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛒 CREADOR DE TABLA DE PEDIDOS ACTIVOS - MARUZ DISTRIBUCIONES
Script para crear la tabla de carrito persistente
"""

import mysql.connector
from mysql.connector import Error

def crear_tabla_pedidos():
    """
    Crea la tabla de pedidos activos para carrito persistente
    """
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            database='maruz_db',
            user='miguel',
            password='Mg645418037$$',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        cursor = connection.cursor()
        
        print("🛒 Creando tabla de pedidos activos...")
        
        # SQL para crear la tabla de pedidos activos
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS pedidos_activos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id INT NULL,
            session_id VARCHAR(255) NULL,
            producto_codigo VARCHAR(100) NOT NULL,
            cantidad INT NOT NULL DEFAULT 1,
            precio_unitario DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            descuento DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            total_linea DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            estado ENUM('activo', 'cerrado') DEFAULT 'activo',
            
            -- Índices para optimizar consultas
            INDEX idx_cliente_estado (cliente_id, estado),
            INDEX idx_session_estado (session_id, estado),
            INDEX idx_producto (producto_codigo),
            INDEX idx_fecha (fecha_agregado),
            
            -- Clave única para evitar duplicados del mismo producto por cliente/sesión
            UNIQUE KEY unique_producto_cliente (cliente_id, producto_codigo, estado),
            UNIQUE KEY unique_producto_session (session_id, producto_codigo, estado),
            
            -- Foreign keys
            FOREIGN KEY (cliente_id) REFERENCES usuarios(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_sql)
        connection.commit()
        
        print("✅ Tabla 'pedidos_activos' creada exitosamente")
        
        # Verificar estructura
        cursor.execute("DESCRIBE pedidos_activos")
        columns = cursor.fetchall()
        
        print(f"\n📋 ESTRUCTURA DE LA TABLA:")
        print(f"{'Campo':<20} {'Tipo':<25} {'Nulo':<8} {'Llave':<8} {'Default':<15}")
        print("-" * 80)
        for column in columns:
            print(f"{column[0]:<20} {column[1]:<25} {column[2]:<8} {column[3]:<8} {str(column[4]):<15}")
        
        # Crear tabla de historial de pedidos cerrados
        print(f"\n📋 Creando tabla de historial de pedidos...")
        
        create_historial_sql = """
        CREATE TABLE IF NOT EXISTS historial_pedidos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pedido_id VARCHAR(50) NOT NULL,
            cliente_id INT NULL,
            session_id VARCHAR(255) NULL,
            total_pedido DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            cantidad_productos INT NOT NULL DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_cierre TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado ENUM('pendiente', 'confirmado', 'cancelado') DEFAULT 'pendiente',
            notas TEXT,
            
            INDEX idx_cliente (cliente_id),
            INDEX idx_pedido (pedido_id),
            INDEX idx_fecha (fecha_creacion),
            INDEX idx_estado (estado)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_historial_sql)
        connection.commit()
        
        print("✅ Tabla 'historial_pedidos' creada exitosamente")
        
        # Crear índices adicionales
        print(f"\n🔍 Creando índices adicionales...")
        
        indices = [
            ("idx_cliente_producto_estado", "cliente_id, producto_codigo, estado"),
            ("idx_session_producto_estado", "session_id, producto_codigo, estado"),
            ("idx_fecha_estado", "fecha_agregado, estado")
        ]
        
        for nombre, campos in indices:
            try:
                sql = f"CREATE INDEX {nombre} ON pedidos_activos ({campos})"
                cursor.execute(sql)
                print(f"✅ Índice '{nombre}' creado")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    print(f"⚠️  Índice '{nombre}' ya existe")
                else:
                    print(f"❌ Error creando índice '{nombre}': {e}")
        
        connection.commit()
        print("✅ Todos los índices han sido procesados")
        
        return True
        
    except Error as e:
        print(f"❌ Error: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("✅ Conexión cerrada")

def main():
    """
    Función principal
    """
    print("🛒 CREADOR DE TABLA DE PEDIDOS ACTIVOS - MARUZ DISTRIBUCIONES")
    print("=" * 70)
    
    if crear_tabla_pedidos():
        print(f"\n✅ SISTEMA DE CARRITO PERSISTENTE CREADO EXITOSAMENTE")
        print(f"   Las funcionalidades implementadas son:")
        print(f"   ✅ Carrito persistente entre páginas")
        print(f"   ✅ Soporte multi-cliente simultáneo")
        print(f"   ✅ Totalización automática en tiempo real")
        print(f"   ✅ Historial de pedidos organizado")
        print(f"   ✅ Botón papelera para limpiar carrito")
    else:
        print(f"\n❌ Error en la creación del sistema de pedidos")
        exit(1)

if __name__ == "__main__":
    main()
