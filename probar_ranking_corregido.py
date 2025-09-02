#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 PROBADOR DE RANKING CORREGIDO - MARUZ DISTRIBUCIONES
Script para probar el sistema de ranking después de las correcciones
"""

import requests
import json
import time
import mysql.connector

def probar_ranking_corregido():
    """
    Prueba el sistema de ranking corregido
    """
    print("🧪 PROBANDO SISTEMA DE RANKING CORREGIDO")
    print("=" * 60)
    
    # URL del endpoint
    base_url = "http://localhost:8002"
    
    # Datos de prueba
    cliente_id = 1  # Usar el primer usuario disponible
    queries = ["aceite", "bujia", "filtro", "5W", "aceite", "bujia"]
    
    print(f"📋 Cliente ID: {cliente_id}")
    print(f"📋 Consultas de prueba: {queries}")
    print()
    
    # 1. Probar autocompletado y registro de ranking
    for i, query in enumerate(queries, 1):
        print(f"🔍 Prueba {i}: Buscando '{query}'...")
        
        # Hacer la petición con cliente_id
        url = f"{base_url}/api/autocomplete?q={query}&cliente_id={cliente_id}"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Respuesta exitosa - {len(data)} productos encontrados")
                
                if data:
                    print(f"   📦 Productos que se registrarán en ranking:")
                    for j, producto in enumerate(data[:3], 1):  # Mostrar solo los primeros 3
                        print(f"      {j}. {producto.get('codigo')} - {producto.get('descripcion')[:40]}...")
                    
                    if len(data) > 3:
                        print(f"      ... y {len(data) - 3} productos más")
                else:
                    print("   📭 No se encontraron productos")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Esperar un poco entre consultas
        time.sleep(2)
        print()
    
    print("⏱️  Esperando 5 segundos para que se procesen todos los registros...")
    time.sleep(5)
    
    # 2. Verificar registros en la base de datos
    verificar_registros_bd(cliente_id)
    
    # 3. Probar consulta de ranking
    probar_consulta_ranking(cliente_id)

def verificar_registros_bd(cliente_id):
    """
    Verifica los registros en la base de datos
    """
    print("📊 VERIFICANDO REGISTROS EN BASE DE DATOS")
    print("=" * 60)
    
    try:
        # Conectar a la base de datos
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
        
        # Verificar total de registros
        cursor.execute("SELECT COUNT(*) FROM ranking_productos_cliente WHERE cliente_id = %s", (cliente_id,))
        total_registros = cursor.fetchone()[0]
        print(f"📊 Total de registros para cliente {cliente_id}: {total_registros}")
        
        if total_registros > 0:
            # Mostrar registros ordenados por score
            cursor.execute("""
                SELECT r.producto_id, r.score_ranking, r.frecuencia_busqueda, 
                       r.ultima_busqueda, p.codigo_producto, p.descripcion
                FROM ranking_productos_cliente r
                JOIN productos p ON r.producto_id = p.id
                WHERE r.cliente_id = %s
                ORDER BY r.score_ranking DESC, r.frecuencia_busqueda DESC
                LIMIT 10
            """, (cliente_id,))
            
            registros = cursor.fetchall()
            print(f"\n🏆 TOP 10 PRODUCTOS POR RANKING:")
            print("-" * 80)
            print(f"{'Pos':<4} {'Score':<8} {'Freq':<4} {'Producto':<20} {'Descripción':<40}")
            print("-" * 80)
            
            for i, reg in enumerate(registros, 1):
                pos = f"{i}º"
                score = f"{reg[1]:.4f}"
                freq = f"{reg[2]}"
                codigo = reg[4][:18]
                desc = reg[5][:38] if reg[5] else ""
                print(f"{pos:<4} {score:<8} {freq:<4} {codigo:<20} {desc:<40}")
        else:
            print("📭 No hay registros de ranking para este cliente")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")

def probar_consulta_ranking(cliente_id):
    """
    Prueba la consulta de ranking
    """
    print("\n🔍 PROBANDO CONSULTA DE RANKING")
    print("=" * 60)
    
    try:
        # Conectar a la base de datos
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
        
        # Consulta de ranking (igual a la que usa la página de productos)
        sql_ranking = """
        SELECT p.codigo_producto, p.descripcion, 
               COALESCE(r.score_ranking, 0) as score_ranking,
               r.frecuencia_busqueda
        FROM productos p
        LEFT JOIN ranking_productos_cliente r ON p.id = r.producto_id AND r.cliente_id = %s
        ORDER BY 
            CASE WHEN r.score_ranking > 0 THEN 0 ELSE 1 END,
            r.score_ranking DESC,
            p.fecha_actualizacion DESC 
        LIMIT 10
        """
        
        cursor.execute(sql_ranking, (cliente_id,))
        resultados = cursor.fetchall()
        
        print(f"📋 TOP 10 PRODUCTOS CON RANKING PERSONALIZADO:")
        print("-" * 80)
        print(f"{'Pos':<4} {'Score':<8} {'Freq':<4} {'Producto':<20} {'Descripción':<40}")
        print("-" * 80)
        
        for i, res in enumerate(resultados, 1):
            pos = f"{i}º"
            score = f"{res[2]:.4f}"
            freq = f"{res[3] or 0}"
            codigo = res[0][:18]
            desc = res[1][:38] if res[1] else ""
            
            # Marcar productos con ranking
            if res[2] and res[2] > 0:
                pos += "⭐"
            
            print(f"{pos:<4} {score:<8} {freq:<4} {codigo:<20} {desc:<40}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error probando consulta de ranking: {e}")

if __name__ == "__main__":
    probar_ranking_corregido()
    
    print("\n" + "=" * 60)
    print("🧪 PRUEBA COMPLETADA")
    print("📝 Revisa los resultados arriba para verificar que el ranking funcione")
    print("💡 Si ves productos con ⭐, significa que tienen ranking personalizado")
