# 🖼️ MODELO PRODUCTO IMAGEN - MARUZ DISTRIBUCIONES
# Modelo SQLAlchemy para la tabla producto_imagenes

from datetime import datetime

# Importar la instancia de db desde app.py
from app.maruz_distribuciones.app import db

class ProductoImagen(db.Model):
    __tablename__ = 'producto_imagenes'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id', ondelete='CASCADE'), nullable=False)
    numero_imagen = db.Column(db.Integer, nullable=False)  # 1, 2, 3
    
    # Campos de Drive
    drive_id = db.Column(db.String(100))
    
    # URLs locales de las diferentes versiones
    url_original = db.Column(db.String(500))
    url_thumbnail = db.Column(db.String(500))
    url_web = db.Column(db.String(500))
    url_mobile = db.Column(db.String(500))
    
    # Metadatos
    tamanio_bytes = db.Column(db.Integer)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProductoImagen(producto_id={self.producto_id}, numero={self.numero_imagen})>"
    
    def to_dict(self):
        """Convertir modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'numero_imagen': self.numero_imagen,
            'drive_id': self.drive_id,
            'url_original': self.url_original,
            'url_thumbnail': self.url_thumbnail,
            'url_web': self.url_web,
            'url_mobile': self.url_mobile,
            'tamanio_bytes': self.tamanio_bytes,
            'fecha_subida': self.fecha_subida.isoformat() if self.fecha_subida else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    @classmethod
    def from_appsheet_data(cls, producto_id, numero_imagen, drive_url=None):
        """Crear instancia desde datos de AppSheet"""
        return cls(
            producto_id=producto_id,
            numero_imagen=numero_imagen,
            drive_id=drive_url
        )
