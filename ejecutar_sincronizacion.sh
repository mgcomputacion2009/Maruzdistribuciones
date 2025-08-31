#!/bin/bash
# 🚀 SCRIPT DE AUTOMATIZACIÓN DE SINCRONIZACIÓN
# Ejecuta la sincronización de imágenes desde Google Drive Desktop

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
SCRIPT_DIR="/var/www/maruz"
VENV_PATH="/var/www/maruz/venv"
LOG_FILE="/var/www/maruz/app/maruz_distribuciones/storage/logs/sincronizacion_automatica.log"
LOCK_FILE="/var/www/maruz/sincronizacion.lock"

# Función para logging
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

# Función para error
error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Función para éxito
success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Función para advertencia
warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Verificar si ya hay una sincronización en curso
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        error "Sincronización ya en curso (PID: $PID)"
        exit 1
    else
        warning "Lock file encontrado pero proceso no existe. Eliminando lock file."
        rm -f "$LOCK_FILE"
    fi
fi

# Crear lock file
echo $$ > "$LOCK_FILE"

# Función de limpieza al salir
cleanup() {
    log "Limpiando archivos temporales..."
    rm -f "$LOCK_FILE"
    log "Sincronización finalizada"
}

# Capturar señales de salida
trap cleanup EXIT INT TERM

# Inicio del script
log "🚀 INICIANDO SINCRONIZACIÓN AUTOMÁTICA DE IMÁGENES"
log "=" * 60
log "📁 Directorio de trabajo: $SCRIPT_DIR"
log "🐍 Entorno virtual: $VENV_PATH"
log "📝 Log file: $LOG_FILE"

# Verificar que estamos en el directorio correcto
cd "$SCRIPT_DIR" || {
    error "No se pudo cambiar al directorio: $SCRIPT_DIR"
    exit 1
}

# Verificar que existe el entorno virtual
if [ ! -d "$VENV_PATH" ]; then
    error "Entorno virtual no encontrado: $VENV_PATH"
    exit 1
fi

# Verificar que existe el script de sincronización
if [ ! -f "$SCRIPT_DIR/sincronizar_imagenes.py" ]; then
    error "Script de sincronización no encontrado: $SCRIPT_DIR/sincronizar_imagenes.py"
    exit 1
fi

# Verificar que existe el directorio de storage
if [ ! -d "$SCRIPT_DIR/app/maruz_distribuciones/storage" ]; then
    error "Directorio de storage no encontrado"
    exit 1
fi

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

# Activar entorno virtual y ejecutar sincronización
log "🐍 Activando entorno virtual..."
source "$VENV_PATH/bin/activate" || {
    error "No se pudo activar el entorno virtual"
    exit 1
}

log "📦 Verificando dependencias..."
python3 -c "import mysql.connector" || {
    error "mysql-connector-python no está instalado"
    log "Instalando mysql-connector-python..."
    pip install mysql-connector-python || {
        error "No se pudo instalar mysql-connector-python"
        exit 1
    }
}

log "🔄 Ejecutando sincronización..."
python3 "$SCRIPT_DIR/sincronizar_imagenes.py" 2>&1 | tee -a "$LOG_FILE"

# Verificar resultado
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    success "Sincronización completada exitosamente"
else
    error "Sincronización falló con código de salida: ${PIPESTATUS[0]}"
fi

# Verificar espacio en disco
log "💾 Verificando espacio en disco..."
df -h "$SCRIPT_DIR" | tee -a "$LOG_FILE"

# Verificar tamaño de logs
log "📊 Verificando tamaño de logs..."
du -sh "$SCRIPT_DIR/app/maruz_distribuciones/storage/logs/" | tee -a "$LOG_FILE"

# Limpiar logs antiguos (mantener solo los últimos 10MB)
log "🧹 Limpiando logs antiguos..."
find "$SCRIPT_DIR/app/maruz_distribuciones/storage/logs/" -name "*.log" -size +10M -exec ls -lh {} \; | tee -a "$LOG_FILE"

log "✅ SINCRONIZACIÓN AUTOMÁTICA COMPLETADA"
log "=" * 60
