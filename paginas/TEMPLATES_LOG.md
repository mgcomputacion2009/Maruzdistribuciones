# 📄 BITÁCORA - TEMPLATES HTML

## 🎯 PROPÓSITO
Registro de todos los cambios en plantillas HTML

## 📊 ESTADO ACTUAL

### Archivos Existentes
1. **login.html** (95 líneas)
   - Template completo y funcional
   - Diseño moderno tipo Google/GitHub
   - Branding: "Maruz Distributions Corp"
   - Formulario email/password
   - Botones sociales (Google, Apple, Facebook)
   - Modal "Under Development"
   - JavaScript integrado

2. **base.html** (11 líneas)
   - Template base simple
   - Solo para página home básica
   - Título: "Tienda Maruz"

### Características del Login
```html
<!-- Elementos importantes preservar -->
- Logo: maruz-logo.png
- Título: "Welcome back"
- Formulario: email + password
- Botones sociales funcionales
- Modal de desarrollo
```

## 🚧 CAMBIOS PLANIFICADOS

### MIGRACIÓN A ESTRUCTURA MULTI-EMPRESA
1. **Mover a maruz_distributions_corp/templates/**
   - Mantener login.html exactamente igual
   - Adaptar base.html si es necesario

2. **Crear templates para maruz_distribuciones/**
   - Nuevo login.html para segunda empresa
   - Cambiar branding y colores
   - Mantener funcionalidad

## 📝 REGISTRO DE CAMBIOS

### Pendiente - Migración Inicial
**Archivos a Mover**:
- `paginas/login.html` → `app/maruz_distributions_corp/templates/login.html`
- `paginas/base.html` → `app/maruz_distributions_corp/templates/base.html`

**Elementos Críticos a Preservar**:
- Estructura HTML completa
- Clases CSS (login-container, form-input, etc.)
- IDs JavaScript (loginForm, developmentModal, etc.)
- Referencias a assets estáticos

## ⚠️ PRECAUCIONES
- NO modificar estructura HTML hasta migración completa
- Mantener todas las clases CSS existentes
- Preservar IDs para JavaScript
- Validar rutas de assets después de mover

---
**Última Actualización**: $(date)
**Estado**: Sin modificaciones
