# 🔐 CONFIGURACIÓN GOOGLE OAUTH - MARUZ DISTRIBUCIONES
# Configuración para la autenticación con Google

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('/var/www/maruz/.env')

class GoogleOAuthConfig:
    """Configuración para Google OAuth"""
    
    # Google OAuth 2.0
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'demo')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', 'demo_secret')
    
    # URLs de Google OAuth
    GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'
    
    # Scopes solicitados
    GOOGLE_SCOPES = [
        'openid',
        'email',
        'profile'
    ]
    
    # Configuración de JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'maruz_jwt_secret_2024')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # Configuración de sesión
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    @classmethod
    def get_google_auth_url(cls, redirect_uri, state=None):
        """Generar URL de autorización de Google"""
        params = {
            'client_id': cls.GOOGLE_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'scope': ' '.join(cls.GOOGLE_SCOPES),
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        if state:
            params['state'] = state
            
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{cls.GOOGLE_AUTH_URL}?{query_string}"
    
    @classmethod
    def is_configured(cls):
        """Verificar si la configuración está completa"""
        return (
            cls.GOOGLE_CLIENT_ID != 'demo' and 
            cls.GOOGLE_CLIENT_SECRET != 'demo_secret' and
            cls.JWT_SECRET != 'maruz_jwt_secret_2024'
        )
