/**
 * Sistema de Interações AgroTech Portugal
 * Gerencia dropdowns, navegação e interações específicas
 */

(function() {
    'use strict';
    
    // Estado global das interações
    let activeDropdown = null;
    let sidebarOpen = false;
    
    // Inicialização quando DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function() {
        initDropdowns();
        initSidebar();
        initThemeToggle();
        initLogoutModal();
        initKeyboardNavigation();
        initAccessibility();
        
        console.log('🇵🇹 AgroTech Portugal - Sistema de interações inicializado');
    });
    
    /**
     * Inicializa sistema de dropdowns portugueses
     */
    function initDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown-portugal');
        
        dropdowns.forEach(dropdown => {
            const trigger = dropdown.querySelector('.dropdown-trigger-pt');
            const menu = dropdown.querySelector('.dropdown-menu-pt');
            
            if (!trigger || !menu) return;
            
            // Click no trigger
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const isActive = dropdown.classList.contains('active');
                
                // Fecha todos os outros dropdowns
                closeAllDropdowns();
                
                if (!isActive) {
                    openDropdown(dropdown);
                }
            });
            
            // Hover para desktop
            if (window.innerWidth >= 1024) {
                dropdown.addEventListener('mouseenter', () => {
                    openDropdown(dropdown);
                });
                
                dropdown.addEventListener('mouseleave', () => {
                    closeDropdown(dropdown);
                });
            }
            
            // Click nos itens do menu
            const items = menu.querySelectorAll('.dropdown-item-pt');
            items.forEach(item => {
                item.addEventListener('click', () => {
                    closeAllDropdowns();
                });
            });
        });
        
        // Fecha dropdowns ao clicar fora
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown-portugal')) {
                closeAllDropdowns();
            }
        });
        
        // Fecha dropdowns ao pressionar ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeAllDropdowns();
            }
        });
    }
    
    /**
     * Abre um dropdown específico
     */
    function openDropdown(dropdown) {
        closeAllDropdowns();
        
        dropdown.classList.add('active');
        activeDropdown = dropdown;
        
        const trigger = dropdown.querySelector('.dropdown-trigger-pt');
        const menu = dropdown.querySelector('.dropdown-menu-pt');
        const arrow = trigger.querySelector('.fa-chevron-down');
        
        if (trigger) {
            trigger.setAttribute('aria-expanded', 'true');
        }
        
        if (arrow) {
            arrow.style.transform = 'rotate(180deg)';
        }
        
        if (menu) {
            menu.style.opacity = '1';
            menu.style.visibility = 'visible';
            menu.style.transform = 'translateY(0)';
        }
        
        // Foco no primeiro item para acessibilidade
        const firstItem = menu.querySelector('.dropdown-item-pt');
        if (firstItem && document.activeElement === trigger) {
            setTimeout(() => firstItem.focus(), 100);
        }
    }
    
    /**
     * Fecha um dropdown específico
     */
    function closeDropdown(dropdown) {
        dropdown.classList.remove('active');
        
        const trigger = dropdown.querySelector('.dropdown-trigger-pt');
        const menu = dropdown.querySelector('.dropdown-menu-pt');
        const arrow = trigger.querySelector('.fa-chevron-down');
        
        if (trigger) {
            trigger.setAttribute('aria-expanded', 'false');
        }
        
        if (arrow) {
            arrow.style.transform = 'rotate(0deg)';
        }
        
        if (menu) {
            menu.style.opacity = '0';
            menu.style.visibility = 'hidden';
            menu.style.transform = 'translateY(-10px)';
        }
        
        if (activeDropdown === dropdown) {
            activeDropdown = null;
        }
    }
    
    /**
     * Fecha todos os dropdowns
     */
    function closeAllDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown-portugal.active');
        dropdowns.forEach(dropdown => {
            closeDropdown(dropdown);
        });
    }
    
    /**
     * Inicializa controle da sidebar mobile
     */
    function initSidebar() {
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.querySelector('.app-sidebar');
        const overlay = document.createElement('div');
        
        if (!sidebarToggle || !sidebar) return;
        
        // Cria overlay para mobile
        overlay.className = 'sidebar-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        `;
        document.body.appendChild(overlay);
        
        // Toggle sidebar
        sidebarToggle.addEventListener('click', function() {
            sidebarOpen = !sidebarOpen;
            
            if (sidebarOpen) {
                sidebar.style.transform = 'translateX(0)';
                overlay.style.opacity = '1';
                overlay.style.visibility = 'visible';
                document.body.style.overflow = 'hidden';
            } else {
                sidebar.style.transform = 'translateX(-100%)';
                overlay.style.opacity = '0';
                overlay.style.visibility = 'hidden';
                document.body.style.overflow = '';
            }
        });
        
        // Fecha sidebar ao clicar no overlay
        overlay.addEventListener('click', function() {
            if (sidebarOpen) {
                sidebarToggle.click();
            }
        });
        
        // Fecha sidebar ao redimensionar para desktop
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 1024 && sidebarOpen) {
                sidebarToggle.click();
            }
        });
    }
    
    /**
     * Inicializa toggle de tema
     */
    function initThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        const themeIcon = document.getElementById('theme-icon');
        
        if (!themeToggle) return;
        
        // Verifica tema salvo
        const savedTheme = localStorage.getItem('agrotech-theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const currentTheme = savedTheme || (prefersDark ? 'dark' : 'light');
        
        // Aplica tema inicial
        applyTheme(currentTheme);
        
        // Toggle tema
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            applyTheme(newTheme);
            localStorage.setItem('agrotech-theme', newTheme);
        });
        
        function applyTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            
            if (themeIcon) {
                if (theme === 'dark') {
                    themeIcon.className = 'fas fa-sun';
                    themeToggle.setAttribute('aria-label', 'Ativar tema claro');
                } else {
                    themeIcon.className = 'fas fa-moon';
                    themeToggle.setAttribute('aria-label', 'Ativar tema escuro');
                }
            }
        }
    }
    
    /**
     * Inicializa modal de logout
     */
    function initLogoutModal() {
        const logoutBtn = document.getElementById('logout-btn');
        const modal = document.getElementById('logoutModal');
        const cancelBtn = document.getElementById('modal-cancel-btn');
        const confirmBtn = document.getElementById('modal-confirm-btn');
        
        if (!logoutBtn || !modal) return;
        
        // Abre modal
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            modal.style.display = 'flex';
            modal.style.opacity = '0';
            
            setTimeout(() => {
                modal.style.opacity = '1';
            }, 10);
            
            // Foco no botão cancelar
            if (cancelBtn) {
                cancelBtn.focus();
            }
        });
        
        // Fecha modal
        function closeModal() {
            modal.style.opacity = '0';
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', closeModal);
        }
        
        // Confirma logout
        if (confirmBtn) {
            confirmBtn.addEventListener('click', function() {
                // Aqui você pode adicionar a lógica de logout
                window.location.href = '/logout';
            });
        }
        
        // Fecha modal ao clicar fora
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
        
        // Fecha modal com ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display === 'flex') {
                closeModal();
            }
        });
    }
    
    /**
     * Inicializa navegação por teclado
     */
    function initKeyboardNavigation() {
        // Navegação nos dropdowns
        document.addEventListener('keydown', function(e) {
            if (!activeDropdown) return;
            
            const menu = activeDropdown.querySelector('.dropdown-menu-pt');
            const items = menu.querySelectorAll('.dropdown-item-pt');
            const currentIndex = Array.from(items).indexOf(document.activeElement);
            
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    const nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
                    items[nextIndex].focus();
                    break;
                    
                case 'ArrowUp':
                    e.preventDefault();
                    const prevIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
                    items[prevIndex].focus();
                    break;
                    
                case 'Enter':
                case ' ':
                    if (document.activeElement.classList.contains('dropdown-item-pt')) {
                        e.preventDefault();
                        document.activeElement.click();
                    }
                    break;
                    
                case 'Escape':
                    e.preventDefault();
                    closeAllDropdowns();
                    activeDropdown.querySelector('.dropdown-trigger-pt').focus();
                    break;
            }
        });
    }
    
    /**
     * Inicializa melhorias de acessibilidade
     */
    function initAccessibility() {
        // Adiciona skip link
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Saltar para o conteúdo principal';
        skipLink.className = 'sr-only';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: var(--verde-agricultura);
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 1000;
            transition: top 0.3s;
        `;
        
        skipLink.addEventListener('focus', function() {
            this.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', function() {
            this.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // Adiciona ID ao main content
        const mainContent = document.querySelector('.app-content');
        if (mainContent) {
            mainContent.id = 'main-content';
        }
        
        // Melhora foco visível
        const focusableElements = document.querySelectorAll(
            'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
        );
        
        focusableElements.forEach(element => {
            element.addEventListener('focus', function() {
                this.style.outline = '2px solid var(--verde-agricultura)';
                this.style.outlineOffset = '2px';
            });
            
            element.addEventListener('blur', function() {
                this.style.outline = '';
                this.style.outlineOffset = '';
            });
        });
    }
    
    /**
     * Utilitários para animações
     */
    function animateElement(element, animation, duration = 600) {
        element.style.animation = `${animation} ${duration}ms ease-out`;
        
        setTimeout(() => {
            element.style.animation = '';
        }, duration);
    }
    
    /**
     * Notificações toast portuguesas
     */
    function showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `alert-portugal alert-${type} fixed top-4 right-4 z-50 max-w-sm`;
        toast.style.cssText = `
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        const icon = type === 'sucesso' ? 'fa-check-circle' : 
                    type === 'erro' ? 'fa-exclamation-triangle' :
                    type === 'aviso' ? 'fa-exclamation-circle' : 'fa-info-circle';
        
        toast.innerHTML = `
            <i class="alert-icon-pt fas ${icon}"></i>
            <div class="alert-content-pt">
                <div class="alert-title-pt">${message}</div>
            </div>
            <button class="ml-auto text-current opacity-70 hover:opacity-100" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(toast);
        
        // Anima entrada
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 10);
        
        // Remove automaticamente
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }, duration);
    }
    
    // Expõe funções globalmente
    window.AgroTechPortugal = {
        showToast,
        animateElement,
        closeAllDropdowns
    };
    
})();

