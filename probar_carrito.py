#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del carrito
"""

import requests
import json

def probar_carrito():
    base_url = "http://localhost:8002"
    
    print("🧪 PROBANDO FUNCIÓN DE CARRITO...")
    print("=" * 50)
    
    # 1. Obtener resumen inicial
    print("1️⃣ Obteniendo resumen inicial...")
    try:
        response = requests.get(f"{base_url}/api/carrito/resumen")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resumen inicial: {data['total_unidades']} productos, ${data['total_monto']}")
        else:
            print(f"❌ Error obteniendo resumen: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # 2. Agregar un producto de prueba
    print("\n2️⃣ Agregando producto de prueba...")
    producto_prueba = {
        "producto_codigo": "TEST001",
        "cantidad": 5,
        "precio_unitario": 10.50,
        "descuento": 5.0
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/carrito/agregar",
            json=producto_prueba,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Producto agregado: {data.get('message', 'OK')}")
        else:
            print(f"❌ Error agregando producto: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # 3. Verificar resumen después de agregar
    print("\n3️⃣ Verificando resumen después de agregar...")
    try:
        response = requests.get(f"{base_url}/api/carrito/resumen")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resumen actualizado: {data['total_unidades']} productos, ${data['total_monto']}")
            if data['total_unidades'] > 0:
                print(f"📦 Productos en carrito: {len(data['productos'])}")
                for p in data['productos']:
                    print(f"   - {p['producto_codigo']}: {p['cantidad']} x ${p['precio_unitario']} (descuento: {p['descuento']}%)")
        else:
            print(f"❌ Error obteniendo resumen: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 4. Limpiar carrito
    print("\n4️⃣ Limpiando carrito...")
    try:
        response = requests.post(f"{base_url}/api/carrito/limpiar")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Carrito limpiado: {data.get('message', 'OK')}")
        else:
            print(f"❌ Error limpiando carrito: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 5. Verificar resumen final
    print("\n5️⃣ Verificando resumen final...")
    try:
        response = requests.get(f"{base_url}/api/carrito/resumen")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resumen final: {data['total_unidades']} productos, ${data['total_monto']}")
        else:
            print(f"❌ Error obteniendo resumen: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 PRUEBA COMPLETADA")

if __name__ == "__main__":
    probar_carrito()
