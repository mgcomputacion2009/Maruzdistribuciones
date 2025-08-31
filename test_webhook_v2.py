#!/usr/bin/env python3
# 🧪 SCRIPT DE PRUEBA DEL WEBHOOK V2
# Prueba el webhook actualizado para productos con nombres de archivos

import requests
import json
import time
from datetime import datetime

# Configuración
WEBHOOK_BASE = "http://34.57.121.200:8002"
ENDPOINTS = {
    'health': f"{WEBHOOK_BASE}/api/webhook/productos/health",
    'single': f"{WEBHOOK_BASE}/api/webhook/productos",
    'batch': f"{WEBHOOK_BASE}/api/webhook/productos/batch"
}

def test_health_check():
    """Prueba el endpoint de salud"""
    print("🏥 PRUEBA DE SALUD DEL WEBHOOK")
    print("=" * 50)
    
    try:
        response = requests.get(ENDPOINTS['health'], timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📊 Respuesta: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_single_product():
    """Prueba el endpoint de producto individual"""
    print("\n📦 PRUEBA DE PRODUCTO INDIVIDUAL")
    print("=" * 50)
    
    # Producto de prueba con nombres de archivos
    producto_prueba = {
        "codigo": "PROD-TEST-001",
        "descripcion": "Producto de Prueba para Webhook V2",
        "nota": "Este es un producto de prueba para verificar el webhook actualizado",
        "web": "https://tusam.app/productos/prod-test-001",
        "categoria": "Pruebas",
        "descripcion_producto": "Descripción detallada del producto de prueba",
        "propiedades": "Propiedades físicas y químicas del producto",
        "datos_tecnicos": "Datos técnicos y especificaciones técnicas",
        "especificaciones": "Especificaciones detalladas del producto",
        "campos_aplicacion": "Campos y aplicaciones donde se usa el producto",
        "envases_disponibles": "Tipos de envases disponibles",
        "recomendaciones": "Recomendaciones de uso y manejo",
        "cont": "CONT-TEST-001",
        "pr": "PR-TEST-001.pdf",
        "id_drive": "drive_id_test_001",
        "qrt": "QR-TEST-001",
        "IMAGEN1": "producto_test_001_imagen1.jpg",
        "IMAGEN2": "producto_test_001_imagen2.jpg",
        "IMAGEN3": "producto_test_001_imagen3.png",
        "METADATA": "producto_test_001_metadata.json",
        "pdf": "producto_test_001_ficha.pdf"
    }
    
    print(f"📤 Enviando producto: {producto_prueba['codigo']}")
    print(f"🖼️ Imágenes: {producto_prueba['IMAGEN1']}, {producto_prueba['IMAGEN2']}, {producto_prueba['IMAGEN3']}")
    print(f"📄 Documentos: {producto_prueba['METADATA']}, {producto_prueba['pdf']}")
    
    try:
        response = requests.post(
            ENDPOINTS['single'],
            json=producto_prueba,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📊 Respuesta: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('procesado'):
                print("🎉 ¡Producto procesado exitosamente!")
                print(f"📁 Estructura de carpetas: {data.get('estructura_carpetas')}")
            else:
                print("⚠️ Producto no procesado completamente")
        else:
            print("❌ Error en el procesamiento")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_batch_products():
    """Prueba el endpoint de productos en lote"""
    print("\n📦 PRUEBA DE PRODUCTOS EN LOTE")
    print("=" * 50)
    
    # Lote de productos de prueba
    productos_lote = [
        {
            "codigo": "PROD-TEST-002",
            "descripcion": "Segundo Producto de Prueba",
            "categoria": "Pruebas",
            "IMAGEN1": "producto_test_002_imagen1.jpg",
            "pdf": "producto_test_002_ficha.pdf"
        },
        {
            "codigo": "PROD-TEST-003",
            "descripcion": "Tercer Producto de Prueba",
            "categoria": "Pruebas",
            "IMAGEN1": "producto_test_003_imagen1.jpg",
            "IMAGEN2": "producto_test_003_imagen2.jpg"
        },
        {
            "codigo": "PROD-TEST-004",
            "descripcion": "Cuarto Producto de Prueba",
            "categoria": "Pruebas",
            "METADATA": "producto_test_004_metadata.json"
        }
    ]
    
    print(f"📤 Enviando lote de {len(productos_lote)} productos")
    
    try:
        response = requests.post(
            ENDPOINTS['batch'],
            json=productos_lote,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📊 Respuesta: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Resumen del lote:")
            print(f"   Total recibidos: {data.get('total_recibidos')}")
            print(f"   Productos válidos: {data.get('productos_validos')}")
            print(f"   Productos procesados: {data.get('productos_procesados')}")
            print(f"   Productos con errores: {data.get('productos_invalidos')}")
            
            if data.get('detalle_invalidos'):
                print("   📋 Detalle de errores:")
                for error in data['detalle_invalidos']:
                    print(f"      - Producto {error['indice']}: {error['error']}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_product():
    """Prueba el endpoint con producto inválido"""
    print("\n❌ PRUEBA DE PRODUCTO INVÁLIDO")
    print("=" * 50)
    
    # Producto sin campos requeridos
    producto_invalido = {
        "categoria": "Pruebas",
        "IMAGEN1": "imagen_sin_codigo.jpg"
    }
    
    print("📤 Enviando producto inválido (sin código ni descripción)")
    
    try:
        response = requests.post(
            ENDPOINTS['single'],
            json=producto_invalido,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📊 Respuesta: {json.dumps(response.json(), indent=2)}")
        
        # Debería devolver error 400
        if response.status_code == 400:
            print("✅ Correcto: Se rechazó el producto inválido")
            return True
        else:
            print("⚠️ Inesperado: Se aceptó un producto inválido")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL WEBHOOK V2")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now()}")
    print(f"🌐 Servidor: {WEBHOOK_BASE}")
    print("=" * 60)
    
    # Esperar un momento para que el servidor esté listo
    print("⏳ Esperando 3 segundos para que el servidor esté listo...")
    time.sleep(3)
    
    # Ejecutar pruebas
    resultados = []
    
    # 1. Health Check
    resultados.append(("Health Check", test_health_check()))
    
    # 2. Producto Individual
    resultados.append(("Producto Individual", test_single_product()))
    
    # 3. Productos en Lote
    resultados.append(("Productos en Lote", test_batch_products()))
    
    # 4. Producto Inválido
    resultados.append(("Producto Inválido", test_invalid_product()))
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    exitos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ EXITOSA" if resultado else "❌ FALLIDA"
        print(f"{nombre}: {estado}")
    
    print(f"\n📈 Resultado: {exitos}/{total} pruebas exitosas")
    
    if exitos == total:
        print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("✅ El webhook V2 está funcionando correctamente")
    else:
        print("⚠️ Algunas pruebas fallaron")
        print("🔍 Revisar logs del servidor para más detalles")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Pruebas canceladas por el usuario")
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
