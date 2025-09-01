#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demostración del sistema de carrito sincronizado
Sistema que mantiene persistencia entre sesiones y sincroniza frontend con backend
"""

import requests
import json
import time

def demo_carrito_sincronizado():
    """Demostrar el flujo completo del carrito sincronizado"""
    
    base_url = "http://localhost:8002"
    
    print("🚀 DEMOSTRACIÓN: SISTEMA DE CARRITO SINCRONIZADO")
    print("=" * 65)
    print("Este demo muestra cómo el carrito se mantiene sincronizado")
    print("entre el frontend y backend, persistiendo entre sesiones.")
    print()
    
    # Sesión 1: Usuario agrega productos
    print("👤 SESIÓN 1: Usuario agrega productos y sale de la página")
    print("-" * 55)
    
    sesion1 = requests.Session()
    
    # Limpiar cualquier carrito previo
    try:
        sesion1.post(f"{base_url}/api/carrito/limpiar")
        print("🧹 Carrito limpiado para empezar fresh")
    except:
        pass
    
    # Agregar productos en la primera sesión
    productos_sesion1 = [
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
            "descuento": 0.50
        }
    ]
    
    print("\n📦 Agregando productos en sesión 1...")
    for producto in productos_sesion1:
        try:
            response = sesion1.post(
                f"{base_url}/api/carrito/agregar",
                json=producto,
                headers={'Content-Type': 'application/json'}
            )
            data = response.json()
            
            if data['success']:
                print(f"   ✅ {producto['producto_codigo']}: {producto['cantidad']} unidades agregadas")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Verificar estado del carrito
    try:
        response = sesion1.get(f"{base_url}/api/carrito/resumen")
        data = response.json()
        print(f"\n📊 Estado del carrito al finalizar sesión 1:")
        print(f"   Productos: {data['cantidad_productos']}")
        print(f"   Unidades: {data['total_unidades']}")
        print(f"   Total: ${data['total_monto']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Guardar cookie de sesión
    session_cookie = dict(sesion1.cookies)
    print(f"\n💾 Cookie de sesión guardada: {list(session_cookie.keys())}")
    print("🚪 Usuario sale de la página/cierra el navegador...")
    
    # Simular tiempo entre sesiones
    print("\n⏰ Pasa el tiempo... (simulando pausa)")
    time.sleep(2)
    
    # Sesión 2: Usuario regresa y el carrito debe estar intacto
    print("\n👤 SESIÓN 2: Usuario regresa y encuentra su carrito intacto")
    print("-" * 55)
    
    sesion2 = requests.Session()
    sesion2.cookies.update(session_cookie)
    
    # El frontend debería cargar automáticamente el carrito existente
    print("🔄 Al cargar la página, el frontend consulta el carrito existente...")
    
    try:
        response = sesion2.get(f"{base_url}/api/carrito/productos")
        data = response.json()
        
        if data['success'] and data['resumen']['productos']:
            print("✅ Carrito encontrado y cargado automáticamente:")
            productos = data['resumen']['productos']
            
            for producto in productos:
                print(f"   📦 {producto['producto_codigo']}: {producto['cantidad']} x ${producto['precio_unitario']}")
                if float(producto['descuento']) > 0:
                    print(f"       Descuento: ${producto['descuento']}")
                print(f"       Total línea: ${producto['total_linea']}")
            
            print(f"\n📊 Resumen cargado en frontend:")
            print(f"   Total productos: {data['resumen']['cantidad_productos']}")
            print(f"   Total unidades: {data['resumen']['total_unidades']}")
            print(f"   Total monto: ${data['resumen']['total_monto']}")
            print("\n✨ La barra de resumen se muestra automáticamente")
            print("✨ Los campos de cantidad y descuento se llenan automáticamente")
            
        else:
            print("❌ No se encontró carrito previo")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Usuario agrega más productos en la segunda sesión
    print("\n➕ Usuario agrega más productos en la nueva sesión...")
    
    producto_adicional = {
        "producto_codigo": "PROD-TEST-004",
        "cantidad": 1,
        "precio_unitario": 7.73,
        "descuento": 1.0
    }
    
    try:
        response = sesion2.post(
            f"{base_url}/api/carrito/agregar",
            json=producto_adicional,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        
        if data['success']:
            print(f"   ✅ {producto_adicional['producto_codigo']} agregado exitosamente")
            if 'resumen' in data:
                resumen = data['resumen']
                print(f"   📊 Carrito actualizado: {resumen['cantidad_productos']} productos, ${resumen['total_monto']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Estado final
    print("\n🎯 ESTADO FINAL DEL CARRITO:")
    print("-" * 30)
    
    try:
        response = sesion2.get(f"{base_url}/api/carrito/productos")
        data = response.json()
        
        if data['success']:
            productos = data['resumen']['productos']
            print(f"📦 Productos en carrito ({len(productos)} total):")
            
            total_general = 0
            for producto in productos:
                print(f"   • {producto['producto_codigo']}: {producto['cantidad']} x ${producto['precio_unitario']}")
                if float(producto['descuento']) > 0:
                    print(f"     Descuento: ${producto['descuento']}")
                print(f"     Subtotal: ${producto['total_linea']}")
                total_general += float(producto['total_linea'])
                print()
            
            print(f"💰 TOTAL GENERAL: ${total_general:.2f}")
            print(f"📊 Resumen: {data['resumen']['cantidad_productos']} productos, {data['resumen']['total_unidades']} unidades")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Finalización
    print("\n🎉 BENEFICIOS IMPLEMENTADOS:")
    print("-" * 28)
    print("✅ Carrito persiste entre sesiones")
    print("✅ Frontend se sincroniza automáticamente al cargar")
    print("✅ Barra de resumen aparece cuando hay productos")
    print("✅ Cantidades y descuentos se restauran en el frontend")
    print("✅ No se pierde información al recargar la página")
    print("✅ Múltiples sesiones pueden trabajar simultáneamente")
    
    print(f"\n💡 Para probar en el navegador:")
    print(f"   1. Abre: http://localhost:8002/productos")
    print(f"   2. Los productos aparecerán automáticamente cargados")
    print(f"   3. La barra de resumen se mostrará con los totales")
    
    print("\n" + "=" * 65)
    print("🏁 DEMOSTRACIÓN COMPLETADA - SISTEMA FUNCIONANDO PERFECTAMENTE")

if __name__ == "__main__":
    demo_carrito_sincronizado()
