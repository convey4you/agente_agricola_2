// Aplicação principal AgTech Portugal
class AgTechApp {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupNavigation();
        this.setupServiceWorker();
        this.setupNotifications();
        this.setupOfflineDetection();
        this.loadDashboard();
    }
    
    setupNavigation() {
        // Toggle sidebar em mobile
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
            
            // Fechar sidebar ao clicar fora (mobile)
            document.addEventListener('click', (e) => {
                if (window.innerWidth <= 768 && 
                    !sidebar.contains(e.target) && 
                    !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            });
        }
        
        // Atualizar navegação ativa
        this.updateActiveNavigation();
    }
    
    updateActiveNavigation() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }
    
    setupServiceWorker() {
        // Verificar se estamos em produção
        const isProduction = window.location.hostname !== 'localhost' && 
                            window.location.hostname !== '127.0.0.1' &&
                            !window.location.hostname.includes('localhost');
        
        if (isProduction && 'serviceWorker' in navigator) {
            // FORÇAR atualização do Service Worker
            navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' })
                .then(registration => {
                    console.log('Service Worker registrado:', registration);
                    
                    // FORÇAR verificação de atualizações
                    registration.update();
                    
                    // Listener para novas versões
                    registration.addEventListener('updatefound', () => {
                        console.log('Nova versão do Service Worker encontrada');
                        const newWorker = registration.installing;
                        
                        newWorker.addEventListener('statechange', () => {
                            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                console.log('Nova versão instalada - recarregando página');
                                // Auto-reload para aplicar nova versão
                                window.location.reload();
                            }
                        });
                    });
                })
                .catch(error => {
                    console.log('Erro ao registrar Service Worker:', error);
                });
        } else {
            console.log('Service Worker desabilitado (desenvolvimento)');
        }
    }
    
    setupNotifications() {
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                Notification.requestPermission().then(permission => {
                    console.log('Permissão de notificação:', permission);
                });
            }
        }
    }
    
    setupOfflineDetection() {
        const updateOnlineStatus = () => {
            const status = navigator.onLine ? 'online' : 'offline';
            document.body.classList.toggle('offline', !navigator.onLine);
            
            if (!navigator.onLine) {
                Utils.showToast('Sem conexão com a internet', 'warning');
            }
        };
        
        window.addEventListener('online', updateOnlineStatus);
        window.addEventListener('offline', updateOnlineStatus);
        updateOnlineStatus();
    }
    
    loadDashboard() {
        if (document.querySelector('.dashboard-grid')) {
            this.refreshDashboardData();
            
            // Atualizar dados a cada 5 minutos
            setInterval(() => {
                this.refreshDashboardData();
            }, 5 * 60 * 1000);
        }
    }
    
    async refreshDashboardData() {
        try {
            const response = await fetch('/api/dashboard/stats', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            if (!response.ok) throw new Error('Erro ao carregar dados');
            
            const data = await response.json();
            this.updateDashboardCards(data);
            
        } catch (error) {
            console.error('Erro ao atualizar dashboard:', error);
        }
    }
    
    updateDashboardCards(data) {
        // Atualizar métricas
        if (data.overview) {
            const overviewCard = document.querySelector('.overview-card .card-content');
            if (overviewCard) {
                overviewCard.innerHTML = `
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <span class="metric-value">${data.overview.active_cultures || 0}</span>
                            <span class="metric-label">Culturas Ativas</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-value">${data.overview.total_area || 0}m²</span>
                            <span class="metric-label">Área Total</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-value">${Utils.formatCurrency(data.overview.projected_revenue || 0)}</span>
                            <span class="metric-label">Receita Prevista</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-value">${data.overview.pending_tasks || 0}</span>
                            <span class="metric-label">Tarefas Pendentes</span>
                        </div>
                    </div>
                `;
            }
        }
        
        // Atualizar alertas
        if (data.alerts) {
            const alertsContainer = document.querySelector('.alerts-container');
            if (alertsContainer) {
                alertsContainer.innerHTML = data.alerts.map(alert => 
                    this.createAlertElement(alert)
                ).join('');
            }
        }
        
        // Atualizar clima
        if (data.weather) {
            this.updateWeatherCard(data.weather);
        }
    }
    
    createAlertElement(alert) {
        const alertClass = alert.priority === 'high' ? 'critical' : 
                          alert.priority === 'medium' ? 'warning' : 'info';
        
        return `
            <div class="alert ${alertClass}">
                <i class="alert-icon fas ${this.getAlertIcon(alert.type)}"></i>
                <div class="alert-content">
                    <div class="alert-title">${alert.title}</div>
                    <div class="alert-description">${alert.description}</div>
                </div>
            </div>
        `;
    }
    
    getAlertIcon(type) {
        const icons = {
            weather: 'fa-cloud-rain',
            pest: 'fa-bug',
            disease: 'fa-virus',
            irrigation: 'fa-tint',
            harvest: 'fa-cut',
            fertilizer: 'fa-leaf'
        };
        return icons[type] || 'fa-info-circle';
    }
    
    updateWeatherCard(weather) {
        const weatherCard = document.querySelector('.weather-card .card-content');
        if (weatherCard && weather.current) {
            // Usar EXATAMENTE o mesmo layout do template do servidor
            weatherCard.innerHTML = `
                <div class="weather-current text-center mb-4">
                    <div class="text-3xl font-bold text-gray-800 mb-1">${weather.current.temperature}°C</div>
                    <div class="text-gray-600 mb-2">${weather.current.condition}</div>
                    
                    <div class="grid grid-cols-2 gap-4 text-sm text-gray-500 mb-4">
                        <div class="text-center">
                            <i class="fas fa-tint text-blue-500"></i>
                            <div>${weather.current.humidity}%</div>
                            <div class="text-xs">Humidade</div>
                        </div>
                        <div class="text-center">
                            <i class="fas fa-wind text-gray-500"></i>
                            <div>${(weather.current.wind_speed || 0).toFixed(1)} m/s</div>
                            <div class="text-xs">Vento</div>
                        </div>
                    </div>
                    
                    ${weather.current.alerts && weather.current.alerts.length > 0 ? `
                        <div class="weather-alerts mb-4">
                            ${weather.current.alerts.map(alert => `
                                <div class="text-xs px-2 py-1 bg-orange-100 text-orange-800 rounded mb-1">
                                    ${alert.title}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
                
                <div class="weather-forecast">
                    <div class="text-sm font-medium text-gray-700 mb-2">Previsão 5 dias</div>
                    <div class="space-y-2">
                        ${(weather.forecast || []).slice(0, 5).map(day => {
                            // Formatação de data compatível com strftime('%a') do Python
                            let dayName = 'N/A';
                            if (day.date) {
                                try {
                                    const date = new Date(day.date);
                                    // Usar abreviações portuguesas como no servidor
                                    const days = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb'];
                                    dayName = days[date.getDay()];
                                } catch (e) {
                                    dayName = 'N/A';
                                }
                            }
                            
                            return `
                                <div class="flex justify-between items-center text-sm py-1">
                                    <span class="w-12">${dayName}</span>
                                    <span class="flex-1 text-center text-xs text-gray-500">
                                        ${day.condition || 'N/A'}
                                    </span>
                                    <span class="text-right">
                                        <span class="text-gray-800 font-medium">${day.temperature_max}°</span>
                                        <span class="text-gray-500">/${day.temperature_min}°</span>
                                    </span>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }
    }
}

// Utilitários
class Utils {
    static formatDate(date) {
        return new Intl.DateTimeFormat('pt-PT', {
            weekday: 'short',
            month: 'short',
            day: 'numeric'
        }).format(new Date(date));
    }
    
    static formatCurrency(amount) {
        return new Intl.NumberFormat('pt-PT', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    }
    
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    static showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert ${type} fixed top-4 right-4 z-50 max-w-sm`;
        toast.innerHTML = `
            <i class="alert-icon fas fa-info-circle"></i>
            <div class="alert-content">
                <div class="alert-title">${message}</div>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
    
    static showLoading(show = true) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.toggle('hidden', !show);
        }
    }
    
    static async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
}

// Funcionalidades específicas para formulários
class FormHandler {
    static init() {
        // Validação em tempo real
        document.querySelectorAll('.form-input').forEach(input => {
            input.addEventListener('blur', (e) => {
                FormHandler.validateField(e.target);
            });
        });
        
        // Submissão de formulários
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                FormHandler.handleSubmit(e);
            });
        });
    }
    
    static validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        
        // Remover classes de erro anteriores
        field.classList.remove('border-red-500');
        
        // Validação obrigatória
        if (required && !value) {
            FormHandler.showFieldError(field, 'Este campo é obrigatório');
            return false;
        }
        
        // Validação por tipo
        if (value) {
            if (type === 'email' && !FormHandler.isValidEmail(value)) {
                FormHandler.showFieldError(field, 'Email inválido');
                return false;
            }
            
            if (field.name === 'password' && value.length < 6) {
                FormHandler.showFieldError(field, 'Senha deve ter pelo menos 6 caracteres');
                return false;
            }
        }
        
        // Campo válido
        FormHandler.clearFieldError(field);
        return true;
    }
    
    static isValidEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }
    
    static showFieldError(field, message) {
        field.classList.add('border-red-500');
        
        // Remover erro anterior
        FormHandler.clearFieldError(field);
        
        // Adicionar nova mensagem de erro
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error text-red-500 text-sm mt-1';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    }
    
    static clearFieldError(field) {
        field.classList.remove('border-red-500');
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    static async handleSubmit(event) {
        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"]');
        
        // Validar todos os campos
        const fields = form.querySelectorAll('.form-input');
        let isValid = true;
        
        fields.forEach(field => {
            if (!FormHandler.validateField(field)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            event.preventDefault();
            return;
        }
        
        // Mostrar loading no botão
        if (submitButton) {
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.innerHTML = '<div class="loading"></div> A processar...';
            
            // Restaurar após 5 segundos (fallback)
            setTimeout(() => {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }, 5000);
        }
    }
}

// Inicializar aplicação quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    new AgTechApp();
    FormHandler.init();
    
    // Event listeners para o modal de logout
    const logoutBtn = document.getElementById('logout-btn');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showLogoutModal();
        });
    }
    
    if (modalCancelBtn) {
        modalCancelBtn.addEventListener('click', closeLogoutModal);
    }
    
    // Event listener para fechar modal clicando no fundo
    const logoutModal = document.getElementById('logoutModal');
    if (logoutModal) {
        logoutModal.addEventListener('click', function(e) {
            if (e.target === logoutModal) {
                closeLogoutModal();
            }
        });
    }
});

// Funções para o modal de logout - Estilo Elegante
function showLogoutModal() {
    console.log('🔔 Mostrando modal de logout');
    const modal = document.getElementById('logoutModal');
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden'; // Impedir scroll
        console.log('✅ Modal de logout exibido com sucesso');
    } else {
        console.error('❌ Modal de logout não encontrado');
    }
}
    // Modal AJAX loader for culture wizard
    document.addEventListener('DOMContentLoaded', function() {
        const openWizardBtn = document.getElementById('open-wizard-btn');
        const wizardModal = document.getElementById('wizard-modal');
        const wizardContent = document.getElementById('wizard-content');
        if (openWizardBtn && wizardModal && wizardContent) {
            openWizardBtn.addEventListener('click', function(e) {
                e.preventDefault();
                // Show loading indicator (optional)
                wizardContent.innerHTML = '<div class="p-8 text-center text-gray-500">Carregando...</div>';
                wizardModal.classList.remove('hidden');
                fetch('/cultures/wizard?modal=true', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.text())
                .then(html => {
                    wizardContent.innerHTML = html;
                    setTimeout(initWizardModalEvents, 50); // Ensure DOM is ready
                })
                .catch(() => {
                    wizardContent.innerHTML = '<div class="p-8 text-center text-red-500">Erro ao carregar o assistente.</div>';
                });
        });
    }

    // Re-initialize wizard modal events after AJAX load
    function initWizardModalEvents() {
        // Form submit
        const wizardForm = document.getElementById('wizardStep1Form');
        if (wizardForm) {
            wizardForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = {
                    step: '1',
                    nome: document.getElementById('nome').value.trim(),
                    tipo: document.getElementById('tipo').value,
                    variedade: document.getElementById('variedade').value.trim()
                };
                if (!formData.nome || !formData.tipo) {
                    alert('Por favor, preencha os campos obrigatórios.');
                    return;
                }
                try {
                    const response = await fetch('/cultures/wizard/save', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });
                    const result = await response.json();
                    if (result.success) {
                        loadWizardStep(2);
                    } else {
                        alert('Erro ao salvar dados: ' + (result.error || 'Erro desconhecido'));
                    }
                } catch (error) {
                    alert('Erro de conexão. Tente novamente.');
                }
            });
        }
        // Cancel button
        const cancelBtn = document.getElementById('cancel-wizard-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', function() {
                if (confirm('Deseja cancelar a criação da cultura? Os dados não salvos serão perdidos.')) {
                    wizardModal.classList.add('hidden');
                    wizardContent.innerHTML = '';
                }
            });
        }
        // Close button
        const closeBtn = document.getElementById('close-modal-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                if (confirm('Deseja fechar o wizard? Os dados não salvos serão perdidos.')) {
                    wizardModal.classList.add('hidden');
                    wizardContent.innerHTML = '';
                }
            });
        }
    }

    // Load next wizard step via AJAX
    function loadWizardStep(step) {
        wizardContent.innerHTML = '<div class="p-8 text-center text-gray-500">Carregando...</div>';
        fetch(`/cultures/wizard?step=${step}&modal=true`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.text())
        .then(html => {
            wizardContent.innerHTML = html;
            setTimeout(initWizardModalEvents, 50);
        })
        .catch(() => {
            wizardContent.innerHTML = '<div class="p-8 text-center text-red-500">Erro ao carregar o assistente.</div>';
        });
    }
    // Close wizard modal on click outside
    document.addEventListener('click', function(e) {
        if (wizardModal && !wizardModal.classList.contains('hidden')) {
            if (e.target === wizardModal) {
                wizardModal.classList.add('hidden');
                wizardContent.innerHTML = '';
            }
        }
    });
});

function closeLogoutModal() {
    console.log('🔄 Fechando modal de logout');
    const modal = document.getElementById('logoutModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = ''; // Restaurar scroll
        console.log('✅ Modal de logout fechado com sucesso');
    } else {
        console.error('❌ Modal de logout não encontrado');
    }
}

// Fechar modal ao clicar no overlay - Removido (agora está no event listener acima)

// Fechar modal com tecla ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modal = document.getElementById('logoutModal');
        if (modal && modal.classList.contains('show')) {
            closeLogoutModal();
        }
    }
});

// Exportar para uso global
window.AgTech = {
    Utils,
    FormHandler
};
