# Tarefas para os Programadores
## AgroTech 1.0 - Correções e Melhorias Prioritárias

**Data**: 27 de julho de 2025  
**Autor**: Gerente de Tecnologia  
**Destinatário**: Equipe de Desenvolvimento  

---

## 🚨 TAREFAS CRÍTICAS (Esta Semana)

### 1. Refatoração de Controllers (Prioridade MÁXIMA)

**Responsável**: Desenvolvedor Senior  
**Prazo**: 5 dias úteis  
**Estimativa**: 20 horas  

**Arquivos a refatorar**:
- `app/controllers/auth_controller.py` (217 linhas)
- `app/controllers/culture_controller.py` (265 linhas)
- `app/controllers/dashboard_controller.py` (complexo)
- `app/controllers/agent_controller.py` (complexo)
- `app/controllers/marketplace_controller.py` (complexo)
- `app/controllers/monitoring_controller.py` (complexo)

**Ações específicas**:
```python
# ANTES (Problemático)
@bp.route('/culture/create', methods=['POST'])
def create_culture():
    # 50+ linhas de lógica de negócio aqui
    # Validação, processamento, salvamento, etc.
    pass

# DEPOIS (Correto)
@bp.route('/culture/create', methods=['POST'])
def create_culture():
    try:
        culture_data = request.get_json()
        culture = culture_service.create_culture(culture_data)
        return jsonify(culture.to_dict()), 201
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
```

**Checklist de refatoração**:
- [ ] Extrair validação para validators
- [ ] Mover lógica de negócio para services
- [ ] Reduzir controllers para max 50 linhas por método
- [ ] Implementar tratamento de erro consistente
- [ ] Adicionar logging adequado

### 2. Implementação de Sistema de Cache (Prioridade ALTA)

**Responsável**: Desenvolvedor Backend  
**Prazo**: 3 dias úteis  
**Estimativa**: 12 horas  

**Configuração Redis**:
```python
# config.py
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = REDIS_URL
CACHE_DEFAULT_TIMEOUT = 300
```

**Implementação em services**:
```python
# app/services/weather_service.py
from flask_caching import Cache

cache = Cache()

class WeatherService:
    @cache.memoize(timeout=1800)  # 30 minutos
    def get_weather_data(self, location):
        # Implementação da busca de dados climáticos
        pass
    
    @cache.memoize(timeout=3600)  # 1 hora
    def get_weather_forecast(self, location, days=7):
        # Implementação da previsão
        pass
```

**Arquivos a modificar**:
- [ ] `app/__init__.py` - Configurar cache
- [ ] `app/services/weather_service.py` - Cache de dados climáticos
- [ ] `app/services/ai_service.py` - Cache de recomendações
- [ ] `app/controllers/dashboard_controller.py` - Cache de dashboard
- [ ] `requirements.txt` - Adicionar Flask-Caching e redis

### 3. Limpeza de Código de Debug (Prioridade MÉDIA)

**Responsável**: Toda a equipe  
**Prazo**: 1 dia útil  
**Estimativa**: 4 horas  

**Arquivos com prints identificados**:
- `app/__init__.py`
- `app/controllers/auth_controller.py`
- `app/controllers/culture_controller.py`

**Substituir por logging adequado**:
```python
# REMOVER
print(f"Debug: {variable}")

# SUBSTITUIR POR
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Processing: {variable}")
logger.info(f"User action: {action}")
logger.error(f"Error occurred: {error}")
```

---

## ⚠️ TAREFAS IMPORTANTES (Próximas 2 Semanas)

### 4. Implementação de Testes Abrangentes

**Responsável**: QA + Desenvolvedores  
**Prazo**: 2 semanas  
**Estimativa**: 40 horas  

**Estrutura de testes a implementar**:
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database.py
│   └── test_external_services.py
└── functional/
    ├── test_user_flows.py
    └── test_ui_components.py
```

**Exemplo de teste unitário**:
```python
# tests/unit/test_services.py
import pytest
from app.services.ai_service import AIService

class TestAIService:
    def test_generate_recommendation(self):
        service = AIService()
        result = service.generate_recommendation(
            culture_type="tomate",
            growth_stage="floração",
            weather_data={"temp": 25, "humidity": 70}
        )
        assert result is not None
        assert "recomendação" in result
        assert len(result) > 50
```

**Meta de cobertura**: 80% mínimo

### 5. Implementação de Paginação

**Responsável**: Desenvolvedor Backend  
**Prazo**: 3 dias úteis  
**Estimativa**: 8 horas  

**Implementar em**:
- Lista de culturas
- Lista de alertas
- Histórico de atividades
- Marketplace

**Exemplo de implementação**:
```python
# app/controllers/culture_controller.py
@bp.route('/cultures')
def list_cultures():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    cultures = Culture.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'cultures': [c.to_dict() for c in cultures.items],
        'total': cultures.total,
        'pages': cultures.pages,
        'current_page': page
    })
```

### 6. Implementação PWA (Progressive Web App)

**Responsável**: Desenvolvedor Frontend  
**Prazo**: 1 semana  
**Estimativa**: 20 horas  

**Arquivos a criar**:
- `app/static/sw.js` (Service Worker)
- `app/static/manifest.json` (Web App Manifest)
- `app/templates/base.html` (atualizar com PWA meta tags)

**Service Worker básico**:
```javascript
// app/static/sw.js
const CACHE_NAME = 'agrotech-v1';
const urlsToCache = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/icons/icon-192x192.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
```

---

## 📋 TAREFAS DE MELHORIA (Próximo Mês)

### 7. Integração IPMA

**Responsável**: Desenvolvedor Backend  
**Prazo**: 1 semana  
**Estimativa**: 16 horas  

**Pesquisar e implementar**:
- API do IPMA (Instituto Português do Mar e da Atmosfera)
- Adapter para dados climáticos portugueses
- Fallback para API atual em caso de indisponibilidade

### 8. Interface Wizard-Driven

**Responsável**: Desenvolvedor Frontend  
**Prazo**: 2 semanas  
**Estimativa**: 30 horas  

**Implementar wizards para**:
- Cadastro de nova cultura (5 etapas)
- Onboarding de usuário (5 etapas)
- Configuração de alertas (3 etapas)

### 9. Otimização de Interface Responsiva

**Responsável**: Desenvolvedor Frontend  
**Prazo**: 1 semana  
**Estimativa**: 20 horas  

**Focar em**:
- Tablets (768px - 1024px)
- Smartphones (320px - 767px)
- Touch-friendly interfaces
- Performance em dispositivos baixo custo

---

## 🔧 CONFIGURAÇÕES E SETUP

### Configuração de Ambiente de Desenvolvimento

**Adicionar ao requirements.txt**:
```
Flask-Caching==2.0.2
redis==4.5.4
pytest==7.3.1
pytest-cov==4.0.0
pytest-flask==1.2.0
```

**Configurar pre-commit hooks**:
```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### Configuração de CI/CD

**GitHub Actions** (`.github/workflows/test.yml`):
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run tests
      run: pytest --cov=app --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 📊 MÉTRICAS DE ACOMPANHAMENTO

### Daily Standup (Diário - 9h)

**Perguntas obrigatórias**:
1. O que fiz ontem?
2. O que vou fazer hoje?
3. Há algum impedimento?
4. Qual o progresso das tarefas críticas?

### Weekly Review (Sextas - 16h)

**Métricas a reportar**:
- Tarefas concluídas vs planejadas
- Score de qualidade de código
- Cobertura de testes atual
- Problemas identificados
- Riscos para próxima semana

### Code Review Checklist

**Antes de aprovar PR**:
- [ ] Código segue padrões estabelecidos
- [ ] Testes incluídos e passando
- [ ] Documentação atualizada
- [ ] Performance adequada
- [ ] Segurança verificada

---

## 🎯 DEFINIÇÃO DE PRONTO (Definition of Done)

### Para cada tarefa:
- [ ] Código implementado e testado
- [ ] Testes unitários com cobertura > 80%
- [ ] Code review aprovado
- [ ] Documentação atualizada
- [ ] Deploy em ambiente de teste
- [ ] Validação funcional aprovada

### Para cada sprint:
- [ ] Todas as tarefas críticas concluídas
- [ ] Score de qualidade mantido > 85
- [ ] Nenhum bug crítico em aberto
- [ ] Performance dentro dos parâmetros
- [ ] Aprovação do Gerente de Tecnologia

---

**Lembrete**: Este documento deve ser consultado diariamente. Qualquer dúvida ou impedimento deve ser comunicado imediatamente ao Gerente de Tecnologia.

**Próxima revisão**: Segunda-feira, 29 de julho de 2025

