# 📚 Documentação da API de Alertas - AgroTech Portugal

## 🎯 Visão Geral

A API de Alertas fornece endpoints REST para gerenciar alertas inteligentes do sistema agrícola. Permite criar, listar, marcar como lido e dispensar alertas de forma programática.

**Base URL**: `/api/alerts`  
**Autenticação**: Session-based (Flask-Login)  
**Formato**: JSON  
**Versão**: 2.0 (SPRINT 2)

---

## 🔐 Autenticação

Todos os endpoints (exceto `/health`) requerem autenticação. O usuário deve estar logado via sessão Flask.

**Headers Obrigatórios:**
```
Content-Type: application/json
```

**Resposta de Erro (401):**
```json
{
  "status": "error",
  "message": "Usuário não autenticado",
  "error_code": "AUTH_ERROR",
  "timestamp": "2025-08-01T15:30:00Z"
}
```

---

## 📋 Estrutura de Resposta Padrão

### ✅ Sucesso
```json
{
  "status": "success",
  "message": "Operação realizada com sucesso",
  "data": { ... },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

### ❌ Erro
```json
{
  "status": "error",
  "message": "Descrição amigável do erro",
  "error_code": "VALIDATION_ERROR|AUTH_ERROR|NOT_FOUND|SERVER_ERROR",
  "details": { ... },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

---

## 📡 Endpoints

### 1. 📋 **GET /api/alerts/**
Lista alertas do usuário autenticado com suporte a filtros e paginação.

#### **Query Parameters:**
- `limit` (int, opcional): Número máximo de alertas (padrão: 50, máximo: 100)
- `offset` (int, opcional): Offset para paginação (padrão: 0)
- `status` (string, opcional): Filtrar por status (`pending`, `sent`, `read`, `dismissed`, `expired`)
- `type` (string, opcional): Filtrar por tipo (`weather`, `pest`, `disease`, `irrigation`, `fertilization`, `harvest`, `pruning`, `market`, `general`)
- `priority` (string, opcional): Filtrar por prioridade (`low`, `medium`, `high`, `critical`)

#### **Resposta de Sucesso (200):**
```json
{
  "status": "success",
  "data": {
    "alerts": [
      {
        "id": 123,
        "type": "weather",
        "priority": "high",
        "status": "pending",
        "title": "Chuva Forte Prevista",
        "message": "Chuva intensa prevista para as próximas 6 horas",
        "action_text": "Ver Previsão",
        "action_url": "/weather/forecast",
        "culture_id": 456,
        "created_at": "2025-08-01T10:00:00Z",
        "scheduled_for": null,
        "expires_at": "2025-08-02T10:00:00Z",
        "sent_at": null,
        "read_at": null,
        "alert_metadata": {}
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0,
    "has_more": false
  },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

#### **Exemplos de Uso:**
```bash
# Listar todos os alertas
curl -X GET "https://api.agrotech.pt/api/alerts/"

# Alertas não lidos
curl -X GET "https://api.agrotech.pt/api/alerts/?status=pending"

# Alertas de clima de alta prioridade
curl -X GET "https://api.agrotech.pt/api/alerts/?type=weather&priority=high"

# Paginação (5 alertas, começando do 10º)
curl -X GET "https://api.agrotech.pt/api/alerts/?limit=5&offset=10"
```

---

### 2. ➕ **POST /api/alerts/create**
Cria um novo alerta para o usuário autenticado.

#### **Request Body (JSON):**
```json
{
  "type": "weather",                    // Obrigatório
  "priority": "high",                   // Obrigatório
  "title": "Título do alerta",          // Obrigatório (máx 200 chars)
  "message": "Mensagem detalhada",      // Obrigatório (máx 5000 chars)
  "action_text": "Texto do botão",     // Opcional (máx 100 chars)
  "action_url": "/url/da/acao",        // Opcional (máx 500 chars)
  "culture_id": 123,                   // Opcional (deve pertencer ao usuário)
  "scheduled_for": "2025-08-01T15:30:00Z", // Opcional (ISO 8601)
  "expires_at": "2025-08-02T15:30:00Z"     // Opcional (ISO 8601)
}
```

#### **Tipos Válidos:**
- `weather` - Alertas climáticos
- `pest` - Pragas
- `disease` - Doenças
- `irrigation` - Irrigação
- `fertilization` - Adubação
- `harvest` - Colheita
- `pruning` - Poda
- `market` - Oportunidades de mercado
- `general` - Alertas gerais

#### **Prioridades Válidas:**
- `low` - Baixa
- `medium` - Média
- `high` - Alta
- `critical` - Crítica

#### **Resposta de Sucesso (201):**
```json
{
  "status": "success",
  "message": "Alerta criado com sucesso",
  "data": {
    "alert": {
      "id": 124,
      "type": "weather",
      "priority": "high",
      "status": "pending",
      "title": "Título do alerta",
      "message": "Mensagem detalhada",
      "action_text": "Texto do botão",
      "action_url": "/url/da/acao",
      "culture_id": 123,
      "created_at": "2025-08-01T15:30:00Z",
      "scheduled_for": "2025-08-01T15:30:00Z",
      "expires_at": "2025-08-02T15:30:00Z",
      "sent_at": null,
      "read_at": null,
      "alert_metadata": {}
    }
  },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

#### **Resposta de Erro (400):**
```json
{
  "status": "error",
  "message": "Dados inválidos fornecidos",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "errors": [
      "Campo 'title' é obrigatório",
      "Tipo deve ser um de: weather, pest, disease, irrigation, fertilization, harvest, pruning, market, general"
    ]
  },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

#### **Exemplo de Uso:**
```bash
curl -X POST "https://api.agrotech.pt/api/alerts/create" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "irrigation",
    "priority": "medium",
    "title": "Irrigação Necessária",
    "message": "As plantas de tomate precisam de água",
    "action_text": "Irrigar Agora",
    "culture_id": 456
  }'
```

---

### 3. 👁️ **POST /api/alerts/{id}/read**
Marca um alerta como lido.

#### **Path Parameters:**
- `id` (int): ID do alerta

#### **Resposta de Sucesso (200):**
```json
{
  "status": "success",
  "message": "Alerta marcado como lido",
  "data": {
    "alert": {
      "id": 123,
      "status": "read",
      "read_at": "2025-08-01T15:30:00Z",
      // ... outros campos
    }
  },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

#### **Resposta se Já Lido (200):**
```json
{
  "status": "success",
  "message": "Alerta já estava marcado como lido",
  "data": { ... },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

#### **Resposta de Erro (404):**
```json
{
  "status": "error",
  "message": "Alerta não encontrado",
  "error_code": "NOT_FOUND",
  "timestamp": "2025-08-01T15:30:00Z"
}
```

#### **Exemplo de Uso:**
```bash
curl -X POST "https://api.agrotech.pt/api/alerts/123/read"
```

---

### 4. 🗑️ **POST /api/alerts/{id}/dismiss**
Dispensa um alerta (marca como não relevante).

#### **Path Parameters:**
- `id` (int): ID do alerta

#### **Resposta de Sucesso (200):**
```json
{
  "status": "success",
  "message": "Alerta dispensado",
  "data": {
    "alert": {
      "id": 123,
      "status": "dismissed",
      "dismissed_at": "2025-08-01T15:30:00Z",
      // ... outros campos
    }
  },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

#### **Exemplo de Uso:**
```bash
curl -X POST "https://api.agrotech.pt/api/alerts/123/dismiss"
```

---

### 5. 🏥 **GET /api/alerts/health**
Health check da API de alertas (não requer autenticação).

#### **Resposta de Sucesso (200):**
```json
{
  "status": "success",
  "message": "API de alertas funcionando",
  "data": {
    "total_alerts": 1250,
    "available_types": ["weather", "pest", "disease", "irrigation", "fertilization", "harvest", "pruning", "market", "general"],
    "available_priorities": ["low", "medium", "high", "critical"],
    "available_statuses": ["pending", "sent", "read", "dismissed", "expired"]
  },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

---

## 📊 Códigos de Status HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Operação bem-sucedida |
| 201 | Created | Recurso criado com sucesso |
| 400 | Bad Request | Dados inválidos fornecidos |
| 401 | Unauthorized | Usuário não autenticado |
| 403 | Forbidden | Usuário não autorizado |
| 404 | Not Found | Recurso não encontrado |
| 500 | Internal Server Error | Erro interno do servidor |

---

## 🚨 Códigos de Erro

| Código | Descrição | Ação Sugerida |
|--------|-----------|---------------|
| `VALIDATION_ERROR` | Dados de entrada inválidos | Verificar campos obrigatórios e valores válidos |
| `AUTH_ERROR` | Problema de autenticação | Fazer login novamente |
| `NOT_FOUND` | Recurso não encontrado | Verificar se ID existe e pertence ao usuário |
| `INVALID_CONTENT_TYPE` | Content-Type não é JSON | Definir header `Content-Type: application/json` |
| `INVALID_JSON` | JSON malformado | Verificar sintaxe do JSON |
| `SERVER_ERROR` | Erro interno | Contatar suporte técnico |

---

## 📝 Modelos de Dados

### Alerta
```typescript
interface Alert {
  id: number;
  type: AlertType;
  priority: AlertPriority;
  status: AlertStatus;
  title: string;
  message: string;
  action_text?: string;
  action_url?: string;
  culture_id?: number;
  created_at: string;     // ISO 8601
  scheduled_for?: string; // ISO 8601
  expires_at?: string;    // ISO 8601
  sent_at?: string;       // ISO 8601
  read_at?: string;       // ISO 8601
  dismissed_at?: string;  // ISO 8601
  alert_metadata: object;
}
```

### Enums
```typescript
type AlertType = 'weather' | 'pest' | 'disease' | 'irrigation' | 'fertilization' | 'harvest' | 'pruning' | 'market' | 'general';
type AlertPriority = 'low' | 'medium' | 'high' | 'critical';
type AlertStatus = 'pending' | 'sent' | 'read' | 'dismissed' | 'expired';
```

---

## 🧪 Testando a API

### Usando cURL
```bash
# Health check
curl -X GET "https://api.agrotech.pt/api/alerts/health"

# Listar alertas (requer login)
curl -X GET "https://api.agrotech.pt/api/alerts/" \
  -H "Cookie: session=seu_cookie_de_sessao"

# Criar alerta
curl -X POST "https://api.agrotech.pt/api/alerts/create" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=seu_cookie_de_sessao" \
  -d '{"type":"weather","priority":"high","title":"Teste","message":"Mensagem de teste"}'
```

### Usando Python
```python
import requests

# Login
session = requests.Session()
response = session.post('https://api.agrotech.pt/api/auth/login', 
                       json={'email': 'seu@email.com', 'password': 'senha'})

# Listar alertas
response = session.get('https://api.agrotech.pt/api/alerts/')
alertas = response.json()

# Criar alerta
novo_alerta = {
    'type': 'irrigation',
    'priority': 'medium',
    'title': 'Irrigação Necessária',
    'message': 'Plantas precisam de água'
}
response = session.post('https://api.agrotech.pt/api/alerts/create', json=novo_alerta)
```

### Script de Validação
Use o script de validação manual para testar todos os endpoints:
```bash
python scripts/test_alerts_api_manual.py https://api.agrotech.pt
```

---

## � **ENDPOINTS ADICIONAIS**

### 7. 🎯 **GET /api/alerts/widget**
Endpoint especial para o widget de alertas no dashboard.

#### **Resposta:**
```json
{
  "success": true,
  "data": {
    "stats": {
      "total": 15,
      "unread": 3,
      "critical": 1
    },
    "critical_alerts": [
      {
        "id": 123,
        "type": "weather",
        "priority": "critical",
        "title": "Tempestade se aproximando",
        "message": "Vento forte previsto para as próximas 2 horas",
        "type_icon": "fa-cloud-sun",
        "priority_color": "red",
        "created_at": "2025-08-01T15:30:00Z"
      }
    ],
    "recent_alerts": [...]
  },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

### 8. �🔄 **POST /api/alerts/generate**
Gera novos alertas automaticamente baseado nas condições atuais.

#### **Resposta:**
```json
{
  "success": true,
  "message": "3 novos alertas gerados",
  "data": {
    "count": 3,
    "types_generated": ["weather", "irrigation"]
  },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

### 9. ✅ **POST /api/alerts/<int:alert_id>/resolve**
Marca um alerta como resolvido (diferente de dispensar).

#### **Resposta:**
```json
{
  "success": true,
  "message": "Alerta resolvido",
  "data": {
    "alert": {
      "id": 123,
      "status": "resolved",
      "dismissed_at": "2025-08-01T15:30:00Z"
    }
  },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

### 10. 📚 **POST /api/alerts/bulk-read**
Marca todos os alertas não lidos do usuário como lidos.

#### **Resposta:**
```json
{
  "success": true,
  "message": "5 alertas marcados como lidos",
  "data": {
    "updated_count": 5
  },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

### 11. 💚 **GET /api/alerts/health**
Health check do sistema de alertas.

#### **Resposta:**
```json
{
  "status": "healthy",
  "service": "alerts_api",
  "version": "2.0",
  "timestamp": "2025-08-01T15:30:00Z"
}
```

---

## 🔐 **AUTENTICAÇÃO E CSRF**

Todos os endpoints POST requerem token CSRF:

```javascript
// Frontend
headers: {
  'Content-Type': 'application/json',
  'X-CSRF-Token': window.csrfToken,
  'X-Requested-With': 'XMLHttpRequest'
},
credentials: 'same-origin'
```

---

## 🔄 Versionamento

**Versão Atual**: 2.0 (Sprint 2)

### Mudanças na v2.0:
- ✅ Endpoints padronizados com estrutura REST
- ✅ Validação robusta de dados de entrada
- ✅ Tratamento de erros melhorado
- ✅ Suporte a filtros e paginação
- ✅ Health check endpoint
- ✅ Widget para dashboard
- ✅ Geração automática de alertas
- ✅ Sistema de resolução de alertas
- ✅ Documentação completa

---

## 📞 Suporte

**Documentação**: Este arquivo  
**Testes**: `tests/test_alerts_api.py`  
**Validação Manual**: `scripts/test_alerts_api_manual.py`  
**Código Fonte**: `app/routes/alerts_api.py`

---

**Desenvolvido para AgroTech Portugal - Sistema de Alertas Inteligentes Sprint 2**
