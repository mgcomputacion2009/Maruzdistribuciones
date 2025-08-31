#!/usr/bin/env python3
# ⚙️ CONFIGURADOR DE SINCRONIZACIÓN
# Permite al usuario configurar las rutas de Google Drive Desktop

import os
import json
from pathlib import Path

def configurar_sincronizacion():
    """Configura las rutas de sincronización"""
    print("🔧 CONFIGURADOR DE SINCRONIZACIÓN - MARUZ DISTRIBUCIONES")
    print("=" * 60)
    
    # Obtener configuración actual
    config_file = "/var/www/maruz/config_sincronizacion.json"
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        print("📋 Configuración actual encontrada:")
        print(f"   Drive Local: {config.get('drive_local', 'No configurado')}")
        print(f"   Usuario Windows: {config.get('usuario_windows', 'No configurado')}")
    else:
        config = {}
        print("📋 No hay configuración previa")
    
    print("\n📁 CONFIGURACIÓN DE RUTAS:")
    print("=" * 60)
    
    # Solicitar usuario de Windows
    print("\n1️⃣ USUARIO DE WINDOWS:")
    print("   Ejemplo: TuUsuario, Admin, miguel, etc.")
    usuario_actual = config.get('usuario_windows', '')
    usuario = input(f"   Usuario Windows [{usuario_actual}]: ").strip()
    if not usuario:
        usuario = usuario_actual
    
    if not usuario:
        print("   ❌ Debes especificar un usuario de Windows")
        return False
    
    # Construir ruta de Google Drive
    ruta_base = f"/mnt/c/Users/{usuario}/Google Drive"
    
    print(f"\n2️⃣ RUTA DE GOOGLE DRIVE:")
    print(f"   Ruta base detectada: {ruta_base}")
    
    # Verificar si existe la ruta
    if os.path.exists(ruta_base):
        print("   ✅ Ruta de Google Drive encontrada")
    else:
        print("   ⚠️ Ruta de Google Drive no encontrada")
        print("   💡 Asegúrate de que Google Drive Desktop esté instalado y sincronizando")
    
    # Solicitar carpeta de productos
    print("\n3️⃣ CARPETA DE PRODUCTOS:")
    print("   Esta es la carpeta dentro de Google Drive donde están los productos")
    print("   Ejemplo: Maruz Distribuciones, Productos, etc.")
    
    carpeta_actual = config.get('carpeta_productos', 'Maruz Distribuciones/Productos')
    carpeta = input(f"   Carpeta de productos [{carpeta_actual}]: ").strip()
    if not carpeta:
        carpeta = carpeta_actual
    
    # Ruta completa
    ruta_completa = f"{ruta_base}/{carpeta}"
    
    print(f"\n4️⃣ RUTA COMPLETA:")
    print(f"   {ruta_completa}")
    
    # Verificar si existe
    if os.path.exists(ruta_completa):
        print("   ✅ Carpeta de productos encontrada")
        
        # Listar contenido
        try:
            contenido = os.listdir(ruta_completa)
            print(f"   📁 Contenido: {len(contenido)} elementos")
            if len(contenido) <= 10:
                for item in contenido:
                    print(f"      - {item}")
            else:
                for item in contenido[:5]:
                    print(f"      - {item}")
                print(f"      ... y {len(contenido) - 5} más")
        except Exception as e:
            print(f"   ⚠️ No se pudo listar contenido: {e}")
    else:
        print("   ⚠️ Carpeta de productos no encontrada")
        print("   💡 Verifica que la ruta sea correcta")
    
    # Guardar configuración
    config_actualizada = {
        'usuario_windows': usuario,
        'drive_local': ruta_completa,
        'servidor_remoto': '/var/www/maruz/app/maruz_distribuciones/storage/productos',
        'fecha_configuracion': str(Path().cwd().stat().st_mtime)
    }
    
    print(f"\n5️⃣ GUARDANDO CONFIGURACIÓN:")
    try:
        with open(config_file, 'w') as f:
            json.dump(config_actualizada, f, indent=2)
        print("   ✅ Configuración guardada en config_sincronizacion.json")
    except Exception as e:
        print(f"   ❌ Error guardando configuración: {e}")
        return False
    
    # Actualizar script de sincronización
    print(f"\n6️⃣ ACTUALIZANDO SCRIPT DE SINCRONIZACIÓN:")
    try:
        script_path = "/var/www/maruz/sincronizar_imagenes.py"
        
        with open(script_path, 'r') as f:
            contenido = f.read()
        
        # Reemplazar la ruta hardcodeada
        contenido_actualizado = contenido.replace(
            'self.drive_local = "/mnt/c/Users/TuUsuario/Google Drive/Maruz Distribuciones/Productos"',
            f'self.drive_local = "{ruta_completa}"'
        )
        
        with open(script_path, 'w') as f:
            f.write(contenido_actualizado)
        
        print("   ✅ Script de sincronización actualizado")
        
    except Exception as e:
        print(f"   ❌ Error actualizando script: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 60)
    
    print(f"\n📋 RESUMEN:")
    print(f"   Usuario Windows: {usuario}")
    print(f"   Ruta Drive: {ruta_completa}")
    print(f"   Servidor: /var/www/maruz/app/maruz_distribuciones/storage/productos")
    
    print(f"\n🚀 PRÓXIMOS PASOS:")
    print(f"   1. Instalar Google Drive Desktop en Windows")
    print(f"   2. Sincronizar la carpeta: {carpeta}")
    print(f"   3. Ejecutar: python3 sincronizar_imagenes.py")
    
    return True

if __name__ == "__main__":
    try:
        configurar_sincronizacion()
    except KeyboardInterrupt:
        print("\n\n❌ Configuración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error en configuración: {e}")
