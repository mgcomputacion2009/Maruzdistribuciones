# ⚙️ BITÁCORA - CONFIGURACIONES

## 🎯 PROPÓSITO
Registro de todos los cambios en configuraciones de servidor, deployment y scripts

## 📊 ESTADO ACTUAL

### Archivos de Configuración Existentes

#### 1. nginx-maruz.conf (54 líneas)
```nginx
server {
    listen 80;
    server_name localhost;
    root /var/www/maruz;
    
    # Proxy hacia Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        # Headers y configuración proxy
    }
    
    # Assets estáticos
    location /static { alias /var/www/maruz/static; }
    location /public { alias /var/www/maruz/public; }
}
```

#### 2. run.py (4 líneas)
```python
from app import app
if __name__ == '__main__':
    app.run(debug=True)
```

#### 3. requirements.txt (4 líneas)
```
Flask==2.3.3
gunicorn==21.2.0
Werkzeug==2.3.7
```

#### 4. Otros Archivos de Deployment
- gunicorn_config.py (22 líneas)
- maruz.service (22 líneas)
- setup_deployment.sh (108 líneas)
- manage.sh (57 líneas)
- wsgi.py (7 líneas)

## 🚧 CAMBIOS PLANIFICADOS

### CONFIGURACIÓN MULTI-EMPRESA

#### Nueva Estructura de Scripts
1. **run_maruz_distributions_corp.py**
   - Puerto estándar (producción)
   - Configuración actual

2. **run_maruz_distribuciones.py**
   - Puerto 8002 (desarrollo)
   - Debug mode activado

#### Nueva Configuración Nginx
1. **Virtual Hosts Separados**
   - app.maruzdistributionscorp.com → Puerto 5000
   - localhost:8002 → Puerto 8002 (desarrollo)

2. **Assets Estáticos Actualizados**
   - Rutas adaptadas a nueva estructura
   - Separación por empresa

### Configuración de Puertos
- **Producción (Maruz Distributions Corp)**: Puerto 5000
- **Desarrollo (Maruz Distribuciones)**: Puerto 8002

## 📝 REGISTRO DE CAMBIOS

### 2025-08-23 - Apache movido a 8080 y phpMyAdmin habilitado
**Acciones**:
- Apache: `Listen 8080` en `/etc/apache2/ports.conf` (antes 80)
- VirtualHost por defecto cambiado a `*:8080` en `/etc/apache2/sites-available/000-default.conf`
- Se creó y habilitó `/etc/apache2/conf-available/phpmyadmin.conf` con `Alias /phpmyadmin /usr/share/phpmyadmin`
- Apache reiniciado y validado respondiendo en `http://127.0.0.1:8080` y `.../phpmyadmin/`

**Motivo**:
- Evitar conflicto con Nginx que escucha en 80 (proxy a 5000)

**Estado**:
- Nginx: sin cambios, continúa en 80 → 5000
- Apache: funcionando en 8080
- UFW: inactivo (sin reglas necesarias)

### 2025-08-23 - Usuario MySQL y archivo .env
**Usuario**: `miguel@localhost` con permisos en `maruz_db.*`
**Archivo**: `/var/www/maruz/.env` (perm 600)
**Variables**: `FLASK_ENV, API_DOMAIN, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD`

## 🌐 URLs Y DIRECCIONES ACTUALES

### Servicios Web
- **Maruz Distributions Corp (Producción)**: `http://34.57.121.200:5000` (Nginx proxy)
- **Maruz Distribuciones (Desarrollo)**: `http://34.57.121.200:8002` (Flask directo)
- **phpMyAdmin**: `http://34.57.121.200:8080/phpmyadmin/` (Apache)
- **Apache Default**: `http://34.57.121.200:8080` (página por defecto)

### Puertos Activos
- **Puerto 80**: Nginx (proxy a 5000)
- **Puerto 5000**: Maruz Distributions Corp (producción)
- **Puerto 8002**: Maruz Distribuciones (desarrollo)
- **Puerto 8080**: Apache + phpMyAdmin

### Base de Datos
- **Host**: 127.0.0.1:3306
- **Base**: maruz_db
- **Usuario**: miguel (localhost)
- **Acceso**: Solo desde servidor local

---
### Pendiente - Configuración Multi-Puerto

#### Archivos a Crear
1. **config/maruz_distributions_corp.py**
   ```python
   # Configuración producción
   DEBUG = False
   PORT = 5000
   COMPANY_NAME = "Maruz Distributions Corp"
   ```

2. **config/maruz_distribuciones.py**
   ```python
   # Configuración desarrollo
   DEBUG = True
   PORT = 8002
   COMPANY_NAME = "Maruz Distribuciones"
   ```

#### Nginx - Nueva Configuración
- Mantener configuración actual para producción
- Agregar configuración adicional para puerto 8002

## ⚠️ PRECAUCIONES CRÍTICAS

### Configuraciones de Producción
- 🚨 NO modificar nginx-maruz.conf hasta migración completa
- 🚨 NO cambiar puerto 5000 (puede afectar producción)
- 🚨 Mantener gunicorn_config.py sin cambios
- 🚨 Preservar maruz.service para systemd

### Orden de Implementación
1. Crear nueva estructura sin modificar actual
2. Validar funcionamiento en puerto 8002
3. Solo entonces adaptar configuraciones de producción

### Backup de Configuraciones
- Respaldar nginx-maruz.conf antes de cambios
- Mantener run.py original como referencia
- Documentar cada cambio en esta bitácora

## 🔧 CONFIGURACIONES ESPECÍFICAS A PRESERVAR

### Nginx
- Timeout settings (60s)
- Buffer settings (8k)
- Cache headers para assets
- Security settings (deny dotfiles)

### Gunicorn
- Worker processes
- Bind configuration
- Timeout settings

---
**Última Actualización**: $(date)
**Estado**: Sin modificaciones - Configuraciones de producción intactas
