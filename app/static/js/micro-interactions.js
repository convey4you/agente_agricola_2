// app/static/js/micro-interactions.js

class MicroInteractions {
    constructor() {
        this.init();
    }

    init() {
        this.setupButtonInteractions();
        this.setupFormInteractions();
        this.setupCardInteractions();
        this.setupNavigationInteractions();
        this.setupTooltips();
        this.setupProgressIndicators();
        this.setupNotifications();
    }

    setupButtonInteractions() {
        // Efeito ripple em botões
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn, .btn *')) {
                const button = e.target.closest('.btn');
                this.createRippleEffect(button, e);
            }
        });

        // Loading state em botões de formulário
        document.addEventListener('submit', (e) => {
            const submitBtn = e.target.querySelector('button[type="submit"]');
            if (submitBtn) {
                this.setButtonLoading(submitBtn, true);
                
                // Remover loading após 5 segundos como fallback
                setTimeout(() => {
                    this.setButtonLoading(submitBtn, false);
                }, 5000);
            }
        });
    }

    createRippleEffect(button, event) {
        if (button.querySelector('.ripple')) {
            button.querySelector('.ripple').remove();
        }

        const ripple = document.createElement('span');
        ripple.classList.add('ripple');
        
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple 0.6s linear;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    setButtonLoading(button, isLoading) {
        if (isLoading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.textContent = 'A processar...';
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            if (button.dataset.originalText) {
                button.textContent = button.dataset.originalText;
                delete button.dataset.originalText;
            }
        }
    }

    setupFormInteractions() {
        // Animação de focus em inputs
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('form-group-focused');
            });
            
            input.addEventListener('blur', () => {
                input.parentElement.classList.remove('form-group-focused');
                this.validateField(input);
            });
            
            input.addEventListener('input', () => {
                this.clearFieldError(input);
            });
        });

        // Validação em tempo real
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('input', (e) => {
                if (e.target.matches('.form-control')) {
                    this.validateField(e.target);
                }
            });
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const isRequired = field.hasAttribute('required');
        
        let isValid = true;
        let errorMessage = '';

        // Validação básica
        if (isRequired && !value) {
            isValid = false;
            errorMessage = 'Este campo é obrigatório';
        } else if (type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            errorMessage = 'Por favor, insira um email válido';
        } else if (type === 'tel' && value && !this.isValidPhone(value)) {
            isValid = false;
            errorMessage = 'Por favor, insira um número de telefone válido';
        }

        this.showFieldValidation(field, isValid, errorMessage);
        return isValid;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidPhone(phone) {
        const phoneRegex = /^(\+351\s?)?[29]\d{8}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
    }

    showFieldValidation(field, isValid, message) {
        const formGroup = field.closest('.form-group');
        const existingError = formGroup.querySelector('.field-error');
        
        if (existingError) {
            existingError.remove();
        }
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            
            const errorElement = document.createElement('div');
            errorElement.className = 'field-error text-danger mt-1';
            errorElement.style.fontSize = '0.875rem';
            errorElement.textContent = message;
            
            formGroup.appendChild(errorElement);
        }
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');
        const formGroup = field.closest('.form-group');
        const existingError = formGroup.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }

    setupCardInteractions() {
        // Hover effects em cards
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px)';
                card.style.boxShadow = 'var(--shadow-xl)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = 'var(--shadow)';
            });
        });

        // Click effects em cards clicáveis
        document.querySelectorAll('.card[data-href]').forEach(card => {
            card.style.cursor = 'pointer';
            
            card.addEventListener('click', () => {
                const href = card.dataset.href;
                if (href) {
                    window.location.href = href;
                }
            });
        });
    }

    setupNavigationInteractions() {
        // Smooth scroll para links internos
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Indicador de progresso de scroll
        this.setupScrollProgress();
    }

    setupScrollProgress() {
        const progressBar = document.createElement('div');
        progressBar.className = 'scroll-progress';
        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: var(--primary-green);
            z-index: var(--z-fixed);
            transition: width 0.1s ease;
        `;
        
        document.body.appendChild(progressBar);
        
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset;
            const docHeight = document.body.scrollHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            
            progressBar.style.width = scrollPercent + '%';
        });
    }

    setupTooltips() {
        // Sistema de tooltips simples
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.dataset.tooltip);
            });
            
            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip-custom';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: var(--gray-800);
            color: var(--white);
            padding: var(--spacing-2) var(--spacing-3);
            border-radius: var(--border-radius);
            font-size: var(--font-size-sm);
            white-space: nowrap;
            z-index: var(--z-tooltip);
            opacity: 0;
            transform: translateY(10px);
            transition: all var(--transition-base);
            pointer-events: none;
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        setTimeout(() => {
            tooltip.style.opacity = '1';
            tooltip.style.transform = 'translateY(0)';
        }, 10);
    }

    hideTooltip() {
        const tooltip = document.querySelector('.tooltip-custom');
        if (tooltip) {
            tooltip.remove();
        }
    }

    setupProgressIndicators() {
        // Barras de progresso animadas
        document.querySelectorAll('.progress-bar').forEach(bar => {
            const targetWidth = bar.dataset.progress || '0';
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.width = targetWidth + '%';
                bar.style.transition = 'width 1s ease-in-out';
            }, 100);
        });

        // Contadores animados
        document.querySelectorAll('.counter').forEach(counter => {
            const target = parseInt(counter.dataset.target) || 0;
            const duration = parseInt(counter.dataset.duration) || 2000;
            
            this.animateCounter(counter, 0, target, duration);
        });
    }

    animateCounter(element, start, end, duration) {
        const increment = (end - start) / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            
            if (current >= end) {
                element.textContent = end;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    }

    setupNotifications() {
        // Sistema de notificações toast
        this.createNotificationContainer();
    }

    createNotificationContainer() {
        if (document.querySelector('.notification-container')) return;
        
        const container = document.createElement('div');
        container.className = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: var(--spacing-4);
            right: var(--spacing-4);
            z-index: var(--z-modal);
            max-width: 400px;
            width: 100%;
        `;
        
        document.body.appendChild(container);
    }

    showNotification(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            background: var(--white);
            border-left: 4px solid var(--${type === 'success' ? 'success' : type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'info'});
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-lg);
            padding: var(--spacing-4);
            margin-bottom: var(--spacing-2);
            transform: translateX(100%);
            transition: transform var(--transition-base);
            position: relative;
        `;
        
        notification.innerHTML = `
            <div class="notification-content">
                <p class="mb-0">${message}</p>
            </div>
            <button class="notification-close" style="
                position: absolute;
                top: var(--spacing-2);
                right: var(--spacing-2);
                background: none;
                border: none;
                font-size: var(--font-size-lg);
                cursor: pointer;
                color: var(--gray-500);
            ">&times;</button>
        `;
        
        container.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Configurar fechamento
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.removeNotification(notification);
        });
        
        // Auto-remover
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification);
            }, duration);
        }
    }

    removeNotification(notification) {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 200);
    }
}

// Inicializar micro-interações quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.microInteractions = new MicroInteractions();
});

// Adicionar estilos CSS para animações
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .form-group-focused .form-label {
        color: var(--primary-green);
        transform: translateY(-2px);
        transition: all var(--transition-base);
    }
    
    .form-control.is-valid {
        border-color: var(--success);
        box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
    }
    
    .form-control.is-invalid {
        border-color: var(--danger);
        box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
    }
    
    .card {
        transition: all var(--transition-base);
    }
    
    .progress-bar {
        background: linear-gradient(90deg, var(--primary-green), var(--secondary-gold));
        height: 100%;
        border-radius: inherit;
        position: relative;
        overflow: hidden;
    }
    
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    @media (max-width: 768px) {
        .notification-container {
            left: var(--spacing-4);
            right: var(--spacing-4);
            max-width: none;
        }
    }
    
    .text-danger {
        color: var(--danger) !important;
    }
    
    .mt-1 {
        margin-top: var(--spacing-1) !important;
    }
`;

document.head.appendChild(style);
