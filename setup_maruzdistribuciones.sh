#!/bin/bash

# Habilitar el sitio en Nginx
sudo ln -sf /etc/nginx/sites-available/maruzdistribuciones.app /etc/nginx/sites-enabled/

# Verificar la configuración de Nginx
echo "Verificando configuración de Nginx..."
sudo nginx -t

# Recargar Nginx si la configuración es correcta
if [ $? -eq 0 ]; then
    echo "Recargando Nginx..."
    sudo systemctl reload nginx
else
    echo "Error en la configuración de Nginx. Por favor revisa los errores."
    exit 1
fi

# Habilitar y reiniciar el servicio de maruz-distribuciones
echo "Configurando servicio maruz-distribuciones..."
sudo systemctl daemon-reload
sudo systemctl enable maruz-distribuciones
sudo systemctl restart maruz-distribuciones

# Verificar el estado del servicio
echo "Estado del servicio maruz-distribuciones:"
sudo systemctl status maruz-distribuciones

# Verificar que el puerto 8002 está escuchando
echo "Verificando puerto 8002..."
sudo netstat -tlnp | grep :8002

echo "¡Configuración completada!"
echo "Ahora puedes acceder a la aplicación en: http://maruzdistribuciones.app"
