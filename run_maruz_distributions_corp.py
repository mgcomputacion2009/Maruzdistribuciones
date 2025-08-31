#!/usr/bin/env python3
"""
Script de ejecución para Maruz Distributions Corp (Producción)
Migrado desde run.py original
"""

from app.maruz_distributions_corp.app import create_app

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    print("🚀 Iniciando Maruz Distributions Corp")
    print("📍 URL: http://localhost:5000 (Producción)")
    print("🏢 Empresa: Maruz Distributions Corp")
    
    app.run(
        host='0.0.0.0',  # Escuchar en todas las interfaces
        port=5000,
        debug=False  # Producción
    )
