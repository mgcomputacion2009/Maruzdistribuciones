# 🔒 DECORADORES DE AUTENTICACIÓN - MARUZ DISTRIBUCIONES
# Decoradores para proteger rutas que requieren autenticación

from functools import wraps
from flask import request, jsonify, current_app, g
from app.maruz_distribuciones.models.usuario import Usuario
import jwt

def login_required(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token de autorización requerido'
            }), 401
        
        try:
            # Verificar token
            secret_key = current_app.config.get('SECRET_KEY', 'maruz_jwt_secret_2024')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Buscar usuario
            usuario = Usuario.query.get(payload['user_id'])
            if not usuario or not usuario.activo:
                return jsonify({
                    'success': False,
                    'error': 'Usuario no encontrado o inactivo'
                }), 401
            
            # Guardar usuario en g para uso en la función
            g.current_user = usuario
            
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
            return jsonify({
                'success': False,
                'error': 'Error verificando token'
            }), 500
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorador para rutas que requieren rol de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token de autorización requerido'
            }), 401
        
        try:
            # Verificar token
            secret_key = current_app.config.get('SECRET_KEY', 'maruz_jwt_secret_2024')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Buscar usuario
            usuario = Usuario.query.get(payload['user_id'])
            if not usuario or not usuario.activo:
                return jsonify({
                    'success': False,
                    'error': 'Usuario no encontrado o inactivo'
                }), 401
            
            # Verificar rol de administrador
            if usuario.rol != 'admin':
                return jsonify({
                    'success': False,
                    'error': 'Acceso denegado. Se requiere rol de administrador'
                }), 403
            
            # Guardar usuario en g para uso en la función
            g.current_user = usuario
            
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
            return jsonify({
                'success': False,
                'error': 'Error verificando token'
            }), 500
        
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(allowed_roles):
    """Decorador para rutas que requieren roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Obtener token del header Authorization
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            
            if not token:
                return jsonify({
                    'success': False,
                    'error': 'Token de autorización requerido'
                }), 401
            
            try:
                # Verificar token
                secret_key = current_app.config.get('SECRET_KEY', 'maruz_jwt_secret_2024')
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                
                # Buscar usuario
                usuario = Usuario.query.get(payload['user_id'])
                if not usuario or not usuario.activo:
                    return jsonify({
                        'success': False,
                        'error': 'Usuario no encontrado o inactivo'
                    }), 401
                
                # Verificar rol
                if usuario.rol not in allowed_roles:
                    return jsonify({
                        'success': False,
                        'error': f'Acceso denegado. Se requiere uno de estos roles: {", ".join(allowed_roles)}'
                    }), 403
                
                # Guardar usuario en g para uso en la función
                g.current_user = usuario
                
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
                return jsonify({
                    'success': False,
                    'error': 'Error verificando token'
                }), 500
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def get_current_user():
    """Función helper para obtener el usuario actual desde g"""
    return getattr(g, 'current_user', None)
