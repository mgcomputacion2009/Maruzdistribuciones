# 🌐 CONEXIÓN DESDE SISTEMA EXTERNO - MARUZ DISTRIBUCIONES

## 📋 **INFORMACIÓN DEL SERVIDOR**

### **🔗 URLs Base**
```
Servidor Principal: https://maruzdistribuciones.app
Servidor Local: http://localhost:8002 (si accedes desde el mismo servidor)
```

### **🔌 Endpoints Disponibles**

#### **1. Carga de Productos**
```
POST https://maruzdistribuciones.app/api/productos/cargar_v2
Content-Type: application/json
```

**Ejemplo de payload:**
```json
{
  "productos": [
    {
      "CODIGO": "00002A",
      "DESCRIPCION": "SILICON GRIS 85GRS",
      "PRE_PRECIO": 1.44,
      "PRECIOA": 1.44,
      "PRECIOB": 2.22,
      "PRECIOA + IVA": 1.67,
      "PRECIOB + IVA": 2.58,
      "ULTIMO_COSTO": 31.57,
      "COSTO USD": 0.89,
      "UTIL": 61.75,
      "EXIS": 11,
      "ALMACEN": "",
      "UND MED": "UND",
      "TIPO IVA": "GN",
      "MARCA": "SHIMA",
      "GRUPO": "IMPORTACION DIRECTA",
      "SUB GRUPO": "PEGAMENTO",
      "BARRAS": "00002A1"
    }
  ]
}
```

#### **2. Estado del Sistema**
```
GET https://maruzdistribuciones.app/api/productos/status_v2
```

#### **3. Estado con Schema**
```
GET https://maruzdistribuciones.app/api/productos/status_v2?schema=1
```

## 🗄️ **CONFIGURACIÓN DE BASE DE DATOS**

### **📊 Parámetros de Conexión MySQL**
```python
# Configuración de conexión directa
DB_HOST = "127.0.0.1"  # o la IP del servidor
DB_PORT = 3306
DB_NAME = "maruz_db"
DB_USER = "miguel"
DB_PASSWORD = "[PASSWORD_DEL_ENV]"  # Ver archivo .env
```

### **🔧 Conexión Python (mysql-connector)**
```python
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",  # o IP del servidor
            port=3306,
            database="maruz_db",
            user="miguel",
            password="[PASSWORD_DEL_ENV]",
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None
```

### **🔧 Conexión Python (SQLAlchemy)**
```python
from sqlalchemy import create_engine

# URL de conexión SQLAlchemy
DATABASE_URL = "mysql+pymysql://miguel:[PASSWORD]@127.0.0.1:3306/maruz_db?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=False)
```

## 📁 **ENDPOINTS PARA SUBIR IMÁGENES**

### **🖼️ Endpoint de Subida de Imágenes**
```
POST https://maruzdistribuciones.app/api/productos/upload_image
Content-Type: multipart/form-data
```

**Parámetros:**
- `file`: Archivo de imagen (JPG, PNG, GIF)
- `codigo_producto`: Código del producto
- `tipo_imagen`: "imagen1", "imagen2", "imagen3"

**Ejemplo con curl:**
```bash
curl -X POST \
  https://maruzdistribuciones.app/api/productos/upload_image \
  -F "file=@imagen.jpg" \
  -F "codigo_producto=00002A" \
  -F "tipo_imagen=imagen1"
```

**Ejemplo con Python (requests):**
```python
import requests

def upload_image(image_path, codigo_producto, tipo_imagen):
    url = "https://maruzdistribuciones.app/api/productos/upload_image"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {
            'codigo_producto': codigo_producto,
            'tipo_imagen': tipo_imagen
        }
        
        response = requests.post(url, files=files, data=data)
        return response.json()

# Uso
result = upload_image("imagen.jpg", "00002A", "imagen1")
print(result)
```

## 🔐 **CONFIGURACIÓN DE SEGURIDAD**

### **🔑 Variables de Entorno (.env)**
```bash
# Base de datos
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=maruz_db
DB_USER=miguel
DB_PASSWORD=[TU_PASSWORD_AQUI]

# Seguridad
SECRET_KEY=maruz_jwt_secret_2024_development_key

# Webhook
WEBHOOK_SECRET=[TU_WEBHOOK_SECRET]

# Google Drive (opcional)
GOOGLE_DRIVE_CREDENTIALS=[CREDENTIALS_JSON]
GOOGLE_DRIVE_FOLDER_ID=[FOLDER_ID]
```

## 📊 **ESTRUCTURA DE LA TABLA productos_v2**

### **🗂️ Campos Principales**
```sql
CREATE TABLE productos_v2 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_producto VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    pre_precio DECIMAL(10,2) DEFAULT 0.00,
    precio_a DECIMAL(10,2) DEFAULT 0.00,
    precio_b DECIMAL(10,2) DEFAULT 0.00,
    precio_a_iva DECIMAL(10,2) DEFAULT 0.00,
    precio_b_iva DECIMAL(10,2) DEFAULT 0.00,
    ultimo_costo DECIMAL(10,2) DEFAULT 0.00,
    costo_usd DECIMAL(10,2) DEFAULT 0.00,
    utilidad DECIMAL(5,2) DEFAULT 0.00,
    existencia INT DEFAULT 0,
    almacen VARCHAR(100),
    unidad_medida VARCHAR(50),
    tipo_iva VARCHAR(10),
    marca VARCHAR(100),
    grupo VARCHAR(100),
    sub_grupo VARCHAR(100),
    codigo_barras VARCHAR(100),
    imagen1 VARCHAR(500),
    imagen2 VARCHAR(500),
    imagen3 VARCHAR(500),
    imagen1_editada VARCHAR(500),
    imagen2_editada VARCHAR(500),
    imagen3_editada VARCHAR(500),
    metadata JSON,
    nota TEXT,
    web VARCHAR(500),
    categoria VARCHAR(100),
    descripcion_producto TEXT,
    propiedades TEXT,
    datos_tecnicos TEXT,
    especificaciones TEXT,
    campos_aplicacion TEXT,
    envases_disponibles TEXT,
    pdf VARCHAR(500),
    recomendaciones TEXT,
    cont VARCHAR(100),
    pr VARCHAR(100),
    id_drive VARCHAR(100),
    qrt VARCHAR(255),
    empresa_id INT DEFAULT 2,
    ambiente VARCHAR(50) DEFAULT 'desarrollo',
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 🧪 **EJEMPLOS DE USO**

### **📤 Cargar Productos (Python)**
```python
import requests
import json

def cargar_productos(productos):
    url = "https://maruzdistribuciones.app/api/productos/cargar_v2"
    
    payload = {
        "productos": productos,
        "timestamp": "2025-09-02T05:54:34",
        "origen": "Sistema Externo"
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Ejemplo de uso
productos = [
    {
        "CODIGO": "TEST001",
        "DESCRIPCION": "Producto de prueba",
        "PRECIOA": 10.50,
        "PRECIOB": 12.00,
        "EXIS": 100,
        "MARCA": "Test Brand",
        "GRUPO": "Test Group"
    }
]

resultado = cargar_productos(productos)
print(resultado)
```

### **📊 Verificar Estado (Python)**
```python
import requests

def verificar_estado():
    url = "https://maruzdistribuciones.app/api/productos/status_v2"
    
    response = requests.get(url)
    return response.json()

# Uso
estado = verificar_estado()
print(f"Total productos: {estado['estado']['total_productos']}")
print(f"Productos activos: {estado['estado']['productos_activos']}")
```

### **🔍 Consulta Directa a Base de Datos**
```python
import mysql.connector

def consultar_productos():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        database="maruz_db",
        user="miguel",
        password="[PASSWORD]"
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT codigo_producto, descripcion, precio_a FROM productos_v2 LIMIT 10")
    
    productos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return productos

# Uso
productos = consultar_productos()
for producto in productos:
    print(f"Código: {producto[0]}, Descripción: {producto[1]}, Precio: {producto[2]}")
```

## 🚨 **NOTAS IMPORTANTES**

### **⚠️ Consideraciones de Seguridad**
1. **Cambiar contraseñas por defecto** en producción
2. **Usar HTTPS** para todas las conexiones externas
3. **Validar inputs** antes de enviar a la API
4. **Implementar rate limiting** si es necesario

### **🔧 Configuración del Firewall**
```bash
# Permitir conexiones MySQL desde IPs específicas
sudo ufw allow from [IP_CLIENTE] to any port 3306

# Permitir conexiones HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443
```

### **📝 Logs y Monitoreo**
- **Logs de aplicación**: `/var/www/maruz/app/maruz_distribuciones/storage/logs/app.log`
- **Logs del sistema**: `journalctl -u maruz-distribuciones -f`
- **Logs de MySQL**: `/var/log/mysql/error.log`

## 🎯 **PRÓXIMOS PASOS**

1. **Configurar variables de entorno** en el sistema externo
2. **Probar conexión** con endpoints de estado
3. **Implementar carga de productos** con validación
4. **Configurar subida de imágenes** si es necesario
5. **Implementar monitoreo** y logs

---

**💡 Tip**: Usa el endpoint `/api/productos/status_v2?schema=1` para obtener la estructura exacta de campos que espera el servidor.





