#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el sistema de pedido abierto
Sistema de Carrito Avanzado - Maruz Distribuciones
"""

import requests
import json
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
BASE_URL = 'http://localhost:8002'
SESSION = requests.Session()

def test_ensure_pedido():
    """Probar endpoint /api/pedido/ensure"""
    try:
        logger.info("🧪 Probando /api/pedido/ensure...")
        
        response = SESSION.post(f'{BASE_URL}/api/pedido/ensure', 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Pedido asegurado exitosamente")
            logger.info(f"   Pedido ID: {data['pedido_id']}")
            logger.info(f"   Token: {data['pedido_token'][:16]}...")
            logger.info(f"   Estado: {data['estado']}")
            logger.info(f"   Resumen: {data['resumen']}")
            return data
        else:
            logger.error(f"❌ Error en ensure: {response.status_code}")
            logger.error(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Excepción en ensure: {e}")
        return None

def test_resumen(pedido_token):
    """Probar endpoint /api/pedido/resumen"""
    try:
        logger.info("🧪 Probando /api/pedido/resumen...")
        
        response = SESSION.get(f'{BASE_URL}/api/pedido/resumen',
                              headers={'X-Pedido-Token': pedido_token})
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Resumen obtenido exitosamente")
            logger.info(f"   Versión: {data['version']}")
            logger.info(f"   Unidades: {data['unidades']}")
            logger.info(f"   Subtotal: ${data['subtotal']}")
            logger.info(f"   Total: ${data['total']}")
            return data
        else:
            logger.error(f"❌ Error en resumen: {response.status_code}")
            logger.error(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Excepción en resumen: {e}")
        return None

def test_items_query(pedido_token):
    """Probar endpoint /api/pedido/items/query"""
    try:
        logger.info("🧪 Probando /api/pedido/items/query...")
        
        # Códigos de productos de prueba
        codigos = ['PROD001', 'PROD002', 'PROD003']
        
        response = SESSION.post(f'{BASE_URL}/api/pedido/items/query',
                               headers={
                                   'Content-Type': 'application/json',
                                   'X-Pedido-Token': pedido_token
                               },
                               json={'codigos': codigos})
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Items consultados exitosamente")
            logger.info(f"   Items encontrados: {len(data['items'])}")
            for codigo, item in data['items'].items():
                logger.info(f"     {codigo}: {item}")
            return data
        else:
            logger.error(f"❌ Error en items/query: {response.status_code}")
            logger.error(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Excepción en items/query: {e}")
        return None

def test_items_batch(pedido_token, version):
    """Probar endpoint /api/pedido/items/batch"""
    try:
        logger.info("🧪 Probando /api/pedido/items/batch...")
        
        # Cambios de prueba
        cambios = [
            {
                'producto_codigo': 'PROD001',
                'cantidad': 5,
                'precio_unitario': 100.00,
                'descuento_monto': 25.00
            },
            {
                'producto_codigo': 'PROD002',
                'cantidad': 3,
                'precio_unitario': 75.50,
                'descuento_monto': 0.00
            }
        ]
        
        response = SESSION.post(f'{BASE_URL}/api/pedido/items/batch',
                               headers={
                                   'Content-Type': 'application/json',
                                   'X-Pedido-Token': pedido_token
                               },
                               json={
                                   'version': version,
                                   'cambios': cambios
                               })
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Items actualizados en batch exitosamente")
            logger.info(f"   Nueva versión: {data['version']}")
            logger.info(f"   Resumen: {data['resumen']}")
            logger.info(f"   Aplicados: {data['aplicados']}")
            return data
        else:
            logger.error(f"❌ Error en items/batch: {response.status_code}")
            logger.error(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Excepción en items/batch: {e}")
        return None

def test_item_remove(pedido_token):
    """Probar endpoint /api/pedido/item/remove"""
    try:
        logger.info("🧪 Probando /api/pedido/item/remove...")
        
        response = SESSION.post(f'{BASE_URL}/api/pedido/item/remove',
                               headers={
                                   'Content-Type': 'application/json',
                                   'X-Pedido-Token': pedido_token
                               },
                               json={'producto_codigo': 'PROD001'})
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Item removido exitosamente")
            logger.info(f"   Nueva versión: {data['version']}")
            logger.info(f"   Resumen: {data['resumen']}")
            return data
        else:
            logger.error(f"❌ Error en item/remove: {response.status_code}")
            logger.error(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Excepción en item/remove: {e}")
        return None

def test_finalizar_pedido(pedido_token):
    """Probar endpoint /api/pedido/finalizar"""
    try:
        logger.info("🧪 Probando /api/pedido/finalizar...")
        
        datos_cliente = {
            'cliente_nombre': 'Cliente de Prueba',
            'cliente_telefono': '555-1234',
            'cliente_email': 'cliente@prueba.com',
            'direccion_entrega': 'Dirección de Prueba 123',
            'metodo_pago': 'Efectivo',
            'notas': 'Pedido de prueba del sistema'
        }
        
        response = SESSION.post(f'{BASE_URL}/api/pedido/finalizar',
                               headers={
                                   'Content-Type': 'application/json',
                                   'X-Pedido-Token': pedido_token
                               },
                               json=datos_cliente)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Pedido finalizado exitosamente")
            logger.info(f"   Número de pedido: {data['numero_pedido']}")
            logger.info(f"   Total: ${data['total']}")
            return data
        else:
            logger.error(f"❌ Error en finalizar: {response.status_code}")
            logger.error(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Excepción en finalizar: {e}")
        return None

def main():
    """Función principal de pruebas"""
    try:
        logger.info("🚀 Iniciando pruebas del sistema de pedido abierto...")
        
        # 1. Asegurar pedido
        pedido_data = test_ensure_pedido()
        if not pedido_data:
            logger.error("❌ No se pudo asegurar el pedido. Abortando pruebas.")
            return
            
        pedido_token = pedido_data['pedido_token']
        version = pedido_data['version']
        
        # 2. Obtener resumen inicial
        test_resumen(pedido_token)
        
        # 3. Consultar items
        test_items_query(pedido_token)
        
        # 4. Actualizar items en batch
        batch_result = test_items_batch(pedido_token, version)
        if batch_result:
            version = batch_result['version']
        
        # 5. Obtener resumen actualizado
        test_resumen(pedido_token)
        
        # 6. Remover un item
        remove_result = test_item_remove(pedido_token)
        if remove_result:
            version = remove_result['version']
        
        # 7. Obtener resumen final
        test_resumen(pedido_token)
        
        # 8. Finalizar pedido
        test_finalizar_pedido(pedido_token)
        
        logger.info("🎉 Todas las pruebas completadas exitosamente!")
        
    except Exception as e:
        logger.error(f"❌ Error en las pruebas: {e}")
        raise

if __name__ == "__main__":
    main()
