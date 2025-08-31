#!/usr/bin/env python3
# 🧪 SCRIPT DE PRUEBA - WEBHOOK PRODUCTOS
# Envía un producto de ejemplo al webhook para testing

import requests
import json
from datetime import datetime

# Configuración del webhook
WEBHOOK_URL = "http://127.0.0.1:8002/api/webhook/productos"
HEALTH_URL = "http://127.0.0.1:8002/api/webhook/productos/health"

def test_health_check():
    """Probar el endpoint de salud del webhook"""
    print("🔍 Probando health check...")
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        print(f"✅ Health check: {response.status_code}")
        print(f"📄 Respuesta: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_single_product():
    """Probar el endpoint de producto individual"""
    print("\n📦 Probando producto individual...")
    
    # Producto de ejemplo basado en los campos de AppSheet
    producto_ejemplo = {
        "codigo": "PROD_TEST_001",
        "descripcion": "Aceite de motor sintético 5W-30",
        "nota": "Producto de prueba para testing del webhook",
        "web": "https://ejemplo.com/producto",
        "categoria": "Lubricantes",
        "descripcion_producto": "Aceite de motor de alta calidad para vehículos modernos",
        "propiedades": "Viscosidad 5W-30, API SN Plus, ACEA C5",
        "datos_tecnicos": "Punto de inflamación: 230°C, Punto de congelación: -40°C",
        "especificaciones": "Cumple estándares API SN Plus y ACEA C5",
        "campos_aplicacion": "Motores gasolina y diésel modernos",
        "envases_disponibles": "1L, 4L, 20L",
        "recomendaciones": "Se han de cumplir las instrucciones de uso de los fabricantes de automóviles",
        "cont": "CONT_TEST_001",
        "pr": "PR_TEST_001",
        "id_drive": "DRIVE_TEST_001",
        "qrt": "QR_TEST_001"
    }
    
    try:
        print(f"📤 Enviando producto: {producto_ejemplo['codigo']}")
        response = requests.post(
            WEBHOOK_URL,
            json=producto_ejemplo,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"✅ Respuesta: {response.status_code}")
        print(f"📄 Contenido: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error enviando producto: {e}")
        return False

def test_batch_products():
    """Probar el endpoint de lote de productos"""
    print("\n📦 Probando lote de productos...")
    
    # Lote de productos de ejemplo
    productos_lote = [
        {
            "codigo": "PROD_TEST_002",
            "descripcion": "Filtro de aceite de motor",
            "categoria": "Filtros",
            "nota": "Segundo producto de prueba"
        },
        {
            "codigo": "PROD_TEST_003",
            "descripcion": "Bujía de encendido",
            "categoria": "Encendido",
            "nota": "Tercer producto de prueba"
        }
    ]
    
    try:
        print(f"📤 Enviando lote de {len(productos_lote)} productos")
        response = requests.post(
            f"{WEBHOOK_URL}/batch",
            json=productos_lote,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"✅ Respuesta: {response.status_code}")
        print(f"📄 Contenido: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error enviando lote: {e}")
        return False

def main():
    """Función principal de testing"""
    print("🧪 INICIANDO PRUEBAS DEL WEBHOOK")
    print("=" * 50)
    print(f"⏰ Timestamp: {datetime.now()}")
    print(f"🌐 URL del webhook: {WEBHOOK_URL}")
    print("=" * 50)
    
    # Probar health check
    health_ok = test_health_check()
    
    if not health_ok:
        print("❌ Health check falló. Verificar que la app esté corriendo.")
        return
    
    # Probar producto individual
    single_ok = test_single_product()
    
    # Probar lote de productos
    batch_ok = test_batch_products()
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    print(f"🔍 Health Check: {'✅ OK' if health_ok else '❌ FALLÓ'}")
    print(f"📦 Producto Individual: {'✅ OK' if single_ok else '❌ FALLÓ'}")
    print(f"📦 Lote de Productos: {'✅ OK' if batch_ok else '❌ FALLÓ'}")
    
    if all([health_ok, single_ok, batch_ok]):
        print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisar logs.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
