/**
 * 🛒 CARRITO AVANZADO V2 - MARUZ DISTRIBUCIONES
 * Versión mejorada e integrada con el HTML existente
 */

class CarritoAvanzado {
    constructor() {
        // Estado del carrito
        this.pedidoId = null;
        this.pedidoToken = null;
        this.version = 0;
        this.estado = 'activo';
        this.resumen = null;
        
        // Debounce y flush
        this.debounceTimers = new Map();
        this.pendingChanges = new Map();
        
        // SSE
        this.eventSource = null;
        this.fallbackPollInterval = null;
        
        // Inicializar
        this.init();
    }
    
    async init() {
        try {
            console.log('🛒 Inicializando carrito avanzado V2...');
            
            // 1. Ensure - Crear/obtener pedido único
            await this.ensurePedido();
            
            // 2. Conectar SSE para tiempo real
            if (this.pedidoId && this.pedidoToken) {
                this.connectSSE();
            }
            
            // 3. Configurar event listeners
            this.setupEventListeners();
            
            // 4. Cargar estado inicial
            await this.loadResumen();
            
            // 5. Query items visibles
            await this.queryVisibleItems();
            
            console.log('✅ Carrito avanzado V2 inicializado correctamente');
            
        } catch (error) {
            console.error('❌ Error inicializando carrito:', error);
            // Continuar sin carrito avanzado si hay error
        }
    }
    
    async ensurePedido() {
        try {
            const response = await fetch('/api/pedido/ensure', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Pedido-Token': this.pedidoToken || ''
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                console.error(`Error HTTP ${response.status}`);
                return;
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
                    version: this.version
                });
                
                // Guardar token en localStorage para persistencia
                if (this.pedidoToken) {
                    localStorage.setItem('pedido_token', this.pedidoToken);
                }
                
                this.updateSummaryBar();
            }
            
        } catch (error) {
            console.error('❌ Error en ensure:', error);
        }
    }
    
    async loadResumen() {
        if (!this.pedidoToken) return;
        
        try {
            const response = await fetch('/api/pedido/resumen', {
                headers: {
                    'X-Pedido-Token': this.pedidoToken
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    this.resumen = data.resumen;
                    this.version = data.version;
                    this.updateSummaryBar();
                }
            }
            
        } catch (error) {
            console.error('❌ Error cargando resumen:', error);
        }
    }
    
    connectSSE() {
        try {
            if (this.eventSource) {
                this.eventSource.close();
            }
            
            const url = `/api/pedido/stream?pedido_id=${this.pedidoId}&token=${this.pedidoToken}`;
            this.eventSource = new EventSource(url);
            
            this.eventSource.onopen = () => {
                console.log('✅ SSE conectado');
                if (this.fallbackPollInterval) {
                    clearInterval(this.fallbackPollInterval);
                    this.fallbackPollInterval = null;
                }
            };
            
            this.eventSource.onmessage = (event) => {
                this.handleSSEMessage(event);
            };
            
            this.eventSource.onerror = () => {
                console.warn('⚠️ Error SSE, activando fallback');
                this.activateFallbackPoll();
            };
            
        } catch (error) {
            console.error('❌ Error conectando SSE:', error);
            this.activateFallbackPoll();
        }
    }
    
    activateFallbackPoll() {
        if (this.fallbackPollInterval) return;
        
        this.fallbackPollInterval = setInterval(async () => {
            await this.loadResumen();
        }, 10000);
    }
    
    handleSSEMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch (data.tipo) {
                case 'resumen':
                    this.resumen = data.resumen;
                    this.version = data.version;
                    this.updateSummaryBar();
                    break;
                    
                case 'item_update':
                    this.handleItemUpdate(data);
                    break;
                    
                case 'item_remove':
                    this.handleItemRemove(data);
                    break;
            }
            
        } catch (error) {
            console.error('❌ Error procesando SSE:', error);
        }
    }
    
    handleItemUpdate(data) {
        const input = document.querySelector(`[data-codigo="${data.producto_codigo}"] input[type="number"]`);
        if (input && input.value != data.cantidad) {
            input.value = data.cantidad;
            this.updateRowTotal(data.producto_codigo);
        }
    }
    
    handleItemRemove(data) {
        const input = document.querySelector(`[data-codigo="${data.producto_codigo}"] input[type="number"]`);
        if (input) {
            input.value = '0';
            this.updateRowTotal(data.producto_codigo);
        }
    }
    
    setupEventListeners() {
        // Escuchar cambios en inputs de cantidad
        document.addEventListener('input', (e) => {
            if (e.target.matches('.qty')) {
                this.handleQuantityChange(e);
            }
        });
        
        // Escuchar cambios en descuentos
        document.addEventListener('input', (e) => {
            if (e.target.matches('.discount')) {
                this.handleDiscountChange(e);
            }
        });
        
        // Flush en blur
        document.addEventListener('blur', (e) => {
            if (e.target.matches('.qty, .discount')) {
                this.flushChanges();
            }
        }, true);
        
        // Flush en Enter
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.matches('.qty, .discount')) {
                this.flushChanges();
            }
        });
        
        // Flush antes de salir
        window.addEventListener('pagehide', () => {
            this.flushChanges(true);
        });
        
        // Recuperar token de localStorage al cargar
        const savedToken = localStorage.getItem('pedido_token');
        if (savedToken) {
            this.pedidoToken = savedToken;
        }
    }
    
    handleQuantityChange(event) {
        const input = event.target;
        const row = input.closest('.row');
        if (!row) return;
        
        const codigo = row.dataset.codigo;
        const cantidad = parseInt(input.value) || 0;
        
        if (cantidad < 0) {
            input.value = '0';
            return;
        }
        
        // Obtener descuento actual
        const discountInput = row.querySelector('.discount');
        const descuento = discountInput ? parseFloat(discountInput.value) || 0 : 0;
        
        // Agregar a cambios pendientes
        this.pendingChanges.set(codigo, {
            cantidad,
            descuento
        });
        
        // Actualizar total de la fila
        this.updateRowTotal(codigo);
        
        // Debounce
        this.debounceChange(codigo);
    }
    
    handleDiscountChange(event) {
        const input = event.target;
        const row = input.closest('.row');
        if (!row) return;
        
        const codigo = row.dataset.codigo;
        const descuento = parseFloat(input.value) || 0;
        
        if (descuento < 0 || descuento > 100) {
            input.value = '0';
            return;
        }
        
        // Obtener cantidad actual
        const qtyInput = row.querySelector('.qty');
        const cantidad = qtyInput ? parseInt(qtyInput.value) || 0 : 0;
        
        // Agregar a cambios pendientes
        this.pendingChanges.set(codigo, {
            cantidad,
            descuento
        });
        
        // Actualizar total de la fila
        this.updateRowTotal(codigo);
        
        // Debounce
        this.debounceChange(codigo);
    }
    
    updateRowTotal(codigo) {
        const row = document.querySelector(`[data-codigo="${codigo}"]`);
        if (!row) return;
        
        const qtyInput = row.querySelector('.qty');
        const priceElement = row.querySelector('.price');
        const discountInput = row.querySelector('.discount');
        const totalElement = row.querySelector('.total');
        
        if (!qtyInput || !priceElement || !totalElement) return;
        
        const cantidad = parseInt(qtyInput.value) || 0;
        const precio = parseFloat(priceElement.textContent.replace('$', '').replace(',', '')) || 0;
        const descuento = discountInput ? parseFloat(discountInput.value) || 0 : 0;
        
        const subtotal = precio * cantidad;
        const descuentoMonto = subtotal * (descuento / 100);
        const total = subtotal - descuentoMonto;
        
        totalElement.textContent = `$${total.toFixed(2)}`;
    }
    
    debounceChange(codigo) {
        if (this.debounceTimers.has(codigo)) {
            clearTimeout(this.debounceTimers.get(codigo));
        }
        
        const timer = setTimeout(() => {
            this.flushChanges();
        }, 800);
        
        this.debounceTimers.set(codigo, timer);
    }
    
    async flushChanges(sync = false) {
        if (this.pendingChanges.size === 0 || !this.pedidoToken) return;
        
        try {
            const items = Array.from(this.pendingChanges.entries()).map(([codigo, data]) => ({
                producto_codigo: codigo,
                cantidad: data.cantidad,
                descuento: data.descuento
            }));
            
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
                }),
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    this.version = data.version;
                    this.pendingChanges.clear();
                    this.resumen = data.resumen;
                    this.updateSummaryBar();
                    
                    console.log('✅ Cambios guardados');
                }
            } else if (response.status === 409) {
                // Conflicto de versión
                await this.loadResumen();
                await this.queryVisibleItems();
            }
            
        } catch (error) {
            console.error('❌ Error en flush:', error);
        }
    }
    
    async queryVisibleItems() {
        if (!this.pedidoToken) return;
        
        try {
            const rows = document.querySelectorAll('.row[data-codigo]');
            const codigos = Array.from(rows).map(row => row.dataset.codigo);
            
            if (codigos.length === 0) return;
            
            const response = await fetch('/api/pedido/items/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Pedido-Token': this.pedidoToken
                },
                body: JSON.stringify({
                    pedido_id: this.pedidoId,
                    codigos: codigos
                }),
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success && data.items) {
                    data.items.forEach(item => {
                        const row = document.querySelector(`[data-codigo="${item.producto_codigo}"]`);
                        if (!row) return;
                        
                        const qtyInput = row.querySelector('.qty');
                        const discountInput = row.querySelector('.discount');
                        
                        if (qtyInput) {
                            qtyInput.value = item.cantidad;
                        }
                        
                        if (discountInput && item.descuento > 0) {
                            discountInput.value = item.descuento;
                        }
                        
                        this.updateRowTotal(item.producto_codigo);
                    });
                }
            }
            
        } catch (error) {
            console.error('❌ Error querying items:', error);
        }
    }
    
    updateSummaryBar() {
        if (!this.resumen) return;
        
        const summaryBar = document.querySelector('.summary-bar');
        if (!summaryBar) return;
        
        // Actualizar valores
        const unidades = summaryBar.querySelector('[data-summary="unidades"]');
        const subtotal = summaryBar.querySelector('[data-summary="subtotal"]');
        const total = summaryBar.querySelector('[data-summary="total"]');
        
        if (unidades) {
            unidades.textContent = this.resumen.cantidad_productos || 0;
        }
        
        if (subtotal) {
            subtotal.textContent = `$${(this.resumen.subtotal || 0).toFixed(2)}`;
        }
        
        if (total) {
            total.textContent = `$${(this.resumen.total_pedido || 0).toFixed(2)}`;
        }
        
        // Mostrar/ocultar barra
        if (this.resumen.cantidad_productos > 0) {
            summaryBar.style.display = 'flex';
        } else {
            summaryBar.style.display = 'none';
        }
    }
    
    destroy() {
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        if (this.fallbackPollInterval) {
            clearInterval(this.fallbackPollInterval);
        }
        
        this.debounceTimers.forEach(timer => clearTimeout(timer));
        this.debounceTimers.clear();
        
        this.flushChanges(true);
    }
}

// Inicializar cuando DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.carritoAvanzado = new CarritoAvanzado();
});

console.log('🛒 Carrito Avanzado V2 cargado');
