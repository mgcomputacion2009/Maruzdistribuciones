# 🚀 MARUZ_LOADER - Cliente Windows para Carga Inteligente de Productos

## 📋 Descripción

MaruzLoader es un cliente Windows que permite cargar productos masivamente al servidor Maruz usando el flujo de "carga inteligente" del endpoint `/api/productos/cargar_v2`. Utiliza IA para mapear automáticamente las columnas del CSV a los campos del servidor.

## ✨ Características Principales

- **🤖 Mapeo Inteligente por IA**: Usa OpenAI para mapear automáticamente columnas CSV a campos del servidor
- **✈️ Preflight Testing**: Prueba con 1 item antes del envío masivo
- **🔄 Auto-completado**: Completa campos faltantes automáticamente
- **📦 Carga por Lotes**: Procesa archivos grandes en lotes de 200 items
- **🧪 Modo Dry-Run**: Simula el envío sin tocar el servidor
- **📝 Logging Completo**: Registra todo el proceso en archivos de log
- **🖥️ Interfaz Windows**: Selector de archivos nativo y CLI simple

## 🚀 Instalación Rápida

### Opción 1: Ejecutar directamente
```bash
# 1. Descargar archivos
# 2. Doble clic en maruz_loader.bat
```

### Opción 2: Instalación manual
```bash
# 1. Instalar Python 3.7+
# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar API key
set OPENAI_API_KEY=tu_api_key_aqui

# 4. Ejecutar
python maruz_loader.py
```

## 📖 Uso

### 1. Preparar archivo CSV
Tu archivo CSV debe tener columnas con datos de productos. Ejemplo:
```csv
CODIGO,DESCRIPCION,PRECIO,EXISTENCIA,MARCA
PROD001,Producto 1,15.50,100,Marca A
PROD002,Producto 2,25.75,50,Marca B
```

### 2. Ejecutar MaruzLoader
```bash
python maruz_loader.py
```

### 3. Seguir el flujo
1. **Seleccionar archivo CSV** (selector de archivos o ruta manual)
2. **Dar instrucciones** de mapeo en lenguaje natural
3. **Elegir modo**: Envío real o dry-run
4. **Ver resultados** y log detallado

## 💡 Ejemplos de Instrucciones

### Básico
```
Mapear CODIGO a codigo_producto, DESCRIPCION a descripcion, PRECIO a precio_a
```

### Avanzado
```
Mapear CODIGO a codigo_producto, DESCRIPCION a descripcion, PRECIO a precio_a.
Aplicar strip a descripciones, upper a códigos.
Defaults: empresa_id=2, ambiente=desarrollo, activo=true
```

### Con Transforms
```
Mapear campos básicos. Aplicar upper a códigos, strip a descripciones.
Para imágenes, usar url_join:https://ejemplo.com/
Concatenar MARCA+MODELO para descripcion_producto
```

## 🔧 Configuración

### Variables de Entorno
```bash
# API Key de OpenAI (requerida)
OPENAI_API_KEY=sk-proj-...

# Configuración opcional
MARUZ_SERVER_URL=https://maruzdistribuciones.app
BATCH_SIZE=200
TIMEOUT=30
```

### Archivo de Configuración
Puedes crear un archivo `.env` en el mismo directorio:
```env
OPENAI_API_KEY=sk-proj-...
MARUZ_SERVER_URL=https://maruzdistribuciones.app
BATCH_SIZE=200
TIMEOUT=30
```

## 📊 Flujo de Trabajo

### 1. Descubrimiento de Schema
- Intenta obtener schema del servidor via `/api/productos/status_v2?schema=1`
- Si falla, usa fallback de 41 campos conocidos

### 2. Análisis de CSV
- Detecta encoding (utf-8, latin-1)
- Detecta delimitador (comas, punto y coma, tabs)
- Lee cabeceras y 3 filas de muestra

### 3. Mapeo por IA
- Envía contexto a OpenAI
- Recibe mapeo, defaults y transforms
- Valida que las columnas existan

### 4. Preview y Preflight
- Muestra primer item mapeado
- Envía 1 item de prueba
- Auto-completa campos faltantes si es necesario

### 5. Envío por Lotes
- Procesa en lotes de 200 items
- Pausa 150ms entre lotes
- Muestra progreso y errores

## 🎯 Modos de Ejecución

### Envío Real
- Procesa y envía datos al servidor
- Muestra resumen detallado por lote
- Registra errores específicos

### Dry-Run
- Simula el envío sin tocar el servidor
- Muestra conteos y validaciones
- Útil para probar mapeos

### Cancelar
- Sale sin efectos
- Útil si detectas problemas

## 📝 Logging

### Archivo de Log
Se crea automáticamente: `maruz_loader_YYYYMMDD_HHMMSS.log`

### Contenido del Log
- Detecciones iniciales (encoding, delimitador, cabeceras)
- Schema usado (servidor o fallback)
- Propuesta de IA (mapeo, defaults, transforms)
- Preview del primer item
- Resultado del preflight
- Resumen por cada lote
- Resumen final

### Ejemplo de Log
```
2024-01-15 10:30:15 - INFO - 🚀 MaruzLoader iniciado
2024-01-15 10:30:16 - INFO - 🔍 Descubriendo schema del servidor...
2024-01-15 10:30:17 - INFO - ✅ Schema obtenido del servidor
2024-01-15 10:30:18 - INFO - 📁 Analizando archivo CSV: productos.csv
2024-01-15 10:30:19 - INFO - 📝 Encoding detectado: utf-8
2024-01-15 10:30:20 - INFO - 🔧 Delimitador detectado: ','
2024-01-15 10:30:21 - INFO - 📋 Cabeceras encontradas: 5 - ['CODIGO', 'DESCRIPCION', 'PRECIO', 'EXISTENCIA', 'MARCA']...
2024-01-15 10:30:22 - INFO - 🤖 Generando mapeo por IA...
2024-01-15 10:30:25 - INFO - ✅ Mapeo generado: 5 campos mapeados
2024-01-15 10:30:26 - INFO - 💡 Razón: Mapeo basado en nombres de columnas similares
2024-01-15 10:30:27 - INFO - 👁️ PREVIEW del primer item:
2024-01-15 10:30:28 - INFO - {
  "codigo_producto": "PROD001",
  "descripcion": "Producto 1",
  "precio_a": 15.5,
  "existencia": 100,
  "marca": "Marca A"
}
2024-01-15 10:30:29 - INFO - ✈️ Ejecutando preflight con 1 item...
2024-01-15 10:30:30 - INFO - ✅ Preflight exitoso
2024-01-15 10:30:31 - INFO - 📦 Enviando 1 lotes de 200 items cada uno
2024-01-15 10:30:32 - INFO - 📤 Enviando lote 1/1 (2 items)
2024-01-15 10:30:33 - INFO - ✅ Lote 1: 2 insertados, 0 actualizados, 0 errores
2024-01-15 10:30:34 - INFO - 🎉 RESUMEN FINAL: 2 insertados, 0 actualizados, 0 errores
```

## 🚨 Manejo de Errores

### Errores Comunes

#### 1. API Key no encontrada
```
❌ ERROR: OPENAI_API_KEY no encontrada en variables de entorno
```
**Solución**: Configurar la variable de entorno o usar el archivo .bat

#### 2. Archivo CSV no encontrado
```
❌ Archivo no encontrado: productos.csv
```
**Solución**: Verificar la ruta del archivo

#### 3. Error de conexión
```
❌ Error de conexión: HTTPSConnectionPool
```
**Solución**: Verificar conexión a internet y URL del servidor

#### 4. Preflight falló
```
❌ Preflight falló: Not enough parameters for the SQL statement
```
**Solución**: El sistema auto-completa campos faltantes automáticamente

### Códigos de Error por Producto
Si hay errores específicos por producto, se muestran los primeros 8:
```
🚨 Códigos con error (primeros 8):
  - PROD001: ['Campo requerido: precio_a']
  - PROD002: ['Código duplicado']
```

## 🔒 Seguridad

### SSL Verificado
- Todas las conexiones usan HTTPS con verificación SSL
- No se aceptan certificados auto-firmados

### API Key
- La API key de OpenAI se almacena en variables de entorno
- No se incluye en logs ni archivos de configuración

### Timeouts
- Timeout de 30 segundos para conexiones
- Evita bloqueos por conexiones lentas

## 📈 Rendimiento

### Lotes
- Procesa en lotes de 200 items por defecto
- Pausa de 150ms entre lotes para no saturar el servidor

### Memoria
- Carga el CSV completo en memoria
- Para archivos muy grandes (>100MB), considera dividir en archivos más pequeños

### Red
- Usa conexiones HTTP persistentes
- Reutiliza sesiones para múltiples requests

## 🛠️ Desarrollo

### Estructura del Código
```
maruz_loader.py          # Cliente principal
requirements.txt         # Dependencias
maruz_loader.bat         # Lanzador Windows
README.md               # Documentación
```

### Clases Principales
- `MaruzLoader`: Clase principal con toda la lógica
- `main()`: Función principal con interfaz CLI

### Métodos Clave
- `discover_schema()`: Obtiene schema del servidor
- `detect_csv_properties()`: Analiza archivo CSV
- `generate_ai_mapping()`: Mapeo por IA
- `preflight_test()`: Prueba con 1 item
- `send_batches()`: Envío por lotes

## 🤝 Contribuir

### Reportar Bugs
1. Revisar logs para detalles del error
2. Incluir archivo CSV de ejemplo (sin datos sensibles)
3. Especificar versión de Python y sistema operativo

### Mejoras
1. Fork del repositorio
2. Crear branch para la mejora
3. Implementar y probar
4. Crear pull request

## 📄 Licencia

Este proyecto es parte del sistema Maruz y está sujeto a los términos de licencia correspondientes.

## 🆘 Soporte

Para soporte técnico:
1. Revisar esta documentación
2. Verificar logs de error
3. Contactar al equipo de desarrollo

---

**🎉 ¡Disfruta cargando productos de manera inteligente con MaruzLoader!**