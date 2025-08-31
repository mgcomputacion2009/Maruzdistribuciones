# Configuración específica para Maruz Distribuciones (Desarrollo)

# Información de la empresa
COMPANY_NAME = "Maruz Distribuciones"
COMPANY_CODE = "maruz_distribuciones"
COMPANY_THEME = "green"

# Configuración de la aplicación
DEBUG = True
ENVIRONMENT = "development"
PORT = 8002

# Base de datos (compartida)
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'maruz_shared_db',
    'user': 'maruz_user',
    'password': 'maruz_password'
}

# Configuración de assets
STATIC_FOLDER = "app/maruz_distribuciones/static"
TEMPLATE_FOLDER = "app/maruz_distribuciones/templates"

# Configuración de branding
LOGO_PATH = "images/maruz-logo-distribuciones.png"
PRIMARY_COLOR = "#28a745"
SECONDARY_COLOR = "#20c997"

# Features específicas de esta empresa
FEATURES = [
    "login",
    "dashboard",
    "productos",
    "inventario",
    "reportes"
]

# Configuración de desarrollo
DEVELOPMENT_MODE = True
HOT_RELOAD = True
VERBOSE_LOGGING = True
