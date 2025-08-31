# ⚙️ CONFIGURACIÓN DE BASE DE DATOS - PROYECTO MARUZ
# Base de datos compartida entre ambas empresas

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuración de conexión MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'maruz_user',
    'password': 'maruz_password_2024',
    'database': 'maruz_db',
    'charset': 'utf8mb4'
}

# URL de conexión SQLAlchemy
DATABASE_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"

# Configuración Flask-SQLAlchemy
class DatabaseConfig:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': False  # Cambiar a True para debug SQL
    }

# Para uso directo con SQLAlchemy
Base = declarative_base()
engine = create_engine(DATABASE_URL, **DatabaseConfig.SQLALCHEMY_ENGINE_OPTIONS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Función helper para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Función para probar la conexión a la base de datos"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            result.fetchone()
        return True, "Conexión exitosa a la base de datos"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"
