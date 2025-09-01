/**
 * SISTEMA DE CARRITO SIMPLE Y ROBUSTO
 * Para presentación crítica - DEBE FUNCIONAR
 */

// Variables globales
let carritoData = {};
let totalItems = 0;
let totalMonto = 0;

// Inicializar inmediatamente
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando carrito simple...');
    initCarritoSimple();
});

function initCarritoSimple() {
    try {
        // Cargar carrito del localStorage
        loadCarritoFromStorage();
        
        // Actualizar UI
        updateBarraResumen();
        
        // Configurar eventos
        setupEventListeners();
        
        // Guardar automáticamente cada 5 segundos
        setInterval(saveCarritoToStorage, 5000);
        
        console.log('✅ Carrito simple inicializado');
        
    } catch (error) {
        console.error('❌ Error iniciando carrito:', error);
    }
}

function loadCarritoFromStorage() {
    try {
        const stored = localStorage.getItem('maruz_carrito');
        if (stored) {
            carritoData = JSON.parse(stored);
            
            // Aplicar cantidades a los productos visibles
            Object.keys(carritoData).forEach(codigo => {
                const row = document.querySelector(`[data-codigo="${codigo}"]`);
                if (row) {
                    const qtyInput = row.querySelector('.qty');
                    const discountInput = row.querySelector('.discount');
                    
                    if (qtyInput) qtyInput.value = carritoData[codigo].cantidad || '';
                    if (discountInput) discountInput.value = carritoData[codigo].descuento || '';
                }
            });
            
            console.log('✅ Carrito cargado desde localStorage');
        }
    } catch (error) {
        console.warn('⚠️ Error cargando carrito:', error);
        carritoData = {};
    }
}

function saveCarritoToStorage() {
    try {
        localStorage.setItem('maruz_carrito', JSON.stringify(carritoData));
        console.log('💾 Carrito guardado');
    } catch (error) {
        console.warn('⚠️ Error guardando carrito:', error);
    }
}

function setupEventListeners() {
    // Escuchar cambios en cantidad y descuento
    document.addEventListener('input', function(e) {
        if (e.target.matches('.qty, .discount')) {
            handleProductChange(e.target);
        }
    });
    
    // Escuchar blur para guardar inmediatamente
    document.addEventListener('blur', function(e) {
        if (e.target.matches('.qty, .discount')) {
            handleProductChange(e.target);
            saveCarritoToStorage();
        }
    }, true);
    
    // Guardar antes de navegar
    window.addEventListener('beforeunload', function() {
        saveCarritoToStorage();
    });
    
    // Interceptar navegación
    document.addEventListener('click', function(e) {
        if (e.target.matches('a[href*="page="], button[type="submit"]')) {
            saveCarritoToStorage();
        }
    });
}

function handleProductChange(input) {
    try {
        const row = input.closest('.row');
        if (!row) return;
        
        const codigo = row.getAttribute('data-codigo');
        if (!codigo) return;
        
        const qtyInput = row.querySelector('.qty');
        const discountInput = row.querySelector('.discount');
        const priceEl = row.querySelector('.price');
        
        if (!qtyInput || !priceEl) return;
        
        const cantidad = parseInt(qtyInput.value) || 0;
        const descuento = parseFloat(discountInput.value) || 0;
        const precio = parseFloat(priceEl.textContent.replace(/[^\d.-]/g, ''));
        
        if (cantidad > 0) {
            // Agregar/actualizar en carrito
            carritoData[codigo] = {
                cantidad: cantidad,
                descuento: descuento,
                precio: precio,
                timestamp: Date.now()
            };
        } else {
            // Quitar del carrito
            delete carritoData[codigo];
        }
        
        // Actualizar totales
        calculateTotals();
        updateBarraResumen();
        
        console.log(`📦 Producto ${codigo} actualizado:`, carritoData[codigo]);
        
    } catch (error) {
        console.error('❌ Error manejando cambio:', error);
    }
}

function calculateTotals() {
    totalItems = 0;
    totalMonto = 0;
    
    Object.values(carritoData).forEach(item => {
        totalItems += item.cantidad;
        const subtotal = item.precio * item.cantidad;
        const descuentoMonto = (subtotal * item.descuento) / 100;
        totalMonto += subtotal - descuentoMonto;
    });
}

function updateBarraResumen() {
    calculateTotals();
    
    // Buscar o crear barra de resumen
    let summaryBar = document.getElementById('carrito-summary');
    
    if (!summaryBar) {
        summaryBar = createSummaryBar();
    }
    
    // Actualizar contenido
    if (totalItems > 0) {
        summaryBar.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; gap: 20px; color: white;">
                <span><strong>${totalItems}</strong> productos</span>
                <span><strong>$${totalMonto.toFixed(2)}</strong></span>
                <button onclick="mostrarResumenCarrito()" style="background: #16a34a; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                    Ver Carrito
                </button>
            </div>
        `;
        summaryBar.style.display = 'block';
    } else {
        summaryBar.style.display = 'none';
    }
}

function createSummaryBar() {
    const summaryBar = document.createElement('div');
    summaryBar.id = 'carrito-summary';
    summaryBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 12px;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: none;
    `;
    
    document.body.insertBefore(summaryBar, document.body.firstChild);
    
    // Ajustar el body para que no se oculte contenido
    document.body.style.paddingTop = '60px';
    
    return summaryBar;
}

function mostrarResumenCarrito() {
    const items = Object.entries(carritoData);
    if (items.length === 0) {
        alert('El carrito está vacío');
        return;
    }
    
    let resumen = `📦 RESUMEN DEL CARRITO\\n\\n`;
    resumen += `Total productos: ${totalItems}\\n`;
    resumen += `Total monto: $${totalMonto.toFixed(2)}\\n\\n`;
    resumen += `PRODUCTOS:\\n`;
    
    items.forEach(([codigo, item]) => {
        const subtotal = item.precio * item.cantidad;
        const descuentoMonto = (subtotal * item.descuento) / 100;
        const total = subtotal - descuentoMonto;
        
        resumen += `• ${codigo}: ${item.cantidad} x $${item.precio.toFixed(2)}`;
        if (item.descuento > 0) {
            resumen += ` (${item.descuento}% desc)`;
        }
        resumen += ` = $${total.toFixed(2)}\\n`;
    });
    
    alert(resumen);
}

// Función global para limpiar carrito
function limpiarCarrito() {
    if (confirm('¿Estás seguro de que quieres limpiar el carrito?')) {
        carritoData = {};
        localStorage.removeItem('maruz_carrito');
        
        // Limpiar inputs visibles
        document.querySelectorAll('.qty, .discount').forEach(input => {
            input.value = '';
        });
        
        updateBarraResumen();
        console.log('🗑️ Carrito limpiado');
    }
}

// Exportar funciones para uso global
window.mostrarResumenCarrito = mostrarResumenCarrito;
window.limpiarCarrito = limpiarCarrito;
