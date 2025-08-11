// Notification System - Sistema de Notificações Avançado
class NotificationSystem {
  constructor() {
    this.container = null;
    this.notifications = new Map();
    this.init();
  }
  
  init() {
    this.createContainer();
    this.createStyles();
  }
  
  createContainer() {
    this.container = document.createElement('div');
    this.container.id = 'notification-container';
    this.container.className = 'notification-container';
    document.body.appendChild(this.container);
  }
  
  createStyles() {
    if (document.getElementById('notification-styles')) return;
    
    const styles = document.createElement('style');
    styles.id = 'notification-styles';
    styles.textContent = `
      .notification-container {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1080;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        max-width: 400px;
        width: 100%;
        pointer-events: none;
      }
      
      .notification {
        min-width: 300px;
        max-width: 400px;
        padding: 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transform: translateX(100%);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 4px solid;
        background: var(--color-neutral-50);
        pointer-events: auto;
        position: relative;
        overflow: hidden;
      }
      
      .notification.show {
        transform: translateX(0);
      }
      
      .notification-success {
        border-left-color: var(--color-success);
      }
      
      .notification-error {
        border-left-color: var(--color-error);
      }
      
      .notification-warning {
        border-left-color: var(--color-warning);
      }
      
      .notification-info {
        border-left-color: var(--color-info);
      }
      
      .notification-content {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
      }
      
      .notification-icon {
        flex-shrink: 0;
        width: 20px;
        height: 20px;
      }
      
      .notification-icon.success { color: var(--color-success); }
      .notification-icon.error { color: var(--color-error); }
      .notification-icon.warning { color: var(--color-warning); }
      .notification-icon.info { color: var(--color-info); }
      
      .notification-body {
        flex: 1;
      }
      
      .notification-title {
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: var(--color-neutral-900);
        font-size: 0.875rem;
      }
      
      .notification-message {
        font-size: 0.875rem;
        color: var(--color-neutral-700);
        line-height: 1.4;
      }
      
      .notification-close {
        background: none;
        border: none;
        cursor: pointer;
        padding: 0.25rem;
        border-radius: 0.25rem;
        color: var(--color-neutral-500);
        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
        position: absolute;
        top: 0.75rem;
        right: 0.75rem;
      }
      
      .notification-close:hover {
        background: var(--color-neutral-100);
        color: var(--color-neutral-700);
      }
      
      .notification-actions {
        margin-top: 0.75rem;
        display: flex;
        gap: 0.5rem;
      }
      
      .notification-action {
        padding: 0.375rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 500;
        border-radius: 0.375rem;
        border: 1px solid transparent;
        cursor: pointer;
        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
      }
      
      .notification-action.primary {
        background: var(--color-primary-600);
        color: white;
      }
      
      .notification-action.primary:hover {
        background: var(--color-primary-700);
      }
      
      .notification-action.secondary {
        background: var(--color-neutral-100);
        color: var(--color-neutral-700);
        border-color: var(--color-neutral-300);
      }
      
      .notification-action.secondary:hover {
        background: var(--color-neutral-200);
      }
      
      .notification-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        background: var(--color-primary-600);
        transition: width linear;
      }
      
      @media (max-width: 768px) {
        .notification-container {
          left: 1rem;
          right: 1rem;
          max-width: none;
        }
        
        .notification {
          min-width: auto;
          max-width: none;
        }
      }
    `;
    document.head.appendChild(styles);
  }
  
  show(options) {
    const {
      type = 'info',
      title,
      message,
      duration = 5000,
      persistent = false,
      actions = [],
      showProgress = false
    } = options;
    
    const id = this.generateId();
    const notification = this.createNotification(id, type, title, message, actions, showProgress);
    
    this.container.appendChild(notification);
    this.notifications.set(id, notification);
    
    // Trigger animation
    requestAnimationFrame(() => {
      notification.classList.add('show');
    });
    
    // Auto remove with progress
    if (!persistent && duration > 0) {
      if (showProgress) {
        this.startProgress(notification, duration);
      }
      
      setTimeout(() => {
        this.remove(id);
      }, duration);
    }
    
    return id;
  }
  
  createNotification(id, type, title, message, actions, showProgress) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.dataset.id = id;
    
    const icons = {
      success: 'fa-check-circle',
      error: 'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    };
    
    notification.innerHTML = `
      <div class="notification-content">
        <i class="notification-icon ${type} fas ${icons[type]}"></i>
        <div class="notification-body">
          ${title ? `<div class="notification-title">${title}</div>` : ''}
          <div class="notification-message">${message}</div>
          ${actions.length > 0 ? this.createActions(actions, id) : ''}
        </div>
        <button class="notification-close" onclick="NotificationSystem.instance.remove('${id}')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      ${showProgress ? '<div class="notification-progress"></div>' : ''}
    `;
    
    return notification;
  }
  
  createActions(actions, notificationId) {
    const actionsHtml = actions.map((action, index) => `
      <button class="notification-action ${action.style || 'secondary'}" 
              onclick="NotificationSystem.instance.handleAction('${notificationId}', ${index})">
        ${action.label}
      </button>
    `).join('');
    
    return `<div class="notification-actions">${actionsHtml}</div>`;
  }
  
  handleAction(notificationId, actionIndex) {
    const notification = this.notifications.get(notificationId);
    if (!notification) return;
    
    const actions = notification._actions || [];
    const action = actions[actionIndex];
    
    if (action && action.handler) {
      action.handler();
    }
    
    // Auto close after action unless specified otherwise
    if (!action || action.autoClose !== false) {
      this.remove(notificationId);
    }
  }
  
  startProgress(notification, duration) {
    const progressBar = notification.querySelector('.notification-progress');
    if (!progressBar) return;
    
    progressBar.style.width = '100%';
    progressBar.style.transitionDuration = `${duration}ms`;
    
    requestAnimationFrame(() => {
      progressBar.style.width = '0%';
    });
  }
  
  remove(id) {
    const notification = this.notifications.get(id);
    if (notification) {
      notification.classList.remove('show');
      setTimeout(() => {
        if (notification.parentNode) {
          notification.remove();
        }
        this.notifications.delete(id);
      }, 300);
    }
  }
  
  clear() {
    this.notifications.forEach((notification, id) => {
      this.remove(id);
    });
  }
  
  generateId() {
    return `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  // Métodos de conveniência
  success(message, title, options = {}) {
    return this.show({ type: 'success', title, message, ...options });
  }
  
  error(message, title, options = {}) {
    return this.show({ type: 'error', title, message, ...options });
  }
  
  warning(message, title, options = {}) {
    return this.show({ type: 'warning', title, message, ...options });
  }
  
  info(message, title, options = {}) {
    return this.show({ type: 'info', title, message, ...options });
  }
  
  // Notificações especiais
  loading(message, title = 'Carregando') {
    return this.show({
      type: 'info',
      title,
      message,
      persistent: true,
      showProgress: false
    });
  }
  
  confirm(message, title, onConfirm, onCancel) {
    return this.show({
      type: 'warning',
      title,
      message,
      persistent: true,
      actions: [
        {
          label: 'Cancelar',
          style: 'secondary',
          handler: onCancel || (() => {}),
          autoClose: true
        },
        {
          label: 'Confirmar',
          style: 'primary',
          handler: onConfirm || (() => {}),
          autoClose: true
        }
      ]
    });
  }
  
  // Integração com formulários
  showFormErrors(errors) {
    if (Array.isArray(errors)) {
      errors.forEach(error => {
        this.error(error);
      });
    } else if (typeof errors === 'object') {
      Object.entries(errors).forEach(([field, messages]) => {
        const fieldMessages = Array.isArray(messages) ? messages : [messages];
        fieldMessages.forEach(message => {
          this.error(`${field}: ${message}`);
        });
      });
    } else {
      this.error(errors);
    }
  }
  
  showFormSuccess(message = 'Dados salvos com sucesso!') {
    this.success(message);
  }
}

// Instância global
NotificationSystem.instance = new NotificationSystem();
window.notify = NotificationSystem.instance;

// Integração com eventos globais
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
  window.notify.error('Ocorreu um erro inesperado. Tente novamente.', 'Erro');
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  window.notify.error('Ocorreu um erro inesperado. Tente novamente.', 'Erro');
});

