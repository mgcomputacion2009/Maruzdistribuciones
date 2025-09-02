#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 DEBUG RANKING AUTENTICACIÓN - MARUZ DISTRIBUCIONES
Script para diagnosticar problemas de autenticación en el sistema de ranking
"""

import requests
import json
import mysql.connector

def debug_ranking_auth():
    """
    Diagnostica problemas de autenticación en el ranking
    """
    print("🔍 DEBUG RANKING AUTENTICACIÓN")
    print("=" * 50)
    
    base_url = "http://localhost:8002"
    
    # 1. Probar autocompletado SIN cliente_id
    print("1️⃣ PROBANDO SIN CLIENTE_ID...")
    test_without_client_id()
    
    # 2. Probar autocompletado CON cliente_id
    print("\n2️⃣ PROBANDO CON CLIENTE_ID...")
    test_with_client_id()
    
    # 3. Verificar datos en BD
    print("\n3️⃣ VERIFICANDO BASE DE DATOS...")
    check_database()
    
    # 4. Probar manualmente diferentes client_ids
    print("\n4️⃣ PROBANDO DIFERENTES CLIENTE_IDS...")
    test_multiple_client_ids()

def test_without_client_id():
    """
    Prueba autocompletado sin cliente_id
    """
    try:
        url = "http://localhost:8002/api/autocomplete?q=aceite"
        response = requests.get(url, timeout=10)
        
        print(f"   URL: {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Productos encontrados: {len(data)}")
            if data:
                print(f"   📦 Primer producto: {data[0].get('codigo')} - {data[0].get('descripcion')[:30]}...")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

def test_with_client_id():
    """
    Prueba autocompletado con cliente_id
    """
    # Probar con diferentes client_ids
    client_ids = [1, 2, 3, 4, 5]
    
    for client_id in client_ids:
        try:
            url = f"http://localhost:8002/api/autocomplete?q=aceite&cliente_id={client_id}"
            response = requests.get(url, timeout=10)
            
            print(f"   Cliente ID {client_id}:")
            print(f"   URL: {url}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Productos encontrados: {len(data)}")
                
                # Verificar si se registró en BD
                if check_ranking_registered(client_id, data):
                    print(f"   🎯 ¡RANKING REGISTRADO para cliente {client_id}!")
                else:
                    print(f"   ⚠️ Ranking NO registrado para cliente {client_id}")
                    
            else:
                print(f"   ❌ Error: {response.text}")
                
            print()
            
        except Exception as e:
            print(f"   ❌ Excepción para cliente {client_id}: {e}")

def check_ranking_registered(client_id, products):
    """
    Verifica si se registró el ranking en la BD
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
        
        # Verificar registros recientes (últimos 30 segundos)
        cursor.execute("""
            SELECT COUNT(*) FROM ranking_productos_cliente 
            WHERE cliente_id = %s 
            AND ultima_busqueda >= DATE_SUB(NOW(), INTERVAL 30 SECOND)
        """, (client_id,))
        
        count = cursor.fetchone()[0]
        connection.close()
        
        return count > 0
        
    except Exception as e:
        print(f"   ❌ Error verificando BD: {e}")
        return False

def check_database():
    """
    Verifica el estado de la base de datos
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
        
        # Verificar total de registros
        cursor.execute("SELECT COUNT(*) FROM ranking_productos_cliente")
        total = cursor.fetchone()[0]
        print(f"   📊 Total registros ranking: {total}")
        
        # Verificar registros por cliente
        cursor.execute("""
            SELECT cliente_id, COUNT(*) as total, MAX(ultima_busqueda) as ultima
            FROM ranking_productos_cliente 
            GROUP BY cliente_id 
            ORDER BY total DESC 
            LIMIT 10
        """)
        
        registros = cursor.fetchall()
        
        if registros:
            print(f"   👥 Registros por cliente:")
            for reg in registros:
                print(f"      Cliente {reg[0]}: {reg[1]} búsquedas (última: {reg[2]})")
        else:
            print(f"   📭 No hay registros de ranking")
        
        # Verificar usuarios disponibles
        cursor.execute("SELECT id, email FROM usuarios LIMIT 10")
        usuarios = cursor.fetchall()
        
        print(f"   👤 Usuarios disponibles:")
        for usuario in usuarios:
            print(f"      ID {usuario[0]}: {usuario[1]}")
        
        connection.close()
        
    except Exception as e:
        print(f"   ❌ Error accediendo a BD: {e}")

def test_multiple_client_ids():
    """
    Prueba múltiples client_ids para encontrar uno que funcione
    """
    queries = ['aceite', 'bujia', 'filtro']
    
    for query in queries:
        print(f"   🔍 Probando búsqueda: '{query}'")
        
        for client_id in range(1, 6):
            try:
                url = f"http://localhost:8002/api/autocomplete?q={query}&cliente_id={client_id}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"      Cliente {client_id}: {len(data)} productos")
                    
                    # Esperar un poco y verificar BD
                    import time
                    time.sleep(1)
                    
                    if check_ranking_registered(client_id, data):
                        print(f"      🎯 ¡Cliente {client_id} SÍ registra ranking!")
                        return client_id
                else:
                    print(f"      Cliente {client_id}: Error {response.status_code}")
                    
            except Exception as e:
                print(f"      Cliente {client_id}: Excepción {e}")
        
        print()
    
    return None

if __name__ == "__main__":
    debug_ranking_auth()
    
    print("\n" + "=" * 50)
    print("🔍 DEBUG COMPLETADO")
    print("📝 Revisa los resultados para identificar el problema de autenticación")
