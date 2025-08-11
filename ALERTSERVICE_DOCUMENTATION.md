# Documentação do AlertService

## Visão Geral

O `AlertService` é o serviço principal responsável por gerenciar alertas inteligentes no sistema Agente Agrícola. Ele fornece funcionalidades para criar, buscar, atualizar e processar alertas direcionados aos usuários com base em dados agrícolas e meteorológicos.

## Localização

- **Arquivo**: `app/services/alert_service.py`
- **Classe**: `AlertService`
- **Dependências**: `app/models/alerts.py`, SQLAlchemy, logging

## Modelos Relacionados

### Alert (app/models/alerts.py)
```python
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.Enum(AlertType), nullable=False)
    priority = db.Column(db.Enum(AlertPriority), default=AlertPriority.MEDIUM)
    status = db.Column(db.Enum(AlertStatus), default=AlertStatus.PENDING)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    action_text = db.Column(db.String(100))
    action_url = db.Column(db.String(500))
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id'))
    location_data = db.Column(db.Text)  # JSON
    weather_data = db.Column(db.Text)   # JSON
    alert_metadata = db.Column(db.Text) # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    # ... outros campos
```

### Enums
```python
class AlertType(Enum):
    WEATHER = "weather"
    PEST = "pest"
    DISEASE = "disease"
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    HARVEST = "harvest"
    PRUNING = "pruning"
    PLANTING = "planting"
    MARKET = "market"
    GENERAL = "general"

class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SENT = "sent"
    READ = "read"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"
    EXPIRED = "expired"
```

## Métodos Principais

### Métodos de Busca

#### `get_active_alerts(user_id: int, limit: int = 10) -> List[Alert]`
**Descrição**: Busca alertas ativos do usuário (status: PENDING, ACTIVE, SENT)
**Parâmetros**:
- `user_id`: ID do usuário
- `limit`: Número máximo de alertas a retornar

**Implementação Atual**:
```python
def get_active_alerts(self, user_id: int, limit: int = 10) -> List[Alert]:
    try:
        # Buscar todos os alertas do usuário e filtrar no Python
        alerts = Alert.query.filter(
            Alert.user_id == user_id
        ).order_by(
            Alert.priority.desc(),
            Alert.created_at.desc()
        ).all()
        
        # Filtrar por status válidos
        active_alerts = [
            alert for alert in alerts 
            if alert.status in [AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT]
        ]
        
        return active_alerts[:limit]
    except Exception as e:
        logger.error(f"Erro ao buscar alertas ativos: {e}")
        return []
```

#### `get_unread_alerts(user_id: int) -> List[Alert]`
**Descrição**: Busca alertas não lidos do usuário
**Parâmetros**:
- `user_id`: ID do usuário

**Implementação Atual**:
```python
def get_unread_alerts(self, user_id: int) -> List[Alert]:
    try:
        # Buscar todos os alertas do usuário e filtrar no Python
        alerts = Alert.query.filter(
            Alert.user_id == user_id
        ).order_by(Alert.created_at.desc()).all()
        
        # Filtrar por status não lidos
        unread_alerts = [
            alert for alert in alerts 
            if alert.status in [AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT]
        ]
        
        return unread_alerts
    except Exception as e:
        logger.error(f"Erro ao buscar alertas não lidos: {e}")
        return []
```

### Métodos de Criação e Gestão

#### `create_alert(data: dict) -> Alert`
**Descrição**: Cria um novo alerta
**Parâmetros**:
- `data`: Dicionário com dados do alerta (user_id, type, priority, title, message, etc.)

#### `mark_as_read(alert_id: int, user_id: int) -> bool`
**Descrição**: Marca um alerta como lido
**Parâmetros**:
- `alert_id`: ID do alerta
- `user_id`: ID do usuário (para validação)

#### `mark_as_resolved(alert_id: int, user_id: int) -> bool`
**Descrição**: Marca um alerta como resolvido

### Métodos de Geração Automática

#### `generate_planting_alerts(user: User) -> List[Alert]`
**Descrição**: Gera alertas automáticos de oportunidades de plantio baseados na época do ano e dados climáticos
**Parâmetros**:
- `user`: Objeto User para quem gerar os alertas

**Funcionalidade**:
- Analisa o mês atual
- Busca culturas adequadas para plantio na época
- Considera dados climáticos regionais
- Gera alertas personalizados com sugestões

## Rotas de API Relacionadas

### `/api/alerts/` (GET)
**Descrição**: Lista alertas do usuário autenticado
**Retorna**: JSON com lista de alertas

### `/api/alerts/recentes` (GET)
**Descrição**: Busca alertas recentes (até 5)
**Retorna**: JSON com alertas recentes

### `/api/alerts/widget` (GET)
**Descrição**: Dados formatados para widget de alertas
**Retorna**: Estatísticas + alertas críticos/recentes

### `/api/alerts/<id>/read` (POST)
**Descrição**: Marca alerta como lido

### `/api/alerts/<id>/resolve` (POST)
**Descrição**: Marca alerta como resolvido

### `/api/dashboard/alertas` (GET)
**Descrição**: Alertas para o dashboard principal
**Retorna**: JSON com alertas ativos do usuário

## Integração com Frontend

### JavaScript Principal (app.js)
```javascript
// Carregamento de alertas no dashboard
async function carregarDashboard() {
    const [alertasRes] = await Promise.all([
        fetch('/api/dashboard/alertas')
    ]);
    const alertas = await alertasRes.json();
    // Processar alertas...
}

// Alertas recentes
async function carregarAlertasRecentes() {
    const response = await fetch('/api/alertas/recentes');
    const alertas = await response.json();
    // Renderizar alertas...
}
```

### Widget de Alertas (alerts-manager.js)
```javascript
class AlertsManager {
    async loadWidget() {
        const response = await fetch('/api/alerts/widget');
        // Carregar dados para widget
    }
    
    async markAsRead(alertId) {
        const response = await fetch(`/api/alerts/${alertId}/read`, {
            method: 'POST'
        });
    }
}
```

## Dependências e Configuração

### Imports Necessários
```python
from app.models.alerts import Alert, AlertType, AlertPriority, AlertStatus
from app.models.user import User
from app import db
from datetime import datetime, timezone
import logging
import json
```

### Configuração de Logging
```python
logger = logging.getLogger(__name__)
```

## Tratamento de Erros

Todos os métodos incluem tratamento de exceções com:
- Log de erros detalhados
- Retorno de valores padrão seguros (listas vazias, False, etc.)
- Não propagação de exceções para o frontend

## Notas de Implementação

### Questões Resolvidas
1. **SQLAlchemy Syntax Issues**: Métodos `get_active_alerts` e `get_unread_alerts` foram refatorados para usar filtragem em Python em vez de queries SQLAlchemy complexas
2. **Compatibilidade de Rotas**: Registrado blueprint com prefixos `/api/alerts` e `/api/alertas` para compatibilidade
3. **JavaScript Errors**: Corrigido template HTML com sintaxe JavaScript inválida

### Performance
- Filtragem de alertas feita em Python (pode ser otimizada para grandes volumes)
- Caching não implementado (oportunidade de melhoria)
- Queries otimizadas com `order_by` e `limit`

### Segurança
- Validação de `user_id` em todos os métodos sensíveis
- Autenticação obrigatória via `@login_required`
- Sanitização de dados de entrada (implementação básica)

## Uso Típico

```python
# Instanciar serviço
alert_service = AlertService()

# Buscar alertas ativos
active_alerts = alert_service.get_active_alerts(user_id=1, limit=5)

# Marcar como lido
success = alert_service.mark_as_read(alert_id=123, user_id=1)

# Gerar alertas automáticos
new_alerts = alert_service.generate_planting_alerts(user=current_user)
```

## Status Atual

✅ **Funcionando**: Métodos básicos de busca e criação
✅ **Funcionando**: Rotas de API principais  
✅ **Funcionando**: Integração com frontend
⚠️ **Melhorias Pendentes**: Otimização de queries SQLAlchemy
⚠️ **Melhorias Pendentes**: Sistema de cache
⚠️ **Melhorias Pendentes**: Alertas automáticos avançados
