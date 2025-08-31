-- =====================================================
-- ACTUALIZACIÓN TABLA PRODUCTOS - phpMyAdmin
-- =====================================================
-- Ejecutar cada bloque por separado en phpMyAdmin

-- =====================================================
-- BLOQUE 1: AGREGAR CAMPOS DE PRECIOS
-- =====================================================

ALTER TABLE productos ADD COLUMN pre_precio DECIMAL(15,2) DEFAULT 0.00 AFTER descripcion;
ALTER TABLE productos ADD COLUMN precio_a DECIMAL(15,2) DEFAULT 0.00 AFTER pre_precio;
ALTER TABLE productos ADD COLUMN precio_b DECIMAL(15,2) DEFAULT 0.00 AFTER precio_a;
ALTER TABLE productos ADD COLUMN precio_a_iva DECIMAL(15,2) DEFAULT 0.00 AFTER precio_b;
ALTER TABLE productos ADD COLUMN precio_b_iva DECIMAL(15,2) DEFAULT 0.00 AFTER precio_a_iva;
ALTER TABLE productos ADD COLUMN ultimo_costo DECIMAL(15,2) DEFAULT 0.00 AFTER precio_b_iva;
ALTER TABLE productos ADD COLUMN costo_usd DECIMAL(15,2) DEFAULT 0.00 AFTER ultimo_costo;
ALTER TABLE productos ADD COLUMN utilidad DECIMAL(10,2) DEFAULT 0.00 AFTER costo_usd;

-- =====================================================
-- BLOQUE 2: AGREGAR CAMPOS DE INVENTARIO
-- =====================================================

ALTER TABLE productos ADD COLUMN existencia INT DEFAULT 0 AFTER utilidad;
ALTER TABLE productos ADD COLUMN almacen VARCHAR(100) AFTER existencia;
ALTER TABLE productos ADD COLUMN unidad_medida VARCHAR(50) AFTER almacen;

-- =====================================================
-- BLOQUE 3: AGREGAR CAMPOS DE CLASIFICACIÓN
-- =====================================================

ALTER TABLE productos ADD COLUMN tipo_iva VARCHAR(20) AFTER unidad_medida;
ALTER TABLE productos ADD COLUMN marca VARCHAR(100) AFTER tipo_iva;
ALTER TABLE productos ADD COLUMN grupo VARCHAR(100) AFTER marca;
ALTER TABLE productos ADD COLUMN sub_grupo VARCHAR(100) AFTER grupo;
ALTER TABLE productos ADD COLUMN codigo_barras VARCHAR(100) AFTER sub_grupo;

-- =====================================================
-- BLOQUE 4: RENOMBRAR CAMPOS EXISTENTES
-- =====================================================

ALTER TABLE productos CHANGE COLUMN web_url web VARCHAR(500);
ALTER TABLE productos CHANGE COLUMN pr_field pr VARCHAR(100);
ALTER TABLE productos CHANGE COLUMN qr_code qrt VARCHAR(100);

-- =====================================================
-- BLOQUE 5: CREAR ÍNDICES
-- =====================================================

CREATE INDEX idx_codigo_barras ON productos (codigo_barras);
CREATE INDEX idx_marca ON productos (marca);
CREATE INDEX idx_grupo ON productos (grupo);
CREATE INDEX idx_sub_grupo ON productos (sub_grupo);
CREATE INDEX idx_existencia ON productos (existencia);
CREATE INDEX idx_almacen ON productos (almacen);
CREATE INDEX idx_precio_a ON productos (precio_a);
CREATE INDEX idx_precio_b ON productos (precio_b);
CREATE INDEX idx_tipo_iva ON productos (tipo_iva);

-- =====================================================
-- BLOQUE 6: VERIFICAR (OPCIONAL)
-- =====================================================

DESCRIBE productos;
SHOW INDEX FROM productos;
