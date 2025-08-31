# Configuración específica para Maruz Distributions Corp (Producción)

# Información de la empresa
COMPANY_NAME = "Maruz Distributions Corp"
COMPANY_CODE = "maruz_corp"
COMPANY_THEME = "blue"

# Configuración de la aplicación
DEBUG = False
ENVIRONMENT = "production"
PORT = 5000

# Base de datos (compartida)
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'maruz_shared_db',
    'user': 'maruz_user',
    'password': 'maruz_password'
}

# Configuración de assets
STATIC_FOLDER = "app/maruz_distributions_corp/static"
TEMPLATE_FOLDER = "app/maruz_distributions_corp/templates"

# Configuración de branding
LOGO_PATH = "images/maruz-logo.png"
PRIMARY_COLOR = "#4285f4"
SECONDARY_COLOR = "#031c88"

# Features específicas de esta empresa
FEATURES = [
    "login",
    "dashboard",
    "products",
    "users"
]
