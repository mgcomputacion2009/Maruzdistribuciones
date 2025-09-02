/**
 * 🛒 CARRITO POPUP SIMPLE - MARUZ DISTRIBUCIONES
 * Versión simplificada y funcional del carrito popup
 */

class CarritoPopupSimple {
    constructor() {
        // Estado del carrito
        this.pedidoId = null;
        this.pedidoToken = null;
        this.version = 0;
        this.resumen = null;
        this.items = [];
        
        // Estado del popup
        this.isOpen = false;
        
        // Inicializar
        this.init();
    }
    
    init() {
        try {
            console.log('🛒 Inicializando carrito popup simple...');
            
            // 1. Crear botón flotante
            this.createFloatingButton();
            
            // 2. Crear popup HTML
            this.createPopupHTML();
            
            // 3. Configurar event listeners
            this.setupEventListeners();
            
            // 4. Cargar estado inicial (sin bloquear)
            this.loadInitialState();
            
            console.log('✅ Carrito popup simple inicializado correctamente');
            
        } catch (error) {
            console.error('❌ Error inicializando carrito popup simple:', error);
        }
    }
    
    /**
     * 🎯 CREAR BOTÓN FLOTANTE
     */
    createFloatingButton() {
        // Remover botón existente si hay
        const existingButton = document.querySelector('.carrito-flotante');
        if (existingButton) {
            existingButton.remove();
        }
        
        // Crear botón flotante
        const button = document.createElement('div');
        button.className = 'carrito-flotante';
        button.innerHTML = `
            <i class="fas fa-shopping-cart"></i>
            <span class="carrito-contador">0</span>
        `;
        
        // Estilos del botón
        button.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #4285f4, #34a853);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(66, 133, 244, 0.3);
            z-index: 9999;
            transition: all 0.3s ease;
            font-size: 24px;
        `;
        
        // Contador
        const contador = button.querySelector('.carrito-contador');
        contador.style.cssText = `
            position: absolute;
            top: -5px;
            right: -5px;
            background: #ea4335;
            color: white;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        `;
        
        // Event listener para abrir popup
        button.addEventListener('click', () => {
            this.openPopup();
        });
        
        // Hover effects
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'scale(1.1)';
            button.style.boxShadow = '0 12px 35px rgba(66, 133, 244, 0.4)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1)';
            button.style.boxShadow = '0 8px 25px rgba(66, 133, 244, 0.3)';
        });
        
        // Agregar al body
        document.body.appendChild(button);
        
        console.log('✅ Botón flotante del carrito creado');
    }
    
    /**
     * 🪟 CREAR HTML DEL POPUP
     */
    createPopupHTML() {
        // Remover popup existente si hay
        const existingPopup = document.querySelector('.carrito-popup-overlay');
        if (existingPopup) {
            existingPopup.remove();
        }
        
        // Crear overlay y popup
        const overlay = document.createElement('div');
        overlay.className = 'carrito-popup-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 10000;
            display: none;
            align-items: center;
            justify-content: center;
        `;
        
        // HTML del popup
        overlay.innerHTML = `
            <div class="carrito-popup">
                <div class="carrito-popup-header">
                    <h2><i class="fas fa-shopping-cart"></i> Mi Carrito</h2>
                    <button class="carrito-popup-close" data-close-popup>
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="carrito-popup-content">
                    <div class="carrito-items" id="carritoItems">
                        <div class="carrito-loading">
                            <i class="fas fa-spinner fa-spin"></i> Cargando carrito...
                        </div>
                    </div>
                    
                    <div class="carrito-resumen" id="carritoResumen">
                        <div class="resumen-item">
                            <span>Unidades:</span>
                            <span id="resumenUnidades">0</span>
                        </div>
                        <div class="resumen-item">
                            <span>Subtotal:</span>
                            <span id="resumenSubtotal">$0.00</span>
                        </div>
                        <div class="resumen-item total">
                            <span>Total:</span>
                            <span id="resumenTotal">$0.00</span>
                        </div>
                    </div>
                    
                    <div class="carrito-actions">
                        <button class="btn-limpiar" id="btnLimpiarCarrito">
                            <i class="fas fa-trash"></i> Limpiar
                        </button>
                        <button class="btn-finalizar" id="btnFinalizarCompra">
                            <i class="fas fa-check"></i> Finalizar Compra
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Estilos del popup
        const popup = overlay.querySelector('.carrito-popup');
        popup.style.cssText = `
            background: white;
            border-radius: 16px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            animation: carritoSlideIn 0.3s ease;
        `;
        
        // Estilos del header
        const header = popup.querySelector('.carrito-popup-header');
        header.style.cssText = `
            background: linear-gradient(135deg, #4285f4, #34a853);
            color: white;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        `;
        
        header.querySelector('h2').style.cssText = `
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
        `;
        
        const closeBtn = header.querySelector('.carrito-popup-close');
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 5px;
            border-radius: 5px;
            transition: background 0.2s;
        `;
        
        closeBtn.addEventListener('mouseenter', () => {
            closeBtn.style.background = 'rgba(255, 255, 255, 0.2)';
        });
        
        closeBtn.addEventListener('mouseleave', () => {
            closeBtn.style.background = 'none';
        });
        
        // Estilos del contenido
        const content = popup.querySelector('.carrito-popup-content');
        content.style.cssText = `
            padding: 20px;
            max-height: 60vh;
            overflow-y: auto;
        `;
        
        // Estilos de items
        const itemsContainer = content.querySelector('.carrito-items');
        itemsContainer.style.cssText = `
            margin-bottom: 20px;
        `;
        
        // Estilos del resumen
        const resumen = content.querySelector('.carrito-resumen');
        resumen.style.cssText = `
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        `;
        
        // Estilos de acciones
        const actions = content.querySelector('.carrito-actions');
        actions.style.cssText = `
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        `;
        
        // Botones
        const btnLimpiar = actions.querySelector('.btn-limpiar');
        btnLimpiar.style.cssText = `
            background: #6c757d;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
        `;
        
        const btnFinalizar = actions.querySelector('.btn-finalizar');
        btnFinalizar.style.cssText = `
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
        `;
        
        // Hover effects
        btnLimpiar.addEventListener('mouseenter', () => {
            btnLimpiar.style.background = '#5a6268';
        });
        
        btnLimpiar.addEventListener('mouseleave', () => {
            btnLimpiar.style.background = '#6c757d';
        });
        
        btnFinalizar.addEventListener('mouseenter', () => {
            btnFinalizar.style.background = '#218838';
        });
        
        btnFinalizar.addEventListener('mouseleave', () => {
            btnFinalizar.style.background = '#28a745';
        });
        
        // Agregar CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes carritoSlideIn {
                from {
                    opacity: 0;
                    transform: translateY(-20px) scale(0.95);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }
            
            .carrito-item {
                display: flex;
                align-items: center;
                gap: 15px;
                padding: 15px;
                border: 1px solid #e9ecef;
                border-radius: 10px;
                margin-bottom: 10px;
                background: white;
            }
            
            .carrito-item-img {
                width: 60px;
                height: 60px;
                border-radius: 8px;
                object-fit: cover;
            }
            
            .carrito-item-info {
                flex: 1;
            }
            
            .carrito-item-title {
                font-weight: 600;
                margin-bottom: 5px;
                color: #333;
            }
            
            .carrito-item-code {
                font-size: 0.9rem;
                color: #666;
                margin-bottom: 5px;
            }
            
            .carrito-item-price {
                font-weight: 600;
                color: #28a745;
            }
            
            .carrito-item-controls {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .carrito-item-qty {
                width: 60px;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            
            .carrito-item-discount {
                width: 80px;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            
            .carrito-item-total {
                font-weight: 700;
                color: #28a745;
                min-width: 80px;
                text-align: right;
            }
            
            .carrito-loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            
            .carrito-empty {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            
            .resumen-item {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                padding: 5px 0;
            }
            
            .resumen-item.total {
                border-top: 2px solid #dee2e6;
                padding-top: 10px;
                margin-top: 10px;
                font-weight: 700;
                font-size: 1.1rem;
            }
        `;
        
        document.head.appendChild(style);
        
        // Agregar al body
        document.body.appendChild(overlay);
        
        console.log('✅ HTML del popup del carrito creado');
    }
    
    /**
     * 🎯 CONFIGURAR EVENT LISTENERS
     */
    setupEventListeners() {
        // Cerrar popup con botón
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-close-popup]')) {
                this.closePopup();
            }
        });
        
        // Cerrar popup con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closePopup();
            }
        });
        
        // Cerrar popup haciendo clic fuera
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('carrito-popup-overlay')) {
                this.closePopup();
            }
        });
        
        // Botones de acción
        document.addEventListener('click', (e) => {
            if (e.target.id === 'btnLimpiarCarrito') {
                this.limpiarCarrito();
            }
            
            if (e.target.id === 'btnFinalizarCompra') {
                this.finalizarCompra();
            }
        });
        
        // Recuperar token de localStorage
        const savedToken = localStorage.getItem('pedido_token');
        if (savedToken) {
            this.pedidoToken = savedToken;
        }
    }
    
    /**
     * 📊 CARGAR ESTADO INICIAL (NO BLOQUEANTE)
     */
    loadInitialState() {
        // Cargar en background sin bloquear
        setTimeout(async () => {
            try {
                console.log('🔄 Cargando estado inicial del carrito...');
                
                // Intentar ensure con timeout
                await this.ensurePedidoWithTimeout();
                
                // Solo continuar si tenemos token
                if (this.pedidoToken) {
                    await this.loadResumenWithTimeout();
                    await this.loadItemsWithTimeout();
                } else {
                    console.log('⚠️ No se pudo obtener token, mostrando carrito vacío');
                    this.showEmptyCart();
                }
                
            } catch (error) {
                console.error('❌ Error cargando estado inicial:', error);
                this.showEmptyCart();
            }
        }, 100);
    }
    
    /**
     * 🔐 ENSURE CON TIMEOUT
     */
    async ensurePedidoWithTimeout() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 segundos timeout
            
            const response = await fetch('/api/pedido/ensure', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Pedido-Token': this.pedidoToken || ''
                },
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                console.error(`Error HTTP ${response.status}`);
                return;
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.pedidoId = data.pedido_id;
                this.pedidoToken = data.pedido_token;
                this.version = data.version;
                this.resumen = data.resumen;
                
                console.log('✅ Pedido asegurado:', {
                    id: this.pedidoId,
                    version: this.version
                });
                
                // Guardar token en localStorage
                if (this.pedidoToken) {
                    localStorage.setItem('pedido_token', this.pedidoToken);
                }
                
                this.updateFloatingButton();
            }
            
        } catch (error) {
            if (error.name === 'AbortError') {
                console.warn('⚠️ Timeout en ensure, continuando sin conexión');
            } else {
                console.error('❌ Error en ensure:', error);
            }
        }
    }
    
    /**
     * 📊 CARGAR RESUMEN CON TIMEOUT
     */
    async loadResumenWithTimeout() {
        if (!this.pedidoToken) return;
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 segundos timeout
            
            const response = await fetch('/api/pedido/resumen', {
                headers: {
                    'X-Pedido-Token': this.pedidoToken
                },
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    this.resumen = data.resumen;
                    this.version = data.version;
                    this.updateResumen();
                    this.updateFloatingButton();
                }
            }
            
        } catch (error) {
            if (error.name === 'AbortError') {
                console.warn('⚠️ Timeout en resumen, continuando sin datos');
            } else {
                console.error('❌ Error cargando resumen:', error);
            }
        }
    }
    
    /**
     * 📦 CARGAR ITEMS CON TIMEOUT
     */
    async loadItemsWithTimeout() {
        if (!this.pedidoToken) return;
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 segundos timeout
            
            const response = await fetch('/api/pedido/items/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Pedido-Token': this.pedidoToken
                },
                body: JSON.stringify({
                    pedido_id: this.pedidoId,
                    codigos: [] // Todos los items
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success && data.items) {
                    this.items = data.items;
                    this.renderItems();
                } else {
                    this.showEmptyCart();
                }
            } else {
                this.showEmptyCart();
            }
            
        } catch (error) {
            if (error.name === 'AbortError') {
                console.warn('⚠️ Timeout en items, mostrando carrito vacío');
            } else {
                console.error('❌ Error cargando items:', error);
            }
            this.showEmptyCart();
        }
    }
    
    /**
     * 📭 MOSTRAR CARRITO VACÍO
     */
    showEmptyCart() {
        console.log('📭 Mostrando carrito vacío');
        
        // Limpiar items
        this.items = [];
        
        // Crear resumen vacío si no existe
        if (!this.resumen) {
            this.resumen = {
                cantidad_productos: 0,
                subtotal: 0,
                total_pedido: 0
            };
        }
        
        // Actualizar UI
        this.updateResumen();
        this.updateFloatingButton();
        this.renderItems();
    }
    
    /**
     * 🚪 ABRIR POPUP
     */
    openPopup() {
        const overlay = document.querySelector('.carrito-popup-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
            this.isOpen = true;
            
            // Bloquear scroll del body
            document.body.style.overflow = 'hidden';
            
            // Cargar datos actualizados
            this.loadResumenWithTimeout();
            this.loadItemsWithTimeout();
            
            console.log('✅ Popup del carrito abierto');
        }
    }
    
    /**
     * 🚪 CERRAR POPUP
     */
    closePopup() {
        const overlay = document.querySelector('.carrito-popup-overlay');
        if (overlay) {
            overlay.style.display = 'none';
            this.isOpen = false;
            
            // Habilitar scroll del body
            document.body.style.overflow = '';
            
            console.log('🚪 Popup del carrito cerrado');
        }
    }
    
    /**
     * 🎨 RENDERIZAR ITEMS
     */
    renderItems() {
        const container = document.getElementById('carritoItems');
        if (!container) return;
        
        if (this.items.length === 0) {
            container.innerHTML = `
                <div class="carrito-empty">
                    <i class="fas fa-shopping-cart" style="font-size: 3rem; color: #ccc; margin-bottom: 15px;"></i>
                    <p>Tu carrito está vacío</p>
                    <p style="font-size: 0.9rem; color: #999;">Agrega productos desde la página de productos</p>
                </div>
            `;
            return;
        }
        
        const itemsHTML = this.items.map(item => `
            <div class="carrito-item" data-codigo="${item.producto_codigo}">
                <img src="https://via.placeholder.com/60x60/4285f4/ffffff?text=${item.producto_codigo.substring(0, 3)}" 
                     alt="${item.producto_codigo}" 
                     class="carrito-item-img">
                
                <div class="carrito-item-info">
                    <div class="carrito-item-title">Producto ${item.producto_codigo}</div>
                    <div class="carrito-item-code">#${item.producto_codigo}</div>
                    <div class="carrito-item-price">$10.00</div>
                </div>
                
                <div class="carrito-item-controls">
                    <input type="number" 
                           class="carrito-item-qty" 
                           value="${item.cantidad}" 
                           min="0" 
                           data-codigo="${item.producto_codigo}"
                           data-tipo="cantidad">
                    
                    <input type="number" 
                           class="carrito-item-discount" 
                           value="${item.descuento}" 
                           min="0" 
                           max="100" 
                           placeholder="%" 
                           data-codigo="${item.producto_codigo}"
                           data-tipo="descuento">
                    
                    <div class="carrito-item-total">
                        $${((10 * item.cantidad) * (1 - item.descuento / 100)).toFixed(2)}
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = itemsHTML;
        
        // Agregar event listeners para inputs
        this.setupItemInputListeners();
    }
    
    /**
     * 🎯 CONFIGURAR LISTENERS DE INPUTS DE ITEMS
     */
    setupItemInputListeners() {
        // Cantidad
        document.querySelectorAll('.carrito-item-qty').forEach(input => {
            input.addEventListener('input', (e) => {
                this.handleItemInputChange(e);
            });
            
            input.addEventListener('blur', () => {
                this.flushChanges();
            });
        });
        
        // Descuento
        document.querySelectorAll('.carrito-item-discount').forEach(input => {
            input.addEventListener('input', (e) => {
                this.handleItemInputChange(e);
            });
            
            input.addEventListener('blur', () => {
                this.flushChanges();
            });
        });
    }
    
    /**
     * 🔄 MANEJAR CAMBIO EN INPUTS DE ITEMS
     */
    handleItemInputChange(event) {
        const input = event.target;
        const codigo = input.dataset.codigo;
        const tipo = input.dataset.tipo;
        
        if (!codigo || !tipo) return;
        
        const item = this.items.find(i => i.producto_codigo === codigo);
        if (!item) return;
        
        if (tipo === 'cantidad') {
            item.cantidad = parseInt(input.value) || 0;
        } else if (tipo === 'descuento') {
            item.descuento = parseFloat(input.value) || 0;
        }
        
        // Actualizar total del item
        this.updateItemTotal(codigo);
    }
    
    /**
     * 💰 ACTUALIZAR TOTAL DE ITEM
     */
    updateItemTotal(codigo) {
        const item = this.items.find(i => i.producto_codigo === codigo);
        if (!item) return;
        
        const totalElement = document.querySelector(`[data-codigo="${codigo}"] .carrito-item-total`);
        if (totalElement) {
            const precio = 10; // Precio fijo por ahora
            const subtotal = precio * item.cantidad;
            const descuentoMonto = subtotal * (item.descuento / 100);
            const total = subtotal - descuentoMonto;
            
            totalElement.textContent = `$${total.toFixed(2)}`;
        }
    }
    
    /**
     * 🚀 FLUSH DE CAMBIOS PENDIENTES
     */
    async flushChanges() {
        if (!this.pedidoToken) return;
        
        try {
            const items = this.items.map(item => ({
                producto_codigo: item.producto_codigo,
                cantidad: item.cantidad,
                descuento: item.descuento
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
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    this.version = data.version;
                    this.resumen = data.resumen;
                    this.updateResumen();
                    this.updateFloatingButton();
                    
                    console.log('✅ Cambios guardados desde popup');
                }
            }
            
        } catch (error) {
            console.error('❌ Error en flush:', error);
        }
    }
    
    /**
     * 📊 ACTUALIZAR RESUMEN
     */
    updateResumen() {
        if (!this.resumen) return;
        
        const unidades = document.getElementById('resumenUnidades');
        const subtotal = document.getElementById('resumenSubtotal');
        const total = document.getElementById('resumenTotal');
        
        if (unidades) {
            unidades.textContent = this.resumen.cantidad_productos || 0;
        }
        
        if (subtotal) {
            subtotal.textContent = `$${(this.resumen.subtotal || 0).toFixed(2)}`;
        }
        
        if (total) {
            total.textContent = `$${(this.resumen.total_pedido || 0).toFixed(2)}`;
        }
    }
    
    /**
     * 🔘 ACTUALIZAR BOTÓN FLOTANTE
     */
    updateFloatingButton() {
        const contador = document.querySelector('.carrito-contador');
        if (contador && this.resumen) {
            contador.textContent = this.resumen.cantidad_productos || 0;
            
            // Ocultar contador si no hay items
            if (this.resumen.cantidad_productos === 0) {
                contador.style.display = 'none';
            } else {
                contador.style.display = 'flex';
            }
        }
    }
    
    /**
     * 🗑️ LIMPIAR CARRITO
     */
    async limpiarCarrito() {
        if (!this.pedidoToken || !confirm('¿Estás seguro de que quieres limpiar el carrito?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/pedido/items/batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Pedido-Token': this.pedidoToken
                },
                body: JSON.stringify({
                    pedido_id: this.pedidoId,
                    version: this.version,
                    items: []
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    this.version = data.version;
                    this.resumen = data.resumen;
                    this.items = [];
                    
                    this.updateResumen();
                    this.updateFloatingButton();
                    this.renderItems();
                    
                    console.log('✅ Carrito limpiado');
                }
            }
            
        } catch (error) {
            console.error('❌ Error limpiando carrito:', error);
        }
    }
    
    /**
     * ✅ FINALIZAR COMPRA
     */
    async finalizarCompra() {
        if (!this.pedidoToken) {
            alert('No hay carrito activo');
            return;
        }
        
        if (this.items.length === 0) {
            alert('El carrito está vacío');
            return;
        }
        
        if (confirm('¿Estás seguro de que quieres finalizar la compra?')) {
            try {
                const response = await fetch('/api/pedido/finalizar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Pedido-Token': this.pedidoToken
                    },
                    body: JSON.stringify({
                        pedido_id: this.pedidoId
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.success) {
                        alert('¡Compra finalizada exitosamente!');
                        this.closePopup();
                        
                        // Limpiar estado
                        this.items = [];
                        this.resumen = null;
                        this.updateFloatingButton();
                        
                        console.log('✅ Compra finalizada');
                    }
                }
                
            } catch (error) {
                console.error('❌ Error finalizando compra:', error);
                alert('Error al finalizar la compra');
            }
        }
    }
    
    /**
     * 🧹 LIMPIAR RECURSOS
     */
    destroy() {
        // Remover elementos del DOM
        const floatingButton = document.querySelector('.carrito-flotante');
        const overlay = document.querySelector('.carrito-popup-overlay');
        
        if (floatingButton) floatingButton.remove();
        if (overlay) overlay.remove();
        
        console.log('🧹 Carrito popup simple destruido');
    }
}

// Inicializar cuando DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.carritoPopupSimple = new CarritoPopupSimple();
});

console.log('🛒 Carrito Popup Simple cargado - Maruz Distribuciones');
