# 📄 MODELO PRODUCTO DOCUMENTO - MARUZ DISTRIBUCIONES
# Modelo SQLAlchemy para la tabla producto_documentos

import enum
from datetime import datetime

# Importar la instancia de db desde app.py
from app.maruz_distribuciones.app import db

class TipoDocumento(enum.Enum):
    metadata = "metadata"
    pdf = "pdf"
    pr = "pr"

class ProductoDocumento(db.Model):
    __tablename__ = 'producto_documentos'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id', ondelete='CASCADE'), nullable=False)
    tipo_documento = db.Column(db.Enum(TipoDocumento), nullable=False)
    
    # Campos de archivo
    url_local = db.Column(db.String(500))
    drive_id = db.Column(db.String(100))
    nombre_archivo = db.Column(db.String(255))
    
    # Metadatos
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProductoDocumento(producto_id={self.producto_id}, tipo={self.tipo_documento.value})>"
    
    def to_dict(self):
        """Convertir modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'tipo_documento': self.tipo_documento.value,
            'url_local': self.url_local,
            'drive_id': self.drive_id,
            'nombre_archivo': self.nombre_archivo,
            'fecha_subida': self.fecha_subida.isoformat() if self.fecha_subida else None
        }
    
    @classmethod
    def from_appsheet_data(cls, producto_id, tipo_documento, drive_url=None, nombre_archivo=None):
        """Crear instancia desde datos de AppSheet"""
        return cls(
            producto_id=producto_id,
            tipo_documento=tipo_documento,
            drive_id=drive_url,
            nombre_archivo=nombre_archivo
        )
