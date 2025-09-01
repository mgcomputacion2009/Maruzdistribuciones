#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗄️ CREADOR DE TABLA DE RANKING - MARUZ DISTRIBUCIONES
Script para crear la tabla de ranking personalizado de productos por cliente

Autor: Maruz Distribuciones
Fecha: 1 de septiembre 2024
Versión: 1.0
"""

import mysql.connector
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append('/var/www/maruz')

try:
    from app.maruz_distribuciones.config import get_db_connection
    print("✅ Configuración importada correctamente")
except ImportError as e:
    print(f"❌ Error importando configuración: {e}")
    sys.exit(1)

def crear_tabla_ranking():
    """
    Crea la tabla de ranking de productos por cliente
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        print("🔧 Creando tabla de ranking de productos por cliente...")
        
        # SQL para crear la tabla de ranking
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS ranking_productos_cliente (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id INT NOT NULL,
            producto_id INT NOT NULL,
            score_ranking DECIMAL(10,4) DEFAULT 0.0000,
            ultima_busqueda TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            frecuencia_busqueda INT DEFAULT 1,
            UNIQUE KEY unique_cliente_producto (cliente_id, producto_id),
            INDEX idx_cliente_score (cliente_id, score_ranking DESC),
            INDEX idx_producto_score (producto_id, score_ranking DESC),
            FOREIGN KEY (cliente_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_table_sql)
        connection.commit()
        
        print("✅ Tabla 'ranking_productos_cliente' creada exitosamente")
        
        # Verificar que la tabla se creó
        cursor.execute("DESCRIBE ranking_productos_cliente")
        columns = cursor.fetchall()
        
        print(f"\n📋 ESTRUCTURA DE LA TABLA:")
        print(f"{'Campo':<20} {'Tipo':<20} {'Nulo':<8} {'Llave':<8} {'Default':<10}")
        print("-" * 70)
        for column in columns:
            print(f"{column[0]:<20} {column[1]:<20} {column[2]:<8} {column[3]:<8} {str(column[4]):<10}")
        
        # Crear índices adicionales para optimizar consultas
        print(f"\n🔍 Creando índices adicionales...")
        
        # Índice para consultas por cliente y fecha
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cliente_fecha 
        ON ranking_productos_cliente (cliente_id, ultima_busqueda DESC)
        """)
        
        # Índice para consultas por producto y frecuencia
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_producto_frecuencia 
        ON ranking_productos_cliente (producto_id, frecuencia_busqueda DESC)
        """)
        
        connection.commit()
        print("✅ Índices adicionales creados exitosamente")
        
        # Verificar índices
        cursor.execute("SHOW INDEX FROM ranking_productos_cliente")
        indexes = cursor.fetchall()
        
        print(f"\n🔍 ÍNDICES CREADOS:")
        for index in indexes:
            print(f"   - {index[2]} ({index[4]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
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
    print("🗄️ CREADOR DE TABLA DE RANKING - MARUZ DISTRIBUCIONES")
    print("=" * 60)
    
    if crear_tabla_ranking():
        print(f"\n✅ SISTEMA DE RANKING CREADO EXITOSAMENTE")
        print(f"   La tabla está lista para registrar búsquedas de clientes")
        print(f"   Los productos se posicionarán automáticamente por relevancia")
    else:
        print(f"\n❌ Error en la creación del sistema de ranking")
        sys.exit(1)

if __name__ == "__main__":
    main()
