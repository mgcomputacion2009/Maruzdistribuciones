#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la persistencia del carrito
Sistema de Carrito con Sincronización Frontend-Backend
"""

import requests
import json
import time

def test_persistencia_carrito():
    """Probar la persistencia del carrito entre sesiones"""
    
    base_url = "http://localhost:8002"
    
    # Crear una sesión que mantenga las cookies
    session = requests.Session()
    
    print("🧪 PRUEBA DE PERSISTENCIA DEL CARRITO")
    print("=" * 60)
    
    # Paso 1: Verificar estado inicial
    print("📋 PASO 1: Verificando estado inicial del carrito...")
    try:
        response = session.get(f"{base_url}/api/carrito/resumen")
        data = response.json()
        print(f"   Estado inicial: {data['cantidad_productos']} productos, ${data['total_monto']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Paso 2: Agregar productos al carrito (simulando la primera sesión)
    print("\n🛒 PASO 2: Agregando productos al carrito (Primera sesión)...")
    
    productos_prueba = [
        {
            "producto_codigo": "TEST001",
            "cantidad": 2,
            "precio_unitario": 5.84,
            "descuento": 0
        },
        {
            "producto_codigo": "TEST002", 
            "cantidad": 1,
            "precio_unitario": 2.76,
            "descuento": 0.50  # Descuento de $0.50
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
                print(f"   ✅ Producto {i} agregado: {producto['producto_codigo']}")
                if 'resumen' in data:
                    resumen = data['resumen']
                    print(f"      Carrito: {resumen['cantidad_productos']} productos, ${resumen['total_monto']}")
            else:
                print(f"   ❌ Error agregando producto {i}: {data['error']}")
                
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
    
    # Paso 3: Verificar que se guardó correctamente
    print("\n📊 PASO 3: Verificando que se guardó en base de datos...")
    try:
        response = session.get(f"{base_url}/api/carrito/productos")
        data = response.json()
        
        if data['success']:
            productos = data['resumen']['productos']
            print(f"   Productos guardados: {len(productos)}")
            for producto in productos:
                print(f"     - {producto['producto_codigo']}: {producto['cantidad']} x ${producto['precio_unitario']} (desc: ${producto['descuento']}) = ${producto['total_linea']}")
        else:
            print(f"   ❌ Error: {data['error']}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Guardar cookies de la sesión para simular segunda sesión
    cookies_guardadas = dict(session.cookies)
    print(f"\n💾 Cookies guardadas: {list(cookies_guardadas.keys())}")
    
    # Paso 4: Simular una nueva sesión (nueva instancia pero con las mismas cookies)
    print("\n🔄 PASO 4: Simulando nueva sesión (recarga de página)...")
    
    # Crear nueva sesión pero con las cookies guardadas
    nueva_sesion = requests.Session()
    nueva_sesion.cookies.update(cookies_guardadas)
    
    # Verificar que el carrito persiste
    try:
        response = nueva_sesion.get(f"{base_url}/api/carrito/productos")
        data = response.json()
        
        if data['success'] and data['resumen']['productos']:
            print("   ✅ Carrito persistido correctamente en nueva sesión")
            productos = data['resumen']['productos']
            print(f"   Productos recuperados: {len(productos)}")
            for producto in productos:
                print(f"     - {producto['producto_codigo']}: {producto['cantidad']} x ${producto['precio_unitario']} = ${producto['total_linea']}")
        else:
            print("   ❌ Carrito no se persistió correctamente")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Paso 5: Agregar más productos en la nueva sesión
    print("\n➕ PASO 5: Agregando más productos en nueva sesión...")
    
    producto_adicional = {
        "producto_codigo": "PROD-TEST-004",
        "cantidad": 1,
        "precio_unitario": 7.73,
        "descuento": 1.0  # Descuento de $1.00
    }
    
    try:
        response = nueva_sesion.post(
            f"{base_url}/api/carrito/agregar",
            json=producto_adicional,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        
        if data['success']:
            print(f"   ✅ Producto adicional agregado: {producto_adicional['producto_codigo']}")
            if 'resumen' in data:
                resumen = data['resumen']
                print(f"      Carrito actualizado: {resumen['cantidad_productos']} productos, ${resumen['total_monto']}")
        else:
            print(f"   ❌ Error: {data['error']}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Paso 6: Verificar estado final
    print("\n📈 PASO 6: Verificando estado final del carrito...")
    try:
        response = nueva_sesion.get(f"{base_url}/api/carrito/resumen")
        data = response.json()
        print(f"   Estado final: {data['cantidad_productos']} productos, {data['total_unidades']} unidades, ${data['total_monto']}")
        
        # Obtener detalle
        response = nueva_sesion.get(f"{base_url}/api/carrito/productos")
        data = response.json()
        
        if data['success']:
            productos = data['resumen']['productos']
            print(f"\n   📦 Detalle final del carrito:")
            for producto in productos:
                print(f"     - {producto['producto_codigo']}: {producto['cantidad']} x ${producto['precio_unitario']} (desc: ${producto['descuento']}) = ${producto['total_linea']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Paso 7: Limpiar carrito para próximas pruebas
    print("\n🧹 PASO 7: Limpiando carrito...")
    try:
        response = nueva_sesion.post(f"{base_url}/api/carrito/limpiar")
        data = response.json()
        
        if data['success']:
            print("   ✅ Carrito limpiado correctamente")
        else:
            print(f"   ❌ Error limpiando: {data['error']}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBA DE PERSISTENCIA COMPLETADA")

if __name__ == "__main__":
    test_persistencia_carrito()
