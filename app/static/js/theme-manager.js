// Theme Manager - Dark Mode Support
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
      toggle.style.marginRight = '1rem';
      
      // Adicionar ao header
      const headerActions = document.querySelector('.app-header .flex .space-x-4');
      if (headerActions) {
        headerActions.insertBefore(toggle, headerActions.firstChild);
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
    
    // Trigger custom event
    window.dispatchEvent(new CustomEvent('themeChanged', {
      detail: { theme: this.currentTheme }
    }));
  }
  
  applyTheme() {
    document.documentElement.classList.toggle('dark', this.currentTheme === 'dark');
    
    // Atualizar meta theme-color
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (!metaThemeColor) {
      metaThemeColor = document.createElement('meta');
      metaThemeColor.name = 'theme-color';
      document.head.appendChild(metaThemeColor);
    }
    metaThemeColor.content = this.currentTheme === 'dark' ? '#0f172a' : '#ffffff';
    
    this.updateToggleButton();
  }
  
  updateToggleButton() {
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      const icon = toggle.querySelector('i');
      if (icon) {
        icon.className = this.currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
      }
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

