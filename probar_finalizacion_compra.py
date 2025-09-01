#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el endpoint de finalización de compra
Sistema de Carrito Avanzado - Maruz Distribuciones
"""

import requests
import json
import uuid

def test_finalizar_compra():
    """Probar el endpoint de finalización de compra"""
    
    # URL base del servidor
    base_url = "http://localhost:8002"
    
    # Datos de prueba para finalizar compra
    datos_compra = {
        "cliente_nombre": "Juan Pérez Test",
        "cliente_telefono": "555-1234",
        "cliente_email": "juan.test@example.com",
        "direccion_entrega": "Calle Test 123, Ciudad Test, CP 12345",
        "metodo_pago": "efectivo",
        "notas": "Prueba del sistema de finalización de compra"
    }
    
    print("🚀 Probando endpoint de finalización de compra...")
    print(f"URL: {base_url}/api/carrito/finalizar-compra")
    print(f"Datos: {json.dumps(datos_compra, indent=2)}")
    print("-" * 50)
    
    try:
        # Hacer la solicitud POST
        response = requests.post(
            f"{base_url}/api/carrito/finalizar-compra",
            json=datos_compra,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Intentar obtener la respuesta JSON
        try:
            data = response.json()
            print(f"Respuesta JSON: {json.dumps(data, indent=2)}")
            
            if response.status_code == 200 and data.get('success'):
                print("✅ ¡Éxito! La compra se finalizó correctamente")
                print(f"📋 Número de Pedido: {data['pedido']['numero_pedido']}")
                print(f"💰 Total: ${data['pedido']['total_pedido']}")
            else:
                print("❌ Error en la respuesta")
                if 'error' in data:
                    print(f"Error: {data['error']}")
                    
        except json.JSONDecodeError:
            print("❌ No se pudo decodificar la respuesta JSON")
            print(f"Respuesta raw: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se pudo conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en el puerto 8002")
    except requests.exceptions.Timeout:
        print("❌ Error de timeout: La solicitud tardó demasiado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_endpoints_disponibles():
    """Verificar que todos los endpoints del carrito estén disponibles"""
    
    base_url = "http://localhost:8002"
    endpoints = [
        "/api/carrito/agregar",
        "/api/carrito/actualizar", 
        "/api/carrito/quitar",
        "/api/carrito/limpiar",
        "/api/carrito/resumen",
        "/api/carrito/productos",
        "/api/carrito/finalizar-compra"
    ]
    
    print("🔍 Verificando endpoints disponibles...")
    print("-" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 405:  # Method Not Allowed (esperado para POST endpoints)
                print(f"✅ {endpoint} - Disponible (POST)")
            elif response.status_code == 200:
                print(f"✅ {endpoint} - Disponible (GET)")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    print("🧪 PRUEBA DEL SISTEMA DE FINALIZACIÓN DE COMPRA")
    print("=" * 60)
    
    # Verificar endpoints disponibles
    test_endpoints_disponibles()
    print()
    
    # Probar finalización de compra
    test_finalizar_compra()
    
    print("\n" + "=" * 60)
    print("🏁 Prueba completada")
