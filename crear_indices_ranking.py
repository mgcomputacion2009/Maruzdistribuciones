#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 CREADOR DE ÍNDICES - TABLA RANKING
Script simple para crear índices en la tabla de ranking

Autor: Maruz Distribuciones
Fecha: 1 de septiembre 2024
Versión: 1.0
"""

import mysql.connector

def crear_indices():
    """
    Crea los índices necesarios para la tabla de ranking
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
        
        print("🔍 Creando índices para la tabla de ranking...")
        
        # Crear índices uno por uno
        indices = [
            ("idx_cliente_score", "cliente_id, score_ranking DESC"),
            ("idx_producto_score", "producto_id, score_ranking DESC"),
            ("idx_cliente_fecha", "cliente_id, ultima_busqueda DESC"),
            ("idx_producto_frecuencia", "producto_id, frecuencia_busqueda DESC")
        ]
        
        for nombre_indice, campos in indices:
            try:
                sql = f"CREATE INDEX {nombre_indice} ON ranking_productos_cliente ({campos})"
                cursor.execute(sql)
                print(f"✅ Índice '{nombre_indice}' creado exitosamente")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    print(f"⚠️  Índice '{nombre_indice}' ya existe")
                else:
                    print(f"❌ Error creando índice '{nombre_indice}': {e}")
        
        connection.commit()
        print("✅ Todos los índices han sido procesados")
        
        # Verificar índices existentes
        cursor.execute("SHOW INDEX FROM ranking_productos_cliente")
        indexes = cursor.fetchall()
        
        print(f"\n🔍 ÍNDICES EXISTENTES:")
        for index in indexes:
            print(f"   - {index[2]} ({index[4]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("✅ Conexión cerrada")

if __name__ == "__main__":
    crear_indices()
