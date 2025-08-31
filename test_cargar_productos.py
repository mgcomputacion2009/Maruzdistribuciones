#!/usr/bin/env python3
# 🧪 SCRIPT DE PRUEBA - ENDPOINT CARGAR PRODUCTOS
# Prueba el endpoint /api/productos/cargar desde Windows

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://34.57.121.200:8002"
ENDPOINT = "/api/productos/cargar"
STATUS_ENDPOINT = "/api/productos/status"

def test_status():
    """Probar endpoint de status"""
    print("🔍 Probando endpoint de status...")
    
    try:
        response = requests.get(f"{BASE_URL}{STATUS_ENDPOINT}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Status OK:")
            print(f"   - Total productos: {data['tabla_productos']['total_productos']}")
            print(f"   - Estado: {data['status']}")
        else:
            print(f"❌ Error en status: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")

def test_cargar_productos():
    """Probar endpoint de cargar productos"""
    print("\n🚀 Probando endpoint de cargar productos...")
    
    # Datos de prueba
    productos_prueba = [
        {
            "CODIGO": "PROD001",
            "DESCRIPCION": "Producto de prueba 1 - Descripción completa del producto",
            "ALTERNO": "ALT001",
            "IMAGEN1": "imagen1_prod001.jpg",
            "IMAGEN2": "imagen2_prod001.jpg",
            "IMAGEN3": "imagen3_prod001.jpg",
            "IMAGEN1(EDITADA)": "imagen1_editada_prod001.jpg",
            "IMAGEN2(EDITADA)": "imagen2_editada_prod001.jpg",
            "IMAGEN3(EDITADA)": "imagen3_editada_prod001.jpg",
            "METADATA": "Metadatos del producto 1",
            "NOTA": "Nota importante del producto 1",
            "WEB": "https://ejemplo.com/producto1",
            "CATEGORIA": "Categoría A",
            "Descripción Producto": "Descripción técnica detallada del producto 1",
            "Propiedades": "Propiedades físicas y químicas",
            "Datos técnicos": "Especificaciones técnicas completas",
            "Especificaciones": "Especificaciones de calidad y rendimiento",
            "Campos de aplicación": "Industria, construcción, etc.",
            "Envases disponibles": "Tambor 200L, IBC 1000L",
            "pdf": "ficha_tecnica_prod001.pdf",
            "RECOMENDACIONES": "Recomendaciones de uso y seguridad",
            "cont": "CONT001",
            "PR": "PR001",
            "IDdrive": "DRIVE001",
            "qrt": "QR001"
        },
        {
            "CODIGO": "PROD002",
            "DESCRIPCION": "Producto de prueba 2 - Otro producto de ejemplo",
            "ALTERNO": "ALT002",
            "IMAGEN1": "imagen1_prod002.jpg",
            "IMAGEN2": "",
            "IMAGEN3": "",
            "IMAGEN1(EDITADA)": "imagen1_editada_prod002.jpg",
            "IMAGEN2(EDITADA)": "",
            "IMAGEN3(EDITADA)": "",
            "METADATA": "Metadatos del producto 2",
            "NOTA": "Nota del producto 2",
            "WEB": "https://ejemplo.com/producto2",
            "CATEGORIA": "Categoría B",
            "Descripción Producto": "Descripción del producto 2",
            "Propiedades": "Propiedades del producto 2",
            "Datos técnicos": "Datos técnicos del producto 2",
            "Especificaciones": "Especificaciones del producto 2",
            "Campos de aplicación": "Aplicaciones del producto 2",
            "Envases disponibles": "Tambor 100L",
            "pdf": "ficha_prod002.pdf",
            "RECOMENDACIONES": "Recomendaciones del producto 2",
            "cont": "CONT002",
            "PR": "PR002",
            "IDdrive": "DRIVE002",
            "qrt": "QR002"
        }
    ]
    
    # Preparar payload
    payload = {
        "productos": productos_prueba,
        "timestamp": datetime.now().isoformat(),
        "origen": "Windows - Script de prueba"
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Maruz-Productos-Loader/1.0'
    }
    
    try:
        print(f"📤 Enviando {len(productos_prueba)} productos...")
        print(f"   URL: {BASE_URL}{ENDPOINT}")
        
        # Hacer request
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Respuesta recibida: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Carga exitosa:")
            print(f"   - Total procesados: {data['resumen']['total_productos']}")
            print(f"   - Insertados: {data['resumen']['insertados']}")
            print(f"   - Actualizados: {data['resumen']['actualizados']}")
            print(f"   - Errores: {data['resumen']['errores']}")
            print(f"   - Tiempo: {data['resumen']['tiempo_procesamiento_segundos']}s")
            
            if data['detalles']['productos_con_errores']:
                print("⚠️ Productos con errores:")
                for error in data['detalles']['productos_con_errores']:
                    print(f"   - {error['codigo']}: {error.get('errores', error.get('error', 'Error desconocido'))}")
                    
        else:
            print(f"❌ Error en la carga: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Error desconocido')}")
            except:
                print(f"   Respuesta: {response.text}")
                
    except requests.exceptions.Timeout:
        print("⏰ Timeout - El servidor tardó demasiado en responder")
    except requests.exceptions.ConnectionError:
        print("🔌 Error de conexión - No se pudo conectar al servidor")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_validaciones():
    """Probar validaciones del endpoint"""
    print("\n🧪 Probando validaciones...")
    
    # Test 1: Sin campo productos
    print("   Test 1: Sin campo 'productos'")
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json={"otro_campo": "valor"},
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code} - {'✅ OK' if response.status_code == 400 else '❌ Falló'}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Array vacío
    print("   Test 2: Array de productos vacío")
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json={"productos": []},
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code} - {'✅ OK' if response.status_code == 400 else '❌ Falló'}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Producto sin código
    print("   Test 3: Producto sin código")
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json={"productos": [{"DESCRIPCION": "Sin código"}]},
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code} - {'✅ OK' if response.status_code == 200 else '❌ Falló'}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Errores: {data['resumen']['errores']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Función principal"""
    print("🧪 PRUEBAS DEL ENDPOINT CARGAR PRODUCTOS")
    print("=" * 50)
    print(f"🌐 Servidor: {BASE_URL}")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Probar status
    test_status()
    
    # Probar validaciones
    test_validaciones()
    
    # Probar carga de productos
    test_cargar_productos()
    
    print("\n" + "=" * 50)
    print("🏁 PRUEBAS COMPLETADAS")
    print("=" * 50)

if __name__ == "__main__":
    main()
