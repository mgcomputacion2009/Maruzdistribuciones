#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 PROBADOR DE SISTEMA DE RANKING - MARUZ DISTRIBUCIONES
Script para probar el sistema de ranking personalizado
"""

import requests
import json
import time

def probar_autocompletado():
    """
    Prueba el endpoint de autocompletado con cliente_id
    """
    print("🧪 PROBANDO SISTEMA DE RANKING")
    print("=" * 50)
    
    # URL del endpoint
    base_url = "http://localhost:8002"
    
    # Datos de prueba
    cliente_id = 4  # ID del usuario mgcomputacion2009@gmail.com
    queries = ["aceite", "bujia", "filtro", "5W", "aceite"]
    
    print(f"📋 Cliente ID: {cliente_id}")
    print(f"📋 Consultas de prueba: {queries}")
    print()
    
    for i, query in enumerate(queries, 1):
        print(f"🔍 Prueba {i}: Buscando '{query}'...")
        
        # Hacer la petición
        url = f"{base_url}/api/autocomplete?q={query}&cliente_id={cliente_id}"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Respuesta exitosa - {len(data)} productos encontrados")
                
                if data:
                    primer_producto = data[0]
                    print(f"   📦 Primer producto: {primer_producto.get('codigo')} - {primer_producto.get('descripcion')[:50]}...")
                else:
                    print("   📭 No se encontraron productos")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Esperar un poco entre consultas
        time.sleep(1)
        print()
    
    print("⏱️  Esperando 3 segundos para que se procesen los registros...")
    time.sleep(3)
    
    # Verificar registros en la base de datos
    verificar_registros_bd()

def verificar_registros_bd():
    """
    Verifica los registros en la base de datos
    """
    import mysql.connector
    
    print("🗄️ VERIFICANDO REGISTROS EN BASE DE DATOS")
    print("=" * 50)
    
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
        
        # Obtener registros de ranking
        cursor.execute("""
            SELECT r.*, p.codigo_producto, p.descripcion, u.email
            FROM ranking_productos_cliente r
            JOIN productos p ON r.producto_id = p.id
            JOIN usuarios u ON r.cliente_id = u.id
            WHERE r.cliente_id = 4
            ORDER BY r.score_ranking DESC, r.ultima_busqueda DESC
        """)
        
        registros = cursor.fetchall()
        
        if registros:
            print(f"✅ Se encontraron {len(registros)} registros de ranking:")
            print()
            print(f"{'#':<3} {'Producto':<20} {'Score':<8} {'Frecuencia':<10} {'Última búsqueda':<20}")
            print("-" * 70)
            
            for i, reg in enumerate(registros, 1):
                print(f"{i:<3} {reg['codigo_producto']:<20} {reg['score_ranking']:<8} {reg['frecuencia_busqueda']:<10} {reg['ultima_busqueda']}")
        else:
            print("❌ No se encontraron registros de ranking")
            print("   Posibles causas:")
            print("   - El cliente_id no está llegando al backend")
            print("   - Hay errores en el registro")
            print("   - El usuario no está autenticado correctamente")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")

def mostrar_logs():
    """
    Muestra los logs recientes de la aplicación
    """
    print("\n📋 LOGS RECIENTES DE LA APLICACIÓN")
    print("=" * 50)
    
    try:
        with open('/var/www/maruz/maruz_dev.log', 'r') as f:
            lines = f.readlines()
            # Mostrar las últimas 20 líneas
            for line in lines[-20:]:
                if 'ranking' in line.lower() or 'autocompletado' in line.lower():
                    print(line.strip())
    except Exception as e:
        print(f"❌ Error leyendo logs: {e}")

if __name__ == "__main__":
    probar_autocompletado()
    mostrar_logs()
    
    print("\n🎯 RESUMEN DE LA PRUEBA")
    print("=" * 50)
    print("✅ Si ves registros en la base de datos, el sistema funciona correctamente")
    print("❌ Si no hay registros, revisa los logs para encontrar el problema")
    print("📝 Los logs deben mostrar mensajes como:")
    print("   - 'Autocompletado - Query: aceite, Cliente ID: 4'")
    print("   - 'Registrando búsqueda en ranking'")
    print("   - 'Ranking registrado exitosamente'")
