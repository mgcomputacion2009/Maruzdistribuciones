#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VERIFICADOR DE RANKING - MARUZ DISTRIBUCIONES
Script para verificar el estado de la tabla de ranking

Autor: Maruz Distribuciones
Fecha: 1 de septiembre 2024
Versión: 1.0
"""

import mysql.connector

def verificar_ranking():
    """
    Verifica el estado de la tabla de ranking
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
        
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 VERIFICANDO SISTEMA DE RANKING")
        print("=" * 50)
        
        # 1. Verificar que la tabla existe
        print("1️⃣ Verificando existencia de la tabla...")
        cursor.execute("SHOW TABLES LIKE 'ranking_productos_cliente'")
        tabla_existe = cursor.fetchone()
        
        if tabla_existe:
            print("✅ Tabla 'ranking_productos_cliente' existe")
        else:
            print("❌ Tabla 'ranking_productos_cliente' NO existe")
            return False
        
        # 2. Verificar estructura de la tabla
        print("\n2️⃣ Verificando estructura de la tabla...")
        cursor.execute("DESCRIBE ranking_productos_cliente")
        columnas = cursor.fetchall()
        
        print("📋 Columnas encontradas:")
        for col in columnas:
            print(f"   - {col['Field']}: {col['Type']}")
        
        # 3. Verificar si hay datos
        print("\n3️⃣ Verificando contenido de la tabla...")
        cursor.execute("SELECT COUNT(*) as total FROM ranking_productos_cliente")
        total_registros = cursor.fetchone()['total']
        
        print(f"📊 Total de registros en ranking: {total_registros}")
        
        if total_registros > 0:
            print("\n📋 Primeros 5 registros:")
            cursor.execute("""
                SELECT r.*, p.codigo_producto, p.descripcion, u.email
                FROM ranking_productos_cliente r
                JOIN productos p ON r.producto_id = p.id
                JOIN usuarios u ON r.cliente_id = u.id
                ORDER BY r.score_ranking DESC
                LIMIT 5
            """)
            
            registros = cursor.fetchall()
            for i, reg in enumerate(registros, 1):
                print(f"   {i}. Cliente: {reg['email']} | Producto: {reg['codigo_producto']} | Score: {reg['score_ranking']} | Frecuencia: {reg['frecuencia_busqueda']}")
        else:
            print("📭 La tabla está vacía - no hay rankings registrados")
        
        # 4. Verificar usuarios disponibles
        print("\n4️⃣ Verificando usuarios disponibles...")
        cursor.execute("SELECT id, email, nombre FROM usuarios LIMIT 5")
        usuarios = cursor.fetchall()
        
        print("👥 Usuarios disponibles:")
        for user in usuarios:
            print(f"   - ID: {user['id']} | Email: {user['email']} | Nombre: {user['nombre']}")
        
        # 5. Verificar productos disponibles
        print("\n5️⃣ Verificando productos disponibles...")
        cursor.execute("SELECT id, codigo_producto, descripcion FROM productos LIMIT 5")
        productos = cursor.fetchall()
        
        print("📦 Productos disponibles:")
        for prod in productos:
            print(f"   - ID: {prod['id']} | Código: {prod['codigo_producto']} | Descripción: {prod['descripcion'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("\n✅ Conexión cerrada")

if __name__ == "__main__":
    verificar_ranking()
