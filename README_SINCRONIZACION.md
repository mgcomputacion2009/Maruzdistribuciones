# 🚀 SISTEMA DE SINCRONIZACIÓN DE PRODUCTOS - MARUZ DISTRIBUCIONES

## 📋 **DESCRIPCIÓN GENERAL**

Sistema completo para importar productos desde AppSheet a través de webhooks, almacenar datos en MySQL y sincronizar imágenes desde Google Drive Desktop al servidor.

## 🏗️ **ARQUITECTURA DEL SISTEMA**

```
AppSheet → Webhook → Base de Datos → Script de Sincronización → Imágenes Locales
    ↓              ↓              ↓              ↓              ↓
  Productos    Procesamiento   MySQL         Python Script   Storage Server
  + Imágenes   + Validación    maruz_db      + Logs         /storage/productos/
```

## 📁 **ESTRUCTURA DE ARCHIVOS**

```
/var/www/maruz/
├── app/maruz_distribuciones/
│   ├── api/webhook_productos.py      # Webhook principal
│   ├── models/                       # Modelos SQLAlchemy
│   ├── storage/                      # Almacenamiento local
│   │   ├── productos/               # Imágenes y documentos
│   │   └── logs/                    # Logs del sistema
│   ├── config.py                     # Configuración centralizada
│   └── app.py                        # Aplicación Flask
├── sincronizar_imagenes.py           # Script de sincronización
├── configurar_sincronizacion.py      # Configurador de rutas
├── ejecutar_sincronizacion.sh        # Script de automatización
├── test_webhook_v2.py                # Pruebas del webhook
└── .env                              # Variables de entorno
```

## 🔧 **INSTALACIÓN Y CONFIGURACIÓN**

### **1. Dependencias del Sistema**

```bash
# Activar entorno virtual
source /var/www/maruz/venv/bin/activate

# Instalar paquetes Python
pip install flask-sqlalchemy python-dotenv mysql-connector-python
```

### **2. Configuración de Base de Datos**

```bash
# Conectar a MySQL
mysql -u miguel -p

# Verificar base de datos
USE maruz_db;
SHOW TABLES;
```

### **3. Configuración de Rutas**

```bash
# Ejecutar configurador
python3 configurar_sincronizacion.py

# Seguir las instrucciones para configurar:
# - Usuario de Windows
# - Ruta de Google Drive Desktop
# - Carpeta de productos
```

## 🚀 **USO DEL SISTEMA**

### **1. Iniciar la Aplicación**

```bash
# Activar entorno virtual
source /var/www/maruz/venv/bin/activate

# Iniciar aplicación Flask
cd /var/www/maruz
python3 -c "from app.maruz_distribuciones.app import create_app; app = create_app(); app.run(host='0.0.0.0', port=8002, debug=False)"
```

### **2. Probar el Webhook**

```bash
# Ejecutar pruebas completas
python3 test_webhook_v2.py

# O probar endpoints individuales
curl http://34.57.121.200:8002/api/webhook/productos/health
```

### **3. Sincronizar Imágenes**

```bash
# Sincronización manual
python3 sincronizar_imagenes.py

# Sincronización automática
./ejecutar_sincronizacion.sh
```

## 📡 **ENDPOINTS DEL WEBHOOK**

### **Health Check**
```
GET /api/webhook/productos/health
```

### **Producto Individual**
```
POST /api/webhook/productos
Content-Type: application/json

{
  "codigo": "PROD-001",
  "descripcion": "Descripción del producto",
  "IMAGEN1": "imagen1.jpg",
  "IMAGEN2": "imagen2.jpg",
  "IMAGEN3": "imagen3.jpg",
  "pdf": "ficha.pdf",
  "METADATA": "metadata.json"
}
```

### **Productos en Lote**
```
POST /api/webhook/productos/batch
Content-Type: application/json

[
  {
    "codigo": "PROD-001",
    "descripcion": "Producto 1"
  },
  {
    "codigo": "PROD-002", 
    "descripcion": "Producto 2"
  }
]
```

## 🔄 **FLUJO DE SINCRONIZACIÓN**

### **Paso 1: Recepción de Productos**
1. AppSheet envía producto al webhook
2. Webhook valida datos y los guarda en MySQL
3. Se crea estructura de carpetas automáticamente
4. Se registran nombres de archivos en base de datos

### **Paso 2: Sincronización de Imágenes**
1. Google Drive Desktop sincroniza carpeta localmente
2. Script de sincronización lee base de datos
3. Copia imágenes desde Drive Desktop al servidor
4. Actualiza metadatos en base de datos

### **Paso 3: Verificación**
1. Verificar que las imágenes estén en el servidor
2. Verificar URLs públicas funcionando
3. Verificar logs de sincronización

## 📊 **MONITOREO Y LOGS**

### **Archivos de Log**
- `/storage/logs/webhook_productos.log` - Actividad del webhook
- `/storage/logs/sincronizacion_imagenes.log` - Sincronización de imágenes
- `/storage/logs/sincronizacion_automatica.log` - Sincronización automática

### **Comandos de Monitoreo**
```bash
# Ver logs en tiempo real
tail -f /var/www/maruz/app/maruz_distribuciones/storage/logs/webhook_productos.log

# Verificar espacio en disco
df -h /var/www/maruz

# Verificar procesos activos
ps aux | grep python3
```

## ⚠️ **SOLUCIÓN DE PROBLEMAS**

### **Error: "Module not found"**
```bash
# Activar entorno virtual
source /var/www/maruz/venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### **Error: "Permission denied"**
```bash
# Verificar permisos
ls -la /var/www/maruz/app/maruz_distribuciones/storage/

# Corregir permisos
chmod -R 755 /var/www/maruz/app/maruz_distribuciones/storage/
```

### **Error: "Connection refused"**
```bash
# Verificar que la aplicación esté corriendo
ps aux | grep "python3.*8002"

# Verificar puerto
netstat -tlnp | grep 8002
```

## 🔒 **SEGURIDAD**

### **Variables de Entorno**
- Credenciales de base de datos en `.env`
- Permisos de archivos restringidos (600 para .env)
- Logs de acceso y actividad

### **Validaciones**
- Campos requeridos obligatorios
- Sanitización de nombres de archivos
- Límites de tamaño de archivos

## 📈 **OPTIMIZACIONES FUTURAS**

1. **Compresión de Imágenes**: Reducir tamaño de archivos
2. **CDN**: Distribuir imágenes globalmente
3. **Cache**: Implementar sistema de caché
4. **Backup**: Sistema de respaldo automático
5. **Monitoreo**: Dashboard de métricas

## 📞 **SOPORTE**

### **Archivos de Configuración**
- `config_sincronizacion.json` - Configuración de rutas
- `.env` - Variables de entorno
- `DEVELOPMENT_LOG_MASTER.md` - Bitácora de desarrollo

### **Comandos de Diagnóstico**
```bash
# Estado del sistema
./ejecutar_sincronizacion.sh

# Verificar configuración
python3 configurar_sincronizacion.py

# Probar webhook
python3 test_webhook_v2.py
```

---

## 🎯 **RESUMEN DE IMPLEMENTACIÓN**

✅ **Webhook actualizado** para nombres de archivos  
✅ **Script de sincronización** de imágenes  
✅ **Estructura de carpetas** automática  
✅ **Sistema de logs** completo  
✅ **Scripts de automatización**  
✅ **Pruebas del sistema**  
✅ **Documentación completa**  

**El sistema está listo para recibir productos desde AppSheet y sincronizar imágenes desde Google Drive Desktop.**
