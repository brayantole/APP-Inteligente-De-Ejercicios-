// Funcionalidades JavaScript para FitBoost Pro

document.addEventListener('DOMContentLoaded', function() {
    inicializarApp();
});

function inicializarApp() {
    // Inicializar filtros en página de rutinas
    inicializarFiltrosRutinas();
    
    // Inicializar interactividad del formulario
    inicializarFormulario();
    
    // Inicializar funcionalidades de la página de resumen
    inicializarResumen();

    // Inicializar Modal de Dieta
    inicializarModalDieta();
}

// ===== MODAL DIETA =====
function inicializarModalDieta() {
    const modal = document.getElementById('modal-dieta');
    const btn = document.getElementById('nav-dieta');
    const span = document.querySelector('.close-modal');

    if (btn && modal) {
        // Abrir modal
        btn.addEventListener('click', function(e) {
            e.preventDefault(); // Evita que la página recargue
            modal.style.display = "flex";
        });

        // Cerrar con la X
        if (span) {
            span.addEventListener('click', function() {
                modal.style.display = "none";
            });
        }

        // Cerrar al hacer click fuera del modal
        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    }
}

// ===== FILTROS DE RUTINAS =====
function inicializarFiltrosRutinas() {
    const filtroNombre = document.getElementById('filtro-nombre');
    const filtroVariante = document.getElementById('filtro-variante');
    const rutinasGrid = document.getElementById('rutinas-grid');
    const noResultados = document.getElementById('no-resultados');

    if (filtroNombre && filtroVariante) {
        function filtrarRutinas() {
            const nombreSeleccionado = filtroNombre.value;
            const varianteSeleccionada = filtroVariante.value;
            let rutinasVisibles = 0;

            document.querySelectorAll('.rutina-card').forEach(card => {
                const nombre = card.dataset.nombre;
                const variante = card.dataset.variante;
                
                const coincideNombre = !nombreSeleccionado || nombre === nombreSeleccionado;
                const coincideVariante = !varianteSeleccionada || variante === varianteSeleccionada;
                
                if (coincideNombre && coincideVariante) {
                    card.style.display = 'block';
                    rutinasVisibles++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Mostrar mensaje si no hay resultados
            if (rutinasVisibles === 0) {
                rutinasGrid.style.display = 'none';
                noResultados.style.display = 'block';
            } else {
                rutinasGrid.style.display = 'grid';
                noResultados.style.display = 'none';
            }
        }

        filtroNombre.addEventListener('change', filtrarRutinas);
        filtroVariante.addEventListener('change', filtrarRutinas);
    }
}

// ===== FORMULARIO INTERACTIVO =====
function inicializarFormulario() {
    // Mostrar/ocultar campos de suplementos
    const checkboxSuplementos = document.getElementById('usar_suplementos');
    const grupoPresupuesto = document.getElementById('presupuesto-group');

    if (checkboxSuplementos && grupoPresupuesto) {
        checkboxSuplementos.addEventListener('change', function() {
            if (this.checked) {
                grupoPresupuesto.style.display = 'block';
            } else {
                grupoPresupuesto.style.display = 'none';
            }
        });
    }

    // Mostrar/ocultar intervalos de recordatorios
    const checkboxAgua = document.getElementById('recordatorio_agua');
    const intervaloAgua = document.getElementById('intervalo_agua');
    
    const checkboxEjercicio = document.getElementById('recordatorio_ejercicio');
    const intervaloEjercicio = document.getElementById('intervalo_ejercicio');

    if (checkboxAgua && intervaloAgua) {
        checkboxAgua.addEventListener('change', function() {
            intervaloAgua.style.display = this.checked ? 'block' : 'none';
            if (this.checked) intervaloAgua.required = true;
            else intervaloAgua.required = false;
        });
    }

    if (checkboxEjercicio && intervaloEjercicio) {
        checkboxEjercicio.addEventListener('change', function() {
            intervaloEjercicio.style.display = this.checked ? 'block' : 'none';
            if (this.checked) intervaloEjercicio.required = true;
            else intervaloEjercicio.required = false;
        });
    }

    // Actualizar multiplicador de actividad
    const selectActividad = document.getElementById('nivel_actividad');
    const inputMultiplicador = document.getElementById('multiplicador_actividad');

    if (selectActividad && inputMultiplicador) {
        selectActividad.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const multiplicador = selectedOption.dataset.multiplicador;
            if (multiplicador) {
                inputMultiplicador.value = multiplicador;
            }
        });
    }

    // Validación del formulario
    const formulario = document.getElementById('planForm');
    if (formulario) {
        formulario.addEventListener('submit', function(e) {
            if (!validarFormulario()) {
                e.preventDefault();
                mostrarNotificacion('Por favor completa todos los campos requeridos correctamente.', 'error');
            }
        });
    }
}

function validarFormulario() {
    let valido = true;
    
    // Validar edad
    const edad = document.getElementById('edad');
    if (edad && (edad.value < 10 || edad.value > 100)) {
        valido = false;
        resaltarError(edad);
    }
    
    // Validar peso
    const peso = document.getElementById('peso_kg');
    if (peso && (peso.value < 25 || peso.value > 250)) {
        valido = false;
        resaltarError(peso);
    }
    
    // Validar altura
    const altura = document.getElementById('altura_m');
    if (altura && (altura.value < 1.00 || altura.value > 2.30)) {
        valido = false;
        resaltarError(altura);
    }
    
    return valido;
}

function resaltarError(elemento) {
    elemento.style.borderColor = '#e74c3c';
    elemento.addEventListener('input', function() {
        this.style.borderColor = '#3498db';
    }, { once: true });
}

// ===== FUNCIONALIDADES DEL RESUMEN =====
function inicializarResumen() {
    // Agregar funcionalidad de impresión
    const botonesImprimir = document.querySelectorAll('[onclick*="window.print"]');
    botonesImprimir.forEach(boton => {
        boton.addEventListener('click', function() {
            window.print();
        });
    });
}

// ===== COPiar RUTINA AL PORTAPAPELES =====
function copiarRutina() {
    const contenido = document.querySelector('.contenido-texto').innerText;
    
    navigator.clipboard.writeText(contenido).then(function() {
        mostrarNotificacion('¡Rutina copiada al portapapeles! 📋', 'success');
    }).catch(function(err) {
        console.error('Error al copiar: ', err);
        mostrarNotificacion('Error al copiar la rutina', 'error');
    });
}

// ===== NOTIFICACIONES =====
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear elemento de notificación
    const notificacion = document.createElement('div');
    notificacion.className = `notificacion notificacion-${tipo}`;
    notificacion.innerHTML = `
        <div class="notificacion-contenido">
            <span class="notificacion-mensaje">${mensaje}</span>
            <button class="notificacion-cerrar" onclick="this.parentElement.parentElement.remove()">
                ×
            </button>
        </div>
    `;

    // Estilos para la notificación
    notificacion.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${tipo === 'success' ? '#27ae60' : tipo === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
    `;

    notificacion.querySelector('.notificacion-contenido').style.cssText = `
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    `;

    notificacion.querySelector('.notificacion-cerrar').style.cssText = `
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    `;

    // Agregar al documento
    document.body.appendChild(notificacion);

    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (notificacion.parentElement) {
            notificacion.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notificacion.remove(), 300);
        }
    }, 5000);
}

// ===== ANIMACIONES CSS =====
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }

    @media print {
        .navbar, .footer, .resumen-actions, .back-link, .rutina-actions-sidebar {
            display: none !important;
        }
        
        body {
            background: white !important;
        }
        
        .resumen-card, .rutina-contenido-card {
            box-shadow: none !important;
            border: 1px solid #ccc !important;
            break-inside: avoid;
        }
    }
`;
document.head.appendChild(style);