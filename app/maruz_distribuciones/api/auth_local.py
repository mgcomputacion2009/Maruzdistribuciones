# 🔐 AUTENTICACIÓN LOCAL - MARUZ DISTRIBUCIONES
# Sistema de login tradicional con email/contraseña

from flask import Blueprint, request, jsonify, current_app
from app.maruz_distribuciones.models.usuario import Usuario
from app.maruz_distribuciones.app import db
import jwt
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear Blueprint
auth_local_bp = Blueprint('auth_local', __name__, url_prefix='/api/auth')

def create_jwt_token(usuario):
    """Crear token JWT para usuario autenticado"""
    try:
        payload = {
            'user_id': usuario.id,
            'email': usuario.email,
            'nombre': usuario.nombre,
            'rol': usuario.rol,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow(),
            'iss': 'maruz_distribuciones'
        }
        
        secret_key = current_app.config.get('SECRET_KEY', 'maruz_jwt_secret_2024')
        return jwt.encode(payload, secret_key, algorithm='HS256')
        
    except Exception as e:
        logger.error(f"Error creando JWT: {e}")
        return None

@auth_local_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login con email/contraseña"""
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validaciones básicas
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email y contraseña son obligatorios'
            }), 400
        
        # Buscar usuario
        usuario = Usuario.buscar_por_email(email)
        if not usuario:
            logger.warning(f"Intento de login con email inexistente: {email}")
            return jsonify({
                'success': False,
                'error': 'Credenciales inválidas'
            }), 401
        
        # Verificar contraseña
        if not usuario.verificar_password(password):
            logger.warning(f"Intento de login con contraseña incorrecta para: {email}")
            return jsonify({
                'success': False,
                'error': 'Credenciales inválidas'
            }), 401
        
        # Verificar que el usuario esté activo
        if not usuario.activo:
            return jsonify({
                'success': False,
                'error': 'Cuenta deshabilitada'
            }), 403
        
        # Generar token JWT
        token = create_jwt_token(usuario)
        if not token:
            return jsonify({
                'success': False,
                'error': 'Error generando token de sesión'
            }), 500
        
        # Actualizar último login
        usuario.actualizar_ultimo_login()
        
        # Preparar respuesta
        response_data = {
            'success': True,
            'message': 'Login exitoso',
            'token': token,
            'user': usuario.to_dict(),
            'expires_in': 86400,  # 24 horas
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Login exitoso para: {email}")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"❌ Error en login: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@auth_local_bp.route('/register', methods=['POST'])
def register():
    """Endpoint para registro de nuevos usuarios"""
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        nombre = data.get('nombre', '').strip()
        apellido = data.get('apellido', '').strip()
        
        # Validaciones
        if not email or not password or not nombre:
            return jsonify({
                'success': False,
                'error': 'Email, contraseña y nombre son obligatorios'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'error': 'La contraseña debe tener al menos 6 caracteres'
            }), 400
        
        # Verificar si el email ya existe
        if Usuario.buscar_por_email(email):
            return jsonify({
                'success': False,
                'error': 'El email ya está registrado'
            }), 409
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            email=email,
            nombre=nombre,
            apellido=apellido,
            rol='usuario'  # Rol por defecto
        )
        nuevo_usuario.password = password
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        # Generar token para login automático
        token = create_jwt_token(nuevo_usuario)
        
        response_data = {
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'token': token,
            'user': nuevo_usuario.to_dict(),
            'expires_in': 86400,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Usuario registrado exitosamente: {email}")
        return jsonify(response_data), 201
        
    except Exception as e:
        logger.error(f"❌ Error en registro: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@auth_local_bp.route('/profile', methods=['GET'])
def get_profile():
    """Obtener perfil del usuario autenticado"""
    try:
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Token de autorización requerido'
            }), 401
        
        token = auth_header.split(' ')[1]
        secret_key = current_app.config.get('SECRET_KEY', 'maruz_jwt_secret_2024')
        
        # Verificar token
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
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
        
        # Buscar usuario
        usuario = Usuario.query.get(user_id)
        if not usuario or not usuario.activo:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado o inactivo'
            }), 404
        
        return jsonify({
            'success': True,
            'user': usuario.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo perfil: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@auth_local_bp.route('/change-password', methods=['POST'])
def change_password():
    """Cambiar contraseña del usuario autenticado"""
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        # Verificar token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Token de autorización requerido'
            }), 401
        
        token = auth_header.split(' ')[1]
        secret_key = current_app.config.get('SECRET_KEY', 'maruz_jwt_secret_2024')
        
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
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
        
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'error': 'Contraseña actual y nueva son obligatorias'
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'error': 'La nueva contraseña debe tener al menos 6 caracteres'
            }), 400
        
        # Buscar usuario y verificar contraseña actual
        usuario = Usuario.query.get(user_id)
        if not usuario or not usuario.verificar_password(current_password):
            return jsonify({
                'success': False,
                'error': 'Contraseña actual incorrecta'
            }), 401
        
        # Cambiar contraseña
        usuario.password = new_password
        db.session.commit()
        
        logger.info(f"✅ Contraseña cambiada exitosamente para: {usuario.email}")
        return jsonify({
            'success': True,
            'message': 'Contraseña cambiada exitosamente'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error cambiando contraseña: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
