#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 DIAGNÓSTICO DEL SISTEMA DE RANKING - MARUZ DISTRIBUCIONES
Script para diagnosticar por qué no funciona el ranking de búsquedas
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

def diagnosticar_ranking():
    """
    Diagnostica el sistema de ranking completo
    """
    print("🔍 DIAGNÓSTICO DEL SISTEMA DE RANKING")
    print("=" * 50)
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 1. Verificar que la tabla existe
        print("\n1️⃣ VERIFICANDO TABLA DE RANKING...")
        cursor.execute("SHOW TABLES LIKE 'ranking_productos_cliente'")
        if cursor.fetchone():
            print("✅ Tabla 'ranking_productos_cliente' existe")
        else:
            print("❌ Tabla 'ranking_productos_cliente' NO existe")
            return
        
        # 2. Verificar estructura de la tabla
        print("\n2️⃣ VERIFICANDO ESTRUCTURA DE LA TABLA...")
        cursor.execute("DESCRIBE ranking_productos_cliente")
        columns = cursor.fetchall()
        print("📋 Columnas de la tabla:")
        for col in columns:
            print(f"   - {col[0]} ({col[1]})")
        
        # 3. Verificar si hay datos
        print("\n3️⃣ VERIFICANDO DATOS EN LA TABLA...")
        cursor.execute("SELECT COUNT(*) FROM ranking_productos_cliente")
        total_registros = cursor.fetchone()[0]
        print(f"📊 Total de registros: {total_registros}")
        
        if total_registros > 0:
            # Mostrar algunos registros de ejemplo
            cursor.execute("SELECT * FROM ranking_productos_cliente LIMIT 5")
            registros = cursor.fetchall()
            print("📋 Registros de ejemplo:")
            for reg in registros:
                print(f"   - Cliente: {reg[1]}, Producto: {reg[2]}, Score: {reg[3]}, Frecuencia: {reg[5]}")
        else:
            print("📭 No hay registros en la tabla")
        
        # 4. Verificar usuarios disponibles
        print("\n4️⃣ VERIFICANDO USUARIOS DISPONIBLES...")
        cursor.execute("SELECT id, email FROM usuarios LIMIT 10")
        usuarios = cursor.fetchall()
        print("👥 Usuarios disponibles:")
        for usuario in usuarios:
            print(f"   - ID: {usuario[0]}, Email: {usuario[1]}")
        
        # 5. Verificar productos disponibles
        print("\n5️⃣ VERIFICANDO PRODUCTOS DISPONIBLES...")
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = cursor.fetchone()[0]
        print(f"📦 Total de productos: {total_productos}")
        
        # 6. Verificar índices
        print("\n6️⃣ VERIFICANDO ÍNDICES...")
        cursor.execute("SHOW INDEX FROM ranking_productos_cliente")
        indices = cursor.fetchall()
        print("🔍 Índices existentes:")
        for indice in indices:
            print(f"   - {indice[2]} ({indice[4]})")
        
        # 7. Probar consulta de ranking
        print("\n7️⃣ PROBANDO CONSULTA DE RANKING...")
        if usuarios:
            cliente_id = usuarios[0][0]  # Usar el primer usuario
            print(f"🧪 Probando con cliente ID: {cliente_id}")
            
            # Consulta de ejemplo
            sql_ranking = """
            SELECT p.codigo_producto, p.descripcion, 
                   COALESCE(r.score_ranking, 0) as score_ranking
            FROM productos p
            LEFT JOIN ranking_productos_cliente r ON p.id = r.producto_id AND r.cliente_id = %s
            ORDER BY 
                CASE WHEN r.score_ranking > 0 THEN 0 ELSE 1 END,
                r.score_ranking DESC,
                p.fecha_actualizacion DESC 
            LIMIT 5
            """
            
            cursor.execute(sql_ranking, (cliente_id,))
            resultados = cursor.fetchall()
            print("📋 Resultados de consulta de ranking:")
            for res in resultados:
                print(f"   - {res[0]}: {res[1][:50]}... (Score: {res[2]})")
        
        # 8. Verificar logs recientes
        print("\n8️⃣ VERIFICANDO LOGS DEL SISTEMA...")
        print("📝 Revisa los logs de Flask para ver si hay errores en autocompletado")
        print("   Comando: tail -f /var/log/maruz-distribuciones.log")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()

def probar_autocompletado_manual():
    """
    Prueba el endpoint de autocompletado manualmente
    """
    print("\n🧪 PRUEBA MANUAL DEL AUTOCOMPLETADO")
    print("=" * 50)
    
    try:
        import requests
        
        # URL del endpoint
        base_url = "http://localhost:8002"
        
        # Probar sin cliente_id
        print("1️⃣ Probando sin cliente_id...")
        response = requests.get(f"{base_url}/api/autocomplete?q=aceite", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Productos encontrados: {len(data)}")
        else:
            print(f"   Error: {response.text}")
        
        # Probar con cliente_id
        print("\n2️⃣ Probando con cliente_id...")
        response = requests.get(f"{base_url}/api/autocomplete?q=aceite&cliente_id=1", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Productos encontrados: {len(data)}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en prueba manual: {e}")

if __name__ == "__main__":
    diagnosticar_ranking()
    probar_autocompletado_manual()
    
    print("\n" + "=" * 50)
    print("🔍 DIAGNÓSTICO COMPLETADO")
    print("📝 Revisa los resultados arriba para identificar el problema")
