#!/usr/bin/env python3
# 🪟 SCRIPT WINDOWS - CARGAR PRODUCTOS DESDE CSV
# Lee archivo CSV y envía productos al endpoint del servidor

import csv
import requests
import json
import sys
import os
from datetime import datetime
import time

# Configuración
SERVER_URL = "http://34.57.121.200:8002"
ENDPOINT = "/api/productos/cargar"
STATUS_ENDPOINT = "/api/productos/status"

def mostrar_ayuda():
    """Mostrar ayuda del script"""
    print("🚀 CARGADOR DE PRODUCTOS MARUZ - WINDOWS")
    print("=" * 50)
    print("Uso:")
    print("  python cargar_productos_windows.py <archivo_csv>")
    print("")
    print("Ejemplo:")
    print("  python cargar_productos_windows.py productos.csv")
    print("")
    print("Formato CSV esperado:")
    print("  CODIGO,DESCRIPCION,ALTERNO,IMAGEN1,IMAGEN2,IMAGEN3,...")
    print("")
    print("Opciones:")
    print("  --help     Mostrar esta ayuda")
    print("  --status   Verificar estado del servidor")
    print("  --test     Probar con datos de ejemplo")

def verificar_servidor():
    """Verificar que el servidor esté funcionando"""
    print("🔍 Verificando servidor...")
    
    try:
        response = requests.get(f"{SERVER_URL}{STATUS_ENDPOINT}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Servidor operativo:")
            print(f"   - Estado: {data['status']}")
            print(f"   - Total productos: {data['tabla_productos']['total_productos']}")
            print(f"   - Empresa: Maruz Distribuciones")
            return True
        else:
            print(f"❌ Servidor respondió con error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print(f"   Verifica que esté funcionando en: {SERVER_URL}")
        return False
    except requests.exceptions.Timeout:
        print("⏰ Timeout - El servidor tardó demasiado en responder")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def leer_csv(archivo_csv):
    """Leer archivo CSV y convertir a lista de productos"""
    print(f"📖 Leyendo archivo: {archivo_csv}")
    
    if not os.path.exists(archivo_csv):
        print(f"❌ El archivo {archivo_csv} no existe")
        return None
    
    productos = []
    
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as file:
            # Detectar delimitador
            sample = file.read(1024)
            file.seek(0)
            
            # Intentar diferentes delimitadores
            delimiters = [',', ';', '\t']
            detected_delimiter = ','
            
            for delimiter in delimiters:
                if delimiter in sample:
                    detected_delimiter = delimiter
                    break
            
            print(f"   Delimitador detectado: '{detected_delimiter}'")
            
            # Leer CSV
            reader = csv.DictReader(file, delimiter=detected_delimiter)
            
            # Verificar campos obligatorios
            required_fields = ['CODIGO', 'DESCRIPCION']
            missing_fields = [field for field in required_fields if field not in reader.fieldnames]
            
            if missing_fields:
                print(f"❌ Campos obligatorios faltantes: {missing_fields}")
                print(f"   Campos disponibles: {reader.fieldnames}")
                return None
            
            # Procesar cada fila
            for i, row in enumerate(reader, 1):
                # Limpiar campos vacíos
                producto_limpio = {}
                for key, value in row.items():
                    if value and value.strip():
                        producto_limpio[key.strip()] = value.strip()
                    else:
                        producto_limpio[key.strip()] = ""
                
                productos.append(producto_limpio)
                
                if i % 100 == 0:
                    print(f"   Procesados: {i} productos...")
            
            print(f"✅ Total productos leídos: {len(productos)}")
            return productos
            
    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
        return None

def enviar_productos(productos, batch_size=50):
    """Enviar productos al servidor en lotes"""
    print(f"🚀 Enviando {len(productos)} productos al servidor...")
    
    total_enviados = 0
    total_insertados = 0
    total_actualizados = 0
    total_errores = 0
    
    # Procesar en lotes
    for i in range(0, len(productos), batch_size):
        batch = productos[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(productos) + batch_size - 1) // batch_size
        
        print(f"   Lote {batch_num}/{total_batches} - {len(batch)} productos")
        
        # Preparar payload
        payload = {
            "productos": batch,
            "timestamp": datetime.now().isoformat(),
            "origen": f"Windows - Lote {batch_num}",
            "batch_info": {
                "numero": batch_num,
                "total": total_batches,
                "tamaño": len(batch)
            }
        }
        
        # Headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Maruz-Productos-Loader-Windows/1.0'
        }
        
        try:
            # Enviar lote
            response = requests.post(
                f"{SERVER_URL}{ENDPOINT}",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Actualizar contadores
                total_enviados += data['resumen']['total_productos']
                total_insertados += data['resumen']['insertados']
                total_actualizados += data['resumen']['actualizados']
                total_errores += data['resumen']['errores']
                
                print(f"     ✅ Lote procesado:")
                print(f"       - Insertados: {data['resumen']['insertados']}")
                print(f"       - Actualizados: {data['resumen']['actualizados']}")
                print(f"       - Errores: {data['resumen']['errores']}")
                print(f"       - Tiempo: {data['resumen']['tiempo_procesamiento_segundos']}s")
                
                # Mostrar errores si los hay
                if data['detalles']['productos_con_errores']:
                    print("       ⚠️ Errores en este lote:")
                    for error in data['detalles']['productos_con_errores'][:3]:  # Solo primeros 3
                        print(f"         - {error['codigo']}: {error.get('errores', error.get('error', 'Error'))}")
                    if len(data['detalles']['productos_con_errores']) > 3:
                        print(f"         ... y {len(data['detalles']['productos_con_errores']) - 3} más")
                
            else:
                print(f"     ❌ Error en lote {batch_num}: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"       Error: {error_data.get('error', 'Error desconocido')}")
                except:
                    print(f"       Respuesta: {response.text[:200]}...")
                
                total_errores += len(batch)
            
            # Pausa entre lotes para no sobrecargar el servidor
            if batch_num < total_batches:
                time.sleep(1)
                
        except requests.exceptions.Timeout:
            print(f"     ⏰ Timeout en lote {batch_num}")
            total_errores += len(batch)
        except Exception as e:
            print(f"     ❌ Error inesperado en lote {batch_num}: {e}")
            total_errores += len(batch)
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN FINAL DE CARGA")
    print("=" * 50)
    print(f"Total productos procesados: {total_enviados}")
    print(f"✅ Insertados: {total_insertados}")
    print(f"🔄 Actualizados: {total_actualizados}")
    print(f"❌ Errores: {total_errores}")
    print(f"📈 Tasa de éxito: {((total_insertados + total_actualizados) / total_enviados * 100):.1f}%")
    
    return {
        'total': total_enviados,
        'insertados': total_insertados,
        'actualizados': total_actualizados,
        'errores': total_errores
    }

def crear_csv_ejemplo():
    """Crear archivo CSV de ejemplo"""
    archivo_ejemplo = "productos_ejemplo.csv"
    
    productos_ejemplo = [
        {
            'CODIGO': 'PROD001',
            'DESCRIPCION': 'Producto de ejemplo 1',
            'ALTERNO': 'ALT001',
            'IMAGEN1': 'imagen1_prod001.jpg',
            'IMAGEN2': 'imagen2_prod001.jpg',
            'IMAGEN3': 'imagen3_prod001.jpg',
            'IMAGEN1(EDITADA)': 'imagen1_editada_prod001.jpg',
            'IMAGEN2(EDITADA)': 'imagen2_editada_prod001.jpg',
            'IMAGEN3(EDITADA)': 'imagen3_editada_prod001.jpg',
            'METADATA': 'Metadatos del producto 1',
            'NOTA': 'Nota importante del producto 1',
            'WEB': 'https://ejemplo.com/producto1',
            'CATEGORIA': 'Categoría A',
            'Descripción Producto': 'Descripción técnica detallada del producto 1',
            'Propiedades': 'Propiedades físicas y químicas',
            'Datos técnicos': 'Especificaciones técnicas completas',
            'Especificaciones': 'Especificaciones de calidad y rendimiento',
            'Campos de aplicación': 'Industria, construcción, etc.',
            'Envases disponibles': 'Tambor 200L, IBC 1000L',
            'pdf': 'ficha_tecnica_prod001.pdf',
            'RECOMENDACIONES': 'Recomendaciones de uso y seguridad',
            'cont': 'CONT001',
            'PR': 'PR001',
            'IDdrive': 'DRIVE001',
            'qrt': 'QR001'
        },
        {
            'CODIGO': 'PROD002',
            'DESCRIPCION': 'Producto de ejemplo 2',
            'ALTERNO': 'ALT002',
            'IMAGEN1': 'imagen1_prod002.jpg',
            'IMAGEN2': '',
            'IMAGEN3': '',
            'IMAGEN1(EDITADA)': 'imagen1_editada_prod002.jpg',
            'IMAGEN2(EDITADA)': '',
            'IMAGEN3(EDITADA)': '',
            'METADATA': 'Metadatos del producto 2',
            'NOTA': 'Nota del producto 2',
            'WEB': 'https://ejemplo.com/producto2',
            'CATEGORIA': 'Categoría B',
            'Descripción Producto': 'Descripción del producto 2',
            'Propiedades': 'Propiedades del producto 2',
            'Datos técnicos': 'Datos técnicos del producto 2',
            'Especificaciones': 'Especificaciones del producto 2',
            'Campos de aplicación': 'Aplicaciones del producto 2',
            'Envases disponibles': 'Tambor 100L',
            'pdf': 'ficha_prod002.pdf',
            'RECOMENDACIONES': 'Recomendaciones del producto 2',
            'cont': 'CONT002',
            'PR': 'PR002',
            'IDdrive': 'DRIVE002',
            'qrt': 'QR002'
        }
    ]
    
    try:
        with open(archivo_ejemplo, 'w', newline='', encoding='utf-8') as file:
            if productos_ejemplo:
                fieldnames = productos_ejemplo[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(productos_ejemplo)
        
        print(f"✅ Archivo de ejemplo creado: {archivo_ejemplo}")
        print("   Puedes usarlo como plantilla para tu archivo CSV")
        
    except Exception as e:
        print(f"❌ Error creando archivo de ejemplo: {e}")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        mostrar_ayuda()
        return
    
    comando = sys.argv[1]
    
    if comando == '--help':
        mostrar_ayuda()
        return
    elif comando == '--status':
        verificar_servidor()
        return
    elif comando == '--test':
        crear_csv_ejemplo()
        return
    
    # Verificar que el archivo CSV existe
    archivo_csv = comando
    
    if not os.path.exists(archivo_csv):
        print(f"❌ El archivo {archivo_csv} no existe")
        print("   Usa --test para crear un archivo de ejemplo")
        return
    
    # Verificar servidor
    if not verificar_servidor():
        print("❌ No se puede continuar sin conexión al servidor")
        return
    
    # Leer CSV
    productos = leer_csv(archivo_csv)
    if not productos:
        return
    
    # Confirmar envío
    print(f"\n¿Enviar {len(productos)} productos al servidor? (s/n): ", end="")
    respuesta = input().lower().strip()
    
    if respuesta not in ['s', 'si', 'y', 'yes']:
        print("❌ Operación cancelada")
        return
    
    # Enviar productos
    print("\n" + "=" * 50)
    resultado = enviar_productos(productos)
    
    # Guardar log
    log_file = f"carga_productos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Carga de productos - {datetime.now()}\n")
            f.write(f"Archivo: {archivo_csv}\n")
            f.write(f"Total: {resultado['total']}\n")
            f.write(f"Insertados: {resultado['insertados']}\n")
            f.write(f"Actualizados: {resultado['actualizados']}\n")
            f.write(f"Errores: {resultado['errores']}\n")
        
        print(f"📝 Log guardado en: {log_file}")
        
    except Exception as e:
        print(f"⚠️ No se pudo guardar el log: {e}")

if __name__ == "__main__":
    main()
