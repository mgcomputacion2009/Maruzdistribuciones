/**
 * Sistema de Pedido Abierto - Maruz Distribuciones
 * Script de inicialización que se inyecta en el frontend
 */

class PedidoAbierto {
    constructor() {
        this.pedidoId = null;
        this.pedidoToken = null;
        this.version = null;
        this.eventSource = null;
        this.pollInterval = null;
        this.debounceTimers = new Map();
        this.pendingChanges = new Map();
        
        // Configuración
        this.config = {
            apiBase: '/api/pedido',
            debounceDelay: 500,
            safetyDelay: 10000,
            pollInterval: 10000,
            maxRetries: 3
        };
        
        this.init();
    }
    
    async init() {
        try {
            // Asegurar pedido abierto
            await this.ensurePedido();
            
            // Suscribirse a eventos en tiempo real
            this.subscribeToEvents();
            
            // Cargar estado inicial
            await this.loadInitialState();
            
            // Configurar listeners para cambios
            this.setupChangeListeners();
            
            // Configurar listeners para navegación
            this.setupNavigationListeners();
            
            console.log('✅ Sistema de pedido abierto inicializado');
            
        } catch (error) {
            console.error('❌ Error inicializando sistema de pedido:', error);
            // Fallback a poll
            this.startPolling();
        }
    }
    
    async ensurePedido() {
        try {
            const response = await fetch(`${this.config.apiBase}/ensure`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            this.pedidoId = data.pedido_id;
            this.pedidoToken = data.pedido_token;
            this.version = data.version;
            
            // Guardar en localStorage para persistencia
            localStorage.setItem('pedido_token', this.pedidoToken);
            localStorage.setItem('pedido_id', this.pedidoId);
            
            console.log('✅ Pedido asegurado:', data);
            
        } catch (error) {
            console.error('❌ Error asegurando pedido:', error);
            throw error;
        }
    }
    
    subscribeToEvents() {
        try {
            // Intentar SSE primero
            this.eventSource = new EventSource(`${this.config.apiBase}/stream`, {
                headers: {
                    'X-Pedido-Token': this.pedidoToken
                }
            });
            
            this.eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleEvent(data);
                } catch (error) {
                    console.error('Error parsing SSE event:', error);
                }
            };
            
            this.eventSource.onerror = (error) => {
                console.warn('⚠️ SSE error, switching to polling:', error);
                this.eventSource.close();
                this.startPolling();
            };
            
            this.eventSource.onopen = () => {
                console.log('✅ SSE connection established');
                if (this.pollInterval) {
                    clearInterval(this.pollInterval);
                    this.pollInterval = null;
                }
            };
            
        } catch (error) {
            console.warn('⚠️ SSE not supported, using polling:', error);
            this.startPolling();
        }
    }
    
    startPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }
        
        this.pollInterval = setInterval(async () => {
            try {
                await this.syncState();
            } catch (error) {
                console.error('Error in polling sync:', error);
            }
        }, this.config.pollInterval);
        
        console.log('🔄 Polling iniciado cada', this.config.pollInterval, 'ms');
    }
    
    handleEvent(data) {
        switch (data.event) {
            case 'resumen':
                this.updateSummaryBar(data.data);
                break;
                
            case 'item_update':
                this.updateProductDisplay(data.data);
                break;
                
            case 'item_remove':
                this.removeProductDisplay(data.data);
                break;
                
            case 'sync_hint':
                if (data.data.reason === 'reconnect') {
                    console.log('🔄 Reconectando...');
                    this.reconnect();
                }
                break;
                
            default:
                console.log('Evento desconocido:', data);
        }
    }
    
    async loadInitialState() {
        try {
            // Obtener resumen global
            await this.syncState();
            
            // Obtener items de la página actual
            await this.loadPageItems();
            
        } catch (error) {
            console.error('Error cargando estado inicial:', error);
        }
    }
    
    async syncState() {
        try {
            const response = await fetch(`${this.config.apiBase}/resumen`, {
                headers: {
                    'X-Pedido-Token': this.pedidoToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.version = data.version;
            this.updateSummaryBar(data);
            
        } catch (error) {
            console.error('Error sincronizando estado:', error);
        }
    }
    
    async loadPageItems() {
        try {
            // Obtener códigos de productos visibles en la página
            const codigos = this.getVisibleProductCodes();
            
            if (codigos.length === 0) {
                return;
            }
            
            const response = await fetch(`${this.config.apiBase}/items/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Pedido-Token': this.pedidoToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ codigos }),
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Actualizar inputs con cantidades del pedido
            this.updateProductInputs(data.items);
            
        } catch (error) {
            console.error('Error cargando items de la página:', error);
        }
    }
    
    getVisibleProductCodes() {
        const codigos = [];
        const rows = document.querySelectorAll('.row[data-codigo]');
        
        rows.forEach(row => {
            const codigo = row.getAttribute('data-codigo');
            if (codigo) {
                codigos.push(codigo);
            }
        });
        
        return codigos;
    }
    
    updateProductInputs(items) {
        Object.entries(items).forEach(([codigo, item]) => {
            const row = document.querySelector(`.row[data-codigo="${codigo}"]`);
            if (!row) return;
            
            // Actualizar cantidad
            const qtyInput = row.querySelector('.qty');
            if (qtyInput && item.cantidad > 0) {
                qtyInput.value = item.cantidad;
                qtyInput.classList.add('has-pedido');
            }
            
            // Actualizar descuento
            const discountInput = row.querySelector('.discount');
            if (discountInput && item.descuento_monto > 0) {
                const precio = parseFloat(row.querySelector('.precio').textContent.replace(/[^\d.-]/g, ''));
                const descuentoPorcentaje = (item.descuento_monto / (precio * item.cantidad)) * 100;
                discountInput.value = descuentoPorcentaje.toFixed(2);
                discountInput.classList.add('has-pedido');
            }
        });
    }
    
    updateSummaryBar(data) {
        // Actualizar barra de resumen
        const summaryBar = document.getElementById('resumen-carrito');
        if (summaryBar) {
            const unidadesEl = summaryBar.querySelector('.unidades');
            const subtotalEl = summaryBar.querySelector('.subtotal');
            const totalEl = summaryBar.querySelector('.total');
            
            if (unidadesEl) unidadesEl.textContent = data.unidades;
            if (subtotalEl) subtotalEl.textContent = `$${data.subtotal.toFixed(2)}`;
            if (totalEl) totalEl.textContent = `$${data.total.toFixed(2)}`;
            
            // Mostrar/ocultar barra según si hay productos
            if (data.unidades > 0) {
                summaryBar.style.display = 'block';
            } else {
                summaryBar.style.display = 'none';
            }
        }
    }
    
    updateProductDisplay(data) {
        const row = document.querySelector(`.row[data-codigo="${data.producto_codigo}"]`);
        if (!row) return;
        
        // Actualizar cantidad
        const qtyInput = row.querySelector('.qty');
        if (qtyInput) {
            qtyInput.value = data.cantidad;
            qtyInput.classList.toggle('has-pedido', data.cantidad > 0);
        }
        
        // Actualizar descuento
        const discountInput = row.querySelector('.discount');
        if (discountInput && data.descuento_monto > 0) {
            const precio = parseFloat(row.querySelector('.precio').textContent.replace(/[^\d.-]/g, ''));
            const descuentoPorcentaje = (data.descuento_monto / (precio * data.cantidad)) * 100;
            discountInput.value = descuentoPorcentaje.toFixed(2);
            discountInput.classList.add('has-pedido');
        }
    }
    
    removeProductDisplay(data) {
        const row = document.querySelector(`.row[data-codigo="${data.producto_codigo}"]`);
        if (!row) return;
        
        // Limpiar inputs
        const qtyInput = row.querySelector('.qty');
        if (qtyInput) {
            qtyInput.value = '';
            qtyInput.classList.remove('has-pedido');
        }
        
        const discountInput = row.querySelector('.discount');
        if (discountInput) {
            discountInput.value = '';
            discountInput.classList.remove('has-pedido');
        }
    }
    
    setupChangeListeners() {
        // Escuchar cambios en inputs de cantidad y descuento
        document.addEventListener('input', (event) => {
            if (event.target.matches('.qty, .discount')) {
                this.scheduleUpdate(event.target);
            }
        });
        
        // Escuchar blur para flush inmediato
        document.addEventListener('blur', (event) => {
            if (event.target.matches('.qty, .discount')) {
                this.flushChanges();
            }
        }, true);
        
        // Escuchar Enter para flush inmediato
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && event.target.matches('.qty, .discount')) {
                this.flushChanges();
            }
        });
    }
    
    setupNavigationListeners() {
        // Guardar cambios antes de navegar
        window.addEventListener('beforeunload', () => {
            this.flushChanges(true);
        });
        
        // Guardar cambios cuando la pestaña se oculta
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.flushChanges(true);
            }
        });
        
        // Interceptar clicks en paginación y búsqueda
        document.addEventListener('click', (event) => {
            if (event.target.matches('a[href*="page="], a[href*="search="], button[type="submit"]')) {
                event.preventDefault();
                this.flushChanges(true).then(() => {
                    // Continuar con la navegación
                    if (event.target.href) {
                        window.location.href = event.target.href;
                    } else if (event.target.form) {
                        event.target.form.submit();
                    }
                });
            }
        });
    }
    
    scheduleUpdate(input) {
        const codigo = input.closest('.row').getAttribute('data-codigo');
        
        // Cancelar timer anterior
        if (this.debounceTimers.has(codigo)) {
            clearTimeout(this.debounceTimers.get(codigo));
        }
        
        // Programar actualización
        const timer = setTimeout(() => {
            this.updateProduct(codigo);
        }, this.config.debounceDelay);
        
        this.debounceTimers.set(codigo, timer);
        
        // Timer de seguridad
        setTimeout(() => {
            this.flushChanges();
        }, this.config.safetyDelay);
    }
    
    async updateProduct(codigo) {
        const row = document.querySelector(`.row[data-codigo="${codigo}"]`);
        if (!row) return;
        
        const qtyInput = row.querySelector('.qty');
        const discountInput = row.querySelector('.discount');
        const precioEl = row.querySelector('.precio');
        
        if (!qtyInput || !precioEl) return;
        
        const cantidad = parseInt(qtyInput.value) || 0;
        const precio = parseFloat(precioEl.textContent.replace(/[^\d.-]/g, ''));
        const descuentoPorcentaje = parseFloat(discountInput.value) || 0;
        const descuentoMonto = (precio * cantidad * descuentoPorcentaje) / 100;
        
        // Agregar a cambios pendientes
        this.pendingChanges.set(codigo, {
            producto_codigo: codigo,
            cantidad: cantidad,
            precio_unitario: precio,
            descuento_monto: descuentoMonto
        });
        
        // Actualizar totales locales
        this.updateLocalTotals();
    }
    
    updateLocalTotals() {
        let subtotal = 0;
        let unidades = 0;
        
        this.pendingChanges.forEach(change => {
            if (change.cantidad > 0) {
                const totalLinea = (change.precio_unitario * change.cantidad) - change.descuento_monto;
                subtotal += totalLinea;
                unidades += change.cantidad;
            }
        });
        
        // Actualizar barra de resumen temporalmente
        const summaryBar = document.getElementById('resumen-carrito');
        if (summaryBar) {
            const unidadesEl = summaryBar.querySelector('.unidades');
            const subtotalEl = summaryBar.querySelector('.subtotal');
            const totalEl = summaryBar.querySelector('.total');
            
            if (unidadesEl) unidadesEl.textContent = unidades;
            if (subtotalEl) subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
            if (totalEl) totalEl.textContent = `$${(subtotal * 1.16).toFixed(2)}`;
        }
    }
    
    async flushChanges(keepalive = false) {
        if (this.pendingChanges.size === 0) return;
        
        try {
            const cambios = Array.from(this.pendingChanges.values());
            
            const response = await fetch(`${this.config.apiBase}/items/batch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Pedido-Token': this.pedidoToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    version: this.version,
                    cambios: cambios
                }),
                credentials: 'same-origin',
                keepalive: keepalive
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Actualizar versión
            this.version = data.version;
            
            // Limpiar cambios pendientes
            this.pendingChanges.clear();
            
            // Limpiar timers
            this.debounceTimers.forEach(timer => clearTimeout(timer));
            this.debounceTimers.clear();
            
            // Actualizar resumen con datos del servidor
            this.updateSummaryBar(data.resumen);
            
            console.log('✅ Cambios guardados:', data.aplicados);
            
        } catch (error) {
            console.error('❌ Error guardando cambios:', error);
            
            // Reintentar en caso de error
            if (keepalive) {
                setTimeout(() => this.flushChanges(false), 1000);
            }
        }
    }
    
    async reconnect() {
        try {
            // Cerrar conexión SSE si existe
            if (this.eventSource) {
                this.eventSource.close();
                this.eventSource = null;
            }
            
            // Limpiar polling
            if (this.pollInterval) {
                clearInterval(this.pollInterval);
                this.pollInterval = null;
            }
            
            // Reintentar conexión
            await this.ensurePedido();
            this.subscribeToEvents();
            
        } catch (error) {
            console.error('Error reconectando:', error);
            this.startPolling();
        }
    }
    
    destroy() {
        // Limpiar recursos
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }
        
        this.debounceTimers.forEach(timer => clearTimeout(timer));
        this.debounceTimers.clear();
        
        this.pendingChanges.clear();
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.pedidoAbierto = new PedidoAbierto();
    });
} else {
    window.pedidoAbierto = new PedidoAbierto();
}

// Exportar para uso global
window.PedidoAbierto = PedidoAbierto;
