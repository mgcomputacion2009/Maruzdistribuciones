#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 ACTUALIZADOR SIMPLE DE PRECIOS ALEATORIOS - MARUZ DISTRIBUCIONES
Script simple para actualizar precios aleatorios entre $1 y $10

Autor: Maruz Distribuciones
Fecha: 1 de septiembre 2024
Versión: 1.0
"""

import mysql.connector
import random
import sys

def conectar_base_datos():
    """
    Conecta directamente a la base de datos MySQL
    """
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            database='maruz_db',
            user='miguel',
            password='Mg645418037$$',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def generar_precio_aleatorio():
    """
    Genera un precio aleatorio entre $1.00 y $10.00
    """
    precio = round(random.uniform(1.00, 10.00), 2)
    return precio

def actualizar_precios_productos():
    """
    Función principal para actualizar precios
    """
    print("🔄 ACTUALIZADOR SIMPLE DE PRECIOS ALEATORIOS")
    print("=" * 50)
    
    # Conectar a la base de datos
    connection = conectar_base_datos()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todos los productos
        print("🔍 Obteniendo productos...")
        cursor.execute("SELECT id, codigo_producto, descripcion, pre_precio FROM productos ORDER BY id")
        productos = cursor.fetchall()
        
        if not productos:
            print("❌ No se encontraron productos")
            return
        
        print(f"✅ Se encontraron {len(productos)} productos")
        
        # Mostrar algunos productos como ejemplo
        print(f"\n📋 EJEMPLO DE PRODUCTOS:")
        for i, producto in enumerate(productos[:5], 1):
            precio_actual = producto['pre_precio'] if producto['pre_precio'] else 'Sin precio'
            print(f"   {i}. ID: {producto['id']} | {producto['codigo_producto']} | Precio: {precio_actual}")
        
        if len(productos) > 5:
            print(f"   ... y {len(productos) - 5} productos más")
        
        # Confirmar acción
        print(f"\n⚠️  ADVERTENCIA: Se actualizarán TODOS los precios")
        respuesta = input("¿Continuar? (s/N): ").strip().lower()
        
        if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada")
            return
        
        # Actualizar precios
        print(f"\n🔄 Actualizando precios...")
        productos_actualizados = 0
        
        for i, producto in enumerate(productos, 1):
            nuevo_precio = generar_precio_aleatorio()
            
            # Actualizar precio
            update_cursor = connection.cursor()
            update_cursor.execute(
                "UPDATE productos SET pre_precio = %s WHERE id = %s",
                (nuevo_precio, producto['id'])
            )
            update_cursor.close()
            
            productos_actualizados += 1
            print(f"   [{i:3d}/{len(productos)}] ID {producto['id']}: ${nuevo_precio:.2f}")
        
        # Confirmar cambios
        connection.commit()
        print(f"\n✅ Se actualizaron {productos_actualizados} productos")
        
        # Verificar precios
        print(f"\n🔍 Verificando precios...")
        cursor.execute("SELECT MIN(pre_precio) as min_precio, MAX(pre_precio) as max_precio, AVG(pre_precio) as avg_precio FROM productos")
        stats = cursor.fetchone()
        
        if stats:
            print(f"   Precio mínimo: ${stats['min_precio']:.2f}")
            print(f"   Precio máximo: ${stats['max_precio']:.2f}")
            print(f"   Precio promedio: ${stats['avg_precio']:.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        connection.rollback()
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()
            print("✅ Conexión cerrada")

if __name__ == "__main__":
    actualizar_precios_productos()
