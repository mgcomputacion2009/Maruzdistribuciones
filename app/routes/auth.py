import os
from flask import Blueprint, redirect, url_for, session, flash, current_app, request, jsonify
from authlib.integrations.flask_client import OAuth

bp = Blueprint("oauth_auth", __name__)

@bp.route("/login/google")
def login_google():
    redirect_uri = os.getenv("OAUTH_REDIRECT_URI") or url_for("oauth_auth.auth_callback_google", _external=True)
    # Usar la instancia OAuth desde la aplicación principal
    from app.maruz_distribuciones.app import oauth
    return oauth.google.authorize_redirect(redirect_uri)

@bp.route("/auth/callback/google")
def auth_callback_google():
    try:
        # Usar la instancia OAuth desde la aplicación principal
        from app.maruz_distribuciones.app import oauth
        token = oauth.google.authorize_access_token()
        userinfo = token.get("userinfo")
        if not userinfo:
            userinfo = oauth.google.parse_id_token(token)
        
        # Verificar si el usuario ya existe en la base de datos
        from app.maruz_distribuciones.models.usuario import Usuario
        from app.maruz_distribuciones.app import db
        
        usuario_existente = Usuario.query.filter_by(google_id=userinfo.get("sub")).first()
        
        if usuario_existente:
            # Usuario existe, crear sesión y redirigir al dashboard
            session["user"] = {
                "sub": userinfo.get("sub"),
                "email": userinfo.get("email"),
                "name": f"{usuario_existente.nombre} {usuario_existente.apellido}",
                "picture": userinfo.get("picture"),
                "id": usuario_existente.id,
                "rol": usuario_existente.rol,
                "telefono": usuario_existente.telefono,
                "whatsapp": usuario_existente.whatsapp
            }
            
            flash("Login exitoso con Google", "success")
            return redirect(url_for("oauth_views.home"))  # Redirigir a la página de inicio
        else:
            # Usuario nuevo, crear sesión temporal y redirigir a completar perfil
            session["user"] = {
                "sub": userinfo.get("sub"),
                "email": userinfo.get("email"),
                "name": userinfo.get("name", ""),
                "picture": userinfo.get("picture")
            }
            
            flash("Primera vez aquí. Completa tu perfil para continuar.", "info")
            return redirect(url_for("oauth_views.complete_profile"))
        
    except Exception as e:
        flash(f"Error en login con Google: {e}", "error")
        return redirect(url_for("oauth_views.login"))

@bp.route("/logout")
def logout():
    try:
        print("🔒 Proceso de logout iniciado")
        
        # Limpiar completamente la sesión
        session.clear()
        
        # Crear respuesta de redirección
        response = redirect(url_for("oauth_views.login"))
        
        # Agregar headers para prevenir cache
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        print("✅ Sesión y cache limpiados completamente")
        flash("Sesión cerrada exitosamente. Debes iniciar sesión nuevamente.", "info")
        
        return response
        
    except Exception as e:
        print(f"❌ Error en logout: {str(e)}")
        # Aún así, limpiar la sesión
        session.clear()
        return redirect(url_for("oauth_views.login"))

@bp.route("/api/auth/complete-profile", methods=["POST"])
def complete_profile():
    try:
        print("🔍 API complete-profile llamada")
        data = request.get_json()
        print(f"📊 Datos recibidos: {data}")
        
        # Verificar que el usuario esté en sesión
        if 'user' not in session:
            print("❌ No hay usuario en sesión")
            return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
        
        print(f"✅ Usuario en sesión: {session['user']}")
        
        # Verificar datos requeridos
        required_fields = ['nombre', 'apellido', 'telefono', 'whatsapp', 'password']
        for field in required_fields:
            if not data.get(field):
                print(f"❌ Campo faltante: {field}")
                return jsonify({'success': False, 'error': f'Campo {field} es requerido'}), 400
        
        # Verificar longitud de contraseña
        if len(data['password']) < 6:
            print("❌ Contraseña muy corta")
            return jsonify({'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
        # Crear usuario en la base de datos
        from app.maruz_distribuciones.models.usuario import Usuario
        from app.maruz_distribuciones.app import db
        from werkzeug.security import generate_password_hash
        
        nuevo_usuario = Usuario(
            email=data['email'],
            google_id=data['google_id'],
            nombre=data['nombre'],
            apellido=data['apellido'],
            telefono=data['telefono'],
            whatsapp=data['whatsapp'],
            rol='cliente',  # Siempre cliente por defecto
            password_hash=generate_password_hash(data['password']),
            activo=True
        )
        
        print(f"👤 Creando usuario: {nuevo_usuario.email}")
        db.session.add(nuevo_usuario)
        db.session.commit()
        print("✅ Usuario creado en base de datos")
        
        # Actualizar sesión con datos completos
        session['user'].update({
            'id': nuevo_usuario.id,
            'name': f"{data['nombre']} {data['apellido']}",
            'telefono': data['telefono'],
            'whatsapp': data['whatsapp'],
            'rol': 'cliente'
        })
        
        print("✅ Sesión actualizada")
        return jsonify({
            'success': True, 
            'message': 'Perfil completado exitosamente',
            'redirect_url': '/'  # Redirigir a la página de inicio
        })
        
    except Exception as e:
        print(f"❌ Error en complete-profile: {str(e)}")
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route("/api/auth/login", methods=["POST"])
def login_manual():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email y contraseña son requeridos'}), 400
        
        # Verificar si hay demasiados intentos fallidos
        failed_attempts_key = f"failed_attempts_{email}"
        if failed_attempts_key in session:
            failed_attempts = session[failed_attempts_key]
            if failed_attempts >= 5:
                # Bloquear por 15 minutos
                block_until_key = f"block_until_{email}"
                if block_until_key in session:
                    block_until = session[block_until_key]
                    from datetime import datetime
                    if datetime.now().isoformat() < block_until:
                        remaining_time = int((datetime.fromisoformat(block_until) - datetime.now()).total_seconds() / 60)
                        return jsonify({
                            'success': False, 
                            'error': f'Demasiados intentos fallidos. Intenta nuevamente en {remaining_time} minutos.'
                        }), 429
                    else:
                        # Desbloquear después del tiempo
                        session.pop(failed_attempts_key, None)
                        session.pop(block_until_key, None)
        
        # Buscar usuario por email
        from app.maruz_distribuciones.models.usuario import Usuario
        from werkzeug.security import check_password_hash
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario or not usuario.activo:
            return jsonify({'success': False, 'error': 'Usuario no encontrado o inactivo'}), 401
        
        if not check_password_hash(usuario.password_hash, password):
            # Incrementar intentos fallidos
            current_failed = session.get(failed_attempts_key, 0) + 1
            session[failed_attempts_key] = current_failed
            
            if current_failed >= 5:
                # Bloquear por 15 minutos
                from datetime import datetime, timedelta
                block_until = (datetime.now() + timedelta(minutes=15)).isoformat()
                session[f"block_until_{email}"] = block_until
                
                return jsonify({
                    'success': False, 
                    'error': 'Demasiados intentos fallidos. Tu cuenta ha sido bloqueada por 15 minutos.'
                }), 429
            
            return jsonify({
                'success': False, 
                'error': f'Contraseña incorrecta. Intentos restantes: {5 - current_failed}'
            }), 401
        
        # Login exitoso - limpiar intentos fallidos
        session.pop(failed_attempts_key, None)
        session.pop(f"block_until_{email}", None)
        
        # Crear sesión
        session["user"] = {
            "sub": usuario.google_id or f"local_{usuario.id}",
            "email": usuario.email,
            "name": f"{usuario.nombre} {usuario.rol}",
            "picture": None,
            "id": usuario.id,
            "rol": usuario.rol,
            "telefono": usuario.telefono,
            "whatsapp": usuario.whatsapp
        }
        
        print(f"✅ Login manual exitoso para: {email}")
        return jsonify({'success': True, 'message': 'Login exitoso'})
        
    except Exception as e:
        print(f"❌ Error en login manual: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route("/api/auth/check-block-status", methods=["POST"])
def check_block_status():
    """Verificar si un email está bloqueado"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email requerido'}), 400
        
        failed_attempts_key = f"failed_attempts_{email}"
        block_until_key = f"block_until_{email}"
        
        failed_attempts = session.get(failed_attempts_key, 0)
        block_until = session.get(block_until_key)
        
        if block_until:
            from datetime import datetime
            if datetime.now().isoformat() < block_until:
                remaining_time = int((datetime.fromisoformat(block_until) - datetime.now()).total_seconds() / 60)
                return jsonify({
                    'success': True,
                    'blocked': True,
                    'remaining_minutes': remaining_time,
                    'failed_attempts': failed_attempts
                })
            else:
                # Desbloquear automáticamente
                session.pop(failed_attempts_key, None)
                session.pop(block_until_key, None)
                return jsonify({
                    'success': True,
                    'blocked': False,
                    'failed_attempts': 0
                })
        
        return jsonify({
            'success': True,
            'blocked': False,
            'failed_attempts': failed_attempts
        })
        
    except Exception as e:
        print(f"❌ Error verificando estado de bloqueo: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
