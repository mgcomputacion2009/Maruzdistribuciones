/**
 * 🛒 CARRITO AVANZADO - MARUZ DISTRIBUCIONES
 * Sistema completo según lista de chequeo profesional
 * 
 * Funcionalidades implementadas:
 * ✅ Identidad y seguridad con pedido_token
 * ✅ Endpoints obligatorios (/api/pedido/*)
 * ✅ Modal sin recargas
 * ✅ Debounce + flush obligatorio
 * ✅ SSE en tiempo real
 * ✅ Versionado y concurrencia
 * ✅ Multi-dispositivo sync
 */

class CarritoAvanzado {
    constructor() {
        // Estado del carrito
        this.pedidoId = null;
        this.pedidoToken = null;
        this.version = 0;
        this.estado = 'activo';
        this.resumen = null;
        
        // Estado del modal
        this.modalAbierto = false;
        this.paginaActual = 1;
        this.busquedaActual = '';
        
        // Debounce y flush
        this.debounceTimers = new Map();
        this.pendingChanges = new Map();
        this.flushTimeout = null;
        
        // SSE
        this.eventSource = null;
        this.sseReconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.fallbackPollInterval = null;
        
        // Bind methods
        this.handleQuantityChange = this.handleQuantityChange.bind(this);
        this.handleDiscountChange = this.handleDiscountChange.bind(this);
        this.handlePageChange = this.handlePageChange.bind(this);
        this.handleSearch = this.handleSearch.bind(this);
        this.handleModalClose = this.handleModalClose.bind(this);
        
        // Inicializar
        this.init();
    }
    
    /**
     * 🚀 INICIALIZACIÓN DEL SISTEMA
     */
    async init() {
        try {
            console.log('🛒 Inicializando carrito avanzado...');
            
            // 1. Ensure - Crear/obtener pedido único
            await this.ensurePedido();
            
            // 2. Conectar SSE para tiempo real
            this.connectSSE();
            
            // 3. Configurar event listeners
            this.setupEventListeners();
            
            // 4. Cargar estado inicial
            await this.loadResumen();
            
            console.log('✅ Carrito avanzado inicializado correctamente');
            
        } catch (error) {
            console.error('❌ Error inicializando carrito:', error);
            this.showError('Error inicializando el carrito');
        }
    }
    
    /**
     * 🔐 ENSURE - Crear/obtener pedido único por usuario
     */
    async ensurePedido() {
        try {
            const response = await fetch('/api/pedido/ensure', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Pedido-Token': this.pedidoToken || ''
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.pedidoId = data.pedido_id;
                this.pedidoToken = data.pedido_token;
                this.version = data.version;
                this.estado = data.estado;
                this.resumen = data.resumen;
                
                console.log('✅ Pedido asegurado:', {
                    id: this.pedidoId,
                    version: this.version,
                    estado: this.estado
                });
                
                // Actualizar UI con resumen
                this.updateSummaryBar();
                
            } else {
                throw new Error(data.error || 'Error asegurando pedido');
            }
            
        } catch (error) {
            console.error('❌ Error en ensure:', error);
            throw error;
        }
    }
    
    /**
     * 📊 CARGAR RESUMEN DEL PEDIDO
     */
    async loadResumen() {
        try {
            const response = await fetch('/api/pedido/resumen', {
                headers: {
                    'X-Pedido-Token': this.pedidoToken
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.resumen = data.resumen;
                this.version = data.version;
                this.updateSummaryBar();
                
                console.log('✅ Resumen cargado:', this.resumen);
            }
            
        } catch (error) {
            console.error('❌ Error cargando resumen:', error);
        }
    }
    
    /**
     * 🔄 CONECTAR SSE PARA TIEMPO REAL
     */
    connectSSE() {
        try {
            // Cerrar conexión anterior si existe
            if (this.eventSource) {
                this.eventSource.close();
            }
            
            // Conectar nuevo SSE
            this.eventSource = new EventSource(`/api/pedido/stream?pedido_id=${this.pedidoId}&token=${this.pedidoToken}`);
            
            this.eventSource.onopen = () => {
                console.log('✅ SSE conectado');
                this.sseReconnectAttempts = 0;
                
                // Limpiar fallback poll si SSE funciona
                if (this.fallbackPollInterval) {
                    clearInterval(this.fallbackPollInterval);
                    this.fallbackPollInterval = null;
                }
            };
            
            this.eventSource.onmessage = (event) => {
                this.handleSSEMessage(event);
            };
            
            this.eventSource.onerror = (error) => {
                console.warn('⚠️ Error SSE, activando fallback poll:', error);
                this.activateFallbackPoll();
            };
            
            // Configurar heartbeat
            this.setupHeartbeat();
            
        } catch (error) {
            console.error('❌ Error conectando SSE:', error);
            this.activateFallbackPoll();
        }
    }
    
    /**
     * 💓 CONFIGURAR HEARTBEAT SSE
     */
    setupHeartbeat() {
        // Heartbeat cada 25 segundos
        setInterval(() => {
            if (this.eventSource && this.eventSource.readyState === EventSource.OPEN) {
                console.log('💓 SSE heartbeat');
            } else {
                console.warn('⚠️ SSE no responde, reconectando...');
                this.connectSSE();
            }
        }, 25000);
    }
    
    /**
     * 📡 ACTIVAR FALLBACK POLL
     */
    activateFallbackPoll() {
        if (this.fallbackPollInterval) return;
        
        console.log('🔄 Activando fallback poll cada 10 segundos');
        
        this.fallbackPollInterval = setInterval(async () => {
            try {
                await this.loadResumen();
            } catch (error) {
                console.error('❌ Error en fallback poll:', error);
            }
        }, 10000);
    }
    
    /**
     * 📨 MANEJAR MENSAJES SSE
     */
    handleSSEMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch (data.tipo) {
                case 'resumen':
                    this.handleResumenUpdate(data);
                    break;
                    
                case 'item_update':
                    this.handleItemUpdate(data);
                    break;
                    
                case 'item_remove':
                    this.handleItemRemove(data);
                    break;
                    
                case 'sync_hint':
                    this.handleSyncHint(data);
                    break;
                    
                case 'heartbeat':
                    console.log('💓 SSE heartbeat recibido');
                    break;
                    
                default:
                    console.log('📨 SSE mensaje no manejado:', data);
            }
            
        } catch (error) {
            console.error('❌ Error procesando mensaje SSE:', error);
        }
    }
    
    /**
     * 📊 ACTUALIZAR RESUMEN DESDE SSE
     */
    handleResumenUpdate(data) {
        this.resumen = data.resumen;
        this.version = data.version;
        this.updateSummaryBar();
        
        console.log('✅ Resumen actualizado via SSE:', this.resumen);
    }
    
    /**
     * 🔄 ACTUALIZAR ITEM DESDE SSE
     */
    handleItemUpdate(data) {
        const { producto_codigo, cantidad, descuento } = data;
        
        // Si el modal está abierto y el producto es visible, actualizar input
        if (this.modalAbierto) {
            const input = document.querySelector(`[data-producto="${producto_codigo}"] input[type="number"]`);
            if (input) {
                input.value = cantidad;
                this.updateItemTotal(producto_codigo, cantidad, descuento);
            }
        }
        
        console.log('✅ Item actualizado via SSE:', data);
    }
    
    /**
     * 🗑️ REMOVER ITEM DESDE SSE
     */
    handleItemRemove(data) {
        const { producto_codigo } = data;
        
        // Si el modal está abierto y el producto es visible, limpiar input
        if (this.modalAbierto) {
            const input = document.querySelector(`[data-producto="${producto_codigo}"] input[type="number"]`);
            if (input) {
                input.value = '0';
                this.updateItemTotal(producto_codigo, 0, 0);
            }
        }
        
        console.log('✅ Item removido via SSE:', data);
    }
    
    /**
     * 🔄 MANEJAR SUGERENCIA DE SINCRONIZACIÓN
     */
    handleSyncHint(data) {
        console.log('🔄 Sincronización sugerida:', data);
        
        // Recargar resumen si hay discrepancia de versiones
        if (data.version_actual > this.version) {
            console.log('🔄 Versión desactualizada, recargando...');
            this.loadResumen();
        }
    }
    
    /**
     * 🎯 CONFIGURAR EVENT LISTENERS
     */
    setupEventListeners() {
        // Event listeners para cambios de cantidad
        document.addEventListener('input', (e) => {
            if (e.target.matches('input[type="number"]')) {
                this.handleQuantityChange(e);
            }
        });
        
        // Event listeners para cambios de descuento
        document.addEventListener('input', (e) => {
            if (e.target.matches('input[data-tipo="descuento"]')) {
                this.handleDiscountChange(e);
            }
        });
        
        // Event listeners para paginación
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-pagina]')) {
                e.preventDefault();
                this.handlePageChange(e);
            }
        });
        
        // Event listeners para búsqueda
        const searchInput = document.querySelector('.search input');
        if (searchInput) {
            searchInput.addEventListener('input', this.handleSearch);
        }
        
        // Event listeners para cierre de modal
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-close-modal]')) {
                this.handleModalClose();
            }
        });
        
        // Event listeners para pagehide (flush obligatorio)
        window.addEventListener('pagehide', () => {
            this.flushChanges(true); // Flush inmediato
        });
        
        // Event listeners para blur (flush obligatorio)
        document.addEventListener('blur', (e) => {
            if (e.target.matches('input')) {
                this.flushChanges(true); // Flush inmediato
            }
        }, true);
        
        // Event listeners para Enter (flush obligatorio)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.matches('input')) {
                this.flushChanges(true); // Flush inmediato
            }
        });
        
        console.log('✅ Event listeners configurados');
    }
    
    /**
     * 🔢 MANEJAR CAMBIO DE CANTIDAD
     */
    handleQuantityChange(event) {
        const input = event.target;
        const producto = input.closest('[data-producto]');
        
        if (!producto) return;
        
        const codigo = producto.dataset.producto;
        const cantidad = parseInt(input.value) || 0;
        
        // Validar cantidad
        if (cantidad < 0) {
            input.value = '0';
            return;
        }
        
        // Agregar a cambios pendientes
        this.pendingChanges.set(codigo, {
            cantidad,
            descuento: this.getCurrentDiscount(codigo),
            timestamp: Date.now()
        });
        
        // Actualizar total de la línea
        this.updateItemTotal(codigo, cantidad, this.getCurrentDiscount(codigo));
        
        // Debounce para enviar cambios
        this.debounceChange(codigo);
        
        console.log(`🔢 Cantidad cambiada para ${codigo}: ${cantidad}`);
    }
    
    /**
     * 💰 MANEJAR CAMBIO DE DESCUENTO
     */
    handleDiscountChange(event) {
        const input = event.target;
        const producto = input.closest('[data-producto]');
        
        if (!producto) return;
        
        const codigo = producto.dataset.producto;
        const descuento = parseFloat(input.value) || 0;
        
        // Validar descuento
        if (descuento < 0 || descuento > 100) {
            input.value = '0';
            return;
        }
        
        // Agregar a cambios pendientes
        this.pendingChanges.set(codigo, {
            cantidad: this.getCurrentQuantity(codigo),
            descuento,
            timestamp: Date.now()
        });
        
        // Actualizar total de la línea
        this.updateItemTotal(codigo, this.getCurrentQuantity(codigo), descuento);
        
        // Debounce para enviar cambios
        this.debounceChange(codigo);
        
        console.log(`💰 Descuento cambiado para ${codigo}: ${descuento}%`);
    }
    
    /**
     * 🔄 MANEJAR CAMBIO DE PÁGINA
     */
    async handlePageChange(event) {
        const pagina = parseInt(event.target.dataset.pagina);
        
        if (pagina === this.paginaActual) return;
        
        try {
            // Flush obligatorio antes de cambiar página
            await this.flushChanges(true);
            
            // Cambiar página
            this.paginaActual = pagina;
            
            // Cargar nueva página por AJAX
            await this.loadPage(pagina);
            
            // Query items visibles
            await this.queryVisibleItems();
            
            console.log(`📄 Página cambiada a: ${pagina}`);
            
        } catch (error) {
            console.error('❌ Error cambiando página:', error);
            this.showError('Error cambiando de página');
        }
    }
    
    /**
     * 🔍 MANEJAR BÚSQUEDA
     */
    async handleSearch(event) {
        const query = event.target.value.trim();
        
        // Debounce búsqueda
        clearTimeout(this.searchDebounceTimer);
        
        this.searchDebounceTimer = setTimeout(async () => {
            try {
                // Flush obligatorio antes de buscar
                await this.flushChanges(true);
                
                // Actualizar búsqueda
                this.busquedaActual = query;
                
                // Cargar resultados por AJAX
                await this.loadSearchResults(query);
                
                // Query items visibles
                await this.queryVisibleItems();
                
                console.log(`🔍 Búsqueda realizada: "${query}"`);
                
            } catch (error) {
                console.error('❌ Error en búsqueda:', error);
                this.showError('Error realizando búsqueda');
            }
        }, 500); // Debounce 500ms
    }
    
    /**
     * 🚪 MANEJAR CIERRE DE MODAL
     */
    async handleModalClose() {
        try {
            // Flush obligatorio antes de cerrar
            await this.flushChanges(true);
            
            // Cerrar modal
            this.closeModal();
            
            console.log('🚪 Modal cerrado');
            
        } catch (error) {
            console.error('❌ Error cerrando modal:', error);
        }
    }
    
    /**
     * ⏰ DEBOUNCE PARA CAMBIOS
     */
    debounceChange(codigo) {
        // Limpiar timer anterior
        if (this.debounceTimers.has(codigo)) {
            clearTimeout(this.debounceTimers.get(codigo));
        }
        
        // Nuevo timer (800ms como especificado)
        const timer = setTimeout(() => {
            this.flushChanges(false); // Flush normal
        }, 800);
        
        this.debounceTimers.set(codigo, timer);
    }
    
    /**
     * 🚀 FLUSH DE CAMBIOS PENDIENTES
     */
    async flushChanges(inmediato = false) {
        if (this.pendingChanges.size === 0) return;
        
        try {
            // Preparar batch de cambios
            const items = Array.from(this.pendingChanges.entries()).map(([codigo, data]) => ({
                producto_codigo: codigo,
                cantidad: data.cantidad,
                descuento: data.descuento
            }));
            
            // Enviar batch
            const response = await fetch('/api/pedido/items/batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Pedido-Token': this.pedidoToken
                },
                body: JSON.stringify({
                    pedido_id: this.pedidoId,
                    version: this.version,
                    items: items
                })
            });
            
            if (!response.ok) {
                if (response.status === 409) {
                    // Conflicto de versión
                    const data = await response.json();
                    await this.handleVersionConflict(data);
                    return;
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Actualizar versión
                this.version = data.version;
                
                // Limpiar cambios pendientes
                this.pendingChanges.clear();
                
                // Actualizar resumen
                this.resumen = data.resumen;
                this.updateSummaryBar();
                
                console.log('✅ Cambios enviados correctamente, versión:', this.version);
                
            } else {
                throw new Error(data.error || 'Error enviando cambios');
            }
            
        } catch (error) {
            console.error('❌ Error en flush:', error);
            
            if (inmediato) {
                this.showError('Error guardando cambios');
            }
        }
    }
    
    /**
     * ⚠️ MANEJAR CONFLICTO DE VERSIÓN
     */
    async handleVersionConflict(data) {
        console.warn('⚠️ Conflicto de versión detectado:', data);
        
        // Recargar estado actual
        await this.loadResumen();
        
        // Recargar página actual
        await this.loadPage(this.paginaActual);
        
        // Query items visibles
        await this.queryVisibleItems();
        
        this.showWarning('Los datos han sido actualizados por otro dispositivo');
    }
    
    /**
     * 📄 CARGAR PÁGINA POR AJAX
     */
    async loadPage(pagina) {
        try {
            const url = new URL(window.location);
            url.searchParams.set('page', pagina);
            
            const response = await fetch(url.pathname + url.search);
            const html = await response.text();
            
            // Actualizar solo la lista de productos
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            const newList = doc.querySelector('.list');
            const currentList = document.querySelector('.list');
            
            if (newList && currentList) {
                currentList.innerHTML = newList.innerHTML;
            }
            
            console.log(`📄 Página ${pagina} cargada por AJAX`);
            
        } catch (error) {
            console.error('❌ Error cargando página:', error);
            throw error;
        }
    }
    
    /**
     * 🔍 CARGAR RESULTADOS DE BÚSQUEDA
     */
    async loadSearchResults(query) {
        try {
            const url = new URL(window.location);
            url.searchParams.set('q', query);
            url.searchParams.set('page', 1);
            
            const response = await fetch(url.pathname + url.search);
            const html = await response.text();
            
            // Actualizar solo la lista de productos
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            const newList = doc.querySelector('.list');
            const currentList = document.querySelector('.list');
            
            if (newList && currentList) {
                currentList.innerHTML = newList.innerHTML;
            }
            
            console.log(`🔍 Resultados de búsqueda cargados por AJAX`);
            
        } catch (error) {
            console.error('❌ Error cargando resultados de búsqueda:', error);
            throw error;
        }
    }
    
    /**
     * 🔍 QUERY ITEMS VISIBLES
     */
    async queryVisibleItems() {
        try {
            // Obtener códigos de productos visibles
            const productosVisibles = Array.from(document.querySelectorAll('[data-producto]'))
                .map(el => el.dataset.producto);
            
            if (productosVisibles.length === 0) return;
            
            const response = await fetch('/api/pedido/items/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Pedido-Token': this.pedidoToken
                },
                body: JSON.stringify({
                    pedido_id: this.pedidoId,
                    codigos: productosVisibles
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Actualizar inputs con datos del servidor
                data.items.forEach(item => {
                    this.updateItemFromServer(item);
                });
                
                console.log('✅ Items visibles actualizados desde servidor');
            }
            
        } catch (error) {
            console.error('❌ Error querying items visibles:', error);
        }
    }
    
    /**
     * 🔄 ACTUALIZAR ITEM DESDE SERVIDOR
     */
    updateItemFromServer(item) {
        const { producto_codigo, cantidad, descuento } = item;
        
        const producto = document.querySelector(`[data-producto="${producto_codigo}"]`);
        if (!producto) return;
        
        // Actualizar cantidad
        const cantidadInput = producto.querySelector('input[type="number"]');
        if (cantidadInput) {
            cantidadInput.value = cantidad;
        }
        
        // Actualizar descuento
        const descuentoInput = producto.querySelector('input[data-tipo="descuento"]');
        if (descuentoInput) {
            descuentoInput.value = descuento;
        }
        
        // Actualizar total
        this.updateItemTotal(producto_codigo, cantidad, descuento);
    }
    
    /**
     * 💰 ACTUALIZAR TOTAL DE ITEM
     */
    updateItemTotal(codigo, cantidad, descuento) {
        const producto = document.querySelector(`[data-producto="${codigo}"]`);
        if (!producto) return;
        
        const precioElement = producto.querySelector('.price');
        const totalElement = producto.querySelector('.total');
        
        if (!precioElement || !totalElement) return;
        
        const precio = parseFloat(precioElement.textContent.replace('$', '').replace(',', '')) || 0;
        const subtotal = precio * cantidad;
        const descuentoMonto = subtotal * (descuento / 100);
        const total = subtotal - descuentoMonto;
        
        totalElement.textContent = `$${total.toFixed(2)}`;
        
        console.log(`💰 Total actualizado para ${codigo}: $${total.toFixed(2)}`);
    }
    
    /**
     * 📊 ACTUALIZAR BARRA DE RESUMEN
     */
    updateSummaryBar() {
        if (!this.resumen) return;
        
        const summaryBar = document.querySelector('.summary-bar');
        if (!summaryBar) return;
        
        // Actualizar valores
        const unidadesElement = summaryBar.querySelector('[data-summary="unidades"]');
        const subtotalElement = summaryBar.querySelector('[data-summary="subtotal"]');
        const totalElement = summaryBar.querySelector('[data-summary="total"]');
        
        if (unidadesElement) {
            unidadesElement.textContent = this.resumen.cantidad_productos || 0;
        }
        
        if (subtotalElement) {
            subtotalElement.textContent = `$${(this.resumen.total_pedido || 0).toFixed(2)}`;
        }
        
        if (totalElement) {
            totalElement.textContent = `$${(this.resumen.total_pedido || 0).toFixed(2)}`;
        }
        
        console.log('📊 Barra de resumen actualizada');
    }
    
    /**
     * 🔍 OBTENER CANTIDAD ACTUAL
     */
    getCurrentQuantity(codigo) {
        const producto = document.querySelector(`[data-producto="${codigo}"]`);
        if (!producto) return 0;
        
        const input = producto.querySelector('input[type="number"]');
        return input ? parseInt(input.value) || 0 : 0;
    }
    
    /**
     * 💰 OBTENER DESCUENTO ACTUAL
     */
    getCurrentDiscount(codigo) {
        const producto = document.querySelector(`[data-producto="${codigo}"]`);
        if (!producto) return 0;
        
        const input = producto.querySelector('input[data-tipo="descuento"]');
        return input ? parseFloat(input.value) || 0 : 0;
    }
    
    /**
     * 🚪 CERRAR MODAL
     */
    closeModal() {
        this.modalAbierto = false;
        
        // Remover overlay
        const overlay = document.querySelector('.modal-overlay');
        if (overlay) {
            overlay.remove();
        }
        
        // Habilitar scroll del body
        document.body.style.overflow = '';
        
        console.log('🚪 Modal cerrado');
    }
    
    /**
     * ❌ MOSTRAR ERROR
     */
    showError(message) {
        console.error('❌ Error:', message);
        // Implementar UI de error
        alert(`Error: ${message}`);
    }
    
    /**
     * ⚠️ MOSTRAR ADVERTENCIA
     */
    showWarning(message) {
        console.warn('⚠️ Advertencia:', message);
        // Implementar UI de advertencia
        alert(`Advertencia: ${message}`);
    }
    
    /**
     * 🧹 LIMPIAR RECURSOS
     */
    destroy() {
        // Cerrar SSE
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        // Limpiar timers
        this.debounceTimers.forEach(timer => clearTimeout(timer));
        this.debounceTimers.clear();
        
        // Limpiar fallback poll
        if (this.fallbackPollInterval) {
            clearInterval(this.fallbackPollInterval);
        }
        
        // Flush final
        this.flushChanges(true);
        
        console.log('🧹 Carrito avanzado destruido');
    }
}

// Exportar para uso global
window.CarritoAvanzado = CarritoAvanzado;

// Auto-inicializar cuando DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.carritoAvanzado = new CarritoAvanzado();
});

console.log('🛒 Carrito Avanzado cargado - Maruz Distribuciones');
