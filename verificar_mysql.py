#!/usr/bin/env python3
"""
Script simple para verificar MySQL y crear tabla productos_v2
"""

import mysql.connector
from mysql.connector import Error

# Configuración de base de datos
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'maruz_db',
    'user': 'miguel',
    'password': 'Mg645418037$$',
    'charset': 'utf8mb4'
}

def main():
    print("🔄 Verificando conexión a MySQL...")
    
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✅ Conexión a MySQL establecida")
            
            cursor = connection.cursor()
            
            # Crear tabla productos_v2
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS productos_v2 (
                id INT AUTO_INCREMENT PRIMARY KEY,
                codigo_producto VARCHAR(100) NOT NULL UNIQUE,
                descripcion TEXT NOT NULL,
                pre_precio DECIMAL(15,2) DEFAULT 0.00,
                precio_a DECIMAL(15,2) DEFAULT 0.00,
                precio_b DECIMAL(15,2) DEFAULT 0.00,
                precio_a_iva DECIMAL(15,2) DEFAULT 0.00,
                precio_b_iva DECIMAL(15,2) DEFAULT 0.00,
                ultimo_costo DECIMAL(15,2) DEFAULT 0.00,
                costo_usd DECIMAL(15,2) DEFAULT 0.00,
                utilidad DECIMAL(10,2) DEFAULT 0.00,
                existencia INT DEFAULT 0,
                almacen VARCHAR(100),
                unidad_medida VARCHAR(50),
                tipo_iva VARCHAR(20),
                marca VARCHAR(100),
                grupo VARCHAR(100),
                sub_grupo VARCHAR(100),
                codigo_barras VARCHAR(100),
                imagen1 VARCHAR(255),
                imagen2 VARCHAR(255),
                imagen3 VARCHAR(255),
                imagen1_editada VARCHAR(255),
                imagen2_editada VARCHAR(255),
                imagen3_editada VARCHAR(255),
                metadata TEXT,
                nota TEXT,
                web VARCHAR(500),
                categoria VARCHAR(100),
                descripcion_producto TEXT,
                propiedades TEXT,
                datos_tecnicos TEXT,
                especificaciones TEXT,
                campos_aplicacion TEXT,
                envases_disponibles TEXT,
                pdf VARCHAR(255),
                recomendaciones TEXT,
                cont VARCHAR(100),
                pr VARCHAR(100),
                id_drive VARCHAR(100),
                qrt VARCHAR(100),
                empresa_id INT DEFAULT 2,
                ambiente VARCHAR(20) DEFAULT 'desarrollo',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT TRUE,
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
            connection.commit()
            print("✅ Tabla productos_v2 creada exitosamente")
            
            # Verificar que la tabla existe
            cursor.execute("SHOW TABLES LIKE 'productos_v2'")
            tabla_existe = cursor.fetchone()
            
            if tabla_existe:
                print("✅ Tabla productos_v2 verificada")
                
                # Mostrar estructura
                cursor.execute("DESCRIBE productos_v2")
                columnas = cursor.fetchall()
                print(f"📋 La tabla tiene {len(columnas)} columnas:")
                for columna in columnas[:10]:  # Mostrar solo las primeras 10
                    print(f"   - {columna[0]}: {columna[1]}")
                if len(columnas) > 10:
                    print(f"   ... y {len(columnas) - 10} columnas más")
            else:
                print("❌ Error: La tabla no se creó correctamente")
            
            cursor.close()
            connection.close()
            print("✅ Conexión cerrada")
            
        else:
            print("❌ No se pudo conectar a MySQL")
            
    except Error as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
