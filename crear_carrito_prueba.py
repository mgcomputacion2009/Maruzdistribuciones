#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear un carrito de prueba y ver si el frontend lo carga
"""

import requests
import json

def crear_carrito_prueba():
    """Crear carrito de prueba para verificar carga en frontend"""
    
    base_url = "http://localhost:8002"
    session = requests.Session()
    
    print("🛒 CREANDO CARRITO DE PRUEBA PARA FRONTEND")
    print("=" * 50)
    
    # Productos de prueba
    productos = [
        {
            "producto_codigo": "TEST001",
            "cantidad": 3,
            "precio_unitario": 5.84,
            "descuento": 0
        },
        {
            "producto_codigo": "TEST002", 
            "cantidad": 2,
            "precio_unitario": 2.76,
            "descuento": 1.0
        },
        {
            "producto_codigo": "PROD-TEST-004",
            "cantidad": 1,
            "precio_unitario": 7.73,
            "descuento": 0
        }
    ]
    
    # Agregar productos
    for producto in productos:
        try:
            response = session.post(
                f"{base_url}/api/carrito/agregar",
                json=producto,
                headers={'Content-Type': 'application/json'}
            )
            data = response.json()
            
            if data['success']:
                print(f"✅ {producto['producto_codigo']} agregado: {producto['cantidad']} unidades")
            else:
                print(f"❌ Error: {data['error']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Mostrar resumen
    try:
        response = session.get(f"{base_url}/api/carrito/resumen")
        data = response.json()
        print(f"\n📊 RESUMEN DEL CARRITO:")
        print(f"   Productos: {data['cantidad_productos']}")
        print(f"   Unidades: {data['total_unidades']}")
        print(f"   Total: ${data['total_monto']}")
        
        # Mostrar cookie de sesión
        print(f"\n🍪 Cookie de sesión: {dict(session.cookies)}")
        
        print(f"\n💡 Ahora abre el navegador en:")
        print(f"   http://localhost:8002/productos")
        print(f"   Y verifica que se cargan los productos automáticamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    crear_carrito_prueba()
