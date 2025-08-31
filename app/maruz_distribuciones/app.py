import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.maruz_distribuciones.config import config
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

# Instancia global de SQLAlchemy
db = SQLAlchemy()

# Instancia global de OAuth
oauth = OAuth()

# Configuración específica para Maruz Distribuciones (Desarrollo)
def create_app():
    # Cargar variables de entorno
    load_dotenv()
    
    app = Flask(
        __name__,
        template_folder="templates",  # Path relativo
        static_folder="static"        # Path relativo
    )
    
    # Configurar secret key para sesiones
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
    
    # Cargar configuración
    app.config.from_object(config['development'])
    
    # Inicializar OAuth
    oauth.init_app(app)
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        client_kwargs={"scope": "openid email profile"},
    )
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Registrar blueprints de OAuth PRIMERO (para que tengan prioridad)
    from app.routes.auth import bp as oauth_auth_bp
    app.register_blueprint(oauth_auth_bp)
    
    from app.routes.views import bp as oauth_views_bp
    app.register_blueprint(oauth_views_bp)
    
    # Registrar blueprints existentes DESPUÉS
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
    app.register_blueprint(auth_bp, name='google_auth')
    
    # Registrar el blueprint de autenticación local (email/contraseña)
    from app.maruz_distribuciones.api.auth_local import auth_local_bp
    app.register_blueprint(auth_local_bp, name='local_auth')
    
    # Crear tablas de base de datos si no existen
    with app.app_context():
        try:
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
        except Exception as e:
            print(f"⚠️ Error inicializando base de datos: {e}")
    
    return app
