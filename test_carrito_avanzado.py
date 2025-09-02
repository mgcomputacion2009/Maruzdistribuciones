#!/usr/bin/env python3
"""
Script de prueba para verificar el carrito avanzado
"""
import requests
import json

# URL base del desarrollo
BASE_URL = "http://localhost:8002"

def test_ensure_pedido():
    """Probar el endpoint ensure para crear/obtener pedido"""
    print("🔍 Probando /api/pedido/ensure...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/pedido/ensure",
            headers={
                "Content-Type": "application/json",
                "X-Pedido-Token": ""
            }
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Ensure funcionando correctamente")
            return data.get('pedido_token')
        else:
            print("❌ Error en ensure")
            return None
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_resumen(pedido_token):
    """Probar el endpoint resumen"""
    print("\n🔍 Probando /api/pedido/resumen...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/pedido/resumen",
            headers={
                "X-Pedido-Token": pedido_token
            }
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Resumen funcionando correctamente")
        else:
            print("❌ Error en resumen")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_items_query(pedido_token):
    """Probar el endpoint items/query"""
    print("\n🔍 Probando /api/pedido/items/query...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/pedido/items/query",
            headers={
                "Content-Type": "application/json",
                "X-Pedido-Token": pedido_token
            },
            json={
                "pedido_id": 1,  # Asumiendo pedido_id 1
                "codigos": ["PROD001", "PROD002"]
            }
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Items/query funcionando correctamente")
        else:
            print("❌ Error en items/query")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("🛒 PRUEBA DEL CARRITO AVANZADO")
    print("=" * 50)
    
    # Test 1: Ensure
    token = test_ensure_pedido()
    
    if token:
        # Test 2: Resumen
        test_resumen(token)
        
        # Test 3: Items Query
        test_items_query(token)
    else:
        print("\n❌ No se pudo obtener el token, abortando pruebas")
    
    print("\n" + "=" * 50)
    print("Pruebas completadas")
