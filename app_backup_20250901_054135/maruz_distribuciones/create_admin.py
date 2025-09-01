#!/usr/bin/env python3
# 🚀 CREAR USUARIO ADMINISTRADOR - MARUZ DISTRIBUCIONES
# Script para crear el primer usuario administrador del sistema

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, '/var/www/maruz')

from app.maruz_distribuciones.app import create_app, db
from app.maruz_distribuciones.models.usuario import Usuario

def create_admin_user():
    """Crear usuario administrador inicial"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si ya existe un usuario administrador
            admin_exists = Usuario.query.filter_by(rol='admin').first()
            if admin_exists:
                print("⚠️ Ya existe un usuario administrador en el sistema")
                print(f"   Email: {admin_exists.email}")
                print(f"   Nombre: {admin_exists.nombre}")
                return
            
            # Crear usuario administrador
            admin_user = Usuario(
                email='admin@maruz.com',
                nombre='Administrador',
                apellido='Sistema',
                rol='admin',
                activo=True
            )
            admin_user.password = 'admin123'  # Contraseña temporal
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Usuario administrador creado exitosamente")
            print(f"   Email: {admin_user.email}")
            print(f"   Contraseña: admin123")
            print(f"   Rol: {admin_user.rol}")
            print("\n⚠️ IMPORTANTE: Cambia la contraseña después del primer login")
            
        except Exception as e:
            print(f"❌ Error creando usuario administrador: {e}")
            db.session.rollback()

def create_test_users():
    """Crear usuarios de prueba para desarrollo"""
    app = create_app()
    
    with app.app_context():
        try:
            # Usuario vendedor
            vendedor = Usuario(
                email='vendedor@maruz.com',
                nombre='Juan',
                apellido='Vendedor',
                rol='vendedor',
                activo=True
            )
            vendedor.password = 'vendedor123'
            
            # Usuario normal
            usuario = Usuario(
                email='usuario@maruz.com',
                nombre='María',
                apellido='Usuario',
                rol='usuario',
                activo=True
            )
            usuario.password = 'usuario123'
            
            db.session.add(vendedor)
            db.session.add(usuario)
            db.session.commit()
            
            print("✅ Usuarios de prueba creados exitosamente")
            print(f"   Vendedor: {vendedor.email} / vendedor123")
            print(f"   Usuario: {usuario.email} / usuario123")
            
        except Exception as e:
            print(f"❌ Error creando usuarios de prueba: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("🚀 CREANDO USUARIOS INICIALES - MARUZ DISTRIBUCIONES")
    print("=" * 60)
    
    # Crear usuario administrador
    print("\n1️⃣ Creando usuario administrador...")
    create_admin_user()
    
    # Crear usuarios de prueba
    print("\n2️⃣ Creando usuarios de prueba...")
    create_test_users()
    
    print("\n" + "=" * 60)
    print("✅ Proceso completado")
    print("\n📋 CREDENCIALES DE ACCESO:")
    print("   🔐 Admin: admin@maruz.com / admin123")
    print("   👨‍💼 Vendedor: vendedor@maruz.com / vendedor123")
    print("   👤 Usuario: usuario@maruz.com / usuario123")
    print("\n⚠️ RECUERDA: Cambia las contraseñas después del primer login")
