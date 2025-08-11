/**
 * Sistema de Fallback para Ícones - AgTech Portugal v2.0
 * Garante que os ícones sejam exibidos mesmo se Font Awesome falhar
 */

(function() {
    'use strict';
    
    // Mapeamento de ícones Font Awesome para emojis
    const iconMap = {
        'fa-seedling': '🌱',
        'fa-tachometer-alt': '📊',
        'fa-robot': '🤖',
        'fa-chart-bar': '📈',
        'fa-bell': '🔔',
        'fa-cloud-sun': '🌤️',
        'fa-calendar-alt': '📅',
        'fa-map': '🗺️',
        'fa-euro-sign': '💰',
        'fa-tasks': '✅',
        'fa-info-circle': 'ℹ️',
        'fa-moon': '🌙',
        'fa-sun': '☀️',
        'fa-bars': '☰',
        'fa-chevron-down': '▼',
        'fa-plus': '➕',
        'fa-sign-out-alt': '🚪',
        'fa-user': '👤',
        'fa-cog': '⚙️',
        'fa-refresh': '🔄',
        'fa-sync': '🔄',
        'fa-home': '🏠',
        'fa-leaf': '🍃',
        'fa-water': '💧',
        'fa-thermometer': '🌡️',
        'fa-wind': '💨',
        'fa-eye': '👁️',
        'fa-compress': '📊'
    };
    
    // Função para verificar se Font Awesome carregou
    function isFontAwesomeLoaded() {
        const testElement = document.createElement('i');
        testElement.className = 'fa fa-home';
        testElement.style.position = 'absolute';
        testElement.style.left = '-9999px';
        document.body.appendChild(testElement);
        
        const computedStyle = window.getComputedStyle(testElement, ':before');
        const content = computedStyle.getPropertyValue('content');
        
        document.body.removeChild(testElement);
        
        // Se Font Awesome carregou, o content não será 'none' ou vazio
        return content && content !== 'none' && content !== '""';
    }
    
    // Função para aplicar fallback de ícones
    function applyIconFallback() {
        const icons = document.querySelectorAll('.fa, .fas, .far, .fal, .fab');
        
        icons.forEach(icon => {
            // Verifica se o ícone já tem conteúdo visível
            const computedStyle = window.getComputedStyle(icon, ':before');
            const content = computedStyle.getPropertyValue('content');
            
            if (!content || content === 'none' || content === '""') {
                // Procura por classes de ícone conhecidas
                const classList = Array.from(icon.classList);
                let emojiFound = false;
                
                for (const className of classList) {
                    if (iconMap[className]) {
                        icon.textContent = iconMap[className];
                        icon.style.fontFamily = '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
                        icon.style.fontStyle = 'normal';
                        icon.style.fontWeight = 'normal';
                        emojiFound = true;
                        break;
                    }
                }
                
                // Se não encontrou um emoji específico, usa um genérico
                if (!emojiFound && icon.classList.contains('fa')) {
                    icon.textContent = '●';
                    icon.style.fontFamily = 'Arial, sans-serif';
                }
            }
        });
    }
    
    // Função para melhorar ícones existentes
    function enhanceIcons() {
        const icons = document.querySelectorAll('.fa, .fas, .far, .fal, .fab');
        
        icons.forEach(icon => {
            // Adiciona classes para melhor estilização
            icon.style.display = 'inline-block';
            icon.style.textAlign = 'center';
            icon.style.lineHeight = '1';
            icon.style.verticalAlign = 'baseline';
            
            // Garante que emojis sejam coloridos
            if (icon.textContent && /[\u{1F000}-\u{1F9FF}]/u.test(icon.textContent)) {
                icon.style.fontVariantEmoji = 'emoji';
                icon.style.textRendering = 'auto';
            }
        });
    }
    
    // Função para adicionar ícones em elementos específicos
    function addMissingIcons() {
        // Adiciona ícones em links de navegação que não têm
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            const icon = link.querySelector('.fa, .fas, .far, .fal, .fab');
            if (!icon) {
                const newIcon = document.createElement('i');
                newIcon.className = 'fas fa-circle mr-3';
                newIcon.textContent = '●';
                link.insertBefore(newIcon, link.firstChild);
            }
        });
        
        // Adiciona ícones em cards de métricas
        const metricCards = document.querySelectorAll('.metric-card');
        metricCards.forEach((card, index) => {
            const icon = card.querySelector('.fa, .fas, .far, .fal, .fab');
            if (!icon) {
                const iconContainer = card.querySelector('.flex.items-center.justify-between > div:last-child');
                if (iconContainer) {
                    const newIcon = document.createElement('i');
                    const icons = ['🌱', '🗺️', '💰', '✅'];
                    newIcon.textContent = icons[index] || '📊';
                    newIcon.style.fontSize = '1.5em';
                    newIcon.style.fontFamily = '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
                    iconContainer.appendChild(newIcon);
                }
            }
        });
    }
    
    // Função principal de inicialização
    function initIconSystem() {
        // Aguarda um pouco para Font Awesome tentar carregar
        setTimeout(() => {
            if (!isFontAwesomeLoaded()) {
                console.log('Font Awesome não carregou, aplicando fallback...');
                applyIconFallback();
            }
            
            enhanceIcons();
            addMissingIcons();
            
            // Adiciona classe para indicar que o sistema de ícones foi inicializado
            document.body.classList.add('icons-initialized');
        }, 1000);
    }
    
    // Função para reprocessar ícones quando novo conteúdo é adicionado
    function reprocessIcons() {
        applyIconFallback();
        enhanceIcons();
        addMissingIcons();
    }
    
    // Observador para detectar mudanças no DOM
    const observer = new MutationObserver((mutations) => {
        let shouldReprocess = false;
        
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.classList && (node.classList.contains('fa') || node.querySelector('.fa'))) {
                            shouldReprocess = true;
                        }
                    }
                });
            }
        });
        
        if (shouldReprocess) {
            setTimeout(reprocessIcons, 100);
        }
    });
    
    // Inicia o sistema quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initIconSystem);
    } else {
        initIconSystem();
    }
    
    // Inicia o observador
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Expõe funções globalmente para uso manual se necessário
    window.AgTechIcons = {
        reprocess: reprocessIcons,
        applyFallback: applyIconFallback,
        enhance: enhanceIcons
    };
    
})();

