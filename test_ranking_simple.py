#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TEST RANKING SIMPLE - MARUZ DISTRIBUCIONES
Prueba simple para verificar si el ranking funciona
"""

import requests
import mysql.connector
import time

def test_ranking_simple():
    """
    Prueba simple del sistema de ranking
    """
    print("🧪 TEST RANKING SIMPLE")
    print("=" * 40)
    
    base_url = "http://localhost:8002"
    
    # 1. Verificar que el servicio esté corriendo
    print("1️⃣ VERIFICANDO SERVICIO...")
    try:
        response = requests.get(f"{base_url}/productos", timeout=5)
        if response.status_code == 200:
            print("   ✅ Servicio funcionando")
        else:
            print(f"   ❌ Servicio con problemas: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Servicio no disponible: {e}")
        return
    
    # 2. Probar autocompletado con diferentes usuarios
    print("\n2️⃣ PROBANDO AUTOCOMPLETADO...")
    usuarios_test = [1, 2, 3, 4, 5]
    
    for user_id in usuarios_test:
        print(f"\n   👤 Probando Usuario ID: {user_id}")
        
        # Hacer búsqueda
        url = f"{base_url}/api/autocomplete?q=aceite&cliente_id={user_id}"
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Búsqueda exitosa: {len(data)} productos")
                
                # Esperar un poco para que se procese
                time.sleep(2)
                
                # Verificar en BD
                registros = verificar_ranking_bd(user_id)
                if registros > 0:
                    print(f"      🎯 ¡RANKING REGISTRADO! ({registros} registros)")
                else:
                    print(f"      ⚠️ Ranking NO registrado")
                    
            else:
                print(f"      ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Excepción: {e}")
    
    # 3. Mostrar estado actual de la BD
    print("\n3️⃣ ESTADO DE LA BASE DE DATOS...")
    mostrar_estado_bd()

def verificar_ranking_bd(cliente_id):
    """
    Verifica registros de ranking en la BD para un cliente
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
        
        # Contar registros del cliente en los últimos 60 segundos
        cursor.execute("""
            SELECT COUNT(*) FROM ranking_productos_cliente 
            WHERE cliente_id = %s 
            AND ultima_busqueda >= DATE_SUB(NOW(), INTERVAL 60 SECOND)
        """, (cliente_id,))
        
        count = cursor.fetchone()[0]
        connection.close()
        
        return count
        
    except Exception as e:
        print(f"      ❌ Error BD: {e}")
        return 0

def mostrar_estado_bd():
    """
    Muestra el estado actual de la base de datos
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
        
        # Total de registros
        cursor.execute("SELECT COUNT(*) FROM ranking_productos_cliente")
        total = cursor.fetchone()[0]
        print(f"   📊 Total registros: {total}")
        
        # Registros por cliente
        cursor.execute("""
            SELECT cliente_id, COUNT(*) as total, MAX(ultima_busqueda) as ultima
            FROM ranking_productos_cliente 
            GROUP BY cliente_id 
            ORDER BY total DESC 
            LIMIT 5
        """)
        
        registros = cursor.fetchall()
        
        if registros:
            print(f"   👥 Top clientes:")
            for reg in registros:
                print(f"      Cliente {reg[0]}: {reg[1]} búsquedas (última: {reg[2]})")
        else:
            print(f"   📭 No hay registros")
        
        # Registros recientes (últimos 5 minutos)
        cursor.execute("""
            SELECT cliente_id, producto_id, ultima_busqueda
            FROM ranking_productos_cliente 
            WHERE ultima_busqueda >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)
            ORDER BY ultima_busqueda DESC 
            LIMIT 10
        """)
        
        recientes = cursor.fetchall()
        
        if recientes:
            print(f"   🕐 Búsquedas recientes:")
            for rec in recientes:
                print(f"      Cliente {rec[0]} → Producto {rec[1]} ({rec[2]})")
        else:
            print(f"   📭 No hay búsquedas recientes")
        
        connection.close()
        
    except Exception as e:
        print(f"   ❌ Error accediendo BD: {e}")

if __name__ == "__main__":
    test_ranking_simple()
    
    print("\n" + "=" * 40)
    print("🧪 PRUEBA COMPLETADA")
    print("📝 Si ves 'RANKING REGISTRADO', el sistema funciona")
    print("📝 Si ves 'Ranking NO registrado', hay un problema")
