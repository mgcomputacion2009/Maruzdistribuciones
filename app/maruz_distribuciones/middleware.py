from functools import wraps
from flask import request, session, redirect, url_for

def no_cache_middleware():
    """Middleware para prevenir cache en páginas autenticadas"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Ejecutar la función original
            result = f(*args, **kwargs)
            
            # Si es una respuesta HTTP, agregar headers anti-cache
            if hasattr(result, 'headers'):
                result.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
                result.headers['Pragma'] = 'no-cache'
                result.headers['Expires'] = '0'
                result.headers['X-Content-Type-Options'] = 'nosniff'
                result.headers['X-Frame-Options'] = 'DENY'
                result.headers['X-XSS-Protection'] = '1; mode=block'
            
            return result
        return decorated_function
    return decorator

def require_fresh_session():
    """Decorador para requerir sesión fresca (sin cache)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si hay usuario en sesión
            if 'user' not in session:
                return redirect(url_for('oauth_views.login'))
            
            # Agregar timestamp de última actividad
            if 'last_activity' not in session:
                session['last_activity'] = None
            
            # Verificar si la sesión es muy antigua (más de 24 horas)
            from datetime import datetime, timedelta
            if session.get('last_activity'):
                last_activity = datetime.fromisoformat(session['last_activity'])
                if datetime.now() - last_activity > timedelta(hours=24):
                    # Sesión expirada, limpiar y redirigir
                    session.clear()
                    return redirect(url_for('oauth_views.login'))
            
            # Actualizar timestamp de actividad
            session['last_activity'] = datetime.now().isoformat()
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
