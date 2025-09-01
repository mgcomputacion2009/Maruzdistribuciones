#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple del sistema de pedido abierto
"""

import requests
import json

def test_pedido_simple():
    """Prueba básica del sistema"""
    print("🧪 Probando sistema de pedido abierto...")
    
    # Usar session para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Probar endpoint ensure
        print("1. Probando /api/pedido/ensure...")
        response = session.post('http://localhost:8002/api/pedido/ensure', 
                               headers={'Content-Type': 'application/json'})
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Pedido creado: {data['pedido_id']}")
            print(f"   Token: {data['pedido_token'][:16]}...")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False

if __name__ == "__main__":
    success = test_pedido_simple()
    print("🎉 ¡Prueba exitosa!" if success else "❌ Prueba fallida")
