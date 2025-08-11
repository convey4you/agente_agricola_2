// ALERTS MANAGER - Sistema de Alertas Inteligentes
// Gerenciamento de alertas no frontend

class AlertsManager {
    constructor() {
        this.alerts = [];
        this.unreadCount = 0;
        this.init();
    }
    
    init() {
        console.log('AlertsManager inicializado');
        this.setupEventListeners();
        this.loadAlertsWidget();
        
        // Auto-refresh a cada 2 minutos
        setInterval(() => {
            this.refreshAlerts();
        }, 2 * 60 * 1000);
    }
    
    setupEventListeners() {
        // Event listeners para ações dos alertas
        document.addEventListener('click', (e) => {
            console.log('Click detectado:', e.target);
            
            // Verificar se clicou no botão ou no ícone dentro do botão
            let button = e.target;
            if (e.target.tagName === 'I') {
                button = e.target.closest('button');
            }
            
            if (button && button.matches('.alert-mark-read')) {
                console.log('Clique em marcar como lido');
                const alertId = button.dataset.alertId;
                console.log('Alert ID:', alertId);
                this.markAsRead(alertId);
            }
            
            if (button && button.matches('.alert-resolve')) {
                console.log('Clique em resolver');
                const alertId = button.dataset.alertId;
                console.log('Alert ID:', alertId);
                this.resolveAlert(alertId);
            }
            
            if (e.target.matches('.alert-acknowledge')) {
                const alertId = e.target.dataset.alertId;
                this.acknowledgeAlert(alertId);
            }
            
            if (e.target.matches('.alert-generate')) {
                this.generateAlerts();
            }
            
            if (e.target.matches('.alert-refresh')) {
                this.refreshAlerts();
            }
            
            if (e.target.matches('.alerts-mark-all-read')) {
                this.markAllAsRead();
            }
            
            if (e.target.matches('.toast-close')) {
                e.target.closest('.toast').remove();
            }
        });
        
        // Event listeners para filtros
        document.addEventListener('change', (e) => {
            if (e.target.matches('.alert-filter')) {
                this.filterAlerts();
            }
        });
    }
    
    async loadAlertsWidget() {
        try {
            const response = await fetch('/api/alerts/widget');
            
            if (!response.ok) {
                // Tratar diferentes códigos de erro
                if (response.status === 401) {
                    console.log('Usuário não autenticado - widget de alertas indisponível');
                    this.updateWidgetWithError('Faça login para ver alertas');
                } else if (response.status === 500) {
                    console.log('Erro interno do servidor no widget de alertas');
                    this.updateWidgetWithError('Temporariamente indisponível');
                } else {
                    console.log('Erro ao carregar widget:', response.status);
                    this.updateWidgetWithError('Erro ao carregar');
                }
                return;
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.updateWidget(data.data);
                console.log('Widget de alertas carregado com sucesso');
            } else {
                console.log('Erro ao carregar widget:', data.error);
                this.updateWidgetWithError('Erro ao carregar dados');
            }
        } catch (error) {
            console.log('Erro de rede ao carregar widget de alertas:', error.message);
            this.updateWidgetWithError('Problema de conexão');
        }
    }
    
    updateWidgetWithError(message) {
        // Atualizar widget com mensagem de erro amigável
        const widgets = document.querySelectorAll('.alerts-widget');
        widgets.forEach(widget => {
            widget.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-exclamation-triangle text-yellow-500 text-2xl mb-2"></i>
                    <p class="text-sm text-gray-600">${message}</p>
                </div>
            `;
        });
    }
    
    updateWidget(data) {
        const container = document.getElementById('alerts-widget');
        if (!container) return;
        
        const stats = data.stats;
        const criticalAlerts = data.critical_alerts || [];
        const recentAlerts = data.recent_alerts || [];
        
        // Atualizar badge de notificações
        this.updateNotificationBadge(stats.unread);
        
        container.innerHTML = `
            <div class="alerts-header flex justify-between items-center mb-3">
                <h3 class="text-lg font-semibold text-gray-800">
                    <i class="fas fa-bell text-blue-600 mr-2"></i>
                    Alertas
                </h3>
                <div class="flex items-center space-x-2">
                    ${stats.unread > 0 ? `
                        <span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                            ${stats.unread} não lidos
                        </span>
                    ` : ''}
                    <button class="alert-generate text-green-600 hover:text-green-800 text-sm" title="Gerar novos alertas">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                </div>
            </div>
            
            ${stats.critical > 0 ? `
                <div class="critical-alerts mb-4">
                    <div class="bg-red-50 border-l-4 border-red-400 p-3 mb-3">
                        <div class="flex items-center">
                            <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
                            <span class="text-red-800 font-medium">
                                ${stats.critical} alerta${stats.critical > 1 ? 's' : ''} crítico${stats.critical > 1 ? 's' : ''}
                            </span>
                        </div>
                    </div>
                    ${criticalAlerts.slice(0, 2).map(alert => this.renderAlertItem(alert)).join('')}
                </div>
            ` : ''}
            
            <div class="recent-alerts">
                <div class="text-sm font-medium text-gray-700 mb-2">Alertas Recentes</div>
                ${recentAlerts.length > 0 ? `
                    <div class="space-y-2">
                        ${recentAlerts.map(alert => this.renderAlertItem(alert)).join('')}
                    </div>
                ` : `
                    <div class="text-center py-4 text-gray-500">
                        <i class="fas fa-check-circle text-green-500 text-2xl mb-2"></i>
                        <p class="text-sm">Nenhum alerta ativo</p>
                    </div>
                `}
            </div>
            
            <div class="alerts-footer mt-4 pt-3 border-t border-gray-200">
                <div class="flex justify-between items-center">
                    <a href="/alerts" class="text-blue-600 hover:text-blue-800 text-sm">
                        Ver todos os alertas
                    </a>
                    ${stats.unread > 0 ? `
                        <button class="alerts-mark-all-read text-gray-600 hover:text-gray-800 text-sm">
                            Marcar todos como lidos
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    renderAlertItem(alert) {
        const priorityColors = {
            'critical': 'border-red-400 bg-red-50',
            'medium': 'border-orange-400 bg-orange-50',
            'low': 'border-blue-400 bg-blue-50'
        };
        
        const priorityColor = priorityColors[alert.priority] || 'border-gray-400 bg-gray-50';
        
        return `
            <div class="alert-item border-l-4 ${priorityColor} p-3 mb-2 rounded-r">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="flex items-center mb-1">
                            <i class="fas ${alert.type_icon} text-${alert.priority_color}-600 mr-2"></i>
                            <span class="font-medium text-gray-800 text-sm">${alert.title}</span>
                            ${!alert.is_read ? '<span class="w-2 h-2 bg-blue-500 rounded-full ml-2"></span>' : ''}
                        </div>
                        <p class="text-xs text-gray-600 leading-relaxed">${alert.message}</p>
                        ${alert.culture_name ? `
                            <div class="mt-1">
                                <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                    ${alert.culture_name}
                                </span>
                            </div>
                        ` : ''}
                        <div class="text-xs text-gray-400 mt-1">
                            ${this.formatDate(alert.created_at)}
                        </div>
                    </div>
                    <div class="flex flex-col space-y-1 ml-2">
                        ${!alert.is_read ? `
                            <button class="alert-mark-read text-blue-600 hover:text-blue-800 text-xs" 
                                    data-alert-id="${alert.id}" title="Marcar como lido">
                                <i class="fas fa-eye"></i>
                            </button>
                        ` : ''}
                        ${!alert.is_resolved ? `
                            <button class="alert-resolve text-green-600 hover:text-green-800 text-xs" 
                                    data-alert-id="${alert.id}" title="Resolver">
                                <i class="fas fa-check"></i>
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    updateNotificationBadge(count) {
        const badge = document.getElementById('alerts-notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
        
        // Atualizar título da página se houver alertas não lidos
        if (count > 0) {
            document.title = `(${count}) AgTech Portugal - Dashboard`;
        } else {
            document.title = 'AgTech Portugal - Dashboard';
        }
    }
    
    getCSRFToken() {
        return window.csrfToken || '';
    }
    
    async markAsRead(alertId) {
        try {
            console.log('Enviando requisição para marcar alerta como lido:', alertId);
            
            const headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            };
            
            // Adicionar token CSRF se disponível
            if (window.csrfToken) {
                headers['X-CSRF-Token'] = window.csrfToken;
                console.log('🔒 Token CSRF adicionado ao header');
            } else {
                console.warn('⚠️ Token CSRF não encontrado!');
            }
            
            const response = await fetch(`/api/alerts/${alertId}/read`, {
                method: 'POST',
                headers: headers,
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            console.log('Resposta da API:', data);
            
            if (data.status === 'success') {
                console.log('Alerta marcado como lido');
                this.refreshAlerts();
            } else {
                console.error('Erro ao marcar como lido:', data.message);
            }
        } catch (error) {
            console.error('Erro ao marcar alerta como lido:', error);
        }
    }
    
    async resolveAlert(alertId) {
        try {
            console.log('Enviando requisição para resolver alerta:', alertId);
            
            const headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            };
            
            // Adicionar token CSRF se disponível
            if (window.csrfToken) {
                headers['X-CSRF-Token'] = window.csrfToken;
                console.log('🔒 Token CSRF adicionado ao header');
            } else {
                console.warn('⚠️ Token CSRF não encontrado!');
            }
            
            const response = await fetch(`/api/alerts/${alertId}/dismiss`, {
                method: 'POST',
                headers: headers,
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            console.log('Resposta da API:', data);
            
            if (data.status === 'success') {
                console.log('Alerta resolvido');
                this.refreshAlerts();
            } else {
                console.error('Erro ao resolver alerta:', data.message);
            }
        } catch (error) {
            console.error('Erro ao resolver alerta:', error);
        }
    }
    
    async generateAlerts() {
        try {
            // Mostrar loading
            const button = document.querySelector('.alert-generate');
            if (button) {
                const icon = button.querySelector('i');
                icon.classList.add('fa-spin');
            }
            
            const response = await fetch('/api/alerts/generate');
            const data = await response.json();
            
            if (data.success) {
                console.log(`${data.count} novos alertas gerados`);
                this.refreshAlerts();
                
                // Mostrar notificação de sucesso
                this.showNotification(`${data.count} novos alertas gerados`, 'success');
            } else {
                console.error('Erro ao gerar alertas:', data.error);
                this.showNotification('Erro ao gerar alertas', 'error');
            }
        } catch (error) {
            console.error('Erro ao gerar alertas:', error);
            this.showNotification('Erro ao gerar alertas', 'error');
        } finally {
            // Remover loading
            const button = document.querySelector('.alert-generate');
            if (button) {
                const icon = button.querySelector('i');
                icon.classList.remove('fa-spin');
            }
        }
    }
    
    async markAllAsRead() {
        try {
            const response = await fetch('/api/alerts/bulk-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Todos os alertas marcados como lidos');
                this.refreshAlerts();
                this.showNotification('Todos os alertas marcados como lidos', 'success');
            } else {
                console.error('Erro ao marcar todos como lidos:', data.error);
            }
        } catch (error) {
            console.error('Erro ao marcar todos como lidos:', error);
        }
    }
    
    async refreshAlerts() {
        await this.loadAlertsWidget();
    }
    
    formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        // Menos de 1 minuto
        if (diff < 60000) {
            return 'Agora mesmo';
        }
        
        // Menos de 1 hora
        if (diff < 3600000) {
            const minutes = Math.floor(diff / 60000);
            return `${minutes} min atrás`;
        }
        
        // Menos de 24 horas
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours}h atrás`;
        }
        
        // Mais de 24 horas
        return date.toLocaleDateString('pt-PT', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    showNotification(message, type = 'info') {
        // Criar notificação temporária
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
            type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' :
            type === 'error' ? 'bg-red-100 text-red-800 border border-red-200' :
            'bg-blue-100 text-blue-800 border border-blue-200'
        }`;
        
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${
                    type === 'success' ? 'fa-check-circle' :
                    type === 'error' ? 'fa-exclamation-circle' :
                    'fa-info-circle'
                } mr-2"></i>
                <span>${message}</span>
                <button class="ml-4 text-gray-600 hover:text-gray-800" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remover após 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar em páginas com dashboard ou página de alertas
    if (document.querySelector('.dashboard-grid') || window.location.pathname.includes('/alerts')) {
        window.alertsManager = new AlertsManager();
        console.log('Sistema de Alertas Inteligentes ativado');
    }
});

// Exportar para uso global
window.AlertsManager = AlertsManager;
