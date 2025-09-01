from app.maruz_distribuciones.app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app.maruz_distribuciones.config import config

class Usuario(db.Model):
    """Modelo de usuario para autenticación"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable para usuarios de Google
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    rol = db.Column(db.String(20), default='cliente')  # cliente, admin, vendedor
    activo = db.Column(db.Boolean, default=True)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'
    
    @property
    def password(self):
        raise AttributeError('password no es un atributo legible')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verificar_password(self, password):
        """Verificar si la contraseña es correcta"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    
    def generar_token(self):
        """Generar token JWT para el usuario"""
        payload = {
            'user_id': self.id,
            'email': self.email,
            'nombre': self.nombre,
            'rol': self.rol,
            'exp': datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.utcnow(),
            'iss': 'maruz_distribuciones'
        }
        
        secret_key = config['development'].SECRET_KEY
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    def actualizar_ultimo_login(self):
        """Actualizar timestamp del último login"""
        self.ultimo_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convertir usuario a diccionario (sin información sensible)"""
        return {
            'id': self.id,
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'telefono': self.telefono,
            'whatsapp': self.whatsapp,
            'avatar_url': self.avatar_url,
            'rol': self.rol,
            'activo': self.activo,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None,
            'fecha_registro': self.fecha_registro.isoformat()
        }
    
    @classmethod
    def buscar_por_email(cls, email):
        """Buscar usuario por email"""
        return cls.query.filter_by(email=email, activo=True).first()
    
    @classmethod
    def buscar_por_google_id(cls, google_id):
        """Buscar usuario por Google ID"""
        return cls.query.filter_by(google_id=google_id, activo=True).first()
    
    @classmethod
    def crear_usuario_google(cls, google_data):
        """Crear usuario desde datos de Google OAuth"""
        usuario = cls(
            email=google_data['email'],
            nombre=google_data.get('name', 'Usuario'),
            google_id=google_data['sub'],
            avatar_url=google_data.get('picture'),
            password_hash=None,  # Usuario de Google no tiene contraseña
            telefono=None,
            whatsapp=None,
            rol='cliente'
        )
        db.session.add(usuario)
        db.session.commit()
        return usuario
