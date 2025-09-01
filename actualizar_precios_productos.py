#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 ACTUALIZADOR DE PRECIOS ALEATORIOS - MARUZ DISTRIBUCIONES
Script para actualizar precios aleatorios entre $1 y $10 en la tabla de productos

Autor: Maruz Distribuciones
Fecha: 1 de septiembre 2024
Versión: 1.0
"""

import mysql.connector
import random
import sys
import os
from decimal import Decimal, ROUND_HALF_UP

# Agregar el directorio del proyecto al path
sys.path.append('/var/www/maruz')

try:
    from app.maruz_distribuciones.config import get_db_connection
    print("✅ Configuración importada correctamente")
except ImportError as e:
    print(f"❌ Error importando configuración: {e}")
    sys.exit(1)

def generar_precio_aleatorio():
    """
    Genera un precio aleatorio entre $1.00 y $10.00
    Retorna un Decimal con 2 decimales
    """
    # Generar precio entre 1.00 y 10.00
    precio = random.uniform(1.00, 10.00)
    
    # Redondear a 2 decimales
    decimal_precio = Decimal(str(precio)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return decimal_precio

def obtener_productos_sin_precio(connection):
    """
    Obtiene productos que no tienen precio o tienen precio 0
    """
    cursor = connection.cursor(dictionary=True)
    
    query = """
    SELECT id, codigo_producto, descripcion, pre_precio 
    FROM productos 
    WHERE pre_precio IS NULL OR pre_precio = 0 OR pre_precio = 0.00
    ORDER BY id
    """
    
    cursor.execute(query)
    productos = cursor.fetchall()
    cursor.close()
    
    return productos

def obtener_todos_los_productos(connection):
    """
    Obtiene todos los productos para actualizar precios
    """
    cursor = connection.cursor(dictionary=True)
    
    query = """
    SELECT id, codigo_producto, descripcion, pre_precio 
    FROM productos 
    ORDER BY id
    """
    
    cursor.execute(query)
    productos = cursor.fetchall()
    cursor.close()
    
    return productos

def actualizar_precio_producto(connection, producto_id, nuevo_precio):
    """
    Actualiza el precio de un producto específico
    """
    cursor = connection.cursor()
    
    query = """
    UPDATE productos 
    SET pre_precio = %s, 
        fecha_actualizacion = NOW()
    WHERE id = %s
    """
    
    try:
        cursor.execute(query, (nuevo_precio, producto_id))
        connection.commit()
        return True
    except Exception as e:
        print(f"❌ Error actualizando producto {producto_id}: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()

def mostrar_resumen_productos(productos):
    """
    Muestra un resumen de los productos a procesar
    """
    print(f"\n📊 RESUMEN DE PRODUCTOS:")
    print(f"   Total de productos: {len(productos)}")
    
    if len(productos) <= 10:
        print(f"\n📋 PRODUCTOS A PROCESAR:")
        for i, producto in enumerate(productos, 1):
            precio_actual = producto['pre_precio'] if producto['pre_precio'] else 'Sin precio'
            print(f"   {i:2d}. ID: {producto['id']:4d} | Código: {producto['codigo_producto']:15s} | Precio actual: {precio_actual}")
    else:
        print(f"\n📋 MOSTRANDO PRIMEROS 10 PRODUCTOS:")
        for i, producto in enumerate(productos[:10], 1):
            precio_actual = producto['pre_precio'] if producto['pre_precio'] else 'Sin precio'
            print(f"   {i:2d}. ID: {producto['id']:4d} | Código: {producto['codigo_producto']:15s} | Precio actual: {precio_actual}")
        print(f"   ... y {len(productos) - 10} productos más")

def main():
    """
    Función principal del script
    """
    print("🔄 ACTUALIZADOR DE PRECIOS ALEATORIOS - MARUZ DISTRIBUCIONES")
    print("=" * 60)
    
    # Conectar a la base de datos
    try:
        connection = get_db_connection()
        print("✅ Conexión a la base de datos establecida")
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        sys.exit(1)
    
    try:
        # Obtener productos
        print("\n🔍 Obteniendo productos de la base de datos...")
        productos = obtener_todos_los_productos(connection)
        
        if not productos:
            print("❌ No se encontraron productos en la base de datos")
            return
        
        print(f"✅ Se encontraron {len(productos)} productos")
        
        # Mostrar resumen
        mostrar_resumen_productos(productos)
        
        # Confirmar acción
        print(f"\n⚠️  ADVERTENCIA: Se actualizarán TODOS los precios de los productos")
        respuesta = input("¿Deseas continuar? (s/N): ").strip().lower()
        
        if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada por el usuario")
            return
        
        # Procesar productos
        print(f"\n🔄 Actualizando precios...")
        productos_actualizados = 0
        productos_con_error = 0
        
        for i, producto in enumerate(productos, 1):
            nuevo_precio = generar_precio_aleatorio()
            
            print(f"   [{i:3d}/{len(productos)}] Producto ID {producto['id']}: ${nuevo_precio:.2f}")
            
            if actualizar_precio_producto(connection, producto['id'], nuevo_precio):
                productos_actualizados += 1
            else:
                productos_con_error += 1
        
        # Mostrar resumen final
        print(f"\n✅ ACTUALIZACIÓN COMPLETADA:")
        print(f"   Productos actualizados: {productos_actualizados}")
        print(f"   Productos con error: {productos_con_error}")
        print(f"   Total procesados: {len(productos)}")
        
        # Verificar precios actualizados
        print(f"\n🔍 Verificando precios actualizados...")
        productos_verificados = obtener_todos_los_productos(connection)
        
        precios_verificados = [p['pre_precio'] for p in productos_verificados if p['pre_precio']]
        if precios_verificados:
            precio_min = min(precios_verificados)
            precio_max = max(precios_verificados)
            precio_promedio = sum(precios_verificados) / len(precios_verificados)
            
            print(f"   Precio mínimo: ${precio_min:.2f}")
            print(f"   Precio máximo: ${precio_max:.2f}")
            print(f"   Precio promedio: ${precio_promedio:.2f}")
        
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        connection.rollback()
    
    finally:
        # Cerrar conexión
        if connection.is_connected():
            connection.close()
            print("✅ Conexión a la base de datos cerrada")

if __name__ == "__main__":
    main()
