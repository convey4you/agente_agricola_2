# 🔧 PROMPT CRÍTICO 2: CORREÇÃO COMPLETA DA API DE ALERTAS

**Prioridade:** CRÍTICA (48 horas)  
**Dependência:** PROMPT 1 (schema do banco) deve estar completo  
**Objetivo:** API de alertas 100% funcional

---

## 📋 CONTEXTO COMPLETO PARA CLAUDE SONNET 4

### Situação Atual
Você é um desenvolvedor backend especialista em APIs REST com Flask trabalhando no **AgroTech Portugal**. O schema do banco foi corrigido (coluna `status` adicionada), mas agora precisa garantir que todos os endpoints da API de alertas funcionem perfeitamente.

### Endpoints Críticos para Corrigir
1. **GET /api/alerts/** - Listagem de alertas do usuário
2. **POST /api/alerts/create** - Criação manual de alertas
3. **POST /api/alerts/{id}/read** - Marcar alerta como lido
4. **POST /api/alerts/{id}/dismiss** - Dispensar alerta

### Problemas Identificados na Validação
- Erro "Erro interno do servidor" na criação de alertas
- Possíveis problemas de validação de dados
- Tratamento de erros inadequado
- Respostas JSON inconsistentes
- Falta de logs apropriados

### Arquitetura Técnica
- **Backend:** Flask 3.1.1
- **ORM:** SQLAlchemy 2.0.41
- **Autenticação:** Flask-Login (session-based)
- **Banco:** PostgreSQL (Railway)
- **Formato:** API REST com JSON

---

## 🎯 ESPECIFICAÇÕES TÉCNICAS DETALHADAS

### Estrutura de Resposta Padronizada

**Sucesso:**
```json
{
  "status": "success",
  "message": "Operação realizada com sucesso",
  "data": { ... },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

**Erro:**
```json
{
  "status": "error", 
  "message": "Descrição amigável do erro",
  "error_code": "VALIDATION_ERROR|AUTH_ERROR|SERVER_ERROR",
  "details": { ... },
  "timestamp": "2025-08-01T15:30:00Z"
}
```

### Códigos de Status HTTP
- **200** - Operação bem-sucedida
- **201** - Recurso criado com sucesso
- **400** - Dados inválidos fornecidos
- **401** - Usuário não autenticado
- **403** - Usuário não autorizado
- **404** - Recurso não encontrado
- **500** - Erro interno do servidor

---

## 📝 ENDPOINT 1: GET /api/alerts/

### Especificação Completa
```python
@alerts_bp.route('/api/alerts/', methods=['GET'])
@login_required
def list_alerts():
    """
    Lista alertas do usuário autenticado
    
    Query Parameters:
    - limit (int): Número máximo de alertas (padrão: 50, máximo: 100)
    - offset (int): Offset para paginação (padrão: 0)
    - status (str): Filtrar por status específico
    - type (str): Filtrar por tipo específico
    - priority (str): Filtrar por prioridade específica
    
    Returns:
    - 200: Lista de alertas
    - 401: Usuário não autenticado
    - 500: Erro interno
    """
```

### Implementação Esperada
```python
@alerts_bp.route('/api/alerts/', methods=['GET'])
@login_required
def list_alerts():
    try:
        # Parâmetros de query
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        status_filter = request.args.get('status')
        type_filter = request.args.get('type')
        priority_filter = request.args.get('priority')
        
        # Query base
        query = Alert.query.filter_by(user_id=current_user.id)
        
        # Aplicar filtros
        if status_filter:
            query = query.filter(Alert.status == status_filter)
        if type_filter:
            query = query.filter(Alert.type == type_filter)
        if priority_filter:
            query = query.filter(Alert.priority == priority_filter)
        
        # Ordenação e paginação
        alerts = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()
        total = query.count()
        
        # Serializar dados
        alerts_data = [alert.to_dict() for alert in alerts]
        
        return jsonify({
            'status': 'success',
            'data': {
                'alerts': alerts_data,
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar alertas para usuário {current_user.id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

---

## 📝 ENDPOINT 2: POST /api/alerts/create

### Especificação Completa
```python
@alerts_bp.route('/api/alerts/create', methods=['POST'])
@login_required
def create_alert():
    """
    Cria novo alerta para o usuário autenticado
    
    Request Body (JSON):
    {
      "type": "weather|pest|disease|irrigation|fertilization|harvest|pruning|market|general",
      "priority": "low|medium|high|critical",
      "title": "Título do alerta (máx 200 chars)",
      "message": "Mensagem do alerta",
      "action_text": "Texto do botão de ação (opcional)",
      "action_url": "URL da ação (opcional)",
      "culture_id": 123 (opcional),
      "scheduled_for": "2025-08-01T15:30:00Z" (opcional),
      "expires_at": "2025-08-02T15:30:00Z" (opcional)
    }
    
    Returns:
    - 201: Alerta criado com sucesso
    - 400: Dados inválidos
    - 401: Usuário não autenticado
    - 500: Erro interno
    """
```

### Validações Obrigatórias
```python
def validate_alert_data(data):
    """Valida dados de entrada para criação de alerta"""
    errors = []
    
    # Campos obrigatórios
    required_fields = ['type', 'priority', 'title', 'message']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Campo '{field}' é obrigatório")
    
    # Validar valores permitidos
    valid_types = ['weather', 'pest', 'disease', 'irrigation', 'fertilization', 
                   'harvest', 'pruning', 'market', 'general']
    if data.get('type') not in valid_types:
        errors.append(f"Tipo deve ser um de: {', '.join(valid_types)}")
    
    valid_priorities = ['low', 'medium', 'high', 'critical']
    if data.get('priority') not in valid_priorities:
        errors.append(f"Prioridade deve ser uma de: {', '.join(valid_priorities)}")
    
    # Validar tamanhos
    if len(data.get('title', '')) > 200:
        errors.append("Título não pode ter mais de 200 caracteres")
    
    if len(data.get('message', '')) > 5000:
        errors.append("Mensagem não pode ter mais de 5000 caracteres")
    
    # Validar datas (se fornecidas)
    for date_field in ['scheduled_for', 'expires_at']:
        if data.get(date_field):
            try:
                datetime.fromisoformat(data[date_field].replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"Data '{date_field}' deve estar no formato ISO 8601")
    
    return errors
```

### Implementação Esperada
```python
@alerts_bp.route('/api/alerts/create', methods=['POST'])
@login_required
def create_alert():
    try:
        # Validar Content-Type
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type deve ser application/json',
                'error_code': 'INVALID_CONTENT_TYPE',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        data = request.get_json()
        
        # Validar dados
        validation_errors = validate_alert_data(data)
        if validation_errors:
            return jsonify({
                'status': 'error',
                'message': 'Dados inválidos fornecidos',
                'error_code': 'VALIDATION_ERROR',
                'details': {'errors': validation_errors},
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Criar alerta
        alert = Alert(
            user_id=current_user.id,
            type=data['type'],
            priority=data['priority'],
            status='PENDING',  # Status padrão
            title=data['title'],
            message=data['message'],
            action_text=data.get('action_text'),
            action_url=data.get('action_url'),
            culture_id=data.get('culture_id'),
            scheduled_for=datetime.fromisoformat(data['scheduled_for'].replace('Z', '+00:00')) if data.get('scheduled_for') else None,
            expires_at=datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00')) if data.get('expires_at') else None,
            created_at=datetime.utcnow()
        )
        
        db.session.add(alert)
        db.session.commit()
        
        current_app.logger.info(f"Alerta {alert.id} criado para usuário {current_user.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Alerta criado com sucesso',
            'data': {
                'alert': alert.to_dict()
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar alerta para usuário {current_user.id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

---

## 📝 ENDPOINT 3: POST /api/alerts/{id}/read

### Especificação Completa
```python
@alerts_bp.route('/api/alerts/<int:alert_id>/read', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    """
    Marca alerta como lido
    
    Path Parameters:
    - alert_id (int): ID do alerta
    
    Returns:
    - 200: Alerta marcado como lido
    - 404: Alerta não encontrado
    - 403: Usuário não autorizado
    - 401: Usuário não autenticado
    - 500: Erro interno
    """
```

### Implementação Esperada
```python
@alerts_bp.route('/api/alerts/<int:alert_id>/read', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    try:
        # Buscar alerta
        alert = Alert.query.filter_by(id=alert_id, user_id=current_user.id).first()
        
        if not alert:
            return jsonify({
                'status': 'error',
                'message': 'Alerta não encontrado',
                'error_code': 'NOT_FOUND',
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        # Verificar se já foi lido
        if alert.status == 'READ':
            return jsonify({
                'status': 'success',
                'message': 'Alerta já estava marcado como lido',
                'data': {
                    'alert': alert.to_dict()
                },
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        
        # Marcar como lido
        alert.status = 'READ'
        alert.read_at = datetime.utcnow()
        
        db.session.commit()
        
        current_app.logger.info(f"Alerta {alert_id} marcado como lido por usuário {current_user.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Alerta marcado como lido',
            'data': {
                'alert': alert.to_dict()
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao marcar alerta {alert_id} como lido: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

---

## 📝 ENDPOINT 4: POST /api/alerts/{id}/dismiss

### Implementação Esperada
```python
@alerts_bp.route('/api/alerts/<int:alert_id>/dismiss', methods=['POST'])
@login_required
def dismiss_alert(alert_id):
    try:
        # Buscar alerta
        alert = Alert.query.filter_by(id=alert_id, user_id=current_user.id).first()
        
        if not alert:
            return jsonify({
                'status': 'error',
                'message': 'Alerta não encontrado',
                'error_code': 'NOT_FOUND',
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        # Verificar se já foi dispensado
        if alert.status == 'DISMISSED':
            return jsonify({
                'status': 'success',
                'message': 'Alerta já estava dispensado',
                'data': {
                    'alert': alert.to_dict()
                },
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        
        # Dispensar alerta
        alert.status = 'DISMISSED'
        alert.dismissed_at = datetime.utcnow()
        
        db.session.commit()
        
        current_app.logger.info(f"Alerta {alert_id} dispensado por usuário {current_user.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Alerta dispensado',
            'data': {
                'alert': alert.to_dict()
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao dispensar alerta {alert_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'error_code': 'SERVER_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

---

## 🧪 TESTES OBRIGATÓRIOS

### Script de Teste da API
Criar `tests/test_alerts_api.py`:

```python
import pytest
import json
from datetime import datetime
from app import create_app, db
from app.models import User, Alert

class TestAlertsAPI:
    
    @pytest.fixture
    def client(self):
        app = create_app('testing')
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()
    
    @pytest.fixture
    def auth_user(self, client):
        # Criar usuário de teste
        user = User(email='test@example.com', password='password')
        db.session.add(user)
        db.session.commit()
        
        # Fazer login
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['_fresh'] = True
        
        return user
    
    def test_list_alerts_empty(self, client, auth_user):
        """Testar listagem quando não há alertas"""
        response = client.get('/api/alerts/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['total'] == 0
        assert len(data['data']['alerts']) == 0
    
    def test_create_alert_success(self, client, auth_user):
        """Testar criação de alerta com dados válidos"""
        alert_data = {
            'type': 'weather',
            'priority': 'high',
            'title': 'Teste de Alerta',
            'message': 'Este é um alerta de teste'
        }
        
        response = client.post('/api/alerts/create', 
                             data=json.dumps(alert_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['alert']['title'] == 'Teste de Alerta'
        assert data['data']['alert']['status'] == 'PENDING'
    
    def test_create_alert_validation_error(self, client, auth_user):
        """Testar criação com dados inválidos"""
        alert_data = {
            'type': 'invalid_type',
            'priority': 'high'
            # title e message faltando
        }
        
        response = client.post('/api/alerts/create',
                             data=json.dumps(alert_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['error_code'] == 'VALIDATION_ERROR'
    
    def test_mark_alert_read(self, client, auth_user):
        """Testar marcar alerta como lido"""
        # Criar alerta primeiro
        alert = Alert(
            user_id=auth_user.id,
            type='weather',
            priority='high',
            status='PENDING',
            title='Teste',
            message='Teste'
        )
        db.session.add(alert)
        db.session.commit()
        
        # Marcar como lido
        response = client.post(f'/api/alerts/{alert.id}/read')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['alert']['status'] == 'READ'
    
    def test_dismiss_alert(self, client, auth_user):
        """Testar dispensar alerta"""
        # Criar alerta primeiro
        alert = Alert(
            user_id=auth_user.id,
            type='weather',
            priority='high',
            status='PENDING',
            title='Teste',
            message='Teste'
        )
        db.session.add(alert)
        db.session.commit()
        
        # Dispensar
        response = client.post(f'/api/alerts/{alert.id}/dismiss')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['alert']['status'] == 'DISMISSED'
    
    def test_alert_not_found(self, client, auth_user):
        """Testar acesso a alerta inexistente"""
        response = client.post('/api/alerts/99999/read')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['error_code'] == 'NOT_FOUND'
```

---

## 📋 ENTREGÁVEIS OBRIGATÓRIOS

### 1. Controllers/Routes Corrigidos
- Arquivo `app/routes/alerts.py` ou similar
- Todos os 4 endpoints implementados
- Validações robustas
- Tratamento de erros completo
- Logs apropriados

### 2. Testes Unitários
- Arquivo `tests/test_alerts_api.py`
- Cobertura de todos os endpoints
- Casos de sucesso e erro
- Validação de autenticação
- Testes de permissões

### 3. Documentação da API
- Arquivo `docs/alerts_api.md`
- Especificação de cada endpoint
- Exemplos de request/response
- Códigos de erro possíveis

### 4. Script de Validação Manual
- Arquivo `scripts/test_alerts_api_manual.py`
- Testes que podem ser executados em produção
- Validação de todos os endpoints
- Relatório de resultados

---

## ✅ CRITÉRIOS DE VALIDAÇÃO

### Validação Técnica Obrigatória
1. **Todos os endpoints respondem corretamente:**
   - GET /api/alerts/ → 200 com lista de alertas
   - POST /api/alerts/create → 201 com alerta criado
   - POST /api/alerts/{id}/read → 200 com status atualizado
   - POST /api/alerts/{id}/dismiss → 200 com status atualizado

2. **Validações funcionam:**
   - Dados inválidos retornam 400
   - Usuário não autenticado retorna 401
   - Alerta de outro usuário retorna 404

3. **Integração com banco:**
   - Dados são persistidos corretamente
   - Queries são eficientes
   - Transações são seguras

### Critérios de Sucesso
- [ ] Todos os testes unitários passam
- [ ] API responde em < 200ms
- [ ] Logs estruturados implementados
- [ ] Documentação completa
- [ ] Validação manual bem-sucedida

---

**Ferramentas:** VS Code + GitHub Copilot  
**Prazo:** 48 horas  
**Dependência:** PROMPT 1 (schema) completo  
**Validação:** Testes automatizados + Gerente de Tecnologia

