from flask import Flask

# Configuración específica para Maruz Distributions Corp (Producción)
def create_app():
    app = Flask(
        __name__,
        template_folder="templates",  # Nuevo path relativo
        static_folder="static"        # Nuevo path relativo
    )
    
    # Configuración específica de la empresa
    app.config['COMPANY_NAME'] = 'Maruz Distributions Corp'
    app.config['ENVIRONMENT'] = 'production'
    app.config['DEBUG'] = False
    
    # Registrar el blueprint DESPUÉS de crear la app
    from app.maruz_distributions_corp.routes import bp
    app.register_blueprint(bp)
    
    return app
