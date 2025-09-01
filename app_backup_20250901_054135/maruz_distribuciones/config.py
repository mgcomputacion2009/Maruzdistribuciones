# ⚙️ CONFIGURACIÓN - MARUZ DISTRIBUCIONES
# Configuración para la app de desarrollo

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('/var/www/maruz/.env')

class Config:
    """Configuración base para Maruz Distribuciones"""
    
    # Configuración de la empresa
    COMPANY_NAME = 'Maruz Distribuciones'
    ENVIRONMENT = 'development'
    DEBUG = True
    PORT = 8002
    
    # Configuración de seguridad
    SECRET_KEY = os.getenv('SECRET_KEY', 'maruz_jwt_secret_2024_development_key')
    
    # Configuración de base de datos
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'maruz_db')
    DB_USER = os.getenv('DB_USER', 'miguel')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    # URL de conexión SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': False
    }
    
    # Configuración de almacenamiento
    STORAGE_PATH = '/var/www/maruz/app/maruz_distribuciones/storage'
    PRODUCTOS_STORAGE = f"{STORAGE_PATH}/productos"
    LOGS_STORAGE = f"{STORAGE_PATH}/logs"
    
    # Configuración de logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = f"{LOGS_STORAGE}/app.log"
    
    # Configuración de webhook
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    
    # Configuración de Google Drive (pendiente)
    GOOGLE_DRIVE_CREDENTIALS = os.getenv('GOOGLE_DRIVE_CREDENTIALS', '')
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')

class DevelopmentConfig(Config):
    """Configuración específica para desarrollo"""
    DEBUG = True
    ENVIRONMENT = 'development'

class ProductionConfig(Config):
    """Configuración específica para producción"""
    DEBUG = False
    ENVIRONMENT = 'production'

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Función para conexión directa a MySQL
def get_db_connection():
    """Crear conexión directa a MySQL para operaciones específicas"""
    import mysql.connector
    from mysql.connector import Error
    
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except Error as e:
        raise e
