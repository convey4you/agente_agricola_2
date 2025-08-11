# 📱 Documentação Frontend - Sistema de Alertas

**Versão**: 2.0 (Sprint 2)  
**Última Atualização**: 2025-08-10  
**Status**: ✅ Totalmente Funcional

---

## 🎯 VISÃO GERAL

O frontend de alertas consiste em dois componentes principais:
1. **Widget do Dashboard** - Visão resumida integrada ao dashboard
2. **Página de Alertas** - Interface completa para gestão

---

## 🏠 WIDGET DO DASHBOARD

### **Localização**: Dashboard principal (`/`)
### **Arquivo**: `app/static/js/alerts-manager.js`
### **Template**: Integrado em `app/templates/dashboard/index.html`

### **Funcionalidades:**
- ✅ **Estatísticas em tempo real** (total, não lidos, críticos)
- ✅ **Lista de alertas críticos** (máximo 3)
- ✅ **Lista de alertas recentes** (máximo 5)
- ✅ **Ícones de ação funcionais** (marcar como lido, resolver)
- ✅ **Auto-refresh** a cada 2 minutos
- ✅ **Geração de novos alertas** (botão 🔄)

### **APIs Utilizadas:**
```javascript
// Carregamento do widget
GET /api/alerts/widget

// Marcar como lido
POST /api/alerts/{id}/read

// Resolver alerta
POST /api/alerts/{id}/dismiss

// Gerar novos alertas
POST /api/alerts/generate
```

### **Estrutura de Dados:**
```javascript
{
  "success": true,
  "data": {
    "stats": {
      "total": 15,      // Total de alertas
      "unread": 3,      // Não lidos (pending/sent)
      "critical": 1     // Críticos ativos
    },
    "critical_alerts": [...],  // Array de alertas críticos
    "recent_alerts": [...]     // Array de alertas recentes
  }
}
```

---

## 📋 PÁGINA DE ALERTAS

### **Localização**: `/alerts/`
### **Template**: `app/templates/alerts/index.html`
### **JavaScript**: Integrado no template

### **Funcionalidades:**
- ✅ **Estatísticas detalhadas** por prioridade
- ✅ **Lista completa de alertas** com paginação
- ✅ **Filtros avançados** (tipo, prioridade, status)
- ✅ **Busca textual** em tempo real
- ✅ **Ações em lote** (marcar todos como lidos)
- ✅ **Geração de alertas** com feedback visual

### **Filtros Disponíveis:**
```html
<!-- Tipo de Alerta -->
<select id="typeFilter">
  <option value="weather">Meteorológico</option>
  <option value="culture">Cultura</option>
  <option value="pest">Praga</option>
  <option value="irrigation">Irrigação</option>
  <option value="harvest">Colheita</option>
</select>

<!-- Prioridade -->
<select id="priorityFilter">
  <option value="critical">Crítica</option>
  <option value="high">Alta</option>
  <option value="medium">Média</option>
  <option value="low">Baixa</option>
</select>

<!-- Status -->
<select id="statusFilter">
  <option value="pending">Pendente</option>
  <option value="sent">Enviado</option>
  <option value="read">Lido</option>
  <option value="resolved">Resolvido</option>
  <option value="dismissed">Dispensado</option>
</select>
```

### **Estados dos Alertas:**
```javascript
// Lógica de exibição de botões
if (alert.status.value in ['pending', 'sent']) {
  // Mostrar: "Marcar como lido" + "Resolver"
} else if (alert.status.value == 'read') {
  // Mostrar apenas: "Resolver"  
} else {
  // Mostrar: "Resolvido" (badge)
}
```

---

## 🔐 AUTENTICAÇÃO E SEGURANÇA

### **Token CSRF:**
```javascript
// Definido em ambas as páginas
window.csrfToken = '{{ csrf_token() }}';

// Usado em todas as requisições POST
headers: {
  'Content-Type': 'application/json',
  'X-CSRF-Token': window.csrfToken,
  'X-Requested-With': 'XMLHttpRequest'
},
credentials: 'same-origin'
```

### **Validação de Sessão:**
- ✅ Todas as APIs verificam `@login_required`
- ✅ Alertas filtrados por `user_id` automaticamente
- ✅ Erro 401 tratado com redirecionamento para login

---

## 🎨 INTERFACE VISUAL

### **Ícones e Cores:**
```css
/* Prioridades */
.critical { color: #dc3545; }    /* Vermelho */
.high     { color: #fd7e14; }    /* Laranja */
.medium   { color: #0dcaf0; }    /* Azul */
.low      { color: #198754; }    /* Verde */

/* Ações */
.alert-mark-read  { color: #0d6efd; }  /* Azul - Olho */
.alert-resolve    { color: #198754; }  /* Verde - Check */
.alert-generate   { color: #198754; }  /* Verde - Sync */
```

### **Ícones FontAwesome:**
```html
<!-- Ações -->
<i class="fas fa-eye"></i>        <!-- Marcar como lido -->
<i class="fas fa-check"></i>      <!-- Resolver -->
<i class="fas fa-sync-alt"></i>   <!-- Gerar/Atualizar -->

<!-- Tipos de Alerta -->
<i class="fas fa-cloud-sun"></i>   <!-- Clima -->
<i class="fas fa-tint"></i>        <!-- Irrigação -->
<i class="fas fa-bug"></i>         <!-- Praga -->
<i class="fas fa-carrot"></i>      <!-- Colheita -->
```

---

## 🔄 FLUXO DE INTERAÇÃO

### **1. Carregamento Inicial:**
```javascript
// AlertsManager auto-inicializa
document.addEventListener('DOMContentLoaded', function() {
  if (document.querySelector('.dashboard-grid')) {
    window.alertsManager = new AlertsManager();
  }
});
```

### **2. Ações do Usuário:**
```javascript
// Clique em ícone detectado
document.addEventListener('click', (e) => {
  // Verifica se clique foi no ícone ou botão
  let button = e.target.tagName === 'I' ? 
    e.target.closest('button') : e.target;
    
  if (button.matches('.alert-mark-read')) {
    this.markAsRead(button.dataset.alertId);
  }
});
```

### **3. Atualização da Interface:**
```javascript
// Após sucesso na API
if (data.status === 'success') {
  this.refreshAlerts();  // Recarrega lista
  this.updateNotificationBadge(newCount);
}
```

---

## 🐛 TRATAMENTO DE ERROS

### **Códigos de Erro Tratados:**
```javascript
// 401 - Não autenticado
if (response.status === 401) {
  window.location.href = '/auth/login';
}

// 403 - Token CSRF inválido
if (response.status === 403) {
  console.error('Token CSRF inválido');
  this.showNotification('Erro de autenticação', 'error');
}

// 404 - Alerta não encontrado
if (response.status === 404) {
  this.showNotification('Alerta não encontrado', 'error');
}
```

### **Feedback Visual:**
```javascript
// Toast notifications
this.showNotification(message, type); // success, error, info, warning

// Loading states
button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
button.disabled = true;
```

---

## 📱 RESPONSIVIDADE

### **Breakpoints:**
- ✅ **Desktop** (>= 1024px): Layout completo
- ✅ **Tablet** (768px - 1023px): Layout condensado
- ✅ **Mobile** (< 768px): Layout empilhado

### **Adaptações Mobile:**
- Botões maiores para touch
- Filtros em accordions
- Lista simplificada
- Scroll infinito

---

## 🧪 TESTING

### **Casos de Teste Frontend:**
1. **Carregamento inicial** do widget
2. **Clique nos ícones** de ação
3. **Filtros** funcionando
4. **Auto-refresh** ativo
5. **Geração de alertas** com feedback
6. **Tratamento de erros** de rede
7. **Responsividade** em diferentes telas

### **Comandos de Debug:**
```javascript
// Console do navegador
window.alertsManager.loadAlertsWidget();  // Recarregar widget
window.alertsManager.refreshAlerts();     // Refresh manual
console.log(window.csrfToken);            // Verificar CSRF
```

---

## 📋 CHECKLIST DE VALIDAÇÃO

### ✅ **Widget do Dashboard:**
- [x] Carrega estatísticas corretamente
- [x] Mostra alertas críticos
- [x] Mostra alertas recentes  
- [x] Ícones funcionam (marcar lido/resolver)
- [x] Auto-refresh ativo
- [x] Token CSRF configurado

### ✅ **Página de Alertas:**
- [x] Lista todos os alertas
- [x] Filtros funcionam
- [x] Busca textual funciona
- [x] Botões de ação funcionam
- [x] Geração de alertas funciona
- [x] Feedback visual adequado

### ✅ **Integração API:**
- [x] Endpoints corretos
- [x] Headers de autenticação
- [x] Tratamento de erros
- [x] Resposta JSON válida

---

## 🚀 PRÓXIMAS MELHORIAS

### **V2.1 Planejadas:**
- 🔔 **Notificações push** do navegador
- 📊 **Gráficos de tendência** de alertas
- 🔍 **Busca avançada** com filtros múltiplos
- 📱 **PWA support** para mobile
- ⚡ **WebSocket** para updates em tempo real

**Status Frontend**: ✅ **100% Funcional e Documentado**
