# 📦 MODELO PRODUCTO - MARUZ DISTRIBUCIONES
# Modelo SQLAlchemy para la tabla productos

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Importar la instancia de db desde app.py
from app.maruz_distribuciones.app import db

class Producto(db.Model):
    __tablename__ = 'productos'
    
    # Campos de identificación
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo_producto = db.Column(db.String(100), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=False)
    
    # Campos de información del producto
    nota = db.Column(db.Text)
    web_url = db.Column(db.String(500))
    categoria = db.Column(db.String(100))
    descripcion_producto = db.Column(db.Text)
    propiedades = db.Column(db.Text)
    datos_tecnicos = db.Column(db.Text)
    especificaciones = db.Column(db.Text)
    campos_aplicacion = db.Column(db.Text)
    envases_disponibles = db.Column(db.Text)
    recomendaciones = db.Column(db.Text)
    
    # Campos de control
    cont = db.Column(db.String(100))
    pr_field = db.Column(db.String(100))
    id_drive = db.Column(db.String(100))
    qr_code = db.Column(db.String(100))
    
    # Campos de sistema
    empresa_id = db.Column(db.Integer, default=2)  # Maruz Distribuciones
    ambiente = db.Column(db.String(20), default='desarrollo')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    imagenes = db.relationship('ProductoImagen', backref='producto', lazy=True, cascade='all, delete-orphan')
    documentos = db.relationship('ProductoDocumento', backref='producto', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Producto(codigo='{self.codigo_producto}', descripcion='{self.descripcion[:50]}...')>"
    
    def to_dict(self):
        """Convertir modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'codigo_producto': self.codigo_producto,
            'descripcion': self.descripcion,
            'nota': self.nota,
            'web_url': self.web_url,
            'categoria': self.categoria,
            'descripcion_producto': self.descripcion_producto,
            'propiedades': self.propiedades,
            'datos_tecnicos': self.datos_tecnicos,
            'especificaciones': self.especificaciones,
            'campos_aplicacion': self.campos_aplicacion,
            'envases_disponibles': self.envases_disponibles,
            'recomendaciones': self.recomendaciones,
            'cont': self.cont,
            'pr_field': self.pr_field,
            'id_drive': self.id_drive,
            'qr_code': self.qr_code,
            'empresa_id': self.empresa_id,
            'ambiente': self.ambiente,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'activo': self.activo
        }
    
    @classmethod
    def from_appsheet_data(cls, data):
        """Crear instancia desde datos de AppSheet"""
        return cls(
            codigo_producto=data.get('codigo'),
            descripcion=data.get('descripcion'),
            nota=data.get('nota'),
            web_url=data.get('web'),
            categoria=data.get('categoria'),
            descripcion_producto=data.get('descripcion_producto'),
            propiedades=data.get('propiedades'),
            datos_tecnicos=data.get('datos_tecnicos'),
            especificaciones=data.get('especificaciones'),
            campos_aplicacion=data.get('campos_aplicacion'),
            envases_disponibles=data.get('envases_disponibles'),
            recomendaciones=data.get('recomendaciones'),
            cont=data.get('cont'),
            pr_field=data.get('pr'),
            id_drive=data.get('id_drive'),
            qr_code=data.get('qrt')
        )
