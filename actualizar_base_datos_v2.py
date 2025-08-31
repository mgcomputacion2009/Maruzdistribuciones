#!/usr/bin/env python3
"""
Script para actualizar la base de datos MySQL con la nueva estructura de productos v2
Incluye todos los campos de precios, inventario y códigos de barras
"""

import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de base de datos
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'maruz_db',
    'user': 'miguel',
    'password': 'Mg645418037$$',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def get_db_connection():
    """Crear conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            logger.info("✅ Conexión a MySQL establecida")
            return connection
    except Error as e:
        logger.error(f"❌ Error conectando a MySQL: {e}")
        raise

def crear_tabla_productos_v2():
    """Crear la tabla productos_v2 con todos los campos nuevos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SQL para crear la tabla productos_v2
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS productos_v2 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            
            -- Campos de identificación
            codigo_producto VARCHAR(100) NOT NULL UNIQUE,
            descripcion TEXT NOT NULL,
            
            -- Campos de precios
            pre_precio DECIMAL(15,2) DEFAULT 0.00,
            precio_a DECIMAL(15,2) DEFAULT 0.00,
            precio_b DECIMAL(15,2) DEFAULT 0.00,
            precio_a_iva DECIMAL(15,2) DEFAULT 0.00,
            precio_b_iva DECIMAL(15,2) DEFAULT 0.00,
            ultimo_costo DECIMAL(15,2) DEFAULT 0.00,
            costo_usd DECIMAL(15,2) DEFAULT 0.00,
            utilidad DECIMAL(10,2) DEFAULT 0.00,
            
            -- Campos de inventario
            existencia INT DEFAULT 0,
            almacen VARCHAR(100),
            unidad_medida VARCHAR(50),
            
            -- Campos de clasificación
            tipo_iva VARCHAR(20),
            marca VARCHAR(100),
            grupo VARCHAR(100),
            sub_grupo VARCHAR(100),
            
            -- Campos de códigos
            codigo_barras VARCHAR(100),
            
            -- Campos de imágenes (mantener compatibilidad)
            imagen1 VARCHAR(255),
            imagen2 VARCHAR(255),
            imagen3 VARCHAR(255),
            imagen1_editada VARCHAR(255),
            imagen2_editada VARCHAR(255),
            imagen3_editada VARCHAR(255),
            
            -- Campos de información adicional
            metadata TEXT,
            nota TEXT,
            web VARCHAR(500),
            categoria VARCHAR(100),
            descripcion_producto TEXT,
            
            -- Campos técnicos
            propiedades TEXT,
            datos_tecnicos TEXT,
            especificaciones TEXT,
            campos_aplicacion TEXT,
            envases_disponibles TEXT,
            
            -- Campos adicionales
            pdf VARCHAR(255),
            recomendaciones TEXT,
            cont VARCHAR(100),
            pr VARCHAR(100),
            id_drive VARCHAR(100),
            qrt VARCHAR(100),
            
            -- Campos de sistema
            empresa_id INT DEFAULT 2,
            ambiente VARCHAR(20) DEFAULT 'desarrollo',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE,
            
            -- Índices para búsquedas rápidas
            INDEX idx_codigo (codigo_producto),
            INDEX idx_barras (codigo_barras),
            INDEX idx_marca (marca),
            INDEX idx_grupo (grupo),
            INDEX idx_sub_grupo (sub_grupo),
            INDEX idx_categoria (categoria),
            INDEX idx_empresa (empresa_id),
            INDEX idx_activo (activo),
            INDEX idx_existencia (existencia),
            INDEX idx_precio_a (precio_a),
            INDEX idx_precio_b (precio_b),
            INDEX idx_almacen (almacen),
            INDEX idx_tipo_iva (tipo_iva)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        logger.info("✅ Tabla productos_v2 creada exitosamente")
        
        return True
        
    except Error as e:
        logger.error(f"❌ Error creando tabla productos_v2: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def actualizar_tabla_productos_existente():
    """Actualizar la tabla productos existente con los nuevos campos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si la tabla productos existe
        cursor.execute("SHOW TABLES LIKE 'productos'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            logger.warning("⚠️ La tabla 'productos' no existe, se creará productos_v2")
            return crear_tabla_productos_v2()
        
        # Lista de campos nuevos a agregar
        campos_nuevos = [
            ("pre_precio", "DECIMAL(15,2) DEFAULT 0.00"),
            ("precio_a", "DECIMAL(15,2) DEFAULT 0.00"),
            ("precio_b", "DECIMAL(15,2) DEFAULT 0.00"),
            ("precio_a_iva", "DECIMAL(15,2) DEFAULT 0.00"),
            ("precio_b_iva", "DECIMAL(15,2) DEFAULT 0.00"),
            ("ultimo_costo", "DECIMAL(15,2) DEFAULT 0.00"),
            ("costo_usd", "DECIMAL(15,2) DEFAULT 0.00"),
            ("utilidad", "DECIMAL(10,2) DEFAULT 0.00"),
            ("existencia", "INT DEFAULT 0"),
            ("almacen", "VARCHAR(100)"),
            ("unidad_medida", "VARCHAR(50)"),
            ("tipo_iva", "VARCHAR(20)"),
            ("marca", "VARCHAR(100)"),
            ("grupo", "VARCHAR(100)"),
            ("sub_grupo", "VARCHAR(100)"),
            ("codigo_barras", "VARCHAR(100)")
        ]
        
        # Obtener estructura actual de la tabla
        cursor.execute("DESCRIBE productos")
        columnas_existentes = [row[0] for row in cursor.fetchall()]
        
        # Agregar campos que no existen
        campos_agregados = 0
        for campo, tipo in campos_nuevos:
            if campo not in columnas_existentes:
                try:
                    alter_sql = f"ALTER TABLE productos ADD COLUMN {campo} {tipo}"
                    cursor.execute(alter_sql)
                    logger.info(f"✅ Campo agregado: {campo}")
                    campos_agregados += 1
                except Error as e:
                    logger.warning(f"⚠️ Error agregando campo {campo}: {e}")
        
        # Crear índices para los nuevos campos
        indices_nuevos = [
            ("idx_barras", "codigo_barras"),
            ("idx_marca", "marca"),
            ("idx_grupo", "grupo"),
            ("idx_sub_grupo", "sub_grupo"),
            ("idx_existencia", "existencia"),
            ("idx_precio_a", "precio_a"),
            ("idx_precio_b", "precio_b"),
            ("idx_almacen", "almacen"),
            ("idx_tipo_iva", "tipo_iva")
        ]
        
        # Obtener índices existentes
        cursor.execute("SHOW INDEX FROM productos")
        indices_existentes = [row[2] for row in cursor.fetchall()]
        
        # Agregar índices que no existen
        indices_agregados = 0
        for nombre_indice, campo in indices_nuevos:
            if nombre_indice not in indices_existentes:
                try:
                    index_sql = f"CREATE INDEX {nombre_indice} ON productos ({campo})"
                    cursor.execute(index_sql)
                    logger.info(f"✅ Índice agregado: {nombre_indice} en {campo}")
                    indices_agregados += 1
                except Error as e:
                    logger.warning(f"⚠️ Error agregando índice {nombre_indice}: {e}")
        
        conn.commit()
        logger.info(f"✅ Actualización completada: {campos_agregados} campos y {indices_agregados} índices agregados")
        
        return True
        
    except Error as e:
        logger.error(f"❌ Error actualizando tabla productos: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def verificar_estructura_tabla():
    """Verificar la estructura actual de la tabla"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar tabla productos_v2
        cursor.execute("SHOW TABLES LIKE 'productos_v2'")
        tabla_v2_existe = cursor.fetchone()
        
        if tabla_v2_existe:
            cursor.execute("DESCRIBE productos_v2")
            columnas_v2 = cursor.fetchall()
            logger.info("📋 Estructura de tabla productos_v2:")
            for columna in columnas_v2:
                logger.info(f"   - {columna[0]}: {columna[1]}")
        
        # Verificar tabla productos
        cursor.execute("SHOW TABLES LIKE 'productos'")
        tabla_existe = cursor.fetchone()
        
        if tabla_existe:
            cursor.execute("DESCRIBE productos")
            columnas = cursor.fetchall()
            logger.info("📋 Estructura de tabla productos:")
            for columna in columnas:
                logger.info(f"   - {columna[0]}: {columna[1]}")
        
        # Verificar índices
        if tabla_v2_existe:
            cursor.execute("SHOW INDEX FROM productos_v2")
            indices_v2 = cursor.fetchall()
            logger.info("🔍 Índices de tabla productos_v2:")
            for indice in indices_v2:
                logger.info(f"   - {indice[2]} en {indice[4]}")
        
        if tabla_existe:
            cursor.execute("SHOW INDEX FROM productos")
            indices = cursor.fetchall()
            logger.info("🔍 Índices de tabla productos:")
            for indice in indices:
                logger.info(f"   - {indice[2]} en {indice[4]}")
        
        return True
        
    except Error as e:
        logger.error(f"❌ Error verificando estructura: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def insertar_datos_prueba():
    """Insertar datos de prueba en la tabla productos_v2"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'productos_v2'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            logger.error("❌ La tabla productos_v2 no existe")
            return False
        
        # Datos de prueba
        datos_prueba = [
            {
                'codigo_producto': 'PROD001',
                'descripcion': 'Aceite de motor sintético 5W-30',
                'pre_precio': 25.50,
                'precio_a': 30.00,
                'precio_b': 28.50,
                'precio_a_iva': 35.70,
                'precio_b_iva': 33.35,
                'ultimo_costo': 18.00,
                'costo_usd': 15.50,
                'utilidad': 12.00,
                'existencia': 150,
                'almacen': 'Principal',
                'unidad_medida': 'Litro',
                'tipo_iva': '19%',
                'marca': 'Castrol',
                'grupo': 'Lubricantes',
                'sub_grupo': 'Aceites de motor',
                'codigo_barras': '7891234567890'
            },
            {
                'codigo_producto': 'PROD002',
                'descripcion': 'Filtro de aire de alto rendimiento',
                'pre_precio': 15.00,
                'precio_a': 18.50,
                'precio_b': 17.00,
                'precio_a_iva': 22.02,
                'precio_b_iva': 20.23,
                'ultimo_costo': 12.00,
                'costo_usd': 10.00,
                'utilidad': 6.50,
                'existencia': 75,
                'almacen': 'Secundario',
                'unidad_medida': 'Unidad',
                'tipo_iva': '19%',
                'marca': 'K&N',
                'grupo': 'Filtros',
                'sub_grupo': 'Filtros de aire',
                'codigo_barras': '7891234567891'
            }
        ]
        
        # Insertar datos de prueba
        for dato in datos_prueba:
            campos = ', '.join(dato.keys())
            valores = ', '.join(['%s'] * len(dato))
            insert_sql = f"INSERT INTO productos_v2 ({campos}) VALUES ({valores})"
            
            try:
                cursor.execute(insert_sql, list(dato.values()))
                logger.info(f"✅ Dato de prueba insertado: {dato['codigo_producto']}")
            except Error as e:
                if "Duplicate entry" in str(e):
                    logger.info(f"ℹ️ Producto ya existe: {dato['codigo_producto']}")
                else:
                    logger.error(f"❌ Error insertando {dato['codigo_producto']}: {e}")
        
        conn.commit()
        logger.info("✅ Datos de prueba insertados exitosamente")
        
        return True
        
    except Error as e:
        logger.error(f"❌ Error insertando datos de prueba: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def main():
    """Función principal"""
    print("🔄 ACTUALIZACIÓN DE BASE DE DATOS - PRODUCTOS V2")
    print("=" * 60)
    
    # Paso 1: Crear tabla productos_v2
    print("\n1️⃣ Creando tabla productos_v2...")
    if crear_tabla_productos_v2():
        print("✅ Tabla productos_v2 creada exitosamente")
    else:
        print("❌ Error creando tabla productos_v2")
        return
    
    # Paso 2: Actualizar tabla productos existente
    print("\n2️⃣ Actualizando tabla productos existente...")
    if actualizar_tabla_productos_existente():
        print("✅ Tabla productos actualizada exitosamente")
    else:
        print("❌ Error actualizando tabla productos")
    
    # Paso 3: Verificar estructura
    print("\n3️⃣ Verificando estructura de tablas...")
    if verificar_estructura_tabla():
        print("✅ Estructura verificada exitosamente")
    else:
        print("❌ Error verificando estructura")
    
    # Paso 4: Insertar datos de prueba
    print("\n4️⃣ Insertando datos de prueba...")
    if insertar_datos_prueba():
        print("✅ Datos de prueba insertados exitosamente")
    else:
        print("❌ Error insertando datos de prueba")
    
    print("\n" + "=" * 60)
    print("✅ Actualización de base de datos completada")
    print("\n📋 Resumen:")
    print("   - Tabla productos_v2 creada con todos los campos nuevos")
    print("   - Tabla productos actualizada con campos adicionales")
    print("   - Índices optimizados para búsquedas rápidas")
    print("   - Datos de prueba insertados")
    print("\n🌐 Endpoints disponibles:")
    print("   - POST http://34.57.121.200:8002/api/productos/cargar_v2")
    print("   - GET  http://34.57.121.200:8002/api/productos/status_v2")

if __name__ == "__main__":
    main()
