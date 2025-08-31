#!/bin/bash

# Script de configuración automática para la aplicación Maruz
# Este script configura Nginx, Gunicorn y systemd para servir la aplicación Flask

set -e  # Salir si hay algún error

echo "🚀 Configurando el despliegue de la aplicación Maruz..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   print_error "Este script debe ejecutarse como root"
   echo "Usa: sudo bash setup_deployment.sh"
   exit 1
fi

# 1. Instalar dependencias del sistema
print_status "Instalando dependencias del sistema..."
apt update
apt install -y nginx python3-pip python3-venv

# 2. Instalar Gunicorn en el entorno virtual
print_status "Instalando Gunicorn en el entorno virtual..."
cd /var/www/maruz
source venv/bin/activate
pip install gunicorn
deactivate

# 3. Configurar permisos
print_status "Configurando permisos..."
chown -R www-data:www-data /var/www/maruz
chmod +x /var/www/maruz/wsgi.py

# 4. Configurar Nginx
print_status "Configurando Nginx..."
cp /var/www/maruz/nginx-maruz.conf /etc/nginx/sites-available/maruz
ln -sf /etc/nginx/sites-available/maruz /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Remover configuración por defecto

# Verificar configuración de Nginx
nginx -t

# 5. Configurar servicio systemd
print_status "Configurando servicio systemd..."
cp /var/www/maruz/maruz.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable maruz
systemctl enable nginx

# 6. Iniciar servicios
print_status "Iniciando servicios..."
systemctl start maruz
systemctl start nginx

# 7. Verificar estado de los servicios
print_status "Verificando estado de los servicios..."
sleep 2

if systemctl is-active --quiet maruz; then
    print_status "✅ Servicio Maruz está ejecutándose"
else
    print_error "❌ El servicio Maruz no está ejecutándose"
    print_warning "Revisa los logs con: journalctl -u maruz -f"
fi

if systemctl is-active --quiet nginx; then
    print_status "✅ Nginx está ejecutándose"
else
    print_error "❌ Nginx no está ejecutándose"
    print_warning "Revisa los logs con: journalctl -u nginx -f"
fi

# 8. Mostrar información final
print_status "🎉 ¡Configuración completada!"
echo ""
echo "📋 Información del despliegue:"
echo "   - Aplicación Flask corriendo en: http://127.0.0.1:5000 (interno)"
echo "   - Nginx proxy en: http://localhost (puerto 80)"
echo "   - Logs de la aplicación: journalctl -u maruz -f"
echo "   - Logs de Nginx: tail -f /var/log/nginx/maruz_*.log"
echo ""
echo "🔧 Comandos útiles:"
echo "   - Reiniciar aplicación: sudo systemctl restart maruz"
echo "   - Reiniciar Nginx: sudo systemctl restart nginx"
echo "   - Ver estado: sudo systemctl status maruz nginx"
echo "   - Parar servicios: sudo systemctl stop maruz nginx"
echo ""
print_status "Puedes acceder a tu aplicación desde el navegador en: http://localhost"
