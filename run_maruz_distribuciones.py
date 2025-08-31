#!/usr/bin/env python3
"""
Script de ejecución para Maruz Distribuciones (Desarrollo)
Nueva instancia en puerto 8002
"""

from app.maruz_distribuciones.app import create_app

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    print("🚀 Iniciando Maruz Distribuciones")
    print("📍 URL: http://localhost:8002 (Desarrollo)")
    print("🏢 Empresa: Maruz Distribuciones")
    print("🔧 Modo: Desarrollo con DEBUG activado")
    print("🌐 Acceso:")
    print("   - Home: http://localhost:8002/")
    print("   - Login: http://localhost:8002/login")
    print("   - Dashboard: http://localhost:8002/dashboard")
    print("   - Productos: http://localhost:8002/productos")
    print("📋 Bitácora: Ver DEVELOPMENT_LOG_MASTER.md")
    print("")
    print("🔒 Producción sigue funcionando en puerto 5000")
    
    app.run(
        host='0.0.0.0',  # Escuchar en todas las interfaces
        port=8002,
        debug=True  # Desarrollo
    )
