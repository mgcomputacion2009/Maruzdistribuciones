# 🚀 ENDPOINT SIMPLE - CARGAR PRODUCTOS
# Versión simplificada para pruebas

from flask import Blueprint, request, jsonify
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear Blueprint
cargar_bp = Blueprint('cargar', __name__, url_prefix='/api/productos')

@cargar_bp.route('/status', methods=['GET'])
def status_productos():
    """Endpoint simple para verificar estado"""
    try:
        response = {
            'success': True,
            'status': 'operativo',
            'message': 'Endpoint funcionando correctamente',
            'timestamp': '2024-12-19'
        }
        
        logger.info("✅ Status endpoint llamado exitosamente")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"❌ Error en status_productos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cargar_bp.route('/cargar', methods=['POST'])
def cargar_productos():
    """Endpoint simple para cargar productos"""
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        data = request.get_json()
        
        response = {
            'success': True,
            'message': 'Endpoint funcionando correctamente',
            'data_received': len(data.get('productos', [])),
            'timestamp': '2024-12-19'
        }
        
        logger.info("✅ Cargar endpoint llamado exitosamente")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"❌ Error en cargar_productos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
