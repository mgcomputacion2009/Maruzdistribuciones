# 🔐 AUTENTICACIÓN CON GOOGLE - MARUZ DISTRIBUCIONES
# Endpoint para manejar la autenticación OAuth de Google

from flask import Blueprint, request, jsonify, current_app
import jwt
import json
import logging
from datetime import datetime, timedelta
import requests
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Configuración de Google OAuth (desde variables de entorno)
# Asegúrate de definir GOOGLE_CLIENT_ID en /var/www/maruz/.env
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
JWT_SECRET = 'maruz_jwt_secret_2024'  # Cambiar por una clave secreta real

def verify_google_token(credential):
    """
    Verificar el token de Google usando la API pública de Google
    """
    try:
        # URL de verificación de Google
        google_verify_url = 'https://oauth2.googleapis.com/tokeninfo'
        
        # Verificar el token con Google
        response = requests.get(google_verify_url, params={'id_token': credential})
        
        if response.status_code == 200:
            token_info = response.json()
            
            # Verificar que el token es para nuestra aplicación
            if token_info.get('aud') == GOOGLE_CLIENT_ID:
                return {
                    'success': True,
                    'user_info': {
                        'email': token_info.get('email'),
                        'name': token_info.get('name'),
                        'picture': token_info.get('picture'),
                        'sub': token_info.get('sub')  # Google User ID
                    }
                }
            else:
                logger.warning(f"Token de Google con aud incorrecto: {token_info.get('aud')}")
                return {'success': False, 'error': 'Token de Google inválido'}
        else:
            logger.error(f"Error verificando token con Google: {response.status_code}")
            return {'success': False, 'error': 'Error verificando token con Google'}
            
    except Exception as e:
        logger.error(f"Error en verificación de Google: {e}")
        return {'success': False, 'error': 'Error interno en verificación'}

def create_jwt_token(user_info):
    """
    Crear un token JWT para el usuario autenticado
    """
    try:
        payload = {
            'user_id': user_info['sub'],
            'email': user_info['email'],
            'name': user_info['name'],
            'exp': datetime.utcnow() + timedelta(hours=24),  # Token válido por 24 horas
            'iat': datetime.utcnow(),
            'iss': 'maruz_distribuciones'
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        return token
        
    except Exception as e:
        logger.error(f"Error creando JWT: {e}")
        return None

@auth_bp.route('/google', methods=['POST'])
def google_auth():
    """
    Endpoint principal para autenticación con Google
    """
    try:
        # Verificar que se recibieron datos JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        data = request.get_json()
        
        # Verificar campos obligatorios
        if 'credential' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo "credential" es obligatorio'
            }), 400
        
        credential = data['credential']
        user_info = data.get('user_info', {})
        
        logger.info(f"🔐 Intentando autenticación con Google para: {user_info.get('email', 'N/A')}")
        
        # Verificar el token de Google
        verification_result = verify_google_token(credential)
        
        if not verification_result['success']:
            return jsonify({
                'success': False,
                'error': verification_result['error']
            }), 401
        
        # Usar la información verificada de Google
        verified_user_info = verification_result['user_info']
        
        # Crear token JWT
        jwt_token = create_jwt_token(verified_user_info)
        
        if not jwt_token:
            return jsonify({
                'success': False,
                'error': 'Error creando token de sesión'
            }), 500
        
        # Preparar respuesta exitosa
        response_data = {
            'success': True,
            'message': 'Autenticación exitosa',
            'token': jwt_token,
            'user': {
                'email': verified_user_info['email'],
                'name': verified_user_info['name'],
                'picture': verified_user_info.get('picture'),
                'google_id': verified_user_info['sub']
            },
            'expires_in': 86400,  # 24 horas en segundos
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Autenticación exitosa para: {verified_user_info['email']}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"❌ Error en autenticación con Google: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """
    Endpoint para verificar la validez de un token JWT
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Campo "token" es obligatorio'
            }), 400
        
        # Verificar el token JWT
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            
            # Verificar que el token no haya expirado
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                return jsonify({
                    'success': False,
                    'error': 'Token expirado'
                }), 401
            
            return jsonify({
                'success': True,
                'valid': True,
                'user': {
                    'user_id': payload['user_id'],
                    'email': payload['email'],
                    'name': payload['name']
                }
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'Token expirado'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': 'Token inválido'
            }), 401
            
    except Exception as e:
        logger.error(f"❌ Error verificando token: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Endpoint para cerrar sesión (el token se invalida en el cliente)
    """
    try:
        return jsonify({
            'success': True,
            'message': 'Sesión cerrada exitosamente',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error en logout: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
