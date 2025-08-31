from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.maruz_distribuciones.config import config

# Instancia global de SQLAlchemy
db = SQLAlchemy()

# Configuración específica para Maruz Distribuciones (Desarrollo)
def create_app():
    app = Flask(
        __name__,
        template_folder="templates",  # Path relativo
        static_folder="static"        # Path relativo
    )
    
    # Cargar configuración
    app.config.from_object(config['development'])
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Registrar blueprints
    from app.maruz_distribuciones.routes import bp
    app.register_blueprint(bp)
    
    # Registrar el blueprint del webhook
    from app.maruz_distribuciones.api import webhook_bp
    app.register_blueprint(webhook_bp)
    
    # Registrar el blueprint de cargar productos (versión simplificada final)
    from app.maruz_distribuciones.api.cargar_productos_simple_final import cargar_bp
    app.register_blueprint(cargar_bp)
    
    # Registrar el blueprint de cargar productos v2 (con campos de precios e inventario)
    from app.maruz_distribuciones.api.cargar_productos_v2 import bp as productos_v2_bp
    app.register_blueprint(productos_v2_bp)
    
    # Registrar el blueprint de autenticación con Google
    from app.maruz_distribuciones.api.auth_google import auth_bp
    app.register_blueprint(auth_bp)
    
    # Registrar el blueprint de autenticación local (email/contraseña)
    from app.maruz_distribuciones.api.auth_local import auth_local_bp
    app.register_blueprint(auth_local_bp)
    
    # Crear tablas de base de datos si no existen
    with app.app_context():
        try:
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
        except Exception as e:
            print(f"⚠️ Error inicializando base de datos: {e}")
    
    return app
