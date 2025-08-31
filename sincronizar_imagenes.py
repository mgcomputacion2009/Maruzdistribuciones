#!/usr/bin/env python3
# 🖼️ SCRIPT DE SINCRONIZACIÓN DE IMÁGENES
# Copia imágenes desde Google Drive Desktop al servidor

import os
import shutil
import json
import logging
from datetime import datetime
import mysql.connector
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/www/maruz/app/maruz_distribuciones/storage/logs/sincronizacion_imagenes.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SincronizadorImagenes:
    def __init__(self):
        # Configuración de rutas
        self.drive_local = "/mnt/c/Users/TuUsuario/Google Drive/Maruz Distribuciones/Productos"
        self.servidor_remoto = "/var/www/maruz/app/maruz_distribuciones/storage/productos"
        
        # Configuración de base de datos
        self.db_config = {
            'host': '127.0.0.1',
            'user': 'miguel',
            'password': 'Mg645418037$$',
            'database': 'maruz_db'
        }
        
        # Crear directorio de logs si no existe
        os.makedirs('/var/www/maruz/app/maruz_distribuciones/storage/logs', exist_ok=True)
    
    def get_db_connection(self):
        """Obtener conexión a la base de datos"""
        return mysql.connector.connect(**self.db_config)
    
    def obtener_productos_pendientes(self):
        """Obtiene productos que tienen imágenes registradas pero no copiadas"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT 
                p.codigo_producto,
                p.descripcion,
                pi.nombre_archivo,
                pi.url_local,
                pi.numero_imagen
            FROM productos p
            JOIN producto_imagenes pi ON p.id = pi.producto_id
            WHERE pi.nombre_archivo IS NOT NULL
            ORDER BY p.codigo_producto, pi.numero_imagen
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            logger.info(f"📊 Productos con imágenes registradas: {len(productos)}")
            return productos
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo productos: {e}")
            return []
    
    def verificar_imagen_existe(self, codigo_producto, nombre_archivo):
        """Verifica si la imagen ya existe en el servidor"""
        ruta_servidor = f"{self.servidor_remoto}/{codigo_producto}/imagenes/{nombre_archivo}"
        return os.path.exists(ruta_servidor)
    
    def copiar_imagen(self, codigo_producto, nombre_archivo, numero_imagen):
        """Copia una imagen específica desde Drive Desktop al servidor"""
        try:
            # Ruta origen (Google Drive Desktop)
            origen = f"{self.drive_local}/{codigo_producto}/{nombre_archivo}"
            
            # Ruta destino (servidor)
            destino_dir = f"{self.servidor_remoto}/{codigo_producto}/imagenes"
            destino = f"{destino_dir}/{nombre_archivo}"
            
            # Crear directorio si no existe
            os.makedirs(destino_dir, exist_ok=True)
            
            # Verificar si existe en origen
            if not os.path.exists(origen):
                logger.warning(f"⚠️ Imagen no encontrada en Drive: {origen}")
                return False
            
            # Copiar archivo
            shutil.copy2(origen, destino)
            
            # Asignar permisos
            os.chmod(destino, 0o644)
            
            # Obtener tamaño del archivo
            tamanio = os.path.getsize(destino)
            
            # Actualizar base de datos
            self.actualizar_imagen_copiada(codigo_producto, nombre_archivo, tamanio)
            
            logger.info(f"✅ Imagen {numero_imagen} copiada: {nombre_archivo} ({tamanio} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error copiando imagen {nombre_archivo}: {e}")
            return False
    
    def actualizar_imagen_copiada(self, codigo_producto, nombre_archivo, tamanio):
        """Actualiza la base de datos cuando una imagen se copia exitosamente"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            query = """
            UPDATE producto_imagenes 
            SET tamanio_bytes = %s, fecha_actualizacion = NOW()
            WHERE producto_id = (SELECT id FROM productos WHERE codigo_producto = %s)
            AND nombre_archivo = %s
            """
            
            cursor.execute(query, (tamanio, codigo_producto, nombre_archivo))
            conn.commit()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error actualizando base de datos: {e}")
    
    def sincronizar_producto(self, codigo_producto):
        """Sincroniza todas las imágenes de un producto"""
        logger.info(f"🔄 Sincronizando producto: {codigo_producto}")
        
        # Obtener imágenes del producto
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT nombre_archivo, numero_imagen, url_local
        FROM producto_imagenes 
        WHERE producto_id = (SELECT id FROM productos WHERE codigo_producto = %s)
        ORDER BY numero_imagen
        """
        
        cursor.execute(query, (codigo_producto,))
        imagenes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if not imagenes:
            logger.warning(f"⚠️ No hay imágenes registradas para: {codigo_producto}")
            return 0
        
        # Copiar cada imagen
        copiadas = 0
        for imagen in imagenes:
            if self.copiar_imagen(
                codigo_producto, 
                imagen['nombre_archivo'], 
                imagen['numero_imagen']
            ):
                copiadas += 1
        
        logger.info(f"✅ Producto {codigo_producto}: {copiadas}/{len(imagenes)} imágenes copiadas")
        return copiadas
    
    def sincronizar_documentos(self, codigo_producto):
        """Sincroniza documentos de un producto"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT nombre_archivo, tipo_documento
            FROM producto_documentos 
            WHERE producto_id = (SELECT id FROM productos WHERE codigo_producto = %s)
            """
            
            cursor.execute(query, (codigo_producto,))
            documentos = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            if not documentos:
                return 0
            
            # Copiar cada documento
            copiados = 0
            for doc in documentos:
                origen = f"{self.drive_local}/{codigo_producto}/{doc['nombre_archivo']}"
                destino_dir = f"{self.servidor_remoto}/{codigo_producto}/documentos"
                destino = f"{destino_dir}/{doc['nombre_archivo']}"
                
                # Crear directorio si no existe
                os.makedirs(destino_dir, exist_ok=True)
                
                if os.path.exists(origen):
                    shutil.copy2(origen, destino)
                    os.chmod(destino, 0o644)
                    copiados += 1
                    logger.info(f"📄 Documento copiado: {doc['nombre_archivo']}")
                else:
                    logger.warning(f"⚠️ Documento no encontrado: {origen}")
            
            return copiados
            
        except Exception as e:
            logger.error(f"❌ Error sincronizando documentos: {e}")
            return 0
    
    def ejecutar_sincronizacion(self):
        """Ejecuta la sincronización completa"""
        logger.info("🚀 INICIANDO SINCRONIZACIÓN DE IMÁGENES Y DOCUMENTOS")
        logger.info("=" * 60)
        logger.info(f"⏰ Timestamp: {datetime.now()}")
        logger.info(f"📁 Drive Local: {self.drive_local}")
        logger.info(f"📁 Servidor: {self.servidor_remoto}")
        logger.info("=" * 60)
        
        # Obtener productos pendientes
        productos = self.obtener_productos_pendientes()
        
        if not productos:
            logger.info("✅ No hay productos pendientes de sincronización")
            return
        
        # Agrupar por producto
        productos_unicos = {}
        for producto in productos:
            codigo = producto['codigo_producto']
            if codigo not in productos_unicos:
                productos_unicos[codigo] = []
            productos_unicos[codigo].append(producto)
        
        logger.info(f"📦 Productos únicos a sincronizar: {len(productos_unicos)}")
        
        # Sincronizar cada producto
        total_imagenes = 0
        total_documentos = 0
        
        for codigo_producto in productos_unicos:
            # Sincronizar imágenes
            imagenes_copiadas = self.sincronizar_producto(codigo_producto)
            total_imagenes += imagenes_copiadas
            
            # Sincronizar documentos
            documentos_copiados = self.sincronizar_documentos(codigo_producto)
            total_documentos += documentos_copiados
            
            logger.info(f"📊 {codigo_producto}: {imagenes_copiadas} imágenes, {documentos_copiados} documentos")
        
        # Resumen final
        logger.info("=" * 60)
        logger.info("📊 RESUMEN DE SINCRONIZACIÓN")
        logger.info("=" * 60)
        logger.info(f"📦 Productos procesados: {len(productos_unicos)}")
        logger.info(f"🖼️ Imágenes copiadas: {total_imagenes}")
        logger.info(f"📄 Documentos copiados: {total_documentos}")
        logger.info(f"⏰ Finalizado: {datetime.now()}")
        logger.info("=" * 60)
        
        if total_imagenes > 0 or total_documentos > 0:
            logger.info("🎉 ¡SINCRONIZACIÓN COMPLETADA EXITOSAMENTE!")
        else:
            logger.info("⚠️ No se copió ningún archivo. Verificar rutas y permisos.")

def main():
    """Función principal"""
    try:
        sincronizador = SincronizadorImagenes()
        sincronizador.ejecutar_sincronizacion()
    except Exception as e:
        logger.error(f"❌ Error en sincronización: {e}", exc_info=True)

if __name__ == "__main__":
    main()
