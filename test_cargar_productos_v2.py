#!/usr/bin/env python3
"""
Script de prueba para el endpoint de carga de productos v2
Incluye campos de precios, inventario y códigos de barras
"""

import requests
import json
from datetime import datetime

# Configuración
API_BASE_URL = "http://34.57.121.200:8002"
ENDPOINT_CARGAR = f"{API_BASE_URL}/api/productos/cargar_v2"
ENDPOINT_STATUS = f"{API_BASE_URL}/api/productos/status_v2"

def test_status():
    """Probar endpoint de status"""
    print("🔍 Probando endpoint de status...")
    
    try:
        response = requests.get(ENDPOINT_STATUS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Status exitoso:")
            print(f"   - Tabla existe: {data['estado']['tabla_existe']}")
            print(f"   - Total productos: {data['estado']['total_productos']}")
            print(f"   - Productos activos: {data['estado']['productos_activos']}")
            print(f"   - Productos con stock: {data['estado']['productos_con_stock']}")
            
            if data['ultimas_actualizaciones']:
                print("   - Últimas actualizaciones:")
                for item in data['ultimas_actualizaciones'][:3]:
                    print(f"     • {item['codigo']}: {item['descripcion']}")
        else:
            print(f"❌ Error en status: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error conectando al endpoint: {e}")

def test_cargar_productos():
    """Probar carga de productos con nuevos campos"""
    print("\n🚀 Probando carga de productos v2...")
    
    # Datos de prueba con campos de precios e inventario
    productos_prueba = [
        {
            "CODIGO": "PROD001",
            "DESCRIPCION": "Aceite de motor sintético 5W-30",
            "PRE_PRECIO": "25.50",
            "PRECIOA": "30.00",
            "PRECIOB": "28.50",
            "PRECIOA + IVA": "35.70",
            "PRECIOB + IVA": "33.35",
            "ULTIMO_COSTO": "18.00",
            "COSTO USD": "15.50",
            "UTIL": "12.00",
            "EXIS": "150",
            "ALMACEN": "Principal",
            "UND MED": "Litro",
            "TIPO IVA": "19%",
            "MARCA": "Castrol",
            "GRUPO": "Lubricantes",
            "SUB GRUPO": "Aceites de motor",
            "BARRAS": "7891234567890",
            "IMAGEN1": "aceite_motor_1.jpg",
            "IMAGEN2": "aceite_motor_2.jpg",
            "METADATA": "Aceite sintético de alta calidad",
            "NOTA": "Producto premium",
            "WEB": "https://castrol.com/aceite-5w30",
            "CATEGORIA": "Automotriz",
            "Descripción Producto": "Aceite de motor sintético con aditivos especiales",
            "Propiedades": "Viscosidad 5W-30, API SN Plus",
            "Datos técnicos": "Punto de fluidez -40°C, Viscosidad 100°C: 12.5 cSt",
            "Especificaciones": "Cumple especificaciones API SN Plus, ILSAC GF-6A",
            "Campos de aplicación": "Motores de gasolina modernos",
            "Envases disponibles": "1L, 4L, 20L",
            "pdf": "ficha_tecnica_castrol_5w30.pdf",
            "RECOMENDACIONES": "Cambiar cada 10,000 km o 12 meses"
        },
        {
            "CODIGO": "PROD002",
            "DESCRIPCION": "Filtro de aire de alto rendimiento",
            "PRE_PRECIO": "15.00",
            "PRECIOA": "18.50",
            "PRECIOB": "17.00",
            "PRECIOA + IVA": "22.02",
            "PRECIOB + IVA": "20.23",
            "ULTIMO_COSTO": "12.00",
            "COSTO USD": "10.00",
            "UTIL": "6.50",
            "EXIS": "75",
            "ALMACEN": "Secundario",
            "UND MED": "Unidad",
            "TIPO IVA": "19%",
            "MARCA": "K&N",
            "GRUPO": "Filtros",
            "SUB GRUPO": "Filtros de aire",
            "BARRAS": "7891234567891",
            "IMAGEN1": "filtro_aire_1.jpg",
            "METADATA": "Filtro de aire lavable",
            "NOTA": "Lavable y reutilizable",
            "WEB": "https://knfilters.com/filtros-aire",
            "CATEGORIA": "Automotriz",
            "Descripción Producto": "Filtro de aire de alto flujo lavable",
            "Propiedades": "Material de algodón tratado, reutilizable",
            "Datos técnicos": "Capacidad de flujo 50% mayor que filtros convencionales",
            "Especificaciones": "Cumple especificaciones OEM",
            "Campos de aplicación": "Motores de alto rendimiento",
            "Envases disponibles": "Unidad individual",
            "pdf": "ficha_tecnica_kn_filtro.pdf",
            "RECOMENDACIONES": "Lavar cada 50,000 km"
        },
        {
            "CODIGO": "PROD003",
            "DESCRIPCION": "Batería automotriz 60Ah",
            "PRE_PRECIO": "85.00",
            "PRECIOA": "95.00",
            "PRECIOB": "90.00",
            "PRECIOA + IVA": "113.05",
            "PRECIOB + IVA": "107.10",
            "ULTIMO_COSTO": "65.00",
            "COSTO USD": "55.00",
            "UTIL": "30.00",
            "EXIS": "25",
            "ALMACEN": "Principal",
            "UND MED": "Unidad",
            "TIPO IVA": "19%",
            "MARCA": "Bosch",
            "GRUPO": "Baterías",
            "SUB GRUPO": "Baterías automotrices",
            "BARRAS": "7891234567892",
            "IMAGEN1": "bateria_bosch_1.jpg",
            "IMAGEN2": "bateria_bosch_2.jpg",
            "METADATA": "Batería de plomo-ácido sellada",
            "NOTA": "Libre de mantenimiento",
            "WEB": "https://bosch-automotive.com/baterias",
            "CATEGORIA": "Automotriz",
            "Descripción Producto": "Batería automotriz de 60Ah libre de mantenimiento",
            "Propiedades": "Tecnología AGM, libre de mantenimiento",
            "Datos técnicos": "Capacidad 60Ah, CCA 600A, Dimensiones 242x175x190mm",
            "Especificaciones": "Cumple especificaciones DIN, SAE, JIS",
            "Campos de aplicación": "Vehículos modernos con sistemas start-stop",
            "Envases disponibles": "Unidad individual con garantía",
            "pdf": "ficha_tecnica_bosch_60ah.pdf",
            "RECOMENDACIONES": "Verificar carga cada 6 meses"
        }
    ]
    
    # Preparar datos para envío
    datos_envio = {
        "productos": productos_prueba,
        "timestamp": datetime.now().isoformat(),
        "origen": "Script de prueba v2 - Campos de precios e inventario"
    }
    
    try:
        print(f"📤 Enviando {len(productos_prueba)} productos...")
        
        response = requests.post(
            ENDPOINT_CARGAR,
            json=datos_envio,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Carga exitosa:")
            print(f"   - Total procesados: {data['resumen']['total_productos']}")
            print(f"   - Insertados: {data['resumen']['insertados']}")
            print(f"   - Actualizados: {data['resumen']['actualizados']}")
            print(f"   - Errores: {data['resumen']['errores']}")
            print(f"   - Tiempo: {data['resumen']['tiempo_procesamiento_segundos']}s")
            
            if data['detalles']['productos_con_errores']:
                print("   - Productos con errores:")
                for error in data['detalles']['productos_con_errores']:
                    print(f"     • {error['codigo']}: {error['errores']}")
        else:
            print(f"❌ Error en carga: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error enviando datos: {e}")

def test_producto_invalido():
    """Probar validación de productos inválidos"""
    print("\n⚠️ Probando validación de productos inválidos...")
    
    productos_invalidos = [
        {
            "CODIGO": "",  # Código vacío
            "DESCRIPCION": "Producto sin código"
        },
        {
            "CODIGO": "PROD004",
            "DESCRIPCION": "Producto con precio inválido",
            "PRECIOA": "no_es_numero",
            "EXIS": "tampoco_es_numero"
        },
        {
            # Sin código ni descripción
            "MARCA": "Solo marca"
        }
    ]
    
    datos_envio = {
        "productos": productos_invalidos,
        "timestamp": datetime.now().isoformat(),
        "origen": "Prueba de validación"
    }
    
    try:
        response = requests.post(
            ENDPOINT_CARGAR,
            json=datos_envio,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Validación funcionando:")
            print(f"   - Total: {data['resumen']['total_productos']}")
            print(f"   - Errores: {data['resumen']['errores']}")
            
            if data['detalles']['productos_con_errores']:
                print("   - Errores detectados:")
                for error in data['detalles']['productos_con_errores']:
                    print(f"     • {error['codigo']}: {error['errores']}")
        else:
            print(f"❌ Error en validación: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en validación: {e}")

def main():
    """Función principal"""
    print("🧪 PRUEBAS DEL ENDPOINT DE PRODUCTOS V2")
    print("=" * 50)
    
    # Probar status
    test_status()
    
    # Probar carga de productos válidos
    test_cargar_productos()
    
    # Probar validación
    test_producto_invalido()
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")

if __name__ == "__main__":
    main()
