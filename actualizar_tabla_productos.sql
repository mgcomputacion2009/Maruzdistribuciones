-- =====================================================
-- ACTUALIZACIÓN DE TABLA PRODUCTOS - CAMPOS NUEVOS
-- =====================================================
-- Script para agregar campos de precios, inventario y códigos de barras
-- a la tabla productos existente

-- =====================================================
-- PASO 1: AGREGAR CAMPOS DE PRECIOS
-- =====================================================

-- Precio anterior
ALTER TABLE productos ADD COLUMN pre_precio DECIMAL(15,2) DEFAULT 0.00 AFTER descripcion;

-- Precios principales
ALTER TABLE productos ADD COLUMN precio_a DECIMAL(15,2) DEFAULT 0.00 AFTER pre_precio;
ALTER TABLE productos ADD COLUMN precio_b DECIMAL(15,2) DEFAULT 0.00 AFTER precio_a;

-- Precios con IVA
ALTER TABLE productos ADD COLUMN precio_a_iva DECIMAL(15,2) DEFAULT 0.00 AFTER precio_b;
ALTER TABLE productos ADD COLUMN precio_b_iva DECIMAL(15,2) DEFAULT 0.00 AFTER precio_a_iva;

-- Costos
ALTER TABLE productos ADD COLUMN ultimo_costo DECIMAL(15,2) DEFAULT 0.00 AFTER precio_b_iva;
ALTER TABLE productos ADD COLUMN costo_usd DECIMAL(15,2) DEFAULT 0.00 AFTER ultimo_costo;

-- Utilidad
ALTER TABLE productos ADD COLUMN utilidad DECIMAL(10,2) DEFAULT 0.00 AFTER costo_usd;

-- =====================================================
-- PASO 2: AGREGAR CAMPOS DE INVENTARIO
-- =====================================================

-- Existencia/Stock
ALTER TABLE productos ADD COLUMN existencia INT DEFAULT 0 AFTER utilidad;

-- Almacén y unidad de medida
ALTER TABLE productos ADD COLUMN almacen VARCHAR(100) AFTER existencia;
ALTER TABLE productos ADD COLUMN unidad_medida VARCHAR(50) AFTER almacen;

-- =====================================================
-- PASO 3: AGREGAR CAMPOS DE CLASIFICACIÓN
-- =====================================================

-- Tipo de IVA
ALTER TABLE productos ADD COLUMN tipo_iva VARCHAR(20) AFTER unidad_medida;

-- Marca y grupos
ALTER TABLE productos ADD COLUMN marca VARCHAR(100) AFTER tipo_iva;
ALTER TABLE productos ADD COLUMN grupo VARCHAR(100) AFTER marca;
ALTER TABLE productos ADD COLUMN sub_grupo VARCHAR(100) AFTER grupo;

-- Código de barras
ALTER TABLE productos ADD COLUMN codigo_barras VARCHAR(100) AFTER sub_grupo;

-- =====================================================
-- PASO 4: CORREGIR NOMBRES DE CAMPOS EXISTENTES
-- =====================================================

-- Cambiar web_url a web para consistencia
ALTER TABLE productos CHANGE COLUMN web_url web VARCHAR(500);

-- Cambiar pr_field a pr para consistencia
ALTER TABLE productos CHANGE COLUMN pr_field pr VARCHAR(100);

-- Cambiar qr_code a qrt para consistencia
ALTER TABLE productos CHANGE COLUMN qr_code qrt VARCHAR(100);

-- =====================================================
-- PASO 5: CREAR ÍNDICES PARA BÚSQUEDAS RÁPIDAS
-- =====================================================

-- Índices para códigos de barras
CREATE INDEX idx_codigo_barras ON productos (codigo_barras);

-- Índices para marcas y grupos
CREATE INDEX idx_marca ON productos (marca);
CREATE INDEX idx_grupo ON productos (grupo);
CREATE INDEX idx_sub_grupo ON productos (sub_grupo);

-- Índices para inventario
CREATE INDEX idx_existencia ON productos (existencia);
CREATE INDEX idx_almacen ON productos (almacen);

-- Índices para precios
CREATE INDEX idx_precio_a ON productos (precio_a);
CREATE INDEX idx_precio_b ON productos (precio_b);

-- Índices para IVA
CREATE INDEX idx_tipo_iva ON productos (tipo_iva);

-- =====================================================
-- PASO 6: VERIFICAR ESTRUCTURA FINAL
-- =====================================================

-- Mostrar estructura actualizada
DESCRIBE productos;

-- Mostrar índices creados
SHOW INDEX FROM productos;

-- =====================================================
-- PASO 7: INSERTAR DATOS DE PRUEBA (OPCIONAL)
-- =====================================================

-- Insertar un producto de prueba con los nuevos campos
INSERT INTO productos (
    codigo_producto, 
    descripcion, 
    pre_precio, 
    precio_a, 
    precio_b, 
    precio_a_iva, 
    precio_b_iva, 
    ultimo_costo, 
    costo_usd, 
    utilidad, 
    existencia, 
    almacen, 
    unidad_medida, 
    tipo_iva, 
    marca, 
    grupo, 
    sub_grupo, 
    codigo_barras,
    categoria,
    empresa_id,
    ambiente,
    activo
) VALUES (
    'PROD001',
    'Aceite de motor sintético 5W-30',
    25.50,
    30.00,
    28.50,
    35.70,
    33.35,
    18.00,
    15.50,
    12.00,
    150,
    'Principal',
    'Litro',
    '19%',
    'Castrol',
    'Lubricantes',
    'Aceites de motor',
    '7891234567890',
    'Automotriz',
    2,
    'desarrollo',
    1
) ON DUPLICATE KEY UPDATE
    pre_precio = VALUES(pre_precio),
    precio_a = VALUES(precio_a),
    precio_b = VALUES(precio_b),
    precio_a_iva = VALUES(precio_a_iva),
    precio_b_iva = VALUES(precio_b_iva),
    ultimo_costo = VALUES(ultimo_costo),
    costo_usd = VALUES(costo_usd),
    utilidad = VALUES(utilidad),
    existencia = VALUES(existencia),
    almacen = VALUES(almacen),
    unidad_medida = VALUES(unidad_medida),
    tipo_iva = VALUES(tipo_iva),
    marca = VALUES(marca),
    grupo = VALUES(grupo),
    sub_grupo = VALUES(sub_grupo),
    codigo_barras = VALUES(codigo_barras),
    fecha_actualizacion = CURRENT_TIMESTAMP;

-- =====================================================
-- RESUMEN DE CAMBIOS
-- =====================================================
/*
CAMPOS AGREGADOS:
- pre_precio: Precio anterior
- precio_a: Precio A (precio regular)
- precio_b: Precio B (precio especial)
- precio_a_iva: Precio A con IVA incluido
- precio_b_iva: Precio B con IVA incluido
- ultimo_costo: Último costo de compra
- costo_usd: Costo en dólares
- utilidad: Utilidad/margen
- existencia: Stock actual
- almacen: Ubicación del almacén
- unidad_medida: Unidad de medida
- tipo_iva: Tipo de impuesto
- marca: Marca del producto
- grupo: Grupo de productos
- sub_grupo: Subgrupo específico
- codigo_barras: Código de barras

CAMPOS RENOMBRADOS:
- web_url → web
- pr_field → pr
- qr_code → qrt

ÍNDICES CREADOS:
- idx_codigo_barras
- idx_marca
- idx_grupo
- idx_sub_grupo
- idx_existencia
- idx_almacen
- idx_precio_a
- idx_precio_b
- idx_tipo_iva
*/
