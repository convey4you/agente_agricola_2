# 📊 PROMPT CRÍTICO 3: CORREÇÃO DA INTEGRAÇÃO DASHBOARD FRONTEND

**Prioridade:** ALTA (48 horas)  
**Dependência:** PROMPT 2 (API de alertas) deve estar completo  
**Objetivo:** Dashboard carregando alertas corretamente

---

## 📋 CONTEXTO COMPLETO PARA CLAUDE SONNET 4

### Situação Atual
Você é um desenvolvedor frontend especializado em JavaScript/AJAX trabalhando no **AgroTech Portugal**. A API de alertas foi corrigida e está funcionando, mas o dashboard ainda mostra "Carregando alertas..." indefinidamente. A integração entre frontend e backend precisa ser corrigida.

### Problema Identificado
- Dashboard mostra "Carregando alertas..." sem nunca carregar
- Possível problema na chamada AJAX/fetch
- Tratamento de erro inadequado ou ausente
- Loading state não sendo removido
- Possível problema de autenticação nas chamadas

### Arquitetura Frontend
- **HTML/CSS/JavaScript** vanilla ou com framework mínimo
- **Autenticação:** Session-based (Flask-Login)
- **API:** REST endpoints corrigidos no PROMPT 2
- **Formato:** JSON responses

---

## 🎯 ANÁLISE DO PROBLEMA ATUAL

### Estado Atual do Dashboard
Com base na validação, o dashboard está:
- ✅ Carregando a página principal
- ✅ Mostrando interface básica
- ❌ Ficando em "Carregando alertas..." indefinidamente
- ❌ Não exibindo alertas reais
- ❌ Sem tratamento de erro visível

### Possíveis Causas
1. **Chamada AJAX incorreta** para `/api/alerts/`
2. **Autenticação não sendo enviada** (cookies/session)
3. **Parsing de JSON falhando**
4. **Tratamento de erro inadequado**
5. **Loading state não sendo removido**
6. **CORS ou outras questões de rede**

---

## 📝 ESTRUTURA HTML ESPERADA

### HTML Base do Dashboard
```html
<!-- Seção de Alertas no Dashboard -->
<div class="dashboard-section" id="alerts-section">
    <div class="section-header">
        <h3>Alertas Recentes</h3>
        <div class="section-actions">
            <button id="refresh-alerts" class="btn btn-sm btn-outline">
                <i class="icon-refresh"></i> Atualizar
            </button>
            <span id="alerts-count" class="badge badge-warning" style="display: none;">0</span>
        </div>
    </div>
    
    <div class="section-content">
        <!-- Loading State -->
        <div id="alerts-loading" class="loading-state">
            <div class="spinner"></div>
            <span>Carregando alertas...</span>
        </div>
        
        <!-- Container de Alertas -->
        <div id="alerts-container" class="alerts-container" style="display: none;">
            <!-- Alertas serão inseridos aqui dinamicamente -->
        </div>
        
        <!-- Estado Vazio -->
        <div id="alerts-empty" class="empty-state" style="display: none;">
            <div class="empty-icon">
                <i class="icon-bell-off"></i>
            </div>
            <h4>Nenhum alerta no momento</h4>
            <p>Você será notificado quando houver alertas importantes para suas culturas.</p>
            <button id="create-test-alert" class="btn btn-primary">
                Criar Alerta de Teste
            </button>
        </div>
        
        <!-- Estado de Erro -->
        <div id="alerts-error" class="error-state" style="display: none;">
            <div class="error-icon">
                <i class="icon-alert-triangle"></i>
            </div>
            <h4>Erro ao carregar alertas</h4>
            <p id="error-message">Ocorreu um erro ao carregar os alertas. Tente novamente.</p>
            <button id="retry-alerts" class="btn btn-outline">
                Tentar Novamente
            </button>
        </div>
    </div>
</div>
```

### CSS para Estados
```css
/* Estados de Loading, Empty e Error */
.loading-state, .empty-state, .error-state {
    text-align: center;
    padding: 2rem;
    color: #6b7280;
}

.loading-state .spinner {
    width: 2rem;
    height: 2rem;
    border: 2px solid #e5e7eb;
    border-top: 2px solid #10b981;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.alerts-container {
    max-height: 400px;
    overflow-y: auto;
}

.alert-item {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    transition: all 0.2s;
}

.alert-item:hover {
    background: #f3f4f6;
    border-color: #d1d5db;
}

.alert-item.priority-critical {
    border-left: 4px solid #ef4444;
}

.alert-item.priority-high {
    border-left: 4px solid #f59e0b;
}

.alert-item.priority-medium {
    border-left: 4px solid #3b82f6;
}

.alert-item.priority-low {
    border-left: 4px solid #10b981;
}

.alert-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
}

.alert-title {
    font-weight: 600;
    color: #111827;
    margin: 0;
}

.alert-meta {
    display: flex;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: #6b7280;
}

.alert-message {
    color: #374151;
    margin: 0.5rem 0;
    line-height: 1.5;
}

.alert-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.75rem;
}

.alert-actions button {
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    border-radius: 4px;
    border: 1px solid #d1d5db;
    background: white;
    color: #374151;
    cursor: pointer;
    transition: all 0.2s;
}

.alert-actions button:hover {
    background: #f9fafb;
    border-color: #9ca3af;
}

.alert-actions .btn-primary {
    background: #10b981;
    color: white;
    border-color: #10b981;
}

.alert-actions .btn-primary:hover {
    background: #059669;
    border-color: #059669;
}
```

---

## 📝 JAVASCRIPT PARA CARREGAMENTO DE ALERTAS

### Classe Principal AlertsManager
```javascript
class AlertsManager {
    constructor() {
        this.apiBaseUrl = '/api/alerts';
        this.refreshInterval = null;
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        // Inicializar elementos DOM
        this.elements = {
            loading: document.getElementById('alerts-loading'),
            container: document.getElementById('alerts-container'),
            empty: document.getElementById('alerts-empty'),
            error: document.getElementById('alerts-error'),
            errorMessage: document.getElementById('error-message'),
            count: document.getElementById('alerts-count'),
            refreshBtn: document.getElementById('refresh-alerts'),
            retryBtn: document.getElementById('retry-alerts'),
            createTestBtn: document.getElementById('create-test-alert')
        };
        
        // Bind event listeners
        this.bindEvents();
        
        // Carregar alertas inicialmente
        this.loadAlerts();
        
        // Auto-refresh a cada 5 minutos
        this.startAutoRefresh();
    }
    
    bindEvents() {
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.addEventListener('click', () => {
                this.loadAlerts(true); // Force refresh
            });
        }
        
        if (this.elements.retryBtn) {
            this.elements.retryBtn.addEventListener('click', () => {
                this.loadAlerts();
            });
        }
        
        if (this.elements.createTestBtn) {
            this.elements.createTestBtn.addEventListener('click', () => {
                this.createTestAlert();
            });
        }
    }
    
    async loadAlerts(forceRefresh = false) {
        if (this.isLoading && !forceRefresh) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin' // Importante para enviar cookies de sessão
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayAlerts(data.data.alerts);
                this.updateCount(data.data.total);
                console.log(`Carregados ${data.data.alerts.length} alertas`);
            } else {
                throw new Error(data.message || 'Erro desconhecido na API');
            }
            
        } catch (error) {
            console.error('Erro ao carregar alertas:', error);
            this.showError(error.message);
        } finally {
            this.isLoading = false;
        }
    }
    
    displayAlerts(alerts) {
        if (!alerts || alerts.length === 0) {
            this.showEmpty();
            return;
        }
        
        const container = this.elements.container;
        container.innerHTML = '';
        
        alerts.forEach(alert => {
            const alertElement = this.createAlertElement(alert);
            container.appendChild(alertElement);
        });
        
        this.showContainer();
    }
    
    createAlertElement(alert) {
        const div = document.createElement('div');
        div.className = `alert-item priority-${alert.priority}`;
        div.dataset.alertId = alert.id;
        
        const createdAt = new Date(alert.created_at).toLocaleString('pt-PT');
        const isRead = alert.status === 'READ';
        const isDismissed = alert.status === 'DISMISSED';
        
        div.innerHTML = `
            <div class="alert-header">
                <h4 class="alert-title">${this.escapeHtml(alert.title)}</h4>
                <div class="alert-meta">
                    <span class="alert-type">${this.getTypeLabel(alert.type)}</span>
                    <span class="alert-priority priority-${alert.priority}">${this.getPriorityLabel(alert.priority)}</span>
                    <span class="alert-date">${createdAt}</span>
                </div>
            </div>
            <div class="alert-message">${this.escapeHtml(alert.message)}</div>
            <div class="alert-actions">
                ${!isRead && !isDismissed ? `
                    <button class="btn-mark-read" data-alert-id="${alert.id}">
                        Marcar como Lido
                    </button>
                ` : ''}
                ${!isDismissed ? `
                    <button class="btn-dismiss" data-alert-id="${alert.id}">
                        Dispensar
                    </button>
                ` : ''}
                ${alert.action_url ? `
                    <button class="btn-primary btn-action" onclick="window.open('${alert.action_url}', '_blank')">
                        ${alert.action_text || 'Ver Detalhes'}
                    </button>
                ` : ''}
            </div>
        `;
        
        // Bind action buttons
        this.bindAlertActions(div);
        
        return div;
    }
    
    bindAlertActions(alertElement) {
        const markReadBtn = alertElement.querySelector('.btn-mark-read');
        const dismissBtn = alertElement.querySelector('.btn-dismiss');
        
        if (markReadBtn) {
            markReadBtn.addEventListener('click', async (e) => {
                const alertId = e.target.dataset.alertId;
                await this.markAlertRead(alertId);
            });
        }
        
        if (dismissBtn) {
            dismissBtn.addEventListener('click', async (e) => {
                const alertId = e.target.dataset.alertId;
                await this.dismissAlert(alertId);
            });
        }
    }
    
    async markAlertRead(alertId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/${alertId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // Recarregar alertas para atualizar interface
                this.loadAlerts();
            } else {
                throw new Error('Erro ao marcar alerta como lido');
            }
            
        } catch (error) {
            console.error('Erro ao marcar alerta como lido:', error);
            alert('Erro ao marcar alerta como lido. Tente novamente.');
        }
    }
    
    async dismissAlert(alertId) {
        if (!confirm('Tem certeza que deseja dispensar este alerta?')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/${alertId}/dismiss`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // Recarregar alertas para atualizar interface
                this.loadAlerts();
            } else {
                throw new Error('Erro ao dispensar alerta');
            }
            
        } catch (error) {
            console.error('Erro ao dispensar alerta:', error);
            alert('Erro ao dispensar alerta. Tente novamente.');
        }
    }
    
    async createTestAlert() {
        try {
            const testAlert = {
                type: 'general',
                priority: 'medium',
                title: 'Alerta de Teste - Dashboard',
                message: 'Este é um alerta de teste criado para validar a integração do dashboard.'
            };
            
            const response = await fetch(`${this.apiBaseUrl}/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify(testAlert)
            });
            
            if (response.ok) {
                // Recarregar alertas para mostrar o novo
                this.loadAlerts();
            } else {
                throw new Error('Erro ao criar alerta de teste');
            }
            
        } catch (error) {
            console.error('Erro ao criar alerta de teste:', error);
            alert('Erro ao criar alerta de teste. Tente novamente.');
        }
    }
    
    // Métodos de controle de estado da UI
    showLoading() {
        this.hideAllStates();
        this.elements.loading.style.display = 'block';
    }
    
    showContainer() {
        this.hideAllStates();
        this.elements.container.style.display = 'block';
    }
    
    showEmpty() {
        this.hideAllStates();
        this.elements.empty.style.display = 'block';
    }
    
    showError(message) {
        this.hideAllStates();
        this.elements.errorMessage.textContent = message;
        this.elements.error.style.display = 'block';
    }
    
    hideAllStates() {
        this.elements.loading.style.display = 'none';
        this.elements.container.style.display = 'none';
        this.elements.empty.style.display = 'none';
        this.elements.error.style.display = 'none';
    }
    
    updateCount(count) {
        if (this.elements.count) {
            if (count > 0) {
                this.elements.count.textContent = count;
                this.elements.count.style.display = 'inline';
            } else {
                this.elements.count.style.display = 'none';
            }
        }
    }
    
    startAutoRefresh() {
        // Refresh a cada 5 minutos
        this.refreshInterval = setInterval(() => {
            this.loadAlerts();
        }, 5 * 60 * 1000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    // Métodos utilitários
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    getTypeLabel(type) {
        const labels = {
            weather: 'Clima',
            pest: 'Pragas',
            disease: 'Doenças',
            irrigation: 'Irrigação',
            fertilization: 'Adubação',
            harvest: 'Colheita',
            pruning: 'Poda',
            market: 'Mercado',
            general: 'Geral'
        };
        return labels[type] || type;
    }
    
    getPriorityLabel(priority) {
        const labels = {
            low: 'Baixa',
            medium: 'Média',
            high: 'Alta',
            critical: 'Crítica'
        };
        return labels[priority] || priority;
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se estamos na página do dashboard
    if (document.getElementById('alerts-section')) {
        window.alertsManager = new AlertsManager();
    }
});

// Cleanup quando sair da página
window.addEventListener('beforeunload', function() {
    if (window.alertsManager) {
        window.alertsManager.stopAutoRefresh();
    }
});
```

---

## 🧪 TESTES E VALIDAÇÃO

### Script de Teste Manual
Criar `scripts/test_dashboard_integration.js`:

```javascript
// Script para testar integração do dashboard via console do browser

class DashboardTester {
    constructor() {
        this.tests = [];
        this.results = [];
    }
    
    async runAllTests() {
        console.log('🧪 Iniciando testes de integração do dashboard...');
        
        await this.testAPIConnection();
        await this.testAlertLoading();
        await this.testAlertCreation();
        await this.testAlertActions();
        await this.testErrorHandling();
        
        this.printResults();
    }
    
    async testAPIConnection() {
        console.log('📡 Testando conexão com API...');
        
        try {
            const response = await fetch('/api/alerts/', {
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                console.log('✅ Conexão com API funcionando');
                this.results.push({ test: 'API Connection', status: 'PASS' });
            } else {
                console.log('❌ Erro na conexão com API:', response.status);
                this.results.push({ test: 'API Connection', status: 'FAIL', error: response.status });
            }
        } catch (error) {
            console.log('❌ Erro na conexão:', error);
            this.results.push({ test: 'API Connection', status: 'ERROR', error: error.message });
        }
    }
    
    async testAlertLoading() {
        console.log('📋 Testando carregamento de alertas...');
        
        if (window.alertsManager) {
            try {
                await window.alertsManager.loadAlerts();
                console.log('✅ Carregamento de alertas funcionando');
                this.results.push({ test: 'Alert Loading', status: 'PASS' });
            } catch (error) {
                console.log('❌ Erro no carregamento:', error);
                this.results.push({ test: 'Alert Loading', status: 'ERROR', error: error.message });
            }
        } else {
            console.log('❌ AlertsManager não encontrado');
            this.results.push({ test: 'Alert Loading', status: 'FAIL', error: 'AlertsManager not found' });
        }
    }
    
    async testAlertCreation() {
        console.log('➕ Testando criação de alerta...');
        
        if (window.alertsManager) {
            try {
                await window.alertsManager.createTestAlert();
                console.log('✅ Criação de alerta funcionando');
                this.results.push({ test: 'Alert Creation', status: 'PASS' });
            } catch (error) {
                console.log('❌ Erro na criação:', error);
                this.results.push({ test: 'Alert Creation', status: 'ERROR', error: error.message });
            }
        } else {
            this.results.push({ test: 'Alert Creation', status: 'SKIP', error: 'AlertsManager not found' });
        }
    }
    
    async testAlertActions() {
        console.log('🔄 Testando ações de alerta...');
        
        const alertItems = document.querySelectorAll('.alert-item');
        if (alertItems.length > 0) {
            console.log(`✅ ${alertItems.length} alertas encontrados na interface`);
            this.results.push({ test: 'Alert Actions', status: 'PASS' });
        } else {
            console.log('⚠️ Nenhum alerta encontrado na interface');
            this.results.push({ test: 'Alert Actions', status: 'SKIP', error: 'No alerts found' });
        }
    }
    
    async testErrorHandling() {
        console.log('🚨 Testando tratamento de erros...');
        
        try {
            // Testar endpoint inexistente
            const response = await fetch('/api/alerts/nonexistent', {
                credentials: 'same-origin'
            });
            
            if (response.status === 404) {
                console.log('✅ Tratamento de erro 404 funcionando');
                this.results.push({ test: 'Error Handling', status: 'PASS' });
            } else {
                console.log('⚠️ Resposta inesperada para endpoint inexistente');
                this.results.push({ test: 'Error Handling', status: 'PARTIAL' });
            }
        } catch (error) {
            console.log('✅ Erro capturado corretamente:', error.message);
            this.results.push({ test: 'Error Handling', status: 'PASS' });
        }
    }
    
    printResults() {
        console.log('\n📊 RESULTADOS DOS TESTES:');
        console.log('========================');
        
        this.results.forEach(result => {
            const icon = result.status === 'PASS' ? '✅' : 
                        result.status === 'FAIL' ? '❌' : 
                        result.status === 'ERROR' ? '💥' : '⚠️';
            
            console.log(`${icon} ${result.test}: ${result.status}`);
            if (result.error) {
                console.log(`   Erro: ${result.error}`);
            }
        });
        
        const passed = this.results.filter(r => r.status === 'PASS').length;
        const total = this.results.length;
        
        console.log(`\n📈 Score: ${passed}/${total} (${Math.round(passed/total*100)}%)`);
    }
}

// Para executar no console:
// const tester = new DashboardTester();
// tester.runAllTests();
```

---

## 📋 ENTREGÁVEIS OBRIGATÓRIOS

### 1. HTML Atualizado
- Estrutura completa da seção de alertas
- Estados de loading, empty, error
- Elementos para interação

### 2. CSS Responsivo
- Estilos para todos os estados
- Design responsivo para mobile
- Indicadores visuais de prioridade
- Animações suaves

### 3. JavaScript Funcional
- Classe AlertsManager completa
- Carregamento automático de alertas
- Ações de marcar como lido/dispensar
- Tratamento robusto de erros
- Auto-refresh periódico

### 4. Testes de Integração
- Script de teste manual
- Validação de todos os fluxos
- Verificação de estados da UI

---

## ✅ CRITÉRIOS DE VALIDAÇÃO

### Validação Visual
1. **Loading State:** Spinner aparece durante carregamento
2. **Alertas Carregados:** Lista de alertas exibida corretamente
3. **Estado Vazio:** Mensagem apropriada quando não há alertas
4. **Estado de Erro:** Mensagem de erro clara e botão de retry

### Validação Funcional
1. **Carregamento Inicial:** Alertas carregam automaticamente
2. **Refresh Manual:** Botão de atualizar funciona
3. **Ações de Alerta:** Marcar como lido e dispensar funcionam
4. **Criação de Teste:** Botão de criar alerta de teste funciona
5. **Auto-refresh:** Alertas atualizam automaticamente

### Validação Técnica
1. **Chamadas AJAX:** Requests corretos para API
2. **Autenticação:** Cookies de sessão enviados
3. **Tratamento de Erro:** Erros capturados e exibidos
4. **Performance:** Carregamento rápido e responsivo

### Critérios de Sucesso
- [ ] Dashboard carrega alertas em < 2 segundos
- [ ] Todos os estados da UI funcionam
- [ ] Ações de alerta funcionam corretamente
- [ ] Tratamento de erro robusto
- [ ] Interface responsiva e acessível

---

**Ferramentas:** VS Code + GitHub Copilot  
**Prazo:** 48 horas  
**Dependência:** PROMPT 2 (API) completo  
**Validação:** Testes visuais + funcionais + Gerente de Tecnologia

