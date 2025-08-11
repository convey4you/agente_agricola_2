// Funções de otimização mobile-first

// Configurar toggle de tema claro/escuro
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    if (themeToggle && themeIcon) {
        themeToggle.addEventListener('click', function() {
            document.documentElement.classList.toggle('dark');
            
            if (document.documentElement.classList.contains('dark')) {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
                localStorage.setItem('theme', 'dark');
            } else {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
                localStorage.setItem('theme', 'light');
            }
        });
        
        // Verificar tema salvo
        if (localStorage.getItem('theme') === 'dark' || 
            (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        } else {
            document.documentElement.classList.remove('dark');
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        }
    }
}

// Configurar navegação mobile
function setupMobileNavigation() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.app-sidebar');
    const sidebarCloseBtn = document.querySelector('.sidebar-close-btn');
    
    if (sidebarToggle && sidebar) {
        // Criar overlay para mobile se ainda não existir
        let overlay = document.querySelector('.mobile-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.classList.add('mobile-overlay');
            document.body.appendChild(overlay);
        }
        
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.add('open');
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
        
        if (sidebarCloseBtn) {
            sidebarCloseBtn.addEventListener('click', function() {
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            });
        }
        
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
}

// Configurar animações de entrada baseadas em scroll
function setupScrollAnimations() {
    const animateElements = document.querySelectorAll('.fade-in-up, .slide-in-right, .slide-in-left');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        animateElements.forEach(el => {
            observer.observe(el);
        });
    } else {
        // Fallback para navegadores que não suportam IntersectionObserver
        animateElements.forEach(el => {
            el.classList.add('visible');
        });
    }
}

// Configurar dropdowns responsivos
function setupResponsiveDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown-portugal');
    
    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('.dropdown-trigger-pt');
        const menu = dropdown.querySelector('.dropdown-menu-pt');
        
        if (trigger && menu) {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const isExpanded = trigger.getAttribute('aria-expanded') === 'true';
                
                // Fechar todos os outros dropdowns
                document.querySelectorAll('.dropdown-trigger-pt').forEach(t => {
                    if (t !== trigger) {
                        t.setAttribute('aria-expanded', 'false');
                        const parentMenu = t.closest('.dropdown-portugal').querySelector('.dropdown-menu-pt');
                        if (parentMenu) parentMenu.classList.remove('show');
                    }
                });
                
                // Alternar este dropdown
                trigger.setAttribute('aria-expanded', isExpanded ? 'false' : 'true');
                menu.classList.toggle('show');
            });
        }
    });
    
    // Fechar dropdown ao clicar fora
    document.addEventListener('click', function(e) {
        const dropdowns = document.querySelectorAll('.dropdown-menu-pt.show');
        dropdowns.forEach(menu => {
            menu.classList.remove('show');
            const trigger = menu.parentNode.querySelector('.dropdown-trigger-pt');
            if (trigger) {
                trigger.setAttribute('aria-expanded', 'false');
            }
        });
    });
}

// Otimizar imagens e usar lazy loading
function setupLazyLoading() {
    if ('loading' in HTMLImageElement.prototype) {
        // Navegadores modernos com lazy-loading nativo
        const images = document.querySelectorAll('img[data-src]');
        images.forEach(img => {
            img.src = img.dataset.src;
            img.loading = "lazy";
        });
    } else {
        // Fallback para navegadores antigos
        const lazyImages = [].slice.call(document.querySelectorAll('img[data-src]'));
        
        if ('IntersectionObserver' in window) {
            let lazyImageObserver = new IntersectionObserver(function(entries, observer) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        let lazyImage = entry.target;
                        lazyImage.src = lazyImage.dataset.src;
                        lazyImageObserver.unobserve(lazyImage);
                    }
                });
            });
            
            lazyImages.forEach(function(lazyImage) {
                lazyImageObserver.observe(lazyImage);
            });
        }
    }
}

// Configurar skeleton loading para melhor UX
function setupSkeletonLoading() {
    const skeletons = document.querySelectorAll('.skeleton-loader');
    
    // Mostrar skeletons
    skeletons.forEach(skeleton => {
        skeleton.style.display = 'block';
    });
    
    // Esconder skeletons quando o conteúdo estiver pronto
    window.addEventListener('load', () => {
        setTimeout(() => {
            skeletons.forEach(skeleton => {
                const content = skeleton.nextElementSibling;
                if (content) {
                    skeleton.style.display = 'none';
                    content.style.display = 'block';
                }
            });
        }, 500);
    });
}

// Gerenciar PWA install prompt
let deferredPrompt;
function setupPWAInstall() {
    const pwaInstallBtn = document.getElementById('pwa-install-btn');
    
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevenir comportamento padrão do Chrome
        e.preventDefault();
        // Armazenar evento para usar depois
        deferredPrompt = e;
        // Mostrar botão de instalação
        if (pwaInstallBtn) {
            pwaInstallBtn.style.display = 'block';
            pwaInstallBtn.addEventListener('click', async () => {
                // Mostrar prompt de instalação
                deferredPrompt.prompt();
                // Aguardar resposta
                const { outcome } = await deferredPrompt.userChoice;
                // Reset da variável
                deferredPrompt = null;
                // Esconder botão de instalação
                pwaInstallBtn.style.display = 'none';
            });
        }
    });
}
