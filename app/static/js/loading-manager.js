// Loading Manager - Sistema de Loading Avançado
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
        border-top: 4px solid var(--color-primary-600);
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      .btn-loading {
        position: relative;
        color: transparent !important;
        pointer-events: none;
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
        color: white;
      }
      
      .fade-out {
        animation: fadeOut 0.3s ease-out forwards;
      }
      
      @keyframes fadeOut {
        from {
          opacity: 1;
          transform: translateY(0);
        }
        to {
          opacity: 0;
          transform: translateY(-10px);
        }
      }
    `;
    document.head.appendChild(styles);
  }
  
  showSkeleton(container, config = {}) {
    const { type = 'card', count = 1, className = '' } = config;
    
    if (typeof container === 'string') {
      container = document.querySelector(container);
    }
    
    if (!container) return;
    
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
    } else if (type === 'list') {
      skeleton.innerHTML = `
        <div class="flex items-center mb-3">
          <div class="skeleton skeleton-avatar mr-3"></div>
          <div class="flex-1">
            <div class="skeleton-text mb-1"></div>
            <div class="skeleton-text" style="width: 70%"></div>
          </div>
        </div>
      `;
    } else if (type === 'table') {
      skeleton.innerHTML = `
        <div class="skeleton-text mb-2" style="height: 2rem;"></div>
        <div class="skeleton-text mb-2" style="height: 2rem;"></div>
        <div class="skeleton-text mb-2" style="height: 2rem;"></div>
      `;
    }
    
    return skeleton;
  }
  
  hideSkeleton(container) {
    if (typeof container === 'string') {
      container = document.querySelector(container);
    }
    
    if (!container) return;
    
    const skeletons = container.querySelectorAll('.skeleton');
    skeletons.forEach(skeleton => {
      skeleton.classList.add('fade-out');
      setTimeout(() => {
        if (skeleton.parentNode) {
          skeleton.remove();
        }
      }, 300);
    });
    
    this.activeLoaders.delete(container);
  }
  
  showOverlay(message = 'Carregando...') {
    // Remove overlay existente
    this.hideOverlay();
    
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'global-loading-overlay';
    overlay.innerHTML = `
      <div class="bg-white p-6 rounded-lg shadow-xl text-center">
        <div class="loading-spinner mx-auto mb-4"></div>
        <p class="text-gray-600">${message}</p>
      </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Fade in
    requestAnimationFrame(() => {
      overlay.style.opacity = '1';
    });
    
    return overlay;
  }
  
  hideOverlay(overlay) {
    if (!overlay) {
      overlay = document.getElementById('global-loading-overlay');
    }
    
    if (overlay && overlay.parentNode) {
      overlay.style.opacity = '0';
      setTimeout(() => {
        if (overlay.parentNode) {
          overlay.remove();
        }
      }, 300);
    }
  }
  
  setButtonLoading(button, isLoading, originalText) {
    if (typeof button === 'string') {
      button = document.querySelector(button);
    }
    
    if (!button) return;
    
    if (isLoading) {
      button.classList.add('btn-loading');
      button.disabled = true;
      if (!button.dataset.originalText) {
        button.dataset.originalText = button.textContent;
      }
      if (originalText) {
        button.textContent = originalText;
      }
    } else {
      button.classList.remove('btn-loading');
      button.disabled = false;
      if (button.dataset.originalText) {
        button.textContent = button.dataset.originalText;
        delete button.dataset.originalText;
      }
    }
  }
  
  // Método para simular carregamento com progresso
  simulateProgress(container, duration = 3000) {
    if (typeof container === 'string') {
      container = document.querySelector(container);
    }
    
    if (!container) return Promise.resolve();
    
    return new Promise((resolve) => {
      const progressBar = document.createElement('div');
      progressBar.className = 'progress mb-4';
      progressBar.innerHTML = '<div class="progress-bar" style="width: 0%"></div>';
      
      container.innerHTML = '';
      container.appendChild(progressBar);
      
      const bar = progressBar.querySelector('.progress-bar');
      let progress = 0;
      const interval = duration / 100;
      
      const timer = setInterval(() => {
        progress += Math.random() * 3;
        if (progress >= 100) {
          progress = 100;
          clearInterval(timer);
          setTimeout(() => {
            resolve();
          }, 200);
        }
        bar.style.width = `${progress}%`;
      }, interval);
    });
  }
  
  // Método para loading com retry
  withRetry(asyncFunction, maxRetries = 3, retryDelay = 1000) {
    return new Promise(async (resolve, reject) => {
      let attempts = 0;
      
      const attempt = async () => {
        try {
          attempts++;
          const result = await asyncFunction();
          resolve(result);
        } catch (error) {
          if (attempts < maxRetries) {
            setTimeout(attempt, retryDelay);
          } else {
            reject(error);
          }
        }
      };
      
      attempt();
    });
  }
  
  // Cleanup method
  cleanup() {
    this.activeLoaders.forEach(container => {
      this.hideSkeleton(container);
    });
    this.hideOverlay();
  }
}

// Instância global
window.LoadingManager = new LoadingManager();

// Auto cleanup on page unload
window.addEventListener('beforeunload', () => {
  window.LoadingManager.cleanup();
});

