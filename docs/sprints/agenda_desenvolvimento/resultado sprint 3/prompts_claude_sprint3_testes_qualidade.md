# PROMPTS CLAUDE SONNET 4 - SPRINT 3: TESTES E QUALIDADE
## AgroTech Portugal - Sistema de Agente Agrícola Inteligente

**Autor**: Manus AI - Gerente de Tecnologia  
**Data**: 31 de julho de 2025  
**Versão**: 1.0  
**Sprint**: 3 - Testes e Qualidade  
**Período**: 19-30 de agosto de 2025  

---

## 📋 VISÃO GERAL DO SPRINT 3

O Sprint 3 foca na implementação de um sistema robusto de testes e garantia de qualidade para o AgroTech Portugal. Este sprint é fundamental para assegurar que todas as funcionalidades implementadas nos sprints anteriores funcionem corretamente, sejam seguras e ofereçam uma experiência de usuário excepcional.

### Objetivos Principais

O Sprint 3 tem como objetivo estabelecer uma base sólida de qualidade que permita ao AgroTech Portugal ser lançado com confiança no mercado português. Isso inclui a implementação de testes automatizados abrangentes, ferramentas de monitoramento de qualidade, processos de validação de dados e sistemas de detecção precoce de problemas.

### Contexto Estratégico

Com as funcionalidades core implementadas no Sprint 2, o Sprint 3 representa o momento crucial onde transformamos um protótipo funcional em um produto enterprise-grade. A qualidade não é apenas uma questão técnica, mas um diferencial competitivo que determinará o sucesso do AgroTech Portugal no mercado agrícola português.

---

## 🧪 PROMPT 1: SISTEMA DE TESTES UNITÁRIOS ABRANGENTE

### Contexto do Projeto
Você está implementando um sistema completo de testes unitários para o AgroTech Portugal. Este sistema deve garantir que cada componente individual do software funcione corretamente de forma isolada, proporcionando uma base sólida para a detecção precoce de bugs e facilitando a manutenção futura do código.

### Funcionalidade a Implementar
Sistema de testes unitários que cubra todas as funcionalidades críticas do AgroTech Portugal, incluindo modelos de dados, serviços de negócio, controladores, integrações externas e sistema de IA. O objetivo é alcançar uma cobertura de testes de pelo menos 85% e estabelecer um processo automatizado de execução de testes.

### Arquitetura Proposta

O sistema de testes será estruturado em múltiplas camadas, cada uma focada em aspectos específicos da aplicação. A arquitetura seguirá o padrão AAA (Arrange, Act, Assert) e utilizará mocks e fixtures para isolar componentes durante os testes.

**Estrutura de Testes:**
- **Testes de Modelos**: Validação de modelos de dados, relacionamentos e métodos
- **Testes de Serviços**: Lógica de negócio, integrações e processamento de dados
- **Testes de Controladores**: Rotas, autenticação e respostas HTTP
- **Testes de IA**: Algoritmos de recomendação e processamento inteligente
- **Testes de Integração**: Comunicação entre componentes

### Objetivo
Implementar um sistema de testes unitários robusto e automatizado que garanta a qualidade e confiabilidade de todas as funcionalidades do AgroTech Portugal, estabelecendo uma base sólida para desenvolvimento contínuo e manutenção eficiente.

### Instruções Detalhadas

**ETAPA 1: Configuração do Ambiente de Testes**

Primeiro, configure o ambiente de testes criando a estrutura necessária em `tests/`:

```python
# tests/conftest.py
import pytest
import tempfile
import os
from app import create_app, db
from app.models import User, Culture, Recommendation, Product
from datetime import datetime, date

@pytest.fixture
def app():
    """Criar aplicação de teste"""
    # Configuração de teste
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'OPENAI_API_KEY': 'test-openai-key'
    }
    
    app = create_app(test_config)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de teste"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner de comandos CLI"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Headers de autenticação para testes"""
    # Criar usuário de teste
    user_data = {
        'name': 'João Silva',
        'email': 'joao@teste.com',
        'password': 'senha123',
        'phone': '912345678',
        'location_district': 'Porto'
    }
    
    # Registrar usuário
    client.post('/auth/register', data=user_data)
    
    # Fazer login
    login_response = client.post('/auth/login', data={
        'email': 'joao@teste.com',
        'password': 'senha123'
    })
    
    # Extrair token de sessão
    return {'Authorization': f'Bearer {login_response.get_json().get("token", "")}'}

@pytest.fixture
def sample_user():
    """Usuário de exemplo para testes"""
    user = User(
        name='Maria Santos',
        email='maria@exemplo.com',
        phone='913456789',
        location_district='Lisboa',
        experiencia='intermediario',
        tipo_produtor='familiar'
    )
    user.set_password('senha123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def sample_culture(sample_user):
    """Cultura de exemplo para testes"""
    culture = Culture(
        user_id=sample_user.id,
        name='Milho Doce',
        type='annual',
        variety='Golden Bantam',
        area=2.5,
        planting_date=date(2025, 3, 15),
        status='growing'
    )
    db.session.add(culture)
    db.session.commit()
    return culture
```

**ETAPA 2: Testes de Modelos de Dados**

Crie testes abrangentes para todos os modelos em `tests/test_models.py`:

```python
# tests/test_models.py
import pytest
from datetime import date, datetime
from app.models import User, Culture, Recommendation, Product, Alert
from app.models.cultures import CultureType, CultureStatus
from app.models.ai import RecommendationType, RecommendationStatus

class TestUserModel:
    """Testes para o modelo User"""
    
    def test_user_creation(self, app):
        """Testar criação de usuário"""
        with app.app_context():
            user = User(
                name='Pedro Costa',
                email='pedro@teste.com',
                phone='914567890',
                location_district='Braga'
            )
            user.set_password('senha123')
            
            assert user.name == 'Pedro Costa'
            assert user.email == 'pedro@teste.com'
            assert user.check_password('senha123')
            assert not user.check_password('senha_errada')
    
    def test_user_password_hashing(self, app):
        """Testar hash de senha"""
        with app.app_context():
            user = User(name='Teste', email='teste@teste.com')
            user.set_password('minha_senha')
            
            assert user.password_hash != 'minha_senha'
            assert user.check_password('minha_senha')
            assert not user.check_password('senha_errada')
    
    def test_user_interesses_list(self, app):
        """Testar lista de interesses"""
        with app.app_context():
            user = User(
                name='Ana Silva',
                email='ana@teste.com',
                interesses='cereais,horticultura,fruticultura'
            )
            
            interesses = user.get_interesses_list()
            assert 'cereais' in interesses
            assert 'horticultura' in interesses
            assert 'fruticultura' in interesses
            assert len(interesses) == 3
    
    def test_user_validation(self, app):
        """Testar validações do usuário"""
        with app.app_context():
            # Email inválido
            user = User(name='Teste', email='email_invalido')
            with pytest.raises(ValueError):
                user.validate_email()
            
            # Telefone português válido
            user.phone = '912345678'
            assert user.validate_phone()
            
            # Telefone inválido
            user.phone = '123456'
            assert not user.validate_phone()

class TestCultureModel:
    """Testes para o modelo Culture"""
    
    def test_culture_creation(self, app, sample_user):
        """Testar criação de cultura"""
        with app.app_context():
            culture = Culture(
                user_id=sample_user.id,
                name='Tomate Cereja',
                type=CultureType.HORTICULTURE,
                variety='Cherry Roma',
                area=1.2,
                planting_date=date(2025, 4, 1),
                status=CultureStatus.PLANTED
            )
            
            assert culture.name == 'Tomate Cereja'
            assert culture.type == CultureType.HORTICULTURE
            assert culture.area == 1.2
            assert culture.status == CultureStatus.PLANTED
    
    def test_culture_current_stage(self, app, sample_culture):
        """Testar cálculo do estágio atual"""
        with app.app_context():
            # Definir duração do ciclo
            sample_culture.cycle_duration_days = 120
            
            stage = sample_culture.get_current_stage()
            assert stage in [
                'Germinação/Crescimento Inicial',
                'Crescimento Vegetativo',
                'Floração/Frutificação',
                'Maturação',
                'Pronto para Colheita'
            ]
    
    def test_culture_relationships(self, app, sample_culture):
        """Testar relacionamentos da cultura"""
        with app.app_context():
            # Verificar relacionamento com usuário
            assert sample_culture.user is not None
            assert sample_culture.user.name == 'Maria Santos'
            
            # Verificar que usuário tem a cultura
            assert sample_culture in sample_culture.user.cultures

class TestRecommendationModel:
    """Testes para o modelo Recommendation"""
    
    def test_recommendation_creation(self, app, sample_user, sample_culture):
        """Testar criação de recomendação"""
        with app.app_context():
            recommendation = Recommendation(
                user_id=sample_user.id,
                culture_id=sample_culture.id,
                type=RecommendationType.IRRIGATION,
                title='Necessidade de Irrigação',
                summary='Sua cultura precisa de água',
                confidence_score=0.85,
                potential_impact='alto'
            )
            
            assert recommendation.type == RecommendationType.IRRIGATION
            assert recommendation.confidence_score == 0.85
            assert recommendation.status == RecommendationStatus.ACTIVE
    
    def test_recommendation_feedback(self, app, sample_user, sample_culture):
        """Testar sistema de feedback"""
        with app.app_context():
            recommendation = Recommendation(
                user_id=sample_user.id,
                culture_id=sample_culture.id,
                type=RecommendationType.PLANTING,
                title='Época de Plantio',
                summary='Boa época para plantar'
            )
            
            # Fornecer feedback
            recommendation.provide_feedback(5, 'Excelente recomendação!')
            
            assert recommendation.feedback_rating == 5
            assert recommendation.feedback_comment == 'Excelente recomendação!'
            assert recommendation.feedback_at is not None
    
    def test_recommendation_status_changes(self, app, sample_user):
        """Testar mudanças de status"""
        with app.app_context():
            recommendation = Recommendation(
                user_id=sample_user.id,
                type=RecommendationType.HARVEST,
                title='Época de Colheita',
                summary='Hora de colher'
            )
            
            # Aceitar recomendação
            recommendation.accept()
            assert recommendation.status == RecommendationStatus.ACCEPTED
            
            # Rejeitar recomendação
            recommendation.reject()
            assert recommendation.status == RecommendationStatus.REJECTED

class TestProductModel:
    """Testes para o modelo Product (Marketplace)"""
    
    def test_product_creation(self, app, sample_user):
        """Testar criação de produto"""
        with app.app_context():
            product = Product(
                user_id=sample_user.id,
                name='Tomates Frescos',
                description='Tomates orgânicos da nossa quinta',
                price=2.50,
                unit='kg',
                quantity_available=100.0,
                location_district='Lisboa'
            )
            
            assert product.name == 'Tomates Frescos'
            assert product.price == 2.50
            assert product.unit == 'kg'
            assert product.is_active == True
    
    def test_product_search_functionality(self, app, sample_user):
        """Testar funcionalidade de busca de produtos"""
        with app.app_context():
            # Criar vários produtos
            products = [
                Product(user_id=sample_user.id, name='Tomates', price=2.0, unit='kg'),
                Product(user_id=sample_user.id, name='Alface', price=1.5, unit='kg'),
                Product(user_id=sample_user.id, name='Cenouras', price=1.8, unit='kg')
            ]
            
            for product in products:
                db.session.add(product)
            db.session.commit()
            
            # Buscar produtos
            tomate_products = Product.query.filter(
                Product.name.contains('Tomate')
            ).all()
            
            assert len(tomate_products) == 1
            assert tomate_products[0].name == 'Tomates'
```

**ETAPA 3: Testes de Serviços de Negócio**

Crie testes para os serviços em `tests/test_services.py`:

```python
# tests/test_services.py
import pytest
from unittest.mock import Mock, patch
from app.services.ai_engine import AIEngine
from app.services.culture_service import CultureService
from app.services.weather_service import IPMAService
from app.services.alert_service import AlertService
from app.models import User, Culture, Recommendation

class TestAIEngine:
    """Testes para o motor de IA"""
    
    @patch('app.services.ai_engine.IPMAService')
    @patch('app.services.ai_engine.MarketService')
    def test_generate_recommendations_for_user(self, mock_market, mock_weather, app, sample_user, sample_culture):
        """Testar geração de recomendações"""
        with app.app_context():
            # Configurar mocks
            mock_weather.return_value.get_weather_for_location.return_value = {
                'current': {
                    'temperature': 25,
                    'humidity': 80,
                    'days_without_rain': 6
                }
            }
            
            mock_market.return_value.get_market_trends.return_value = [
                {'product': 'cereais', 'trend': 'up', 'change_pct': 5.2}
            ]
            
            # Executar geração de recomendações
            ai_engine = AIEngine()
            ai_engine.generate_recommendations_for_user(sample_user)
            
            # Verificar se recomendações foram criadas
            recommendations = Recommendation.query.filter_by(user_id=sample_user.id).all()
            assert len(recommendations) > 0
    
    def test_build_user_context(self, app, sample_user):
        """Testar construção de contexto do usuário"""
        with app.app_context():
            ai_engine = AIEngine()
            
            with patch.object(ai_engine.weather_service, 'get_weather_for_location') as mock_weather:
                mock_weather.return_value = {'temperature': 22}
                
                context = ai_engine._build_user_context(sample_user)
                
                assert 'user' in context
                assert 'location' in context
                assert 'weather' in context
                assert 'datetime' in context
                assert context['user']['id'] == sample_user.id

class TestCultureService:
    """Testes para o serviço de culturas"""
    
    def test_create_culture(self, app, sample_user):
        """Testar criação de cultura"""
        with app.app_context():
            service = CultureService()
            
            culture_data = {
                'name': 'Batata Doce',
                'type': 'annual',
                'variety': 'Beauregard',
                'area': 1.5,
                'planting_date': '2025-04-15'
            }
            
            culture = service.create_culture(sample_user.id, culture_data)
            
            assert culture.name == 'Batata Doce'
            assert culture.user_id == sample_user.id
            assert culture.area == 1.5
    
    def test_get_user_cultures(self, app, sample_user, sample_culture):
        """Testar obtenção de culturas do usuário"""
        with app.app_context():
            service = CultureService()
            cultures = service.get_user_cultures(sample_user.id)
            
            assert len(cultures) >= 1
            assert sample_culture in cultures
    
    def test_add_activity(self, app, sample_culture):
        """Testar adição de atividade"""
        with app.app_context():
            service = CultureService()
            
            activity_data = {
                'type': 'irrigation',
                'description': 'Irrigação matinal',
                'cost': 15.50
            }
            
            activity = service.add_activity(sample_culture.id, activity_data)
            
            assert activity.culture_id == sample_culture.id
            assert activity.description == 'Irrigação matinal'
            assert activity.cost == 15.50

class TestWeatherService:
    """Testes para o serviço meteorológico"""
    
    @patch('requests.get')
    def test_get_weather_for_location(self, mock_get, app):
        """Testar obtenção de dados meteorológicos"""
        with app.app_context():
            # Configurar mock da resposta
            mock_response = Mock()
            mock_response.json.return_value = {
                'data': [
                    {
                        'tMax': '25',
                        'tMin': '15',
                        'precipitaProb': '10'
                    }
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            service = IPMAService()
            weather = service.get_weather_for_location(41.1579, -8.6291)  # Porto
            
            assert weather is not None
            assert 'current' in weather or 'forecast' in weather

class TestAlertService:
    """Testes para o serviço de alertas"""
    
    def test_create_alert(self, app, sample_user):
        """Testar criação de alerta"""
        with app.app_context():
            service = AlertService()
            
            alert_data = {
                'type': 'weather',
                'title': 'Alerta de Chuva',
                'message': 'Chuva prevista para amanhã',
                'priority': 'medium'
            }
            
            alert = service.create_alert(sample_user.id, alert_data)
            
            assert alert.user_id == sample_user.id
            assert alert.title == 'Alerta de Chuva'
            assert alert.priority == 'medium'
    
    def test_get_active_alerts(self, app, sample_user):
        """Testar obtenção de alertas ativos"""
        with app.app_context():
            service = AlertService()
            
            # Criar alguns alertas
            service.create_alert(sample_user.id, {
                'type': 'weather',
                'title': 'Alerta 1',
                'message': 'Mensagem 1'
            })
            
            service.create_alert(sample_user.id, {
                'type': 'culture',
                'title': 'Alerta 2',
                'message': 'Mensagem 2'
            })
            
            alerts = service.get_active_alerts(sample_user.id)
            assert len(alerts) >= 2
```

**ETAPA 4: Testes de Controladores e Rotas**

Crie testes para os controladores em `tests/test_routes.py`:

```python
# tests/test_routes.py
import pytest
import json
from app.models import User, Culture, Product

class TestAuthRoutes:
    """Testes para rotas de autenticação"""
    
    def test_register_user(self, client):
        """Testar registro de usuário"""
        user_data = {
            'name': 'Carlos Silva',
            'email': 'carlos@teste.com',
            'password': 'senha123',
            'phone': '915678901',
            'location_district': 'Aveiro'
        }
        
        response = client.post('/auth/register', data=user_data)
        assert response.status_code in [200, 302]  # Sucesso ou redirecionamento
    
    def test_login_user(self, client):
        """Testar login de usuário"""
        # Primeiro registrar
        user_data = {
            'name': 'Ana Costa',
            'email': 'ana@teste.com',
            'password': 'senha123',
            'phone': '916789012',
            'location_district': 'Faro'
        }
        client.post('/auth/register', data=user_data)
        
        # Depois fazer login
        login_data = {
            'email': 'ana@teste.com',
            'password': 'senha123'
        }
        
        response = client.post('/auth/login', data=login_data)
        assert response.status_code in [200, 302]
    
    def test_login_invalid_credentials(self, client):
        """Testar login com credenciais inválidas"""
        login_data = {
            'email': 'inexistente@teste.com',
            'password': 'senha_errada'
        }
        
        response = client.post('/auth/login', data=login_data)
        assert response.status_code in [400, 401, 302]  # Erro ou redirecionamento

class TestDashboardRoutes:
    """Testes para rotas do dashboard"""
    
    def test_dashboard_access_authenticated(self, client, auth_headers):
        """Testar acesso ao dashboard autenticado"""
        response = client.get('/dashboard', headers=auth_headers)
        assert response.status_code == 200
    
    def test_dashboard_access_unauthenticated(self, client):
        """Testar acesso ao dashboard sem autenticação"""
        response = client.get('/dashboard')
        assert response.status_code in [302, 401]  # Redirecionamento ou não autorizado

class TestCultureRoutes:
    """Testes para rotas de culturas"""
    
    def test_create_culture(self, client, auth_headers):
        """Testar criação de cultura"""
        culture_data = {
            'name': 'Alface Americana',
            'type': 'horticulture',
            'variety': 'Iceberg',
            'area': 0.5,
            'planting_date': '2025-05-01'
        }
        
        response = client.post('/cultures/new', data=culture_data, headers=auth_headers)
        assert response.status_code in [200, 302]
    
    def test_list_cultures(self, client, auth_headers):
        """Testar listagem de culturas"""
        response = client.get('/cultures', headers=auth_headers)
        assert response.status_code == 200
    
    def test_view_culture_detail(self, client, auth_headers, sample_culture):
        """Testar visualização de detalhes da cultura"""
        response = client.get(f'/cultures/{sample_culture.id}', headers=auth_headers)
        assert response.status_code == 200

class TestMarketplaceRoutes:
    """Testes para rotas do marketplace"""
    
    def test_marketplace_listing(self, client):
        """Testar listagem do marketplace"""
        response = client.get('/marketplace')
        assert response.status_code == 200
    
    def test_create_product(self, client, auth_headers):
        """Testar criação de produto"""
        product_data = {
            'name': 'Morangos Frescos',
            'description': 'Morangos da nossa estufa',
            'price': 4.50,
            'unit': 'kg',
            'quantity_available': 20
        }
        
        response = client.post('/marketplace/new', data=product_data, headers=auth_headers)
        assert response.status_code in [200, 302]
    
    def test_search_products(self, client):
        """Testar busca de produtos"""
        response = client.get('/marketplace?search=tomate')
        assert response.status_code == 200

class TestAPIRoutes:
    """Testes para rotas da API"""
    
    def test_api_weather_endpoint(self, client, auth_headers):
        """Testar endpoint de clima"""
        response = client.get('/api/weather?lat=41.1579&lng=-8.6291', headers=auth_headers)
        assert response.status_code in [200, 503]  # Sucesso ou serviço indisponível
    
    def test_api_recommendations_endpoint(self, client, auth_headers):
        """Testar endpoint de recomendações"""
        response = client.get('/api/recommendations', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_api_alerts_endpoint(self, client, auth_headers):
        """Testar endpoint de alertas"""
        response = client.get('/api/alerts', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
```

### Testes de Validação

**TESTE 1: Execução Completa da Suite de Testes**
```bash
# Executar todos os testes
pytest tests/ -v --cov=app --cov-report=html

# Verificar cobertura mínima
pytest tests/ --cov=app --cov-fail-under=85
```

**TESTE 2: Testes de Performance**
```bash
# Executar testes com medição de tempo
pytest tests/ --durations=10

# Testes de carga básica
pytest tests/test_performance.py -v
```

**TESTE 3: Testes de Integração**
```bash
# Executar apenas testes de integração
pytest tests/test_integration.py -v
```

### Critérios de Aceitação
- Cobertura de testes de pelo menos 85%
- Todos os testes passando sem falhas
- Tempo de execução da suite completa inferior a 5 minutos
- Testes de modelos, serviços e controladores implementados
- Mocks apropriados para integrações externas
- Documentação clara de como executar os testes

### Entregáveis Esperados
1. **Suite Completa de Testes Unitários** com cobertura >= 85%
2. **Configuração de Ambiente de Testes** automatizada
3. **Fixtures e Mocks** para isolamento de componentes
4. **Relatórios de Cobertura** em HTML e terminal
5. **Documentação de Testes** com instruções de execução

### Informações Importantes
- Utilizar pytest como framework principal de testes
- Implementar mocks para todas as integrações externas (IPMA, OpenAI)
- Garantir que testes sejam determinísticos e não dependam de dados externos
- Incluir testes de edge cases e cenários de erro
- Estabelecer convenções claras de nomenclatura para testes

---


## 🔗 PROMPT 2: TESTES DE INTEGRAÇÃO E E2E

### Contexto do Projeto
Você está implementando testes de integração e end-to-end (E2E) para o AgroTech Portugal. Estes testes verificam se diferentes componentes do sistema funcionam corretamente quando integrados, simulando cenários reais de uso e garantindo que o fluxo completo da aplicação funcione conforme esperado.

### Funcionalidade a Implementar
Sistema completo de testes de integração que valide a comunicação entre diferentes módulos, integrações com APIs externas, fluxos de usuário completos e cenários de uso real. Os testes devem cobrir desde o registro de usuário até a utilização completa das funcionalidades principais.

### Arquitetura Proposta

Os testes de integração serão organizados em diferentes categorias, cada uma focada em aspectos específicos da integração entre componentes. A arquitetura utilizará containers Docker para isolar ambientes de teste e garantir consistência.

**Categorias de Testes de Integração:**
- **Testes de Banco de Dados**: Validação de operações CRUD e relacionamentos
- **Testes de API Externa**: Integração com IPMA, OpenAI e outros serviços
- **Testes de Fluxo de Usuário**: Jornadas completas do usuário
- **Testes de Sistema**: Funcionamento integrado de todos os componentes
- **Testes de Performance**: Comportamento sob carga

### Objetivo
Implementar um sistema robusto de testes de integração que garanta que todos os componentes do AgroTech Portugal funcionem harmoniosamente em conjunto, proporcionando uma experiência de usuário fluida e confiável.

### Instruções Detalhadas

**ETAPA 1: Configuração de Ambiente de Integração**

Crie a configuração para testes de integração em `tests/integration/conftest.py`:

```python
# tests/integration/conftest.py
import pytest
import docker
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from app import create_app, db
from app.models import User, Culture, Product

@pytest.fixture(scope="session")
def docker_client():
    """Cliente Docker para testes de integração"""
    return docker.from_env()

@pytest.fixture(scope="session")
def test_database(docker_client):
    """Banco de dados PostgreSQL para testes"""
    container = docker_client.containers.run(
        "postgres:13",
        environment={
            "POSTGRES_DB": "agrotech_test",
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_pass"
        },
        ports={"5432/tcp": 5433},
        detach=True,
        remove=True
    )
    
    # Aguardar banco estar pronto
    time.sleep(10)
    
    yield container
    
    container.stop()

@pytest.fixture(scope="session")
def redis_cache(docker_client):
    """Redis para cache em testes"""
    container = docker_client.containers.run(
        "redis:6-alpine",
        ports={"6379/tcp": 6380},
        detach=True,
        remove=True
    )
    
    time.sleep(5)
    
    yield container
    
    container.stop()

@pytest.fixture
def integration_app(test_database, redis_cache):
    """Aplicação configurada para testes de integração"""
    config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'postgresql://test_user:test_pass@localhost:5433/agrotech_test',
        'REDIS_URL': 'redis://localhost:6380/0',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'integration-test-key'
    }
    
    app = create_app(config)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def selenium_driver():
    """Driver Selenium para testes E2E"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()

@pytest.fixture
def live_server(integration_app):
    """Servidor ao vivo para testes E2E"""
    from threading import Thread
    import socket
    
    # Encontrar porta disponível
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    
    # Iniciar servidor em thread separada
    server_thread = Thread(
        target=lambda: integration_app.run(host='127.0.0.1', port=port, debug=False)
    )
    server_thread.daemon = True
    server_thread.start()
    
    # Aguardar servidor estar pronto
    time.sleep(2)
    
    yield f"http://127.0.0.1:{port}"
```

**ETAPA 2: Testes de Integração de Banco de Dados**

Crie testes de integração de dados em `tests/integration/test_database_integration.py`:

```python
# tests/integration/test_database_integration.py
import pytest
from datetime import date, datetime
from app.models import User, Culture, Recommendation, Product, Alert
from app.services.culture_service import CultureService
from app.services.ai_engine import AIEngine

class TestDatabaseIntegration:
    """Testes de integração com banco de dados"""
    
    def test_user_culture_relationship(self, integration_app):
        """Testar relacionamento usuário-cultura"""
        with integration_app.app_context():
            # Criar usuário
            user = User(
                name='João Agricultor',
                email='joao@quinta.com',
                phone='912345678',
                location_district='Porto'
            )
            user.set_password('senha123')
            db.session.add(user)
            db.session.commit()
            
            # Criar cultura
            culture = Culture(
                user_id=user.id,
                name='Vinha Tinta',
                type='vineyard',
                variety='Touriga Nacional',
                area=5.0,
                planting_date=date(2020, 3, 1)
            )
            db.session.add(culture)
            db.session.commit()
            
            # Verificar relacionamentos
            assert len(user.cultures) == 1
            assert user.cultures[0].name == 'Vinha Tinta'
            assert culture.user.name == 'João Agricultor'
    
    def test_recommendation_cascade_operations(self, integration_app):
        """Testar operações em cascata com recomendações"""
        with integration_app.app_context():
            # Criar usuário e cultura
            user = User(name='Maria', email='maria@teste.com')
            user.set_password('senha')
            db.session.add(user)
            
            culture = Culture(
                user_id=user.id,
                name='Oliveira',
                type='olive_grove',
                area=2.0
            )
            db.session.add(culture)
            db.session.commit()
            
            # Criar recomendação
            recommendation = Recommendation(
                user_id=user.id,
                culture_id=culture.id,
                type='irrigation',
                title='Irrigar oliveiras',
                summary='Necessário irrigar devido ao calor'
            )
            db.session.add(recommendation)
            db.session.commit()
            
            # Verificar que recomendação existe
            assert len(user.recommendations) == 1
            assert len(culture.recommendations) == 1
            
            # Deletar cultura e verificar cascata
            db.session.delete(culture)
            db.session.commit()
            
            # Recomendação deve ter sido deletada também
            remaining_recommendations = Recommendation.query.filter_by(culture_id=culture.id).all()
            assert len(remaining_recommendations) == 0
    
    def test_complex_query_performance(self, integration_app):
        """Testar performance de queries complexas"""
        with integration_app.app_context():
            # Criar dados de teste em massa
            users = []
            for i in range(50):
                user = User(
                    name=f'Usuário {i}',
                    email=f'user{i}@teste.com',
                    location_district='Lisboa'
                )
                user.set_password('senha')
                users.append(user)
            
            db.session.add_all(users)
            db.session.commit()
            
            # Criar culturas para cada usuário
            cultures = []
            for user in users:
                for j in range(3):
                    culture = Culture(
                        user_id=user.id,
                        name=f'Cultura {j}',
                        type='annual',
                        area=1.0 + j
                    )
                    cultures.append(culture)
            
            db.session.add_all(cultures)
            db.session.commit()
            
            # Query complexa com joins
            start_time = datetime.now()
            
            result = db.session.query(User, Culture).join(Culture).filter(
                Culture.area > 1.5
            ).all()
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Verificar resultados e performance
            assert len(result) > 0
            assert execution_time < 1.0  # Deve executar em menos de 1 segundo

class TestServiceIntegration:
    """Testes de integração entre serviços"""
    
    def test_culture_service_with_ai_engine(self, integration_app):
        """Testar integração entre serviço de culturas e motor de IA"""
        with integration_app.app_context():
            # Criar usuário e cultura
            user = User(name='Pedro', email='pedro@teste.com')
            user.set_password('senha')
            db.session.add(user)
            db.session.commit()
            
            # Usar serviço para criar cultura
            culture_service = CultureService()
            culture_data = {
                'name': 'Milho',
                'type': 'annual',
                'area': 3.0,
                'planting_date': '2025-04-01'
            }
            
            culture = culture_service.create_culture(user.id, culture_data)
            
            # Usar motor de IA para gerar recomendações
            ai_engine = AIEngine()
            
            with patch.object(ai_engine.weather_service, 'get_weather_for_location') as mock_weather:
                mock_weather.return_value = {
                    'current': {'temperature': 25, 'humidity': 60}
                }
                
                ai_engine.generate_recommendations_for_user(user)
            
            # Verificar se recomendações foram criadas
            recommendations = ai_engine.get_user_recommendations(user.id)
            assert len(recommendations) >= 0  # Pode não gerar recomendações dependendo da lógica
    
    def test_marketplace_product_search_integration(self, integration_app):
        """Testar integração de busca no marketplace"""
        with integration_app.app_context():
            # Criar usuários e produtos
            users = []
            for i in range(5):
                user = User(name=f'Vendedor {i}', email=f'vendedor{i}@teste.com')
                user.set_password('senha')
                users.append(user)
            
            db.session.add_all(users)
            db.session.commit()
            
            # Criar produtos variados
            products = [
                Product(user_id=users[0].id, name='Tomates Cherry', price=3.0, unit='kg'),
                Product(user_id=users[1].id, name='Tomates Rama', price=2.5, unit='kg'),
                Product(user_id=users[2].id, name='Alface Iceberg', price=1.5, unit='unidade'),
                Product(user_id=users[3].id, name='Cenouras', price=2.0, unit='kg'),
                Product(user_id=users[4].id, name='Batatas', price=1.8, unit='kg')
            ]
            
            db.session.add_all(products)
            db.session.commit()
            
            # Testar busca por termo
            tomate_products = Product.query.filter(
                Product.name.ilike('%tomate%')
            ).all()
            
            assert len(tomate_products) == 2
            
            # Testar busca por faixa de preço
            cheap_products = Product.query.filter(
                Product.price <= 2.0
            ).all()
            
            assert len(cheap_products) >= 2
```

**ETAPA 3: Testes End-to-End (E2E)**

Crie testes E2E em `tests/integration/test_e2e_flows.py`:

```python
# tests/integration/test_e2e_flows.py
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestUserJourneyE2E:
    """Testes end-to-end da jornada do usuário"""
    
    def test_complete_user_registration_and_onboarding(self, selenium_driver, live_server):
        """Testar registro completo e onboarding"""
        driver = selenium_driver
        driver.get(f"{live_server}/auth/register")
        
        # Preencher formulário de registro
        driver.find_element(By.NAME, "name").send_keys("António Silva")
        driver.find_element(By.NAME, "email").send_keys("antonio@teste.com")
        driver.find_element(By.NAME, "password").send_keys("senha123")
        driver.find_element(By.NAME, "phone").send_keys("912345678")
        
        # Selecionar distrito
        district_select = driver.find_element(By.NAME, "location_district")
        district_select.send_keys("Porto")
        
        # Submeter formulário
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Aguardar redirecionamento
        WebDriverWait(driver, 10).until(
            EC.url_contains("/onboarding")
        )
        
        # Verificar se chegou ao onboarding
        assert "/onboarding" in driver.current_url
        
        # Preencher onboarding - Step 1
        driver.find_element(By.NAME, "experiencia").send_keys("intermediario")
        driver.find_element(By.NAME, "tipo_produtor").send_keys("familiar")
        driver.find_element(By.CSS_SELECTOR, "button.next-step").click()
        
        # Step 2 - Interesses
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[name='interesses']")
        checkboxes[0].click()  # Cereais
        checkboxes[1].click()  # Horticultura
        driver.find_element(By.CSS_SELECTOR, "button.next-step").click()
        
        # Step 3 - Localização
        driver.find_element(By.NAME, "location_lat").send_keys("41.1579")
        driver.find_element(By.NAME, "location_lng").send_keys("-8.6291")
        driver.find_element(By.CSS_SELECTOR, "button.finish-onboarding").click()
        
        # Aguardar redirecionamento para dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
        
        assert "/dashboard" in driver.current_url
    
    def test_create_culture_workflow(self, selenium_driver, live_server):
        """Testar fluxo completo de criação de cultura"""
        driver = selenium_driver
        
        # Fazer login primeiro (assumindo usuário já existe)
        driver.get(f"{live_server}/auth/login")
        driver.find_element(By.NAME, "email").send_keys("antonio@teste.com")
        driver.find_element(By.NAME, "password").send_keys("senha123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Navegar para criação de cultura
        driver.get(f"{live_server}/cultures/new")
        
        # Wizard Step 1 - Informações Básicas
        driver.find_element(By.NAME, "name").send_keys("Vinha do Douro")
        
        type_select = driver.find_element(By.NAME, "type")
        type_select.send_keys("vineyard")
        
        driver.find_element(By.NAME, "variety").send_keys("Touriga Nacional")
        driver.find_element(By.CSS_SELECTOR, "button.next-step").click()
        
        # Step 2 - Área e Localização
        driver.find_element(By.NAME, "area").send_keys("2.5")
        driver.find_element(By.CSS_SELECTOR, "button.next-step").click()
        
        # Step 3 - Datas
        driver.find_element(By.NAME, "planting_date").send_keys("2020-03-15")
        driver.find_element(By.NAME, "expected_harvest_date").send_keys("2025-09-15")
        driver.find_element(By.CSS_SELECTOR, "button.next-step").click()
        
        # Step 4 - Solo
        soil_select = driver.find_element(By.NAME, "soil_type")
        soil_select.send_keys("argiloso")
        
        driver.find_element(By.NAME, "soil_ph").send_keys("6.5")
        driver.find_element(By.CSS_SELECTOR, "button.next-step").click()
        
        # Step 5 - Confirmação
        driver.find_element(By.CSS_SELECTOR, "button.create-culture").click()
        
        # Aguardar redirecionamento
        WebDriverWait(driver, 10).until(
            EC.url_contains("/cultures/")
        )
        
        # Verificar se cultura foi criada
        culture_name = driver.find_element(By.CSS_SELECTOR, "h1.culture-name")
        assert "Vinha do Douro" in culture_name.text
    
    def test_marketplace_product_listing_and_contact(self, selenium_driver, live_server):
        """Testar listagem de produto no marketplace e contato"""
        driver = selenium_driver
        
        # Login
        driver.get(f"{live_server}/auth/login")
        driver.find_element(By.NAME, "email").send_keys("antonio@teste.com")
        driver.find_element(By.NAME, "password").send_keys("senha123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Criar produto no marketplace
        driver.get(f"{live_server}/marketplace/new")
        
        driver.find_element(By.NAME, "name").send_keys("Uvas Touriga Nacional")
        driver.find_element(By.NAME, "description").send_keys("Uvas de qualidade superior da nossa vinha")
        driver.find_element(By.NAME, "price").send_keys("3.50")
        driver.find_element(By.NAME, "unit").send_keys("kg")
        driver.find_element(By.NAME, "quantity_available").send_keys("500")
        
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Verificar produto foi listado
        driver.get(f"{live_server}/marketplace")
        
        # Buscar produto
        search_box = driver.find_element(By.NAME, "search")
        search_box.send_keys("Uvas")
        driver.find_element(By.CSS_SELECTOR, "button.search-btn").click()
        
        # Verificar produto aparece nos resultados
        product_cards = driver.find_elements(By.CSS_SELECTOR, ".product-card")
        assert len(product_cards) > 0
        
        # Clicar no produto
        product_cards[0].click()
        
        # Verificar página de detalhes
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-details"))
        )
        
        product_title = driver.find_element(By.CSS_SELECTOR, "h1.product-title")
        assert "Uvas Touriga Nacional" in product_title.text
    
    def test_ai_recommendations_display(self, selenium_driver, live_server):
        """Testar exibição de recomendações de IA"""
        driver = selenium_driver
        
        # Login
        driver.get(f"{live_server}/auth/login")
        driver.find_element(By.NAME, "email").send_keys("antonio@teste.com")
        driver.find_element(By.NAME, "password").send_keys("senha123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Ir para dashboard
        driver.get(f"{live_server}/dashboard")
        
        # Verificar seção de recomendações
        recommendations_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".recommendations-section"))
        )
        
        assert recommendations_section.is_displayed()
        
        # Verificar se há recomendações ou mensagem de "nenhuma recomendação"
        recommendations = driver.find_elements(By.CSS_SELECTOR, ".recommendation-card")
        no_recommendations = driver.find_elements(By.CSS_SELECTOR, ".no-recommendations")
        
        assert len(recommendations) > 0 or len(no_recommendations) > 0
        
        # Se há recomendações, testar interação
        if len(recommendations) > 0:
            # Clicar na primeira recomendação
            recommendations[0].click()
            
            # Verificar modal ou página de detalhes
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".recommendation-details"))
            )
            
            # Testar feedback
            feedback_buttons = driver.find_elements(By.CSS_SELECTOR, ".feedback-btn")
            if len(feedback_buttons) > 0:
                feedback_buttons[0].click()  # Feedback positivo
                
                # Verificar confirmação
                success_message = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".feedback-success"))
                )
                assert success_message.is_displayed()

class TestSystemIntegrationE2E:
    """Testes de integração de sistema completo"""
    
    def test_weather_data_integration(self, selenium_driver, live_server):
        """Testar integração com dados meteorológicos"""
        driver = selenium_driver
        
        # Login
        driver.get(f"{live_server}/auth/login")
        driver.find_element(By.NAME, "email").send_keys("antonio@teste.com")
        driver.find_element(By.NAME, "password").send_keys("senha123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Ir para dashboard
        driver.get(f"{live_server}/dashboard")
        
        # Verificar widget de clima
        weather_widget = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".weather-widget"))
        )
        
        assert weather_widget.is_displayed()
        
        # Verificar se dados meteorológicos são exibidos
        temperature = driver.find_elements(By.CSS_SELECTOR, ".temperature")
        humidity = driver.find_elements(By.CSS_SELECTOR, ".humidity")
        
        # Deve ter pelo menos temperatura ou mensagem de erro
        assert len(temperature) > 0 or "erro" in weather_widget.text.lower()
    
    def test_alert_system_integration(self, selenium_driver, live_server):
        """Testar sistema de alertas integrado"""
        driver = selenium_driver
        
        # Login
        driver.get(f"{live_server}/auth/login")
        driver.find_element(By.NAME, "email").send_keys("antonio@teste.com")
        driver.find_element(By.NAME, "password").send_keys("senha123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Verificar ícone de alertas no header
        alerts_icon = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alerts-icon"))
        )
        
        # Clicar no ícone de alertas
        alerts_icon.click()
        
        # Verificar dropdown ou modal de alertas
        alerts_dropdown = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alerts-dropdown"))
        )
        
        assert alerts_dropdown.is_displayed()
        
        # Verificar se há alertas ou mensagem de "nenhum alerta"
        alert_items = driver.find_elements(By.CSS_SELECTOR, ".alert-item")
        no_alerts = driver.find_elements(By.CSS_SELECTOR, ".no-alerts")
        
        assert len(alert_items) > 0 or len(no_alerts) > 0
```

### Testes de Validação

**TESTE 1: Execução de Testes de Integração**
```bash
# Executar testes de integração
pytest tests/integration/ -v --tb=short

# Executar com relatório de cobertura
pytest tests/integration/ --cov=app --cov-report=term-missing
```

**TESTE 2: Testes E2E com Screenshots**
```bash
# Executar testes E2E com captura de tela em falhas
pytest tests/integration/test_e2e_flows.py -v --capture=no --tb=short
```

**TESTE 3: Testes de Performance de Integração**
```bash
# Executar testes de performance
pytest tests/integration/test_performance.py -v --durations=0
```

### Critérios de Aceitação
- Todos os testes de integração passando
- Testes E2E cobrindo fluxos principais do usuário
- Integração com banco de dados funcionando corretamente
- Mocks apropriados para serviços externos
- Tempo de execução dos testes E2E inferior a 10 minutos
- Documentação clara de como executar testes de integração

### Entregáveis Esperados
1. **Suite de Testes de Integração** completa e funcional
2. **Testes End-to-End** para fluxos críticos do usuário
3. **Configuração Docker** para ambiente de testes
4. **Testes de Performance** básicos
5. **Documentação de Execução** de testes de integração

### Informações Importantes
- Utilizar Docker para isolar ambiente de testes
- Implementar Selenium para testes E2E
- Garantir que testes sejam independentes e possam ser executados em paralelo
- Incluir testes de cenários de erro e edge cases
- Estabelecer timeouts apropriados para testes E2E

---

## 📊 PROMPT 3: MONITORAMENTO DE QUALIDADE E MÉTRICAS

### Contexto do Projeto
Você está implementando um sistema abrangente de monitoramento de qualidade e métricas para o AgroTech Portugal. Este sistema deve fornecer visibilidade em tempo real sobre a saúde da aplicação, performance, erros e comportamento dos usuários, permitindo detecção proativa de problemas e otimização contínua.

### Funcionalidade a Implementar
Sistema completo de monitoramento que inclui coleta de métricas de performance, logging estruturado, alertas automáticos, dashboards de monitoramento e análise de comportamento do usuário. O sistema deve ser capaz de detectar problemas antes que afetem os usuários e fornecer insights para melhorias contínuas.

### Arquitetura Proposta

O sistema de monitoramento será baseado em múltiplas camadas de observabilidade, incluindo logs, métricas e traces. A arquitetura utilizará ferramentas modernas de monitoramento e será integrada nativamente à aplicação.

**Componentes do Sistema de Monitoramento:**
- **Logging Estruturado**: Logs centralizados com contexto rico
- **Métricas de Performance**: Tempo de resposta, throughput, recursos
- **Health Checks**: Verificações automáticas de saúde do sistema
- **Error Tracking**: Rastreamento e análise de erros
- **User Analytics**: Análise de comportamento e uso
- **Alerting**: Sistema de alertas automáticos

### Objetivo
Implementar um sistema robusto de monitoramento que proporcione visibilidade completa sobre o funcionamento do AgroTech Portugal, permitindo manutenção proativa, otimização de performance e garantia de qualidade de serviço para os agricultores portugueses.

### Instruções Detalhadas

**ETAPA 1: Sistema de Logging Estruturado**

Configure logging estruturado em `app/utils/logging_config.py`:

```python
# app/utils/logging_config.py
import logging
import json
import sys
from datetime import datetime
from flask import request, g
from functools import wraps
import traceback

class StructuredFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Adicionar contexto da requisição se disponível
        if hasattr(g, 'user_id'):
            log_entry['user_id'] = g.user_id
        
        if request:
            log_entry['request'] = {
                'method': request.method,
                'url': request.url,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            }
        
        # Adicionar informações de exceção se presente
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Adicionar campos extras
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging(app):
    """Configurar sistema de logging"""
    
    # Configurar formatter estruturado
    formatter = StructuredFormatter()
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Handler para arquivo
    file_handler = logging.FileHandler('logs/agrotech.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Configurar logger da aplicação
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    # Configurar loggers de bibliotecas
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    return app.logger

def log_performance(func):
    """Decorator para logging de performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        
        try:
            result = func(*args, **kwargs)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logging.getLogger(__name__).info(
                f"Function {func.__name__} executed successfully",
                extra={
                    'extra_fields': {
                        'function': func.__name__,
                        'duration_seconds': duration,
                        'status': 'success'
                    }
                }
            )
            
            return result
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logging.getLogger(__name__).error(
                f"Function {func.__name__} failed: {str(e)}",
                exc_info=True,
                extra={
                    'extra_fields': {
                        'function': func.__name__,
                        'duration_seconds': duration,
                        'status': 'error',
                        'error_type': type(e).__name__
                    }
                }
            )
            
            raise
    
    return wrapper

class AuditLogger:
    """Logger para auditoria de ações do usuário"""
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
    
    def log_user_action(self, user_id, action, resource_type, resource_id=None, details=None):
        """Registrar ação do usuário"""
        self.logger.info(
            f"User action: {action}",
            extra={
                'extra_fields': {
                    'audit_type': 'user_action',
                    'user_id': user_id,
                    'action': action,
                    'resource_type': resource_type,
                    'resource_id': resource_id,
                    'details': details or {}
                }
            }
        )
    
    def log_system_event(self, event_type, description, severity='info', details=None):
        """Registrar evento do sistema"""
        log_method = getattr(self.logger, severity, self.logger.info)
        
        log_method(
            f"System event: {description}",
            extra={
                'extra_fields': {
                    'audit_type': 'system_event',
                    'event_type': event_type,
                    'severity': severity,
                    'details': details or {}
                }
            }
        )

# Instância global do audit logger
audit_logger = AuditLogger()
```

**ETAPA 2: Sistema de Métricas de Performance**

Crie sistema de métricas em `app/utils/metrics.py`:

```python
# app/utils/metrics.py
import time
import psutil
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from flask import request, g
from functools import wraps
import json

class MetricsCollector:
    """Coletor de métricas de performance"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()
    
    def increment_counter(self, name, value=1, tags=None):
        """Incrementar contador"""
        with self.lock:
            key = self._build_key(name, tags)
            self.counters[key] += value
    
    def set_gauge(self, name, value, tags=None):
        """Definir valor de gauge"""
        with self.lock:
            key = self._build_key(name, tags)
            self.gauges[key] = value
    
    def record_histogram(self, name, value, tags=None):
        """Registrar valor em histograma"""
        with self.lock:
            key = self._build_key(name, tags)
            self.histograms[key].append({
                'value': value,
                'timestamp': datetime.utcnow()
            })
    
    def record_timing(self, name, duration, tags=None):
        """Registrar tempo de execução"""
        self.record_histogram(f"{name}.duration", duration, tags)
    
    def _build_key(self, name, tags):
        """Construir chave da métrica"""
        if tags:
            tag_str = ','.join([f"{k}={v}" for k, v in sorted(tags.items())])
            return f"{name}[{tag_str}]"
        return name
    
    def get_metrics_summary(self):
        """Obter resumo das métricas"""
        with self.lock:
            summary = {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {}
            }
            
            # Calcular estatísticas dos histogramas
            for key, values in self.histograms.items():
                if values:
                    numeric_values = [v['value'] for v in values]
                    summary['histograms'][key] = {
                        'count': len(numeric_values),
                        'min': min(numeric_values),
                        'max': max(numeric_values),
                        'avg': sum(numeric_values) / len(numeric_values),
                        'p95': self._percentile(numeric_values, 95),
                        'p99': self._percentile(numeric_values, 99)
                    }
            
            return summary
    
    def _percentile(self, values, percentile):
        """Calcular percentil"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]

# Instância global do coletor
metrics = MetricsCollector()

def track_performance(metric_name=None, tags=None):
    """Decorator para rastrear performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = metric_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                metrics.record_timing(name, duration, tags)
                metrics.increment_counter(f"{name}.calls", tags=tags)
                metrics.increment_counter(f"{name}.success", tags=tags)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                metrics.record_timing(name, duration, tags)
                metrics.increment_counter(f"{name}.calls", tags=tags)
                metrics.increment_counter(f"{name}.errors", tags={
                    **(tags or {}),
                    'error_type': type(e).__name__
                })
                
                raise
        
        return wrapper
    return decorator

class SystemMetricsCollector:
    """Coletor de métricas do sistema"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """Iniciar coleta de métricas do sistema"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._collect_loop)
            self.thread.daemon = True
            self.thread.start()
    
    def stop(self):
        """Parar coleta de métricas"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _collect_loop(self):
        """Loop de coleta de métricas"""
        while self.running:
            try:
                self._collect_system_metrics()
                time.sleep(30)  # Coletar a cada 30 segundos
            except Exception as e:
                print(f"Erro na coleta de métricas: {e}")
    
    def _collect_system_metrics(self):
        """Coletar métricas do sistema"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.set_gauge('system.cpu.percent', cpu_percent)
        
        # Memória
        memory = psutil.virtual_memory()
        metrics.set_gauge('system.memory.percent', memory.percent)
        metrics.set_gauge('system.memory.available_mb', memory.available / 1024 / 1024)
        
        # Disco
        disk = psutil.disk_usage('/')
        metrics.set_gauge('system.disk.percent', disk.percent)
        metrics.set_gauge('system.disk.free_gb', disk.free / 1024 / 1024 / 1024)
        
        # Processos
        process_count = len(psutil.pids())
        metrics.set_gauge('system.processes.count', process_count)

# Instância global do coletor de sistema
system_metrics = SystemMetricsCollector()

def track_request_metrics():
    """Middleware para rastrear métricas de requisições"""
    def before_request():
        g.start_time = time.time()
        
        # Incrementar contador de requisições
        metrics.increment_counter('http.requests.total', tags={
            'method': request.method,
            'endpoint': request.endpoint or 'unknown'
        })
    
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Registrar tempo de resposta
            metrics.record_timing('http.request.duration', duration, tags={
                'method': request.method,
                'endpoint': request.endpoint or 'unknown',
                'status_code': response.status_code
            })
            
            # Incrementar contador de respostas
            metrics.increment_counter('http.responses.total', tags={
                'method': request.method,
                'endpoint': request.endpoint or 'unknown',
                'status_code': response.status_code
            })
        
        return response
    
    return before_request, after_request
```

**ETAPA 3: Health Checks e Monitoramento de Saúde**

Implemente health checks em `app/utils/health_checks.py`:

```python
# app/utils/health_checks.py
import time
import requests
from datetime import datetime, timedelta
from flask import current_app
from app.models import db, User
from app.services.weather_service import IPMAService
from app.utils.metrics import metrics

class HealthCheck:
    """Classe base para health checks"""
    
    def __init__(self, name, timeout=10):
        self.name = name
        self.timeout = timeout
    
    def check(self):
        """Executar verificação de saúde"""
        start_time = time.time()
        
        try:
            result = self._perform_check()
            duration = time.time() - start_time
            
            metrics.record_timing(f'health_check.{self.name}.duration', duration)
            metrics.increment_counter(f'health_check.{self.name}.success')
            
            return {
                'name': self.name,
                'status': 'healthy',
                'duration_ms': round(duration * 1000, 2),
                'timestamp': datetime.utcnow().isoformat(),
                'details': result
            }
            
        except Exception as e:
            duration = time.time() - start_time
            
            metrics.record_timing(f'health_check.{self.name}.duration', duration)
            metrics.increment_counter(f'health_check.{self.name}.errors')
            
            return {
                'name': self.name,
                'status': 'unhealthy',
                'duration_ms': round(duration * 1000, 2),
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _perform_check(self):
        """Implementar verificação específica"""
        raise NotImplementedError

class DatabaseHealthCheck(HealthCheck):
    """Verificação de saúde do banco de dados"""
    
    def __init__(self):
        super().__init__('database')
    
    def _perform_check(self):
        # Testar conexão básica
        result = db.session.execute('SELECT 1').scalar()
        
        # Testar query simples
        user_count = User.query.count()
        
        return {
            'connection': 'ok',
            'user_count': user_count,
            'query_test': result == 1
        }

class WeatherServiceHealthCheck(HealthCheck):
    """Verificação de saúde do serviço meteorológico"""
    
    def __init__(self):
        super().__init__('weather_service')
        self.weather_service = IPMAService()
    
    def _perform_check(self):
        # Testar API do IPMA
        weather_data = self.weather_service.get_weather_for_location(41.1579, -8.6291)
        
        return {
            'api_accessible': weather_data is not None,
            'data_available': bool(weather_data.get('current') if weather_data else False)
        }

class DiskSpaceHealthCheck(HealthCheck):
    """Verificação de espaço em disco"""
    
    def __init__(self, threshold_percent=90):
        super().__init__('disk_space')
        self.threshold_percent = threshold_percent
    
    def _perform_check(self):
        import psutil
        
        disk_usage = psutil.disk_usage('/')
        used_percent = (disk_usage.used / disk_usage.total) * 100
        
        if used_percent > self.threshold_percent:
            raise Exception(f"Disk usage {used_percent:.1f}% exceeds threshold {self.threshold_percent}%")
        
        return {
            'used_percent': round(used_percent, 1),
            'free_gb': round(disk_usage.free / 1024 / 1024 / 1024, 2),
            'total_gb': round(disk_usage.total / 1024 / 1024 / 1024, 2)
        }

class MemoryHealthCheck(HealthCheck):
    """Verificação de uso de memória"""
    
    def __init__(self, threshold_percent=85):
        super().__init__('memory')
        self.threshold_percent = threshold_percent
    
    def _perform_check(self):
        import psutil
        
        memory = psutil.virtual_memory()
        
        if memory.percent > self.threshold_percent:
            raise Exception(f"Memory usage {memory.percent:.1f}% exceeds threshold {self.threshold_percent}%")
        
        return {
            'used_percent': round(memory.percent, 1),
            'available_gb': round(memory.available / 1024 / 1024 / 1024, 2),
            'total_gb': round(memory.total / 1024 / 1024 / 1024, 2)
        }

class HealthCheckManager:
    """Gerenciador de health checks"""
    
    def __init__(self):
        self.checks = [
            DatabaseHealthCheck(),
            WeatherServiceHealthCheck(),
            DiskSpaceHealthCheck(),
            MemoryHealthCheck()
        ]
    
    def run_all_checks(self):
        """Executar todas as verificações"""
        results = []
        overall_status = 'healthy'
        
        for check in self.checks:
            result = check.check()
            results.append(result)
            
            if result['status'] == 'unhealthy':
                overall_status = 'unhealthy'
        
        return {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': results
        }
    
    def run_check(self, check_name):
        """Executar verificação específica"""
        for check in self.checks:
            if check.name == check_name:
                return check.check()
        
        raise ValueError(f"Health check '{check_name}' not found")

# Instância global do gerenciador
health_manager = HealthCheckManager()
```

### Testes de Validação

**TESTE 1: Validação do Sistema de Logging**
```python
# Testar logging estruturado
import logging
from app.utils.logging_config import setup_logging, audit_logger

logger = setup_logging(app)
logger.info("Teste de log estruturado", extra={
    'extra_fields': {'test_field': 'test_value'}
})

audit_logger.log_user_action(1, 'create_culture', 'culture', 123)
```

**TESTE 2: Validação de Métricas**
```python
# Testar coleta de métricas
from app.utils.metrics import metrics, track_performance

@track_performance('test.function')
def test_function():
    time.sleep(0.1)
    return "success"

test_function()
summary = metrics.get_metrics_summary()
print(json.dumps(summary, indent=2))
```

**TESTE 3: Validação de Health Checks**
```python
# Testar health checks
from app.utils.health_checks import health_manager

results = health_manager.run_all_checks()
print(json.dumps(results, indent=2))
```

### Critérios de Aceitação
- Sistema de logging estruturado funcionando
- Métricas de performance sendo coletadas
- Health checks executando corretamente
- Dashboards básicos de monitoramento
- Alertas automáticos configurados
- Documentação de monitoramento completa

### Entregáveis Esperados
1. **Sistema de Logging Estruturado** com contexto rico
2. **Coleta de Métricas** automatizada e abrangente
3. **Health Checks** para todos os componentes críticos
4. **Dashboard de Monitoramento** básico
5. **Sistema de Alertas** automático

### Informações Importantes
- Utilizar JSON para logs estruturados
- Implementar métricas de negócio além de técnicas
- Configurar alertas para problemas críticos
- Garantir que monitoramento não impacte performance
- Incluir métricas de experiência do usuário

---

