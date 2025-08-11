# PROMPTS CLAUDE SONNET 4 - SPRINT 5: POLIMENTO E LANÇAMENTO
## AgroTech Portugal - Sistema de Agente Agrícola Inteligente

**Autor**: Manus AI - Gerente de Tecnologia  
**Data**: 31 de julho de 2025  
**Versão**: 1.0  
**Sprint**: 5 - Polimento e Lançamento  
**Período**: 16-30 de setembro de 2025  

---

## 📋 VISÃO GERAL DO SPRINT 5

O Sprint 5 representa a fase final de preparação para o lançamento comercial do AgroTech Portugal. Este sprint concentra-se no polimento da experiência do usuário, otimização final de performance, implementação de recursos de produção, configuração de monitoramento avançado e preparação completa para o lançamento no mercado português.

### Objetivos Principais

O Sprint 5 tem como objetivo transformar o AgroTech Portugal em um produto comercial pronto para lançamento, com qualidade enterprise, experiência de usuário excepcional e infraestrutura robusta capaz de suportar o crescimento esperado. Isso inclui polimento de interface, implementação de recursos de produção, configuração de analytics, preparação de materiais de marketing técnico e estabelecimento de processos de suporte.

### Contexto Estratégico

Este é o sprint decisivo que determinará o sucesso do lançamento comercial. Cada detalhe da experiência do usuário deve ser refinado para garantir que os agricultores portugueses tenham uma primeira impressão excepcional. A qualidade e confiabilidade implementadas neste sprint serão fundamentais para a adoção inicial e crescimento orgânico da plataforma.

---

## ✨ PROMPT 1: POLIMENTO DA EXPERIÊNCIA DO USUÁRIO

### Contexto do Projeto
Você está implementando o polimento final da experiência do usuário (UX/UI) para o AgroTech Portugal. Este trabalho envolve refinamento de interfaces, otimização de fluxos de usuário, implementação de micro-interações, personalização avançada e garantia de que cada interação seja intuitiva e agradável para agricultores portugueses de todos os níveis de experiência tecnológica.

### Funcionalidade a Implementar
Sistema completo de polimento de UX que inclui interfaces responsivas refinadas, animações suaves, feedback visual imediato, personalização baseada no perfil do usuário, acessibilidade completa e otimização para dispositivos móveis. O objetivo é criar uma experiência que seja simultaneamente poderosa para usuários avançados e simples para iniciantes.

### Arquitetura Proposta

O sistema de polimento será baseado em componentes reutilizáveis, design system consistente, animações performáticas e personalização inteligente. A arquitetura utilizará CSS moderno, JavaScript otimizado e técnicas avançadas de UX para criar uma experiência excepcional.

**Componentes de Polimento:**
- **Design System**: Componentes consistentes e reutilizáveis
- **Micro-interações**: Animações e feedback visual
- **Personalização**: Interface adaptada ao perfil do usuário
- **Acessibilidade**: Conformidade com WCAG 2.1
- **Mobile-First**: Otimização completa para dispositivos móveis
- **Performance**: Carregamento rápido e interações fluidas

### Objetivo
Implementar um sistema de polimento que eleve a experiência do usuário do AgroTech Portugal ao nível de aplicações premium, garantindo que agricultores portugueses tenham uma experiência excepcional que os incentive a usar a plataforma diariamente.

### Instruções Detalhadas

**ETAPA 1: Design System e Componentes Refinados**

Crie o design system em `app/static/css/design-system.css`:

```css
/* app/static/css/design-system.css */

/* ===== VARIÁVEIS DO DESIGN SYSTEM ===== */
:root {
  /* Cores Primárias - Inspiradas na Agricultura Portuguesa */
  --primary-green: #2d5a27;
  --primary-green-light: #4a7c59;
  --primary-green-dark: #1a3d1a;
  --secondary-gold: #d4af37;
  --secondary-gold-light: #e6c757;
  --secondary-gold-dark: #b8941f;
  
  /* Cores de Estado */
  --success: #28a745;
  --success-light: #d4edda;
  --warning: #ffc107;
  --warning-light: #fff3cd;
  --danger: #dc3545;
  --danger-light: #f8d7da;
  --info: #17a2b8;
  --info-light: #d1ecf1;
  
  /* Cores Neutras */
  --white: #ffffff;
  --gray-50: #f8f9fa;
  --gray-100: #e9ecef;
  --gray-200: #dee2e6;
  --gray-300: #ced4da;
  --gray-400: #adb5bd;
  --gray-500: #6c757d;
  --gray-600: #495057;
  --gray-700: #343a40;
  --gray-800: #212529;
  --gray-900: #1a1a1a;
  
  /* Tipografia */
  --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-heading: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  
  /* Tamanhos de Fonte */
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */
  
  /* Espaçamentos */
  --spacing-1: 0.25rem;   /* 4px */
  --spacing-2: 0.5rem;    /* 8px */
  --spacing-3: 0.75rem;   /* 12px */
  --spacing-4: 1rem;      /* 16px */
  --spacing-5: 1.25rem;   /* 20px */
  --spacing-6: 1.5rem;    /* 24px */
  --spacing-8: 2rem;      /* 32px */
  --spacing-10: 2.5rem;   /* 40px */
  --spacing-12: 3rem;     /* 48px */
  --spacing-16: 4rem;     /* 64px */
  
  /* Bordas e Raios */
  --border-radius-sm: 0.25rem;
  --border-radius: 0.375rem;
  --border-radius-lg: 0.5rem;
  --border-radius-xl: 0.75rem;
  --border-radius-2xl: 1rem;
  --border-radius-full: 9999px;
  
  /* Sombras */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  
  /* Transições */
  --transition-fast: 150ms ease-in-out;
  --transition-base: 200ms ease-in-out;
  --transition-slow: 300ms ease-in-out;
  
  /* Z-index */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
}

/* ===== RESET E BASE ===== */
*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  font-family: var(--font-family-primary);
  font-size: var(--font-size-base);
  line-height: 1.6;
  color: var(--gray-700);
  background-color: var(--gray-50);
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ===== COMPONENTES BASE ===== */

/* Botões */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-6);
  font-family: var(--font-family-primary);
  font-size: var(--font-size-base);
  font-weight: 500;
  line-height: 1.5;
  text-align: center;
  text-decoration: none;
  white-space: nowrap;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  border: 1px solid transparent;
  border-radius: var(--border-radius);
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}

.btn:focus {
  outline: 2px solid var(--primary-green);
  outline-offset: 2px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

/* Variações de Botões */
.btn-primary {
  color: var(--white);
  background-color: var(--primary-green);
  border-color: var(--primary-green);
}

.btn-primary:hover {
  background-color: var(--primary-green-dark);
  border-color: var(--primary-green-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  color: var(--primary-green);
  background-color: transparent;
  border-color: var(--primary-green);
}

.btn-secondary:hover {
  color: var(--white);
  background-color: var(--primary-green);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-success {
  color: var(--white);
  background-color: var(--success);
  border-color: var(--success);
}

.btn-warning {
  color: var(--gray-800);
  background-color: var(--warning);
  border-color: var(--warning);
}

.btn-danger {
  color: var(--white);
  background-color: var(--danger);
  border-color: var(--danger);
}

/* Tamanhos de Botões */
.btn-sm {
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-sm);
}

.btn-lg {
  padding: var(--spacing-4) var(--spacing-8);
  font-size: var(--font-size-lg);
}

.btn-xl {
  padding: var(--spacing-5) var(--spacing-10);
  font-size: var(--font-size-xl);
}

/* Botão com Loading */
.btn-loading {
  position: relative;
  color: transparent !important;
}

.btn-loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 1rem;
  height: 1rem;
  margin: -0.5rem 0 0 -0.5rem;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Cards */
.card {
  background-color: var(--white);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow);
  overflow: hidden;
  transition: all var(--transition-base);
}

.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-header {
  padding: var(--spacing-6);
  border-bottom: 1px solid var(--gray-200);
  background-color: var(--gray-50);
}

.card-body {
  padding: var(--spacing-6);
}

.card-footer {
  padding: var(--spacing-6);
  border-top: 1px solid var(--gray-200);
  background-color: var(--gray-50);
}

/* Formulários */
.form-group {
  margin-bottom: var(--spacing-6);
}

.form-label {
  display: block;
  margin-bottom: var(--spacing-2);
  font-weight: 500;
  color: var(--gray-700);
}

.form-control {
  display: block;
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  font-family: var(--font-family-primary);
  font-size: var(--font-size-base);
  line-height: 1.5;
  color: var(--gray-700);
  background-color: var(--white);
  background-clip: padding-box;
  border: 1px solid var(--gray-300);
  border-radius: var(--border-radius);
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
}

.form-control:focus {
  outline: 0;
  border-color: var(--primary-green);
  box-shadow: 0 0 0 3px rgba(45, 90, 39, 0.1);
}

.form-control:invalid {
  border-color: var(--danger);
}

.form-control:invalid:focus {
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}

/* Select Customizado */
.form-select {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='m1 6 7 7 7-7'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right var(--spacing-3) center;
  background-size: 16px 12px;
  padding-right: var(--spacing-8);
}

/* Alertas */
.alert {
  position: relative;
  padding: var(--spacing-4) var(--spacing-6);
  margin-bottom: var(--spacing-6);
  border: 1px solid transparent;
  border-radius: var(--border-radius);
  font-size: var(--font-size-base);
}

.alert-success {
  color: #155724;
  background-color: var(--success-light);
  border-color: #c3e6cb;
}

.alert-warning {
  color: #856404;
  background-color: var(--warning-light);
  border-color: #ffeaa7;
}

.alert-danger {
  color: #721c24;
  background-color: var(--danger-light);
  border-color: #f5c6cb;
}

.alert-info {
  color: #0c5460;
  background-color: var(--info-light);
  border-color: #bee5eb;
}

/* Badges */
.badge {
  display: inline-block;
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
  font-weight: 600;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: var(--border-radius-full);
}

.badge-primary {
  color: var(--white);
  background-color: var(--primary-green);
}

.badge-success {
  color: var(--white);
  background-color: var(--success);
}

.badge-warning {
  color: var(--gray-800);
  background-color: var(--warning);
}

.badge-danger {
  color: var(--white);
  background-color: var(--danger);
}

/* Navegação */
.nav {
  display: flex;
  flex-wrap: wrap;
  padding-left: 0;
  margin-bottom: 0;
  list-style: none;
}

.nav-link {
  display: block;
  padding: var(--spacing-3) var(--spacing-4);
  color: var(--gray-600);
  text-decoration: none;
  transition: color var(--transition-base);
  border-radius: var(--border-radius);
}

.nav-link:hover {
  color: var(--primary-green);
  background-color: var(--gray-100);
}

.nav-link.active {
  color: var(--primary-green);
  background-color: var(--primary-green-light);
  color: var(--white);
}

/* Utilitários */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.d-none { display: none; }
.d-block { display: block; }
.d-flex { display: flex; }
.d-inline-flex { display: inline-flex; }

.justify-content-center { justify-content: center; }
.justify-content-between { justify-content: space-between; }
.justify-content-end { justify-content: flex-end; }

.align-items-center { align-items: center; }
.align-items-start { align-items: flex-start; }
.align-items-end { align-items: flex-end; }

.flex-column { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }

.gap-1 { gap: var(--spacing-1); }
.gap-2 { gap: var(--spacing-2); }
.gap-3 { gap: var(--spacing-3); }
.gap-4 { gap: var(--spacing-4); }

.mb-0 { margin-bottom: 0; }
.mb-2 { margin-bottom: var(--spacing-2); }
.mb-4 { margin-bottom: var(--spacing-4); }
.mb-6 { margin-bottom: var(--spacing-6); }

.mt-0 { margin-top: 0; }
.mt-2 { margin-top: var(--spacing-2); }
.mt-4 { margin-top: var(--spacing-4); }
.mt-6 { margin-top: var(--spacing-6); }

.p-2 { padding: var(--spacing-2); }
.p-4 { padding: var(--spacing-4); }
.p-6 { padding: var(--spacing-6); }

.px-2 { padding-left: var(--spacing-2); padding-right: var(--spacing-2); }
.px-4 { padding-left: var(--spacing-4); padding-right: var(--spacing-4); }
.px-6 { padding-left: var(--spacing-6); padding-right: var(--spacing-6); }

.py-2 { padding-top: var(--spacing-2); padding-bottom: var(--spacing-2); }
.py-4 { padding-top: var(--spacing-4); padding-bottom: var(--spacing-4); }
.py-6 { padding-top: var(--spacing-6); padding-bottom: var(--spacing-6); }

/* Responsividade */
@media (max-width: 768px) {
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .card-body {
    padding: var(--spacing-4);
  }
  
  .form-control {
    font-size: 16px; /* Previne zoom no iOS */
  }
}

/* Animações de Entrada */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

.animate-slide-in-right {
  animation: slideInRight 0.5s ease-out;
}

.animate-scale-in {
  animation: scaleIn 0.3s ease-out;
}

/* Estados de Loading */
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.skeleton-text {
  height: 1rem;
  border-radius: var(--border-radius-sm);
  margin-bottom: var(--spacing-2);
}

.skeleton-text:last-child {
  width: 60%;
}

/* Modo Escuro */
@media (prefers-color-scheme: dark) {
  :root {
    --gray-50: #1a1a1a;
    --gray-100: #2d2d2d;
    --gray-200: #404040;
    --gray-300: #525252;
    --gray-400: #737373;
    --gray-500: #a3a3a3;
    --gray-600: #d4d4d4;
    --gray-700: #e5e5e5;
    --gray-800: #f5f5f5;
    --gray-900: #ffffff;
  }
  
  body {
    background-color: var(--gray-50);
    color: var(--gray-700);
  }
  
  .card {
    background-color: var(--gray-100);
    border: 1px solid var(--gray-200);
  }
  
  .form-control {
    background-color: var(--gray-100);
    border-color: var(--gray-300);
    color: var(--gray-700);
  }
}
```

**ETAPA 2: Sistema de Micro-interações**

Crie sistema de micro-interações em `app/static/js/micro-interactions.js`:

```javascript
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
`;

document.head.appendChild(style);
```

### Testes de Validação

**TESTE 1: Validação do Design System**
```html
<!-- Testar componentes do design system -->
<div class="card">
    <div class="card-body">
        <h3>Teste de Componentes</h3>
        <button class="btn btn-primary">Botão Primário</button>
        <button class="btn btn-secondary">Botão Secundário</button>
        <div class="alert alert-success mt-4">Alerta de sucesso</div>
    </div>
</div>
```

**TESTE 2: Validação de Micro-interações**
```javascript
// Testar notificações
microInteractions.showNotification('Teste de notificação de sucesso', 'success');
microInteractions.showNotification('Teste de notificação de erro', 'error');

// Testar validação de formulário
const testInput = document.querySelector('#test-email');
microInteractions.validateField(testInput);
```

**TESTE 3: Validação de Responsividade**
```css
/* Testar em diferentes tamanhos de tela */
@media (max-width: 768px) {
    /* Verificar se componentes se adaptam corretamente */
}
```

### Critérios de Aceitação
- Design system consistente implementado
- Micro-interações funcionando em todos os componentes
- Validação de formulários em tempo real
- Notificações toast funcionais
- Responsividade completa para mobile
- Acessibilidade conforme WCAG 2.1

### Entregáveis Esperados
1. **Design System Completo** com todos os componentes
2. **Sistema de Micro-interações** funcional
3. **Validação de Formulários** em tempo real
4. **Sistema de Notificações** toast
5. **Documentação de Componentes** para desenvolvedores

### Informações Importantes
- Utilizar CSS custom properties para consistência
- Implementar animações performáticas (60fps)
- Garantir acessibilidade em todas as interações
- Testar em dispositivos móveis reais
- Manter compatibilidade com navegadores modernos

---


## 🚀 PROMPT 2: CONFIGURAÇÃO DE PRODUÇÃO E DEPLOY

### Contexto do Projeto
Você está implementando a configuração completa de produção para o AgroTech Portugal. Este trabalho envolve configuração de servidor, otimização de performance, implementação de segurança enterprise, configuração de monitoramento, backup automatizado e estabelecimento de processos de deploy contínuo para garantir operação confiável e escalável.

### Funcionalidade a Implementar
Sistema completo de produção que inclui configuração de servidor otimizada, SSL/TLS, firewall, monitoramento em tempo real, backup automatizado, logging centralizado, alertas proativos e pipeline de deploy automatizado. O objetivo é criar uma infraestrutura robusta que suporte milhares de usuários simultâneos com uptime de 99.9%.

### Arquitetura Proposta

A arquitetura de produção será baseada em containers Docker, proxy reverso Nginx, banco de dados PostgreSQL otimizado, Redis para cache, monitoramento com Prometheus/Grafana e backup automatizado. A infraestrutura será cloud-ready e facilmente escalável.

**Componentes de Produção:**
- **Containerização**: Docker com multi-stage builds
- **Proxy Reverso**: Nginx com SSL e cache
- **Banco de Dados**: PostgreSQL com replicação
- **Cache**: Redis Cluster para alta disponibilidade
- **Monitoramento**: Prometheus, Grafana e alertas
- **Backup**: Automatizado com retenção inteligente

### Objetivo
Implementar uma infraestrutura de produção enterprise-grade que garanta alta disponibilidade, performance excepcional e operação confiável do AgroTech Portugal para agricultores portugueses.

### Instruções Detalhadas

**ETAPA 1: Configuração Docker para Produção**

Crie Dockerfile otimizado em `Dockerfile`:

```dockerfile
# Dockerfile
# Multi-stage build para otimização de tamanho e segurança

# Stage 1: Build dependencies
FROM python:3.11-slim as builder

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash agrotech

# Configurar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim as production

# Instalar apenas dependências de runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash agrotech

# Copiar dependências Python do stage builder
COPY --from=builder /root/.local /home/agrotech/.local

# Configurar PATH para usuário
ENV PATH=/home/agrotech/.local/bin:$PATH

# Configurar diretório de trabalho
WORKDIR /app

# Copiar código da aplicação
COPY --chown=agrotech:agrotech . .

# Criar diretórios necessários
RUN mkdir -p logs uploads static/uploads \
    && chown -R agrotech:agrotech logs uploads static/uploads

# Configurar variáveis de ambiente
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expor porta
EXPOSE 5000

# Mudar para usuário não-root
USER agrotech

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "gevent", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "100", "--timeout", "30", "--keep-alive", "2", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
```

Crie docker-compose para produção em `docker-compose.prod.yml`:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # Aplicação principal
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: agrotech_app
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://agrotech:${DB_PASSWORD}@db:5432/agrotech_prod
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - IPMA_API_KEY=${IPMA_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
      - ./static/uploads:/app/static/uploads
    networks:
      - agrotech_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.agrotech.rule=Host(`agrotech.pt`)"
      - "traefik.http.routers.agrotech.tls=true"
      - "traefik.http.routers.agrotech.tls.certresolver=letsencrypt"

  # Banco de dados PostgreSQL
  db:
    image: postgres:15-alpine
    container_name: agrotech_db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=agrotech_prod
      - POSTGRES_USER=agrotech
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=pt_PT.UTF-8 --lc-ctype=pt_PT.UTF-8
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    networks:
      - agrotech_network
    command: >
      postgres
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
      -c work_mem=4MB
      -c min_wal_size=1GB
      -c max_wal_size=4GB
      -c log_statement=all
      -c log_min_duration_statement=1000

  # Redis para cache
  redis:
    image: redis:7-alpine
    container_name: agrotech_redis
    restart: unless-stopped
    command: >
      redis-server
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
      --appendonly yes
      --appendfsync everysec
    volumes:
      - redis_data:/data
    networks:
      - agrotech_network

  # Nginx como proxy reverso
  nginx:
    image: nginx:alpine
    container_name: agrotech_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/sites-enabled:/etc/nginx/sites-enabled
      - ./static:/var/www/static
      - ./ssl:/etc/nginx/ssl
      - nginx_logs:/var/log/nginx
    depends_on:
      - app
    networks:
      - agrotech_network

  # Monitoramento com Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: agrotech_prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    networks:
      - agrotech_network

  # Grafana para dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: agrotech_grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_DOMAIN=grafana.agrotech.pt
      - GF_SMTP_ENABLED=true
      - GF_SMTP_HOST=${SMTP_HOST}
      - GF_SMTP_USER=${SMTP_USER}
      - GF_SMTP_PASSWORD=${SMTP_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - agrotech_network

  # Node Exporter para métricas do sistema
  node_exporter:
    image: prom/node-exporter:latest
    container_name: agrotech_node_exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - agrotech_network

  # Backup automatizado
  backup:
    image: postgres:15-alpine
    container_name: agrotech_backup
    restart: "no"
    environment:
      - PGPASSWORD=${DB_PASSWORD}
    volumes:
      - ./backups:/backups
      - ./scripts/backup.sh:/backup.sh
    depends_on:
      - db
    networks:
      - agrotech_network
    entrypoint: ["/backup.sh"]

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
  nginx_logs:
    driver: local

networks:
  agrotech_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

**ETAPA 2: Configuração Nginx**

Crie configuração Nginx em `nginx/nginx.conf`:

```nginx
# nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.openweathermap.org https://api.ipma.pt;" always;

    # Upstream para aplicação
    upstream agrotech_app {
        server app:5000;
        keepalive 32;
    }

    # Configuração do servidor principal
    server {
        listen 80;
        server_name agrotech.pt www.agrotech.pt;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name agrotech.pt www.agrotech.pt;

        # SSL certificates
        ssl_certificate /etc/nginx/ssl/agrotech.pt.crt;
        ssl_certificate_key /etc/nginx/ssl/agrotech.pt.key;

        # Root directory
        root /var/www;
        index index.html;

        # Client max body size
        client_max_body_size 10M;

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
            
            # Gzip static files
            location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
                gzip_static on;
            }
        }

        # API endpoints with rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://agrotech_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 5s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Login endpoint with stricter rate limiting
        location /auth/login {
            limit_req zone=login burst=5 nodelay;
            
            proxy_pass http://agrotech_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://agrotech_app;
            access_log off;
        }

        # Main application
        location / {
            proxy_pass http://agrotech_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 5s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Error pages
        error_page 404 /404.html;
        error_page 500 502 503 504 /50x.html;
        
        location = /404.html {
            root /var/www/error_pages;
            internal;
        }
        
        location = /50x.html {
            root /var/www/error_pages;
            internal;
        }
    }

    # Monitoring endpoints
    server {
        listen 8080;
        server_name localhost;
        
        location /nginx_status {
            stub_status on;
            access_log off;
            allow 172.20.0.0/16;
            deny all;
        }
    }
}
```

**ETAPA 3: Scripts de Backup e Manutenção**

Crie script de backup em `scripts/backup.sh`:

```bash
#!/bin/bash
# scripts/backup.sh

set -e

# Configurações
DB_HOST="db"
DB_NAME="agrotech_prod"
DB_USER="agrotech"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Função de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Backup do banco de dados
backup_database() {
    log "Iniciando backup do banco de dados..."
    
    BACKUP_FILE="$BACKUP_DIR/agrotech_db_$DATE.sql"
    
    pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        log "Backup do banco de dados concluído: $BACKUP_FILE"
        
        # Comprimir backup
        gzip $BACKUP_FILE
        log "Backup comprimido: $BACKUP_FILE.gz"
    else
        log "ERRO: Falha no backup do banco de dados"
        exit 1
    fi
}

# Backup de arquivos de upload
backup_uploads() {
    log "Iniciando backup de arquivos de upload..."
    
    UPLOADS_BACKUP="$BACKUP_DIR/agrotech_uploads_$DATE.tar.gz"
    
    if [ -d "/app/uploads" ]; then
        tar -czf $UPLOADS_BACKUP -C /app uploads/
        log "Backup de uploads concluído: $UPLOADS_BACKUP"
    else
        log "Diretório de uploads não encontrado, pulando..."
    fi
}

# Limpeza de backups antigos
cleanup_old_backups() {
    log "Limpando backups antigos (mais de $RETENTION_DAYS dias)..."
    
    find $BACKUP_DIR -name "agrotech_*" -type f -mtime +$RETENTION_DAYS -delete
    
    log "Limpeza concluída"
}

# Verificar integridade do backup
verify_backup() {
    local backup_file="$1"
    
    log "Verificando integridade do backup: $backup_file"
    
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        log "Backup verificado com sucesso"
        return 0
    else
        log "ERRO: Backup inválido ou vazio"
        return 1
    fi
}

# Enviar notificação de status
send_notification() {
    local status="$1"
    local message="$2"
    
    # Aqui você pode integrar com serviços de notificação
    # como Slack, Discord, email, etc.
    log "NOTIFICAÇÃO [$status]: $message"
}

# Função principal
main() {
    log "=== Iniciando processo de backup ==="
    
    # Backup do banco de dados
    backup_database
    
    # Verificar integridade
    if verify_backup "$BACKUP_DIR/agrotech_db_$DATE.sql.gz"; then
        send_notification "SUCCESS" "Backup do banco de dados concluído com sucesso"
    else
        send_notification "ERROR" "Falha na verificação do backup do banco de dados"
        exit 1
    fi
    
    # Backup de uploads
    backup_uploads
    
    # Limpeza de backups antigos
    cleanup_old_backups
    
    log "=== Processo de backup concluído ==="
    send_notification "SUCCESS" "Processo de backup concluído com sucesso"
}

# Executar função principal
main "$@"
```

Crie script de restore em `scripts/restore.sh`:

```bash
#!/bin/bash
# scripts/restore.sh

set -e

# Configurações
DB_HOST="db"
DB_NAME="agrotech_prod"
DB_USER="agrotech"
BACKUP_DIR="/backups"

# Função de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Listar backups disponíveis
list_backups() {
    log "Backups disponíveis:"
    ls -la $BACKUP_DIR/agrotech_db_*.sql.gz | awk '{print $9, $5, $6, $7, $8}'
}

# Restaurar banco de dados
restore_database() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log "ERRO: Arquivo de backup não especificado"
        log "Uso: $0 restore <arquivo_backup>"
        list_backups
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log "ERRO: Arquivo de backup não encontrado: $backup_file"
        exit 1
    fi
    
    log "Iniciando restore do banco de dados..."
    log "Arquivo: $backup_file"
    
    # Confirmar ação
    read -p "ATENÇÃO: Esta ação irá sobrescrever o banco de dados atual. Continuar? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        log "Restore cancelado pelo usuário"
        exit 0
    fi
    
    # Descomprimir se necessário
    if [[ $backup_file == *.gz ]]; then
        log "Descomprimindo backup..."
        gunzip -c "$backup_file" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME
    else
        psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$backup_file"
    fi
    
    if [ $? -eq 0 ]; then
        log "Restore concluído com sucesso"
    else
        log "ERRO: Falha no restore do banco de dados"
        exit 1
    fi
}

# Função principal
case "$1" in
    "list")
        list_backups
        ;;
    "restore")
        restore_database "$2"
        ;;
    *)
        echo "Uso: $0 {list|restore <arquivo_backup>}"
        echo ""
        echo "Comandos:"
        echo "  list     - Listar backups disponíveis"
        echo "  restore  - Restaurar backup especificado"
        echo ""
        echo "Exemplo:"
        echo "  $0 list"
        echo "  $0 restore /backups/agrotech_db_20250731_120000.sql.gz"
        exit 1
        ;;
esac
```

### Testes de Validação

**TESTE 1: Validação do Container Docker**
```bash
# Build e teste do container
docker build -t agrotech:latest .
docker run --rm -p 5000:5000 agrotech:latest

# Testar health check
curl -f http://localhost:5000/health
```

**TESTE 2: Validação do Nginx**
```bash
# Testar configuração do Nginx
nginx -t -c /path/to/nginx.conf

# Testar SSL
openssl s_client -connect agrotech.pt:443 -servername agrotech.pt
```

**TESTE 3: Validação do Backup**
```bash
# Executar backup de teste
./scripts/backup.sh

# Verificar arquivos criados
ls -la backups/

# Testar restore
./scripts/restore.sh list
```

### Critérios de Aceitação
- Container Docker otimizado e seguro
- Nginx configurado com SSL e cache
- Sistema de backup automatizado funcionando
- Monitoramento com Prometheus/Grafana
- Scripts de manutenção operacionais
- Deploy automatizado via Docker Compose

### Entregáveis Esperados
1. **Container Docker** otimizado para produção
2. **Configuração Nginx** completa com SSL
3. **Sistema de Backup** automatizado
4. **Monitoramento** com dashboards
5. **Scripts de Manutenção** operacionais

### Informações Importantes
- Usar usuário não-root no container
- Implementar health checks robustos
- Configurar SSL com certificados válidos
- Estabelecer retenção de backup adequada
- Monitorar métricas de performance continuamente

---

## 📊 PROMPT 3: ANALYTICS E MONITORAMENTO AVANÇADO

### Contexto do Projeto
Você está implementando um sistema abrangente de analytics e monitoramento para o AgroTech Portugal. Este sistema deve fornecer insights detalhados sobre uso da plataforma, comportamento dos usuários, performance das funcionalidades, métricas de negócio e alertas proativos para garantir operação otimizada e crescimento sustentável.

### Funcionalidade a Implementar
Sistema completo de analytics que inclui tracking de eventos, análise de comportamento do usuário, métricas de performance, dashboards executivos, relatórios automatizados, alertas inteligentes e insights acionáveis. O objetivo é fornecer visibilidade completa sobre todos os aspectos da plataforma e seu impacto nos agricultores portugueses.

### Arquitetura Proposta

O sistema de analytics será baseado em coleta de eventos em tempo real, processamento de dados, armazenamento otimizado e visualização interativa. A arquitetura utilizará InfluxDB para séries temporais, Grafana para dashboards e Python para processamento de dados.

**Componentes de Analytics:**
- **Event Tracking**: Coleta de eventos de usuário e sistema
- **Metrics Collection**: Métricas técnicas e de negócio
- **Data Processing**: Análise e agregação de dados
- **Dashboards**: Visualização interativa de métricas
- **Alerting**: Sistema de alertas inteligentes
- **Reporting**: Relatórios automatizados

### Objetivo
Implementar um sistema robusto de analytics que forneça insights valiosos sobre o uso e performance do AgroTech Portugal, permitindo tomada de decisões baseada em dados e otimização contínua da plataforma.

### Instruções Detalhadas

**ETAPA 1: Sistema de Event Tracking**

Crie sistema de tracking em `app/utils/analytics.py`:

```python
# app/utils/analytics.py
import json
import time
from datetime import datetime, timedelta
from flask import request, g, current_app
from functools import wraps
import logging
from typing import Dict, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class AnalyticsTracker:
    """Sistema de tracking de eventos e métricas"""
    
    def __init__(self, app=None):
        self.app = app
        self.events_buffer = []
        self.buffer_size = 100
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar tracker com a aplicação"""
        self.app = app
        
        # Configurações padrão
        app.config.setdefault('ANALYTICS_ENABLED', True)
        app.config.setdefault('ANALYTICS_BUFFER_SIZE', 100)
        app.config.setdefault('ANALYTICS_FLUSH_INTERVAL', 60)
        
        # Registrar middleware
        app.before_request(self._before_request)
        app.after_request(self._after_request)
    
    def track_event(self, event_name: str, properties: Dict[str, Any] = None, user_id: Optional[int] = None):
        """Rastrear evento personalizado"""
        if not current_app.config.get('ANALYTICS_ENABLED', True):
            return
        
        event = {
            'event_id': str(uuid.uuid4()),
            'event_name': event_name,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id or getattr(g, 'user_id', None),
            'session_id': getattr(g, 'session_id', None),
            'properties': properties or {},
            'context': self._get_request_context()
        }
        
        self._add_to_buffer(event)
        logger.debug(f"Event tracked: {event_name}")
    
    def track_page_view(self, page: str, title: str = None):
        """Rastrear visualização de página"""
        self.track_event('page_view', {
            'page': page,
            'title': title,
            'referrer': request.headers.get('Referer'),
            'user_agent': request.headers.get('User-Agent')
        })
    
    def track_user_action(self, action: str, resource_type: str, resource_id: Optional[int] = None, details: Dict[str, Any] = None):
        """Rastrear ação do usuário"""
        self.track_event('user_action', {
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or {}
        })
    
    def track_conversion(self, conversion_type: str, value: float = None, currency: str = 'EUR'):
        """Rastrear conversão/objetivo"""
        self.track_event('conversion', {
            'conversion_type': conversion_type,
            'value': value,
            'currency': currency
        })
    
    def track_error(self, error_type: str, error_message: str, stack_trace: str = None):
        """Rastrear erro"""
        self.track_event('error', {
            'error_type': error_type,
            'error_message': error_message,
            'stack_trace': stack_trace,
            'url': request.url if request else None
        })
    
    def track_performance(self, metric_name: str, value: float, unit: str = 'ms'):
        """Rastrear métrica de performance"""
        self.track_event('performance', {
            'metric_name': metric_name,
            'value': value,
            'unit': unit
        })
    
    def _before_request(self):
        """Middleware executado antes da requisição"""
        g.request_start_time = time.time()
        g.session_id = self._get_or_create_session_id()
        
        # Rastrear início da requisição
        if request.endpoint and not request.endpoint.startswith('static'):
            self.track_event('request_start', {
                'endpoint': request.endpoint,
                'method': request.method,
                'path': request.path
            })
    
    def _after_request(self, response):
        """Middleware executado após a requisição"""
        if hasattr(g, 'request_start_time'):
            duration = (time.time() - g.request_start_time) * 1000  # ms
            
            # Rastrear fim da requisição
            if request.endpoint and not request.endpoint.startswith('static'):
                self.track_event('request_end', {
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration, 2)
                })
                
                # Rastrear performance se for lenta
                if duration > 1000:  # > 1 segundo
                    self.track_performance('slow_request', duration, 'ms')
        
        return response
    
    def _get_or_create_session_id(self):
        """Obter ou criar ID da sessão"""
        if hasattr(g, 'session_id'):
            return g.session_id
        
        # Tentar obter da sessão Flask
        from flask import session
        if 'analytics_session_id' not in session:
            session['analytics_session_id'] = str(uuid.uuid4())
        
        return session['analytics_session_id']
    
    def _get_request_context(self):
        """Obter contexto da requisição"""
        if not request:
            return {}
        
        return {
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'referer': request.headers.get('Referer'),
            'accept_language': request.headers.get('Accept-Language'),
            'method': request.method,
            'path': request.path,
            'query_string': request.query_string.decode('utf-8') if request.query_string else None
        }
    
    def _add_to_buffer(self, event):
        """Adicionar evento ao buffer"""
        self.events_buffer.append(event)
        
        # Flush se buffer estiver cheio
        if len(self.events_buffer) >= self.buffer_size:
            self.flush_events()
    
    def flush_events(self):
        """Enviar eventos do buffer para armazenamento"""
        if not self.events_buffer:
            return
        
        try:
            # Aqui você pode integrar com diferentes sistemas de analytics
            # InfluxDB, Google Analytics, Mixpanel, etc.
            self._send_to_influxdb(self.events_buffer)
            
            logger.info(f"Flushed {len(self.events_buffer)} events to analytics")
            self.events_buffer.clear()
            
        except Exception as e:
            logger.error(f"Error flushing events: {e}")
    
    def _send_to_influxdb(self, events):
        """Enviar eventos para InfluxDB"""
        try:
            from influxdb_client import InfluxDBClient, Point
            from influxdb_client.client.write_api import SYNCHRONOUS
            
            client = InfluxDBClient(
                url=current_app.config.get('INFLUXDB_URL', 'http://localhost:8086'),
                token=current_app.config.get('INFLUXDB_TOKEN'),
                org=current_app.config.get('INFLUXDB_ORG', 'agrotech')
            )
            
            write_api = client.write_api(write_options=SYNCHRONOUS)
            
            points = []
            for event in events:
                point = Point("events") \
                    .tag("event_name", event['event_name']) \
                    .tag("user_id", str(event.get('user_id', 'anonymous'))) \
                    .tag("session_id", event.get('session_id', '')) \
                    .field("event_id", event['event_id']) \
                    .time(event['timestamp'])
                
                # Adicionar propriedades como fields
                for key, value in event.get('properties', {}).items():
                    if isinstance(value, (int, float)):
                        point = point.field(f"prop_{key}", value)
                    else:
                        point = point.field(f"prop_{key}", str(value))
                
                # Adicionar contexto como tags
                context = event.get('context', {})
                if context.get('path'):
                    point = point.tag("path", context['path'])
                if context.get('method'):
                    point = point.tag("method", context['method'])
                
                points.append(point)
            
            write_api.write(
                bucket=current_app.config.get('INFLUXDB_BUCKET', 'agrotech'),
                record=points
            )
            
            client.close()
            
        except ImportError:
            logger.warning("InfluxDB client not installed, events not sent")
        except Exception as e:
            logger.error(f"Error sending events to InfluxDB: {e}")

class BusinessMetrics:
    """Métricas de negócio específicas do AgroTech"""
    
    def __init__(self, tracker: AnalyticsTracker):
        self.tracker = tracker
    
    def track_user_registration(self, user_id: int, registration_method: str = 'web'):
        """Rastrear registro de usuário"""
        self.tracker.track_conversion('user_registration', 1.0)
        self.tracker.track_user_action('register', 'user', user_id, {
            'registration_method': registration_method
        })
    
    def track_culture_creation(self, user_id: int, culture_type: str, area: float):
        """Rastrear criação de cultura"""
        self.tracker.track_user_action('create', 'culture', None, {
            'culture_type': culture_type,
            'area': area
        })
        
        # Métrica de engajamento
        self.tracker.track_event('engagement', {
            'action': 'culture_created',
            'culture_type': culture_type,
            'area': area
        }, user_id)
    
    def track_recommendation_interaction(self, user_id: int, recommendation_id: int, action: str):
        """Rastrear interação com recomendação"""
        self.tracker.track_user_action(action, 'recommendation', recommendation_id)
        
        # Métrica de efetividade da IA
        self.tracker.track_event('ai_interaction', {
            'recommendation_id': recommendation_id,
            'action': action
        }, user_id)
    
    def track_marketplace_activity(self, user_id: int, action: str, product_id: int = None, value: float = None):
        """Rastrear atividade no marketplace"""
        self.tracker.track_user_action(action, 'product', product_id, {
            'value': value
        })
        
        if action == 'purchase' and value:
            self.tracker.track_conversion('marketplace_sale', value)
    
    def track_weather_request(self, user_id: int, location: str):
        """Rastrear solicitação de dados meteorológicos"""
        self.tracker.track_user_action('request', 'weather', None, {
            'location': location
        })
    
    def track_session_duration(self, user_id: int, duration_minutes: float):
        """Rastrear duração da sessão"""
        self.tracker.track_event('session_end', {
            'duration_minutes': duration_minutes
        }, user_id)
        
        self.tracker.track_performance('session_duration', duration_minutes, 'minutes')

# Decorators para tracking automático
def track_function_call(event_name: str = None, track_performance: bool = True):
    """Decorator para rastrear chamadas de função"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = event_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                if track_performance:
                    duration = (time.time() - start_time) * 1000
                    analytics.track_performance(f"function_{name}", duration)
                
                analytics.track_event('function_call', {
                    'function_name': name,
                    'success': True
                })
                
                return result
                
            except Exception as e:
                analytics.track_error('function_error', str(e), name)
                raise
        
        return wrapper
    return decorator

def track_endpoint(track_performance: bool = True):
    """Decorator para rastrear endpoints Flask"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                if track_performance:
                    duration = (time.time() - start_time) * 1000
                    analytics.track_performance(f"endpoint_{request.endpoint}", duration)
                
                return result
                
            except Exception as e:
                analytics.track_error('endpoint_error', str(e))
                raise
        
        return wrapper
    return decorator

# Instâncias globais
analytics = AnalyticsTracker()
business_metrics = BusinessMetrics(analytics)
```

**ETAPA 2: Dashboards Grafana**

Crie dashboard principal em `monitoring/grafana/dashboards/agrotech-main.json`:

```json
{
  "dashboard": {
    "id": null,
    "title": "AgroTech Portugal - Dashboard Principal",
    "tags": ["agrotech", "production"],
    "timezone": "Europe/Lisbon",
    "panels": [
      {
        "id": 1,
        "title": "Usuários Ativos",
        "type": "stat",
        "targets": [
          {
            "expr": "count(count by (user_id) (events{event_name=\"page_view\"} [1h]))",
            "legendFormat": "Usuários Ativos (1h)"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 10},
                {"color": "green", "value": 50}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Requisições por Minuto",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(events{event_name=\"request_start\"}[5m]) * 60",
            "legendFormat": "Requisições/min"
          }
        ],
        "yAxes": [
          {
            "label": "Requisições por minuto"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Tempo de Resposta Médio",
        "type": "stat",
        "targets": [
          {
            "expr": "avg(events{event_name=\"request_end\", prop_duration_ms!=\"\"}) by ()",
            "legendFormat": "Tempo Médio (ms)"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "ms",
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 500},
                {"color": "red", "value": 1000}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0}
      },
      {
        "id": 4,
        "title": "Culturas Criadas (Hoje)",
        "type": "stat",
        "targets": [
          {
            "expr": "count(events{event_name=\"user_action\", prop_action=\"create\", prop_resource_type=\"culture\"} [24h])",
            "legendFormat": "Culturas Criadas"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 8}
      },
      {
        "id": 5,
        "title": "Interações com Recomendações IA",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(events{event_name=\"ai_interaction\"}[5m]) * 60",
            "legendFormat": "Interações/min"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 6, "y": 8}
      },
      {
        "id": 6,
        "title": "Vendas Marketplace (Hoje)",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(events{event_name=\"conversion\", prop_conversion_type=\"marketplace_sale\"} [24h])",
            "legendFormat": "Vendas (€)"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "currencyEUR"
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 8}
      },
      {
        "id": 7,
        "title": "Páginas Mais Visitadas",
        "type": "table",
        "targets": [
          {
            "expr": "topk(10, count by (path) (events{event_name=\"page_view\"} [24h]))",
            "format": "table"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
      },
      {
        "id": 8,
        "title": "Erros por Hora",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(events{event_name=\"error\"}[1h]) * 3600",
            "legendFormat": "Erros/hora"
          }
        ],
        "yAxes": [
          {
            "label": "Erros por hora"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}
      }
    ],
    "time": {
      "from": "now-24h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

### Testes de Validação

**TESTE 1: Validação do Event Tracking**
```python
# Testar tracking de eventos
from app.utils.analytics import analytics, business_metrics

# Testar evento básico
analytics.track_event('test_event', {'test_property': 'test_value'})

# Testar métrica de negócio
business_metrics.track_culture_creation(1, 'vineyard', 2.5)

# Verificar buffer
print(f"Events in buffer: {len(analytics.events_buffer)}")
```

**TESTE 2: Validação do Dashboard**
```bash
# Verificar se Grafana está acessível
curl -f http://localhost:3000/api/health

# Testar query do InfluxDB
curl -G 'http://localhost:8086/query' \
  --data-urlencode "q=SELECT * FROM events LIMIT 10"
```

**TESTE 3: Validação de Performance**
```python
# Testar tracking de performance
import time
from app.utils.analytics import track_function_call

@track_function_call(track_performance=True)
def test_function():
    time.sleep(0.1)
    return "test"

result = test_function()
```

### Critérios de Aceitação
- Sistema de event tracking funcionando
- Métricas sendo coletadas e armazenadas
- Dashboards Grafana operacionais
- Alertas configurados e funcionais
- Relatórios automatizados sendo gerados
- Performance de tracking não impactando aplicação

### Entregáveis Esperados
1. **Sistema de Event Tracking** completo
2. **Dashboards Grafana** interativos
3. **Métricas de Negócio** específicas do AgroTech
4. **Sistema de Alertas** automatizado
5. **Relatórios** automatizados

### Informações Importantes
- Implementar sampling para alto volume de eventos
- Garantir privacidade dos dados dos usuários
- Configurar retenção adequada de dados
- Otimizar queries para performance
- Estabelecer alertas para métricas críticas

---

