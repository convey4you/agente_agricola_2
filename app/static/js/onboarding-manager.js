/**
 * Sistema de Onboarding - AgroTech Portugal
 * JavaScript para interface interativa do onboarding
 */

class OnboardingManager {
    constructor() {
        this.currentStep = null;
        this.progress = 0;
        this.userData = {};
        this.apiBase = '/api/onboarding';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCurrentProgress();
        this.setupAccessibility();
    }

    bindEvents() {
        // Eventos de navegação
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action]')) {
                this.handleAction(e.target.dataset.action, e.target);
            }
        });

        // Eventos de teclado para acessibilidade
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                if (e.target.matches('[data-action]')) {
                    e.preventDefault();
                    this.handleAction(e.target.dataset.action, e.target);
                }
            }
        });

        // Eventos de formulário
        document.addEventListener('submit', (e) => {
            if (e.target.matches('.onboarding-form')) {
                e.preventDefault();
                this.handleFormSubmit(e.target);
            }
        });

        // Auto-save de formulários
        document.addEventListener('input', (e) => {
            if (e.target.matches('.onboarding-form input, .onboarding-form select, .onboarding-form textarea')) {
                this.autoSaveFormData(e.target.form);
            }
        });

        // Eventos de modal
        window.addEventListener('click', (e) => {
            if (e.target.matches('.modal')) {
                this.closeModal();
            }
        });

        // Prevenção de saída acidental
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges()) {
                e.preventDefault();
                e.returnValue = '';
                return '';
            }
        });
    }

    setupAccessibility() {
        // Adicionar indicadores ARIA
        const progressBar = document.querySelector('.progress-fill');
        if (progressBar) {
            progressBar.setAttribute('role', 'progressbar');
            progressBar.setAttribute('aria-valuenow', this.progress);
            progressBar.setAttribute('aria-valuemin', '0');
            progressBar.setAttribute('aria-valuemax', '100');
        }

        // Adicionar navegação por teclado
        const focusableElements = document.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        focusableElements.forEach((el, index) => {
            if (!el.hasAttribute('tabindex')) {
                el.setAttribute('tabindex', '0');
            }
        });
    }

    async loadCurrentProgress() {
        try {
            const response = await fetch(`${this.apiBase}/progress`);
            const data = await response.json();
            
            if (data.success) {
                this.updateProgress(data.data);
            }
        } catch (error) {
            console.error('Erro ao carregar progresso:', error);
        }
    }

    async handleAction(action, element) {
        try {
            switch (action) {
                case 'start':
                    await this.startOnboarding();
                    break;
                case 'next':
                    await this.nextStep();
                    break;
                case 'skip':
                    await this.skipStep();
                    break;
                case 'previous':
                    this.previousStep();
                    break;
                case 'restart':
                    await this.restartOnboarding();
                    break;
                case 'complete':
                    await this.completeStep();
                    break;
                case 'save':
                    await this.saveProgress();
                    break;
                default:
                    console.warn('Ação não reconhecida:', action);
            }
        } catch (error) {
            console.error('Erro ao executar ação:', error);
            this.showNotification('Erro ao executar ação', 'error');
        }
    }

    async startOnboarding() {
        try {
            const response = await fetch(`${this.apiBase}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Onboarding iniciado!', 'success');
                this.updateProgress(data.data);
                
                // Animar transição
                this.animateTransition(() => {
                    window.location.href = '/onboarding/step/profile_setup';
                });
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Erro ao iniciar onboarding:', error);
            this.showNotification('Erro ao iniciar onboarding', 'error');
        }
    }

    async nextStep() {
        const currentForm = document.querySelector('.onboarding-form');
        
        if (currentForm) {
            if (!this.validateForm(currentForm)) {
                return;
            }
            
            await this.completeStep();
        } else {
            // Navegar para próxima etapa sem formulário
            this.navigateToNextStep();
        }
    }

    async skipStep() {
        const stepId = this.getCurrentStepId();
        
        try {
            const response = await fetch(`${this.apiBase}/step/${stepId}/skip`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Etapa pulada', 'info');
                this.updateProgress(data.data);
                
                if (data.data.next_step) {
                    this.animateTransition(() => {
                        window.location.href = `/onboarding/step/${data.data.next_step.id}`;
                    });
                } else {
                    // Onboarding completo
                    this.completeOnboarding();
                }
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Erro ao pular etapa:', error);
            this.showNotification('Não é possível pular esta etapa', 'warning');
        }
    }

    async completeStep() {
        const stepId = this.getCurrentStepId();
        const form = document.querySelector('.onboarding-form');
        
        let formData = {};
        if (form) {
            formData = this.getFormData(form);
        }

        try {
            const response = await fetch(`${this.apiBase}/step/${stepId}/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Etapa concluída!', 'success');
                this.updateProgress(data.data);
                
                // Celebrar conclusão
                this.celebrateCompletion();
                
                setTimeout(() => {
                    if (data.data.next_step) {
                        this.animateTransition(() => {
                            window.location.href = `/onboarding/step/${data.data.next_step.id}`;
                        });
                    } else {
                        // Onboarding completo
                        this.completeOnboarding();
                    }
                }, 1500);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Erro ao completar etapa:', error);
            this.showNotification('Erro ao completar etapa', 'error');
        }
    }

    async restartOnboarding() {
        if (!confirm('Tem certeza que deseja reiniciar o onboarding? Todo o progresso será perdido.')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/restart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Onboarding reiniciado', 'info');
                window.location.href = '/onboarding/welcome';
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Erro ao reiniciar onboarding:', error);
            this.showNotification('Erro ao reiniciar onboarding', 'error');
        }
    }

    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'Este campo é obrigatório');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });

        // Validações específicas
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !this.isValidEmail(field.value)) {
                this.showFieldError(field, 'Email inválido');
                isValid = false;
            }
        });

        return isValid;
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.textContent = message;
        
        field.parentNode.appendChild(errorElement);
        field.classList.add('error');
        
        // Focar no campo com erro
        field.focus();
    }

    clearFieldError(field) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        field.classList.remove('error');
    }

    getFormData(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                // Campo múltiplo (checkbox)
                if (!Array.isArray(data[key])) {
                    data[key] = [data[key]];
                }
                data[key].push(value);
            } else {
                data[key] = value;
            }
        }
        
        return data;
    }

    autoSaveFormData(form) {
        if (!form) return;
        
        const data = this.getFormData(form);
        localStorage.setItem('onboarding_draft', JSON.stringify(data));
    }

    loadSavedFormData(form) {
        if (!form) return;
        
        const savedData = localStorage.getItem('onboarding_draft');
        if (!savedData) return;
        
        try {
            const data = JSON.parse(savedData);
            
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    if (field.type === 'checkbox' || field.type === 'radio') {
                        const values = Array.isArray(data[key]) ? data[key] : [data[key]];
                        values.forEach(value => {
                            const specificField = form.querySelector(`[name="${key}"][value="${value}"]`);
                            if (specificField) {
                                specificField.checked = true;
                            }
                        });
                    } else {
                        field.value = data[key];
                    }
                }
            });
        } catch (error) {
            console.error('Erro ao carregar dados salvos:', error);
        }
    }

    updateProgress(data) {
        this.progress = data.progress_percentage || 0;
        this.currentStep = data.current_step;
        
        // Atualizar barra de progresso
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = `${this.progress}%`;
            progressFill.setAttribute('aria-valuenow', this.progress);
        }
        
        const progressText = document.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${Math.round(this.progress)}% Concluído`;
        }
    }

    animateTransition(callback) {
        const container = document.querySelector('.onboarding-container');
        if (container) {
            container.style.opacity = '0';
            container.style.transform = 'translateY(20px)';
            
            setTimeout(callback, 300);
        } else {
            callback();
        }
    }

    celebrateCompletion() {
        // Animação de confetti
        this.playConfettiAnimation();
        
        // Som de sucesso (se disponível)
        this.playSuccessSound();
        
        // Vibração (dispositivos móveis)
        if (navigator.vibrate) {
            navigator.vibrate([100, 50, 100]);
        }
    }

    playConfettiAnimation() {
        const colors = ['#28a745', '#20c997', '#17a2b8', '#ffc107', '#fd7e14'];
        const confettiCount = 50;
        
        for (let i = 0; i < confettiCount; i++) {
            setTimeout(() => {
                const confetti = document.createElement('div');
                confetti.className = 'confetti';
                confetti.style.left = Math.random() * 100 + '%';
                confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.animationDelay = Math.random() * 3 + 's';
                confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
                
                document.body.appendChild(confetti);
                
                setTimeout(() => {
                    confetti.remove();
                }, 6000);
            }, i * 50);
        }
    }

    playSuccessSound() {
        try {
            const audio = new Audio('/static/sounds/success.mp3');
            audio.volume = 0.3;
            audio.play().catch(() => {
                // Falhou ao reproduzir - não é crítico
            });
        } catch (error) {
            // Audio não disponível
        }
    }

    completeOnboarding() {
        // Limpar dados temporários
        localStorage.removeItem('onboarding_draft');
        
        // Redirecionar para dashboard
        this.animateTransition(() => {
            window.location.href = '/dashboard?onboarding_complete=true';
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Remover automaticamente
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            
            // Focar no modal para acessibilidade
            const firstButton = modal.querySelector('button');
            if (firstButton) {
                firstButton.focus();
            }
        }
    }

    closeModal() {
        const modal = document.querySelector('.modal.show');
        if (modal) {
            modal.classList.remove('show');
        }
    }

    getCurrentStepId() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 1];
    }

    hasUnsavedChanges() {
        const form = document.querySelector('.onboarding-form');
        if (!form) return false;
        
        const savedData = localStorage.getItem('onboarding_draft');
        const currentData = JSON.stringify(this.getFormData(form));
        
        return savedData !== currentData;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Método público para tracking de eventos
    trackEvent(eventType, data = {}) {
        fetch('/api/onboarding/webhook/step-interaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                step_id: this.getCurrentStepId(),
                interaction_type: eventType,
                interaction_data: data,
                timestamp: new Date().toISOString()
            })
        }).catch(error => {
            console.error('Erro ao registrar evento:', error);
        });
    }
}

// Utilitários globais para onboarding
window.OnboardingUtils = {
    showModal: function(modalId) {
        if (window.onboardingManager) {
            window.onboardingManager.showModal(modalId);
        }
    },
    
    closeModal: function() {
        if (window.onboardingManager) {
            window.onboardingManager.closeModal();
        }
    },
    
    trackEvent: function(eventType, data) {
        if (window.onboardingManager) {
            window.onboardingManager.trackEvent(eventType, data);
        }
    }
};

// Atalhos globais para templates
window.showModal = window.OnboardingUtils.showModal;
window.closeModal = window.OnboardingUtils.closeModal;
window.trackOnboardingInteraction = window.OnboardingUtils.trackEvent;

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    window.onboardingManager = new OnboardingManager();
    
    // Carregar dados salvos em formulários
    const form = document.querySelector('.onboarding-form');
    if (form) {
        window.onboardingManager.loadSavedFormData(form);
    }
});

// Estilos dinâmicos para notificações
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        max-width: 400px;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-content {
        background: white;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 10px;
        border-left: 4px solid #28a745;
    }
    
    .notification-error .notification-content {
        border-left-color: #dc3545;
    }
    
    .notification-warning .notification-content {
        border-left-color: #ffc107;
    }
    
    .notification-info .notification-content {
        border-left-color: #17a2b8;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 18px;
        cursor: pointer;
        color: #666;
        margin-left: auto;
    }
    
    .field-error {
        color: #dc3545;
        font-size: 12px;
        margin-top: 5px;
    }
    
    .onboarding-form input.error,
    .onboarding-form select.error {
        border-color: #dc3545;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
    }
`;

// Injetar estilos
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);
