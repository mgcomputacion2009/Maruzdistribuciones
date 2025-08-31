#!/usr/bin/env python3
"""
Script de Reinicio Completo para Maruz Distribuciones
Incluye limpieza de caché y reinicio del servicio en puerto 8002
"""

import os
import sys
import subprocess
import time
import signal

def limpiar_cache():
    """Limpiar caché del navegador y archivos temporales"""
    print("🧹 Limpiando caché...")
    
    # Limpiar archivos temporales de Python
    try:
        subprocess.run(["find", "/tmp", "-name", "*.pyc", "-delete"], check=False)
        subprocess.run(["find", "/tmp", "-name", "__pycache__", "-type", "d", "-exec", "rm", "-rf", "{}", "+"], check=False)
        print("✅ Cache de Python limpiado")
    except Exception as e:
        print(f"⚠️  Error limpiando cache Python: {e}")
    
    # Limpiar logs antiguos
    try:
        subprocess.run(["find", "/var/www/maruz/logs", "-name", "*.log", "-mtime", "+7", "-delete"], check=False)
        print("✅ Logs antiguos limpiados")
    except Exception as e:
        print(f"⚠️  Error limpiando logs: {e}")

def matar_proceso_puerto(puerto):
    """Matar proceso que esté usando el puerto especificado"""
    print(f"🔫 Matando proceso en puerto {puerto}...")
    
    try:
        # Buscar PID del proceso
        result = subprocess.run(["lsof", "-ti", f":{puerto}"], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"✅ Proceso {pid} terminado")
                    except ProcessLookupError:
                        print(f"⚠️  Proceso {pid} ya no existe")
                    except Exception as e:
                        print(f"❌ Error matando proceso {pid}: {e}")
        else:
            print(f"ℹ️  No hay procesos en puerto {puerto}")
    except Exception as e:
        print(f"❌ Error buscando procesos: {e}")

def reiniciar_servicio():
    """Reiniciar el servicio de Maruz"""
    print("🔄 Reiniciando servicio Maruz...")
    
    # Cambiar al directorio del proyecto
    os.chdir("/var/www/maruz")
    
    # Activar entorno virtual
    activate_script = "source venv/bin/activate"
    
    # Comando de reinicio
    cmd = f"""
    {activate_script} && 
    python3 -c "
from app.maruz_distribuciones.app import create_app
app = create_app()
app.run(host='0.0.0.0', port=8002, debug=False)
"
    """
    
    try:
        # Ejecutar en background
        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        print("✅ Servicio iniciado en background")
        print(f"📋 PID del proceso: {process.pid}")
        
        # Esperar un momento para que se inicie
        time.sleep(3)
        
        # Verificar que esté funcionando
        try:
            result = subprocess.run(["curl", "-s", "http://127.0.0.1:8002/productos"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Servicio respondiendo correctamente")
                print("🌐 URL: http://34.57.121.200:8002/productos")
            else:
                print("⚠️  Servicio iniciado pero no responde")
        except Exception as e:
            print(f"⚠️  No se pudo verificar respuesta: {e}")
            
    except Exception as e:
        print(f"❌ Error iniciando servicio: {e}")

def mostrar_estado():
    """Mostrar estado actual del servicio"""
    print("\n📊 Estado del Servicio:")
    print("=" * 50)
    
    try:
        # Verificar puerto
        result = subprocess.run(["lsof", "-i", ":8002"], capture_output=True, text=True)
        if result.stdout.strip():
            print("🟢 Puerto 8002: OCUPADO")
            print(result.stdout.strip())
        else:
            print("🔴 Puerto 8002: LIBRE")
    except Exception as e:
        print(f"❌ Error verificando puerto: {e}")
    
    try:
        # Verificar respuesta del servicio
        result = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                               "http://127.0.0.1:8002/productos"], 
                              capture_output=True, text=True, timeout=5)
        if result.stdout.strip() == "200":
            print("🟢 Servicio: RESPONDIENDO (HTTP 200)")
        else:
            print(f"🟡 Servicio: Estado HTTP {result.stdout.strip()}")
    except Exception as e:
        print(f"🔴 Servicio: NO RESPONDE")

def main():
    """Función principal"""
    print("🚀 REINICIADOR COMPLETO MARUZ DISTRIBUCIONES")
    print("=" * 60)
    print(f"📁 Directorio: {os.getcwd()}")
    print(f"⏰ Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar que estemos en el directorio correcto
    if not os.path.exists("app/maruz_distribuciones"):
        print("❌ Error: No estás en el directorio correcto de Maruz")
        print("   Ejecuta desde: /var/www/maruz")
        sys.exit(1)
    
    # Mostrar estado actual
    mostrar_estado()
    print()
    
    # Confirmar acción
    respuesta = input("¿Continuar con el reinicio? (s/N): ").strip().lower()
    if respuesta not in ['s', 'si', 'y', 'yes']:
        print("❌ Reinicio cancelado")
        sys.exit(0)
    
    print()
    
    # Ejecutar reinicio
    limpiar_cache()
    print()
    
    matar_proceso_puerto(8002)
    print()
    
    time.sleep(2)  # Esperar a que se libere el puerto
    
    reiniciar_servicio()
    print()
    
    # Mostrar estado final
    time.sleep(2)
    mostrar_estado()
    
    print("\n🎉 Reinicio completado!")
    print("💡 Para ver cambios: Ctrl+F5 o limpiar caché del navegador")

if __name__ == "__main__":
    main()
