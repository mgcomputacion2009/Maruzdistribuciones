# 📱 BITÁCORA - APLICACIÓN FLASK

## 🎯 PROPÓSITO
Registro de todos los cambios en la lógica de aplicación Flask

## 📊 ESTADO ACTUAL

### Archivos Existentes
1. **__init__.py** (12 líneas)
   - App Flask básica
   - Template folder: "../paginas"
   - Static folder: "../public"
   - Blueprint registrado

2. **rutas.py** (12 líneas)
   - Blueprint "main"
   - Ruta "/" → base.html
   - Ruta "/login" → login.html

### Configuración Actual
```python
# __init__.py
app = Flask(
    __name__,
    template_folder="../paginas",
    static_folder="../public"
)
```

## 🚧 CAMBIOS PLANIFICADOS

### MIGRACIÓN A ESTRUCTURA MULTI-EMPRESA
1. **Crear app/maruz_distributions_corp/**
   - Migrar código existente aquí
   - Mantener funcionalidad exacta

2. **Crear app/maruz_distribuciones/**
   - Nueva instancia para desarrollo
   - Puerto 8002

3. **Crear app/core/**
   - Código compartido entre empresas
   - Modelos de base de datos
   - Utilidades comunes

## 📝 REGISTRO DE CAMBIOS

### Pendiente - Migración Inicial
**Archivos a Mover**:
- `app/__init__.py` → `app/maruz_distributions_corp/__init__.py`
- `app/rutas.py` → `app/maruz_distributions_corp/routes.py`

**Cambios Necesarios**:
- Actualizar paths de templates y static
- Adaptar configuración Flask
- Mantener compatibilidad con producción

## ⚠️ PRECAUCIONES
- NO modificar archivos originales hasta migración completa
- Hacer backup antes de cambios
- Validar funcionamiento después de cada cambio

---
**Última Actualización**: $(date)
**Estado**: Sin modificaciones
