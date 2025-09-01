#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba del carrito manteniendo sesión
Sistema de Carrito Avanzado - Maruz Distribuciones
"""

import requests
import json
import time

def test_carrito_con_sesion():
    """Probar el carrito manteniendo la misma sesión"""
    
    # URL base del servidor
    base_url = "http://localhost:8002"
    
    # Crear una sesión que mantenga las cookies
    session = requests.Session()
    
    print("🚀 INICIANDO PRUEBA DEL CARRITO CON SESIÓN MANTENIDA")
    print("=" * 70)
    
    # Paso 1: Verificar estado inicial del carrito
    print("📋 PASO 1: Verificando estado inicial del carrito...")
    try:
        response = session.get(f"{base_url}/api/carrito/resumen")
        data = response.json()
        print(f"   Estado inicial: {data['cantidad_productos']} productos, ${data['total_monto']}")
        print(f"   Cookies de sesión: {dict(session.cookies)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Paso 2: Agregar productos al carrito
    print("\n🛒 PASO 2: Agregando productos al carrito...")
    
    productos_prueba = [
        {
            "producto_codigo": "PROD-TEST-004",
            "cantidad": 2,
            "precio_unitario": 7.73,
            "descuento": 0
        },
        {
            "producto_codigo": "TEST002", 
            "cantidad": 1,
            "precio_unitario": 2.76,
            "descuento": 1.00
        },
        {
            "producto_codigo": "TEST001",
            "cantidad": 3,
            "precio_unitario": 5.84,
            "descuento": 0
        }
    ]
    
    for i, producto in enumerate(productos_prueba, 1):
        try:
            response = session.post(
                f"{base_url}/api/carrito/agregar",
                json=producto,
                headers={'Content-Type': 'application/json'}
            )
            data = response.json()
            
            if data['success']:
                print(f"   ✅ Producto {i} agregado: {producto['producto_codigo']} - {data['message']}")
                if 'resumen' in data:
                    resumen = data['resumen']
                    print(f"      Carrito actual: {resumen['cantidad_productos']} productos, ${resumen['total_monto']}")
            else:
                print(f"   ❌ Error agregando producto {i}: {data['error']}")
                
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
    
    # Esperar un momento para que se procese
    time.sleep(1)
    
    # Paso 3: Verificar carrito después de agregar productos
    print("\n📊 PASO 3: Verificando carrito después de agregar productos...")
    try:
        response = session.get(f"{base_url}/api/carrito/resumen")
        data = response.json()
        print(f"   Productos en carrito: {data['cantidad_productos']}")
        print(f"   Total unidades: {data['total_unidades']}")
        print(f"   Total monto: ${data['total_monto']}")
        print(f"   Cookies de sesión: {dict(session.cookies)}")
        
        if data['cantidad_productos'] > 0:
            print("   ✅ Carrito tiene productos")
        else:
            print("   ❌ Carrito vacío - no se pueden agregar productos de prueba")
            return
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Paso 4: Obtener lista de productos del carrito
    print("\n📋 PASO 4: Obteniendo lista de productos del carrito...")
    try:
        response = session.get(f"{base_url}/api/carrito/productos")
        data = response.json()
        
        if data['success']:
            productos = data['resumen']['productos']
            print(f"   Productos en carrito: {len(productos)}")
            for producto in productos:
                print(f"     - {producto['producto_codigo']}: {producto['cantidad']} x ${producto['precio_unitario']} = ${producto['total_linea']}")
        else:
            print(f"   ❌ Error: {data['error']}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Paso 5: Finalizar compra
    print("\n💳 PASO 5: Finalizando compra...")
    
    datos_compra = {
        "cliente_nombre": "Carlos López Test",
        "cliente_telefono": "555-1111",
        "cliente_email": "carlos.test@example.com",
        "direccion_entrega": "Calle Comercial 789, Zona Industrial, CP 67890",
        "metodo_pago": "efectivo",
        "notas": "Prueba del sistema con sesión mantenida - Entrega urgente"
    }
    
    try:
        response = session.post(
            f"{base_url}/api/carrito/finalizar-compra",
            json=datos_compra,
            headers={'Content-Type': 'application/json'}
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print("   ✅ ¡Éxito! La compra se finalizó correctamente")
            print(f"   📋 Número de Pedido: {data['pedido']['numero_pedido']}")
            print(f"   👤 Cliente: {data['pedido']['cliente_nombre']}")
            print(f"   💰 Subtotal: ${data['pedido']['subtotal']}")
            print(f"   🏛️  IVA: ${data['pedido']['iva']}")
            print(f"   💵 Total: ${data['pedido']['total_pedido']}")
            print(f"   📦 Productos: {data['pedido']['productos']}")
            print(f"   📅 Fecha: {data['pedido']['fecha_pedido']}")
        else:
            print(f"   ❌ Error en la finalización: {data.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # Paso 6: Verificar que el carrito se limpió
    print("\n🧹 PASO 6: Verificando que el carrito se limpió...")
    try:
        response = session.get(f"{base_url}/api/carrito/resumen")
        data = response.json()
        
        if data['cantidad_productos'] == 0:
            print("   ✅ Carrito limpiado correctamente")
        else:
            print(f"   ⚠️  Carrito aún tiene {data['cantidad_productos']} productos")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("🏁 PRUEBA CON SESIÓN MANTENIDA FINALIZADA")

if __name__ == "__main__":
    test_carrito_con_sesion()
