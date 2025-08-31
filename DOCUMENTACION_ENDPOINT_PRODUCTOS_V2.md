# 🚀 DOCUMENTACIÓN COMPLETA - ENDPOINT CARGAR PRODUCTOS V2

## 📋 RESUMEN EJECUTIVO

Se ha implementado una nueva versión del sistema de carga de productos que incluye **campos de precios, inventario y códigos de barras**. El sistema v2 mantiene compatibilidad con los campos anteriores y agrega funcionalidades específicas para gestión comercial.

### 🆕 **NUEVOS CAMPOS AGREGADOS**

#### 💰 **Campos de Precios**
- `PRE_PRECIO` - Precio anterior
- `PRECIOA` - Precio A (precio regular)
- `PRECIOB` - Precio B (precio especial)
- `PRECIOA + IVA` - Precio A con IVA incluido
- `PRECIOB + IVA` - Precio B con IVA incluido
- `ULTIMO_COSTO` - Último costo de compra
- `COSTO USD` - Costo en dólares
- `UTIL` - Utilidad/margen

#### 📦 **Campos de Inventario**
- `EXIS` - Existencia/Stock actual
- `ALMACEN` - Ubicación del almacén
- `UND MED` - Unidad de medida

#### 🏷️ **Campos de Clasificación**
- `TIPO IVA` - Tipo de impuesto (ej: "19%")
- `MARCA` - Marca del producto
- `GRUPO` - Grupo de productos
- `SUB GRUPO` - Subgrupo específico
- `BARRAS` - Código de barras

---

## 🌐 ENDPOINTS IMPLEMENTADOS

### 1. **POST /api/productos/cargar_v2**
**Propósito:** Recibir productos con campos de precios e inventario

**URL:** `http://34.57.121.200:8002/api/productos/cargar_v2`

**Método:** POST

**Headers requeridos:**
```
Content-Type: application/json
```

**Body JSON esperado:**
```json
{
  "productos": [
    {
      "CODIGO": "PROD001",
      "DESCRIPCION": "Aceite de motor sintético 5W-30",
      "PRE_PRECIO": "25.50",
      "PRECIOA": "30.00",
      "PRECIOB": "28.50",
      "PRECIOA + IVA": "35.70",
      "PRECIOB + IVA": "33.35",
      "ULTIMO_COSTO": "18.00",
      "COSTO USD": "15.50",
      "UTIL": "12.00",
      "EXIS": "150",
      "ALMACEN": "Principal",
      "UND MED": "Litro",
      "TIPO IVA": "19%",
      "MARCA": "Castrol",
      "GRUPO": "Lubricantes",
      "SUB GRUPO": "Aceites de motor",
      "BARRAS": "7891234567890",
      "IMAGEN1": "aceite_motor_1.jpg",
      "IMAGEN2": "aceite_motor_2.jpg",
      "IMAGEN3": "aceite_motor_3.jpg",
      "IMAGEN1(EDITADA)": "aceite_motor_1_edit.jpg",
      "IMAGEN2(EDITADA)": "aceite_motor_2_edit.jpg",
      "IMAGEN3(EDITADA)": "aceite_motor_3_edit.jpg",
      "METADATA": "Aceite sintético de alta calidad",
      "NOTA": "Producto premium",
      "WEB": "https://castrol.com/aceite-5w30",
      "CATEGORIA": "Automotriz",
      "Descripción Producto": "Aceite de motor sintético con aditivos especiales",
      "Propiedades": "Viscosidad 5W-30, API SN Plus",
      "Datos técnicos": "Punto de fluidez -40°C, Viscosidad 100°C: 12.5 cSt",
      "Especificaciones": "Cumple especificaciones API SN Plus, ILSAC GF-6A",
      "Campos de aplicación": "Motores de gasolina modernos",
      "Envases disponibles": "1L, 4L, 20L",
      "pdf": "ficha_tecnica_castrol_5w30.pdf",
      "RECOMENDACIONES": "Cambiar cada 10,000 km o 12 meses",
      "cont": "CONT001",
      "PR": "PR001",
      "IDdrive": "DRIVE001",
      "qrt": "QR001"
    }
  ],
  "timestamp": "2024-12-19T10:30:00",
  "origen": "Windows - Script de carga v2"
}
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "resumen": {
    "total_productos": 1,
    "insertados": 1,
    "actualizados": 0,
    "errores": 0,
    "tiempo_procesamiento_segundos": 0.15
  },
  "detalles": {
    "productos_con_errores": []
  },
  "timestamp": "2024-12-19T10:30:00.123456",
  "empresa": "Maruz Distribuciones",
  "ambiente": "desarrollo",
  "version": "v2"
}
```

### 2. **GET /api/productos/status_v2**
**Propósito:** Verificar estado de la tabla productos_v2

**URL:** `http://34.57.121.200:8002/api/productos/status_v2`

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "estado": {
    "tabla_existe": true,
    "total_productos": 150,
    "productos_activos": 145,
    "productos_con_stock": 120
  },
  "ultimas_actualizaciones": [
    {
      "codigo": "PROD001",
      "descripcion": "Aceite de motor sintético 5W-30...",
      "fecha": "2024-12-19T10:30:00"
    }
  ],
  "timestamp": "2024-12-19T10:30:00.123456",
  "empresa": "Maruz Distribuciones",
  "ambiente": "desarrollo",
  "version": "v2"
}
```

---

## 🗄️ ESTRUCTURA DE LA BASE DE DATOS

### Tabla: `productos_v2`

#### **Campos de Identificación**
- `id` - ID autoincremental
- `codigo_producto` - Código único del producto (VARCHAR 100, UNIQUE)
- `descripcion` - Descripción del producto (TEXT)

#### **Campos de Precios**
- `pre_precio` - Precio anterior (DECIMAL 15,2)
- `precio_a` - Precio A (DECIMAL 15,2)
- `precio_b` - Precio B (DECIMAL 15,2)
- `precio_a_iva` - Precio A con IVA (DECIMAL 15,2)
- `precio_b_iva` - Precio B con IVA (DECIMAL 15,2)
- `ultimo_costo` - Último costo (DECIMAL 15,2)
- `costo_usd` - Costo en USD (DECIMAL 15,2)
- `utilidad` - Utilidad/margen (DECIMAL 10,2)

#### **Campos de Inventario**
- `existencia` - Stock actual (INT)
- `almacen` - Ubicación (VARCHAR 100)
- `unidad_medida` - Unidad de medida (VARCHAR 50)

#### **Campos de Clasificación**
- `tipo_iva` - Tipo de IVA (VARCHAR 20)
- `marca` - Marca (VARCHAR 100)
- `grupo` - Grupo (VARCHAR 100)
- `sub_grupo` - Subgrupo (VARCHAR 100)
- `codigo_barras` - Código de barras (VARCHAR 100)

#### **Campos de Imágenes (Compatibilidad)**
- `imagen1`, `imagen2`, `imagen3` - Imágenes originales
- `imagen1_editada`, `imagen2_editada`, `imagen3_editada` - Imágenes editadas

#### **Campos de Información (Compatibilidad)**
- `metadata`, `nota`, `web`, `categoria`
- `descripcion_producto`, `propiedades`, `datos_tecnicos`
- `especificaciones`, `campos_aplicacion`, `envases_disponibles`
- `pdf`, `recomendaciones`, `cont`, `pr`, `id_drive`, `qrt`

#### **Campos de Sistema**
- `empresa_id` - ID de la empresa (INT, DEFAULT 2)
- `ambiente` - Ambiente (VARCHAR 20, DEFAULT 'desarrollo')
- `fecha_creacion` - Fecha de creación (TIMESTAMP)
- `fecha_actualizacion` - Fecha de actualización (TIMESTAMP)
- `activo` - Estado activo (BOOLEAN, DEFAULT TRUE)

#### **Índices Optimizados**
- `idx_codigo` - Búsqueda por código
- `idx_barras` - Búsqueda por código de barras
- `idx_marca` - Búsqueda por marca
- `idx_grupo` - Búsqueda por grupo
- `idx_sub_grupo` - Búsqueda por subgrupo
- `idx_categoria` - Búsqueda por categoría
- `idx_existencia` - Búsqueda por stock
- `idx_empresa` - Búsqueda por empresa
- `idx_activo` - Búsqueda por estado activo

---

## 🧪 SCRIPT DE PRUEBAS

### Archivo: `test_cargar_productos_v2.py`

**Funcionalidades de prueba:**
- ✅ Verificación de endpoint de status
- ✅ Prueba de carga de productos con precios
- ✅ Validación de campos numéricos
- ✅ Pruebas de manejo de errores
- ✅ Verificación de estructura de datos

**Uso:**
```bash
python test_cargar_productos_v2.py
```

**Ejemplo de salida:**
```
🧪 PRUEBAS DEL ENDPOINT DE PRODUCTOS V2
==================================================
🔍 Probando endpoint de status...
✅ Status exitoso:
   - Tabla existe: True
   - Total productos: 3
   - Productos activos: 3
   - Productos con stock: 3

🚀 Probando carga de productos v2...
📤 Enviando 3 productos...
✅ Carga exitosa:
   - Total procesados: 3
   - Insertados: 3
   - Actualizados: 0
   - Errores: 0
   - Tiempo: 0.25s

⚠️ Probando validación de productos inválidos...
✅ Validación funcionando:
   - Total: 3
   - Errores: 3
   - Errores detectados:
     • : ['CODIGO es obligatorio']
     • PROD004: ['PRECIOA debe ser un número válido', 'EXIS debe ser un número válido']
     • N/A: ['CODIGO es obligatorio', 'DESCRIPCION es obligatoria']

==================================================
✅ Pruebas completadas
```

---

## 🔧 CONFIGURACIÓN DEL SERVIDOR

### Archivos modificados:
1. **`app/maruz_distribuciones/api/cargar_productos_v2.py`** - Endpoint principal v2
2. **`app/maruz_distribuciones/app.py`** - Registro del blueprint v2
3. **`test_cargar_productos_v2.py`** - Script de pruebas

### Configuración de base de datos:
- **Host:** 127.0.0.1
- **Puerto:** 3306
- **Base de datos:** maruz_distribuciones
- **Usuario:** miguel
- **Charset:** utf8mb4
- **Collation:** utf8mb4_unicode_ci

---

## 📊 FUNCIONALIDADES IMPLEMENTADAS

### ✅ **Validaciones:**
- Campos obligatorios (CODIGO, DESCRIPCION)
- Validación de campos numéricos (precios, existencia)
- Longitud máxima de campos
- Formato de URLs
- Estructura de datos JSON

### ✅ **Operaciones de Base de Datos:**
- **INSERT:** Productos nuevos
- **UPDATE:** Productos existentes (upsert)
- **Transacciones:** Rollback automático en errores
- **Índices:** Búsquedas optimizadas por múltiples criterios

### ✅ **Manejo de Errores:**
- Logs detallados de operaciones
- Respuestas HTTP apropiadas
- Manejo de excepciones robusto
- Rollback de transacciones fallidas

### ✅ **Rendimiento:**
- Procesamiento en lotes (configurable)
- Conexiones de base de datos optimizadas
- Timeouts configurables
- Pausas entre lotes para no sobrecargar

---

## 🚀 FLUJO DE OPERACIÓN

### 1. **Preparación de Datos:**
```json
{
  "CODIGO": "PROD001",
  "DESCRIPCION": "Descripción del producto",
  "PRE_PRECIO": "25.50",
  "PRECIOA": "30.00",
  "PRECIOB": "28.50",
  "PRECIOA + IVA": "35.70",
  "PRECIOB + IVA": "33.35",
  "ULTIMO_COSTO": "18.00",
  "COSTO USD": "15.50",
  "UTIL": "12.00",
  "EXIS": "150",
  "ALMACEN": "Principal",
  "UND MED": "Litro",
  "TIPO IVA": "19%",
  "MARCA": "Castrol",
  "GRUPO": "Lubricantes",
  "SUB GRUPO": "Aceites de motor",
  "BARRAS": "7891234567890"
}
```

### 2. **Envío al Endpoint:**
```bash
curl -X POST http://34.57.121.200:8002/api/productos/cargar_v2 \
  -H "Content-Type: application/json" \
  -d @productos.json
```

### 3. **Verificación de Estado:**
```bash
curl http://34.57.121.200:8002/api/productos/status_v2
```

---

## 🔄 MIGRACIÓN DESDE V1

### **Compatibilidad:**
- ✅ Los campos de la versión anterior siguen funcionando
- ✅ Nueva tabla `productos_v2` separada de `productos`
- ✅ Endpoints v1 siguen disponibles
- ✅ Migración gradual sin interrupciones

### **Diferencias Clave:**
- **V1:** Enfocado en información técnica y marketing
- **V2:** Enfocado en gestión comercial e inventario
- **V1:** Campos de texto para precios
- **V2:** Campos decimales para cálculos precisos
- **V1:** Sin códigos de barras
- **V2:** Soporte completo para códigos de barras

---

## 📈 BENEFICIOS DE LA VERSIÓN V2

### **Gestión Comercial:**
- ✅ Control de precios múltiples (A, B, con IVA)
- ✅ Seguimiento de costos y utilidades
- ✅ Gestión de inventario en tiempo real
- ✅ Clasificación por marcas y grupos

### **Operaciones:**
- ✅ Códigos de barras para escaneo
- ✅ Unidades de medida estandarizadas
- ✅ Control de almacenes múltiples
- ✅ Tipos de IVA configurables

### **Análisis:**
- ✅ Reportes de rentabilidad
- ✅ Análisis de stock
- ✅ Seguimiento de precios
- ✅ Estadísticas por marca/grupo

---

**Última Actualización:** Diciembre 2024  
**Versión:** 2.0  
**Estado:** ✅ Implementado y probado
