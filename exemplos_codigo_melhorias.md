# Exemplos Práticos de Código - Melhorias Frontend

## 1. Sistema de Design Consolidado

### design-system.css (Versão Melhorada)
```css
/* ===== DESIGN SYSTEM AGTECH PORTUGAL ===== */

/* Tokens de Design */
:root {
  /* Cores Semânticas */
  --color-primary: #16a34a;
  --color-primary-hover: #15803d;
  --color-primary-active: #14532d;
  
  --color-secondary: #d4af37;
  --color-secondary-hover: #b8941f;
  
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;
  
  /* Cores Neutras com Dark Mode */
  --color-neutral-50: light-dark(#f8fafc, #0f172a);
  --color-neutral-100: light-dark(#f1f5f9, #1e293b);
  --color-neutral-200: light-dark(#e2e8f0, #334155);
  --color-neutral-300: light-dark(#cbd5e1, #475569);
  --color-neutral-400: light-dark(#94a3b8, #64748b);
  --color-neutral-500: light-dark(#64748b, #94a3b8);
  --color-neutral-600: light-dark(#475569, #cbd5e1);
  --color-neutral-700: light-dark(#334155, #e2e8f0);
  --color-neutral-800: light-dark(#1e293b, #f1f5f9);
  --color-neutral-900: light-dark(#0f172a, #f8fafc);
  
  /* Tipografia Fluida */
  --font-size-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
  --font-size-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
  --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --font-size-lg: clamp(1.125rem, 1rem + 0.625vw, 1.25rem);
  --font-size-xl: clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem);
  --font-size-2xl: clamp(1.5rem, 1.3rem + 1vw, 2rem);
  --font-size-3xl: clamp(1.875rem, 1.6rem + 1.375vw, 2.5rem);
  
  /* Espaçamentos Responsivos */
  --space-xs: clamp(0.25rem, 0.2rem + 0.25vw, 0.375rem);
  --space-sm: clamp(0.5rem, 0.4rem + 0.5vw, 0.75rem);
  --space-md: clamp(1rem, 0.8rem + 1vw, 1.5rem);
  --space-lg: clamp(1.5rem, 1.2rem + 1.5vw, 2.25rem);
  --space-xl: clamp(2rem, 1.6rem + 2vw, 3rem);
  --space-2xl: clamp(3rem, 2.4rem + 3vw, 4.5rem);
  
  /* Raios de Borda */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  
  /* Sombras com Dark Mode */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -1px rgb(0 0 0 / 0.06);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -2px rgb(0 0 0 / 0.05);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 10px 10px -5px rgb(0 0 0 / 0.04);
  
  /* Transições */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Componentes Base */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  line-height: 1.5;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  min-height: 44px; /* Touch target */
  
  &:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  
  &:hover:not(:disabled) {
    background-color: var(--color-primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
  }
  
  &:active {
    background-color: var(--color-primary-active);
    transform: translateY(0);
  }
}

.card {
  background-color: var(--color-neutral-50);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
  
  &:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
  }
}
```

## 2. Sistema de Loading Avançado

### loading-manager.js
```javascript
class LoadingManager {
  constructor() {
    this.activeLoaders = new Set();
    this.init();
  }
  
  init() {
    this.createStyles();
  }
  
  createStyles() {
    if (document.getElementById('loading-styles')) return;
    
    const styles = document.createElement('style');
    styles.id = 'loading-styles';
    styles.textContent = `
      .skeleton {
        background: linear-gradient(90deg, 
          var(--color-neutral-200) 25%, 
          var(--color-neutral-100) 50%, 
          var(--color-neutral-200) 75%);
        background-size: 200% 100%;
        animation: skeleton-loading 1.5s infinite;
        border-radius: var(--radius-md);
      }
      
      @keyframes skeleton-loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
      }
      
      .skeleton-text {
        height: 1rem;
        margin-bottom: 0.5rem;
      }
      
      .skeleton-text:last-child {
        width: 60%;
      }
      
      .skeleton-card {
        height: 200px;
        width: 100%;
      }
      
      .skeleton-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
      }
      
      .loading-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(4px);
      }
      
      .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid var(--color-neutral-300);
        border-top: 4px solid var(--color-primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(styles);
  }
  
  showSkeleton(container, config = {}) {
    const { type = 'card', count = 1, className = '' } = config;
    
    container.innerHTML = '';
    
    for (let i = 0; i < count; i++) {
      const skeleton = this.createSkeleton(type, className);
      container.appendChild(skeleton);
    }
    
    this.activeLoaders.add(container);
  }
  
  createSkeleton(type, className) {
    const skeleton = document.createElement('div');
    skeleton.className = `skeleton skeleton-${type} ${className}`;
    
    if (type === 'text') {
      skeleton.innerHTML = `
        <div class="skeleton-text"></div>
        <div class="skeleton-text"></div>
        <div class="skeleton-text"></div>
      `;
    } else if (type === 'card') {
      skeleton.innerHTML = `
        <div class="flex items-center mb-4">
          <div class="skeleton skeleton-avatar mr-3"></div>
          <div class="flex-1">
            <div class="skeleton-text mb-2"></div>
            <div class="skeleton-text" style="width: 40%"></div>
          </div>
        </div>
        <div class="skeleton-text mb-2"></div>
        <div class="skeleton-text mb-2"></div>
        <div class="skeleton-text" style="width: 60%"></div>
      `;
    }
    
    return skeleton;
  }
  
  hideSkeleton(container) {
    const skeletons = container.querySelectorAll('.skeleton');
    skeletons.forEach(skeleton => {
      skeleton.style.animation = 'fadeOut 0.3s ease-out';
      setTimeout(() => skeleton.remove(), 300);
    });
    
    this.activeLoaders.delete(container);
  }
  
  showOverlay(message = 'Carregando...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
      <div class="bg-white p-6 rounded-lg shadow-xl text-center">
        <div class="loading-spinner mx-auto mb-4"></div>
        <p class="text-gray-600">${message}</p>
      </div>
    `;
    
    document.body.appendChild(overlay);
    return overlay;
  }
  
  hideOverlay(overlay) {
    if (overlay && overlay.parentNode) {
      overlay.style.opacity = '0';
      setTimeout(() => overlay.remove(), 300);
    }
  }
}

// Instância global
window.LoadingManager = new LoadingManager();
```

## 3. Sistema de Notificações Melhorado

### notification-system.js
```javascript
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
    this.container.className = 'fixed top-4 right-4 z-50 space-y-2';
    document.body.appendChild(this.container);
  }
  
  createStyles() {
    const styles = document.createElement('style');
    styles.textContent = `
      .notification {
        min-width: 300px;
        max-width: 400px;
        padding: 1rem;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-lg);
        transform: translateX(100%);
        transition: all var(--transition-base);
        border-left: 4px solid;
      }
      
      .notification.show {
        transform: translateX(0);
      }
      
      .notification-success {
        background: var(--color-neutral-50);
        border-left-color: var(--color-success);
        color: var(--color-success);
      }
      
      .notification-error {
        background: var(--color-neutral-50);
        border-left-color: var(--color-error);
        color: var(--color-error);
      }
      
      .notification-warning {
        background: var(--color-neutral-50);
        border-left-color: var(--color-warning);
        color: var(--color-warning);
      }
      
      .notification-info {
        background: var(--color-neutral-50);
        border-left-color: var(--color-info);
        color: var(--color-info);
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
      
      .notification-body {
        flex: 1;
      }
      
      .notification-title {
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: var(--color-neutral-900);
      }
      
      .notification-message {
        font-size: var(--font-size-sm);
        color: var(--color-neutral-700);
      }
      
      .notification-close {
        background: none;
        border: none;
        cursor: pointer;
        padding: 0.25rem;
        border-radius: var(--radius-sm);
        color: var(--color-neutral-500);
        transition: all var(--transition-fast);
      }
      
      .notification-close:hover {
        background: var(--color-neutral-100);
        color: var(--color-neutral-700);
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
      actions = []
    } = options;
    
    const id = this.generateId();
    const notification = this.createNotification(id, type, title, message, actions);
    
    this.container.appendChild(notification);
    this.notifications.set(id, notification);
    
    // Trigger animation
    requestAnimationFrame(() => {
      notification.classList.add('show');
    });
    
    // Auto remove
    if (!persistent && duration > 0) {
      setTimeout(() => {
        this.remove(id);
      }, duration);
    }
    
    return id;
  }
  
  createNotification(id, type, title, message, actions) {
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
        <i class="notification-icon fas ${icons[type]}"></i>
        <div class="notification-body">
          ${title ? `<div class="notification-title">${title}</div>` : ''}
          <div class="notification-message">${message}</div>
          ${actions.length > 0 ? this.createActions(actions) : ''}
        </div>
        <button class="notification-close" onclick="NotificationSystem.instance.remove('${id}')">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;
    
    return notification;
  }
  
  createActions(actions) {
    const actionsHtml = actions.map(action => `
      <button class="btn btn-sm ${action.style || 'btn-secondary'}" 
              onclick="${action.handler}">
        ${action.label}
      </button>
    `).join('');
    
    return `<div class="mt-3 space-x-2">${actionsHtml}</div>`;
  }
  
  remove(id) {
    const notification = this.notifications.get(id);
    if (notification) {
      notification.classList.remove('show');
      setTimeout(() => {
        notification.remove();
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
}

// Instância global
NotificationSystem.instance = new NotificationSystem();
window.notify = NotificationSystem.instance;
```

## 4. Theme Manager (Dark Mode)

### theme-manager.js
```javascript
class ThemeManager {
  constructor() {
    this.currentTheme = 'light';
    this.init();
  }
  
  init() {
    this.loadSavedTheme();
    this.setupSystemThemeListener();
    this.setupToggleButton();
    this.applyTheme();
  }
  
  loadSavedTheme() {
    const savedTheme = localStorage.getItem('agtech-theme');
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    this.currentTheme = savedTheme || systemTheme;
  }
  
  setupSystemThemeListener() {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('agtech-theme')) {
        this.currentTheme = e.matches ? 'dark' : 'light';
        this.applyTheme();
      }
    });
  }
  
  setupToggleButton() {
    // Criar botão de toggle se não existir
    if (!document.getElementById('theme-toggle')) {
      const toggle = document.createElement('button');
      toggle.id = 'theme-toggle';
      toggle.className = 'btn btn-secondary btn-sm';
      toggle.innerHTML = '<i class="fas fa-moon"></i>';
      toggle.setAttribute('aria-label', 'Alternar tema');
      
      // Adicionar ao header
      const header = document.querySelector('.app-header .flex');
      if (header) {
        header.insertBefore(toggle, header.lastElementChild);
      }
    }
    
    document.getElementById('theme-toggle').addEventListener('click', () => {
      this.toggle();
    });
  }
  
  toggle() {
    this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
    this.applyTheme();
    this.saveTheme();
    this.updateToggleButton();
  }
  
  applyTheme() {
    document.documentElement.classList.toggle('dark', this.currentTheme === 'dark');
    
    // Atualizar meta theme-color
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.content = this.currentTheme === 'dark' ? '#0f172a' : '#ffffff';
    }
    
    this.updateToggleButton();
  }
  
  updateToggleButton() {
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      const icon = toggle.querySelector('i');
      icon.className = this.currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
      toggle.setAttribute('aria-label', 
        this.currentTheme === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro'
      );
    }
  }
  
  saveTheme() {
    localStorage.setItem('agtech-theme', this.currentTheme);
  }
  
  getTheme() {
    return this.currentTheme;
  }
  
  setTheme(theme) {
    if (['light', 'dark'].includes(theme)) {
      this.currentTheme = theme;
      this.applyTheme();
      this.saveTheme();
    }
  }
}

// Instância global
window.ThemeManager = new ThemeManager();
```

## 5. Wizard Enhanced

### wizard-enhanced.js
```javascript
class WizardEnhanced {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.currentStep = 1;
    this.totalSteps = options.totalSteps || 5;
    this.data = {};
    this.validators = options.validators || {};
    this.onStepChange = options.onStepChange || (() => {});
    this.onComplete = options.onComplete || (() => {});
    
    this.init();
  }
  
  init() {
    this.setupNavigation();
    this.setupValidation();
    this.updateProgress();
  }
  
  setupNavigation() {
    const prevBtn = this.container.querySelector('#prev-step');
    const nextBtn = this.container.querySelector('#next-step');
    
    if (prevBtn) {
      prevBtn.addEventListener('click', () => this.previousStep());
    }
    
    if (nextBtn) {
      nextBtn.addEventListener('click', () => this.nextStep());
    }
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft' && e.ctrlKey) {
        this.previousStep();
      } else if (e.key === 'ArrowRight' && e.ctrlKey) {
        this.nextStep();
      }
    });
  }
  
  setupValidation() {
    const form = this.container.querySelector('form');
    if (form) {
      form.addEventListener('input', (e) => {
        this.validateField(e.target);
      });
    }
  }
  
  async nextStep() {
    if (await this.validateCurrentStep()) {
      this.saveCurrentStepData();
      
      if (this.currentStep < this.totalSteps) {
        this.currentStep++;
        this.showStep(this.currentStep);
        this.updateProgress();
        this.onStepChange(this.currentStep, 'next');
      } else {
        this.complete();
      }
    }
  }
  
  previousStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.showStep(this.currentStep);
      this.updateProgress();
      this.onStepChange(this.currentStep, 'previous');
    }
  }
  
  async showStep(stepNumber) {
    // Hide current step
    const currentStepEl = this.container.querySelector('.wizard-step.active');
    if (currentStepEl) {
      currentStepEl.classList.add('fade-out');
      await this.wait(300);
      currentStepEl.classList.remove('active', 'fade-out');
    }
    
    // Show new step
    const newStepEl = this.container.querySelector(`[data-step="${stepNumber}"]`);
    if (newStepEl) {
      newStepEl.classList.add('active', 'fade-in');
      await this.wait(50);
      newStepEl.classList.remove('fade-in');
    }
    
    this.updateNavigationButtons();
  }
  
  updateProgress() {
    const progress = (this.currentStep / this.totalSteps) * 100;
    const progressBar = this.container.querySelector('.progress-bar');
    const progressText = this.container.querySelector('.progress-text');
    
    if (progressBar) {
      progressBar.style.width = `${progress}%`;
    }
    
    if (progressText) {
      progressText.textContent = `Passo ${this.currentStep} de ${this.totalSteps}`;
    }
    
    // Update step indicators
    const stepIndicators = this.container.querySelectorAll('.step-indicator');
    stepIndicators.forEach((indicator, index) => {
      const stepNum = index + 1;
      indicator.classList.toggle('completed', stepNum < this.currentStep);
      indicator.classList.toggle('active', stepNum === this.currentStep);
    });
  }
  
  updateNavigationButtons() {
    const prevBtn = this.container.querySelector('#prev-step');
    const nextBtn = this.container.querySelector('#next-step');
    
    if (prevBtn) {
      prevBtn.disabled = this.currentStep === 1;
    }
    
    if (nextBtn) {
      nextBtn.textContent = this.currentStep === this.totalSteps ? 'Finalizar' : 'Próximo';
    }
  }
  
  async validateCurrentStep() {
    const stepEl = this.container.querySelector(`[data-step="${this.currentStep}"]`);
    const inputs = stepEl.querySelectorAll('input, select, textarea');
    let isValid = true;
    
    for (const input of inputs) {
      if (!this.validateField(input)) {
        isValid = false;
      }
    }
    
    // Custom validator
    if (this.validators[this.currentStep]) {
      const customValidation = await this.validators[this.currentStep](this.data);
      if (!customValidation.valid) {
        this.showError(customValidation.message);
        isValid = false;
      }
    }
    
    return isValid;
  }
  
  validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    // Required validation
    if (field.hasAttribute('required') && !value) {
      isValid = false;
      message = 'Este campo é obrigatório';
    }
    
    // Email validation
    if (field.type === 'email' && value && !this.isValidEmail(value)) {
      isValid = false;
      message = 'Email inválido';
    }
    
    // Custom validation
    const customValidator = field.dataset.validator;
    if (customValidator && window[customValidator]) {
      const result = window[customValidator](value);
      if (!result.valid) {
        isValid = false;
        message = result.message;
      }
    }
    
    this.showFieldValidation(field, isValid, message);
    return isValid;
  }
  
  showFieldValidation(field, isValid, message) {
    const errorEl = field.parentNode.querySelector('.field-error');
    
    if (errorEl) {
      errorEl.remove();
    }
    
    field.classList.toggle('error', !isValid);
    
    if (!isValid && message) {
      const error = document.createElement('div');
      error.className = 'field-error text-red-500 text-sm mt-1';
      error.textContent = message;
      field.parentNode.appendChild(error);
    }
  }
  
  saveCurrentStepData() {
    const stepEl = this.container.querySelector(`[data-step="${this.currentStep}"]`);
    const formData = new FormData(stepEl.querySelector('form') || stepEl);
    
    for (const [key, value] of formData.entries()) {
      this.data[key] = value;
    }
  }
  
  complete() {
    this.saveCurrentStepData();
    this.onComplete(this.data);
  }
  
  showError(message) {
    window.notify?.error(message, 'Erro de Validação');
  }
  
  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
  
  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  // Public methods
  goToStep(stepNumber) {
    if (stepNumber >= 1 && stepNumber <= this.totalSteps) {
      this.currentStep = stepNumber;
      this.showStep(stepNumber);
      this.updateProgress();
    }
  }
  
  getData() {
    return { ...this.data };
  }
  
  setData(data) {
    this.data = { ...this.data, ...data };
  }
}
```

Estes exemplos mostram implementações práticas das principais melhorias propostas, mantendo a filosofia mobile-first e focando em performance, acessibilidade e experiência do usuário.

