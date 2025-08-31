#!/bin/bash

# Script de gestión para la aplicación Maruz
# Uso: ./manage.sh [start|stop|restart|status|logs|deploy]

case $1 in
    start)
        echo "🚀 Iniciando servicios..."
        sudo systemctl start maruz nginx
        echo "✅ Servicios iniciados"
        ;;
    stop)
        echo "🛑 Deteniendo servicios..."
        sudo systemctl stop maruz nginx
        echo "✅ Servicios detenidos"
        ;;
    restart)
        echo "🔄 Reiniciando servicios..."
        sudo systemctl restart maruz nginx
        echo "✅ Servicios reiniciados"
        ;;
    status)
        echo "📊 Estado de los servicios:"
        sudo systemctl status maruz nginx --no-pager
        ;;
    logs)
        echo "📜 Logs de la aplicación (Ctrl+C para salir):"
        sudo journalctl -u maruz -f
        ;;
    nginx-logs)
        echo "📜 Logs de Nginx:"
        sudo tail -f /var/log/nginx/maruz_*.log
        ;;
    deploy)
        echo "🚀 Desplegando aplicación..."
        sudo bash setup_deployment.sh
        ;;
    test)
        echo "🧪 Probando conexión..."
        curl -s http://localhost || echo "❌ No se pudo conectar a la aplicación"
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs|nginx-logs|deploy|test}"
        echo ""
        echo "Comandos disponibles:"
        echo "  start      - Iniciar servicios"
        echo "  stop       - Detener servicios"
        echo "  restart    - Reiniciar servicios"
        echo "  status     - Ver estado de servicios"
        echo "  logs       - Ver logs de la aplicación"
        echo "  nginx-logs - Ver logs de Nginx"
        echo "  deploy     - Ejecutar configuración completa"
        echo "  test       - Probar si la aplicación responde"
        exit 1
        ;;
esac
