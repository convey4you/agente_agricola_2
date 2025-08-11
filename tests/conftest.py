"""
Configurações e fixtures para testes do Agente Agrícola
SPRINT 3 - Sistema de Testes Unitários Abrangente
Implementação completa com AAA (Arrange, Act, Assert)
CORREÇÕES DE SEGURANÇA - Auditoria Técnica
"""
import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, date
from werkzeug.security import generate_password_hash

# Adicionar o diretório raiz do projeto ao path para imports
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

@pytest.fixture(scope='session')
def app():
    """Fixture da aplicação Flask para testes com configuração completa"""
    from app import create_app, db
    
    # Usar configuração de teste existente
    app = create_app('testing')
    
    # Sobrescrever algumas configurações específicas para teste
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,  # Desabilitar CSRF apenas para testes
        'SECRET_KEY': 'test-secret-key-sprint3-security',
        'OPENAI_API_KEY': 'test-openai-key',
        'IPMA_API_URL': 'http://test-ipma-api.com',
        'REDIS_URL': 'redis://localhost:6379/15',
        'MAIL_SUPPRESS_SEND': True,
        'LOGIN_DISABLED': False,
        # Configurações de segurança para testes
        'BCRYPT_LOG_ROUNDS': 4,  # Mais rápido para testes
        'RATELIMIT_ENABLED': True,  # Testar rate limiting
        'SESSION_COOKIE_SECURE': False,  # HTTP permitido para testes
        'SESSION_COOKIE_HTTPONLY': True,
        'PERMANENT_SESSION_LIFETIME': 3600  # 1 hora para testes
    })
    
    with app.app_context():
        db.create_all()
        
        # Importar todos os modelos para garantir que estejam registrados
        from app.models import user, culture, activity, alerts, marketplace
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_user(app):
    """Fixture para usuário de teste com senha segura"""
    from app.models.user import User
    from app import db
    
    with app.app_context():
        user = User(
            name='Test User',
            email='test@example.com',
            is_active=True,
            created_at=datetime.utcnow()
        )
        user.set_password('TestPass123!')  # Senha forte para testes
        
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        # Cleanup
        db.session.delete(user)
        db.session.commit()

@pytest.fixture 
def admin_user(app):
    """Fixture para usuário administrador"""
    from app.models.user import User
    from app import db
    
    with app.app_context():
        admin = User(
            name='Admin User',
            email='admin@example.com',
            is_active=True,
            is_admin=True,
            created_at=datetime.utcnow()
        )
        admin.set_password('AdminPass123!')
        
        db.session.add(admin)
        db.session.commit()
        
        yield admin
        
        # Cleanup
        db.session.delete(admin)
        db.session.commit()

@pytest.fixture
def authenticated_client(client, test_user):
    """Cliente com usuário autenticado"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True
    
    yield client

@pytest.fixture
def security_test_data():
    """Dados para testes de segurança"""
    return {
        'sql_injection_payloads': [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "' UNION SELECT * FROM users WHERE '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ],
        'xss_payloads': [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>"
        ],
        'invalid_emails': [
            'invalid-email',
            '@invalid.com',
            'test@',
            'test..test@example.com',
            'test@invalid',
            'test@.com',
            ''
        ],
        'weak_passwords': [
            'password',
            '12345678',
            'PASSWORD',
            'Pass123',
            'pass!'
        ],
        'strong_passwords': [
            'StrongPass123!',
            'MySecure@Pass456',
            'Test#Password789',
            'Secure$123Pass'
        ]
    }

@pytest.fixture
def client(app):
    """Cliente de teste Flask"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner de comandos CLI para testes"""
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    """Sessão de banco de dados para testes"""
    from app import db
    
    with app.app_context():
        yield db.session
        db.session.rollback()
        db.session.close()

@pytest.fixture
def auth_headers(client):
    """Headers de autenticação para testes de API"""
    # Criar usuário de teste
    user_data = {
        'name': 'João Silva Teste',
        'email': 'joao@teste.com',
        'password': 'senha123',
        'phone': '912345678',
        'location_district': 'Porto'
    }
    
    # Registrar usuário
    response = client.post('/auth/register', data=user_data, follow_redirects=True)
    
    # Fazer login
    login_response = client.post('/auth/login', data={
        'email': 'joao@teste.com',
        'password': 'senha123'
    }, follow_redirects=True)
    
    # Extrair cookie de sessão
    cookies = []
    for cookie in client.cookie_jar:
        cookies.append(f"{cookie.name}={cookie.value}")
    
    return {'Cookie': '; '.join(cookies)} if cookies else {}

@pytest.fixture
def sample_user(app, db_session):
    """Usuário de exemplo para testes"""
    from app.models.user import User
    from app import db
    import uuid
    
    # Criar dentro do contexto da aplicação
    with app.app_context():
        # Usar email único para evitar conflitos
        unique_email = f"test_{uuid.uuid4().hex[:8]}@exemplo.com"
        
        user = User(
            nome_completo='Maria Santos',
            email=unique_email,
            telefone='913456789',
            cidade='Lisboa',
            latitude=38.7223,
            longitude=-9.1393,
            experience_level='intermediate',
            propriedade_nome='Fazenda Familiar',
            ativo=True,
            onboarding_completed=True
        )
        user.set_password('senha123')
        
        db.session.add(user)
        db.session.commit()
        yield user

@pytest.fixture
def sample_culture(sample_user, db_session):
    """Cultura de exemplo para testes"""
    from app.models.culture import Culture
    from app import db
    
    culture = Culture(
        user_id=sample_user.id,
        name='Milho Doce',
        culture_type='annual',
        variety='Golden Bantam',
        area=2.5,
        planting_date=date(2025, 3, 15),
        expected_harvest_date=date(2025, 7, 15),
        soil_type='argiloso',
        soil_ph=6.5,
        irrigation_system='aspersao',
        status='growing',
        location_lat=sample_user.location_lat,
        location_lng=sample_user.location_lng
    )
    
    db.session.add(culture)
    db.session.commit()
    
    yield culture
    
    # Cleanup
    db.session.delete(culture)
    db.session.commit()

@pytest.fixture
def sample_alert(sample_user, db_session):
    """Alerta de exemplo para testes"""
    from app.models.alerts import Alert
    from app import db
    
    alert = Alert(
        user_id=sample_user.id,
        type='weather',
        title='Alerta de Chuva',
        message='Chuva prevista para as próximas 24 horas',
        priority='medium',
        status='active'
    )
    
    db.session.add(alert)
    db.session.commit()
    
    yield alert
    
    # Cleanup
    db.session.delete(alert)
    db.session.commit()

@pytest.fixture
def sample_product(sample_user, db_session):
    """Produto do marketplace para testes"""
    from app.models.marketplace import MarketplaceItem
    from app import db
    
    product = MarketplaceItem(
        user_id=sample_user.id,
        name='Tomates Frescos',
        description='Tomates orgânicos da nossa quinta',
        price=2.50,
        unit='kg',
        quantity_available=100.0,
        location_district='Lisboa',
        category='vegetables',
        is_active=True
    )
    
    db.session.add(product)
    db.session.commit()
    
    yield product
    
    # Cleanup
    db.session.delete(product)
    db.session.commit()

@pytest.fixture
def mock_weather_service():
    """Mock do serviço meteorológico"""
    with patch('app.services.weather_service.IPMAService') as mock_service:
        mock_instance = Mock()
        mock_instance.get_weather_for_location.return_value = {
            'current': {
                'temperature': 25.0,
                'humidity': 70,
                'wind_speed': 10,
                'precipitation_probability': 20,
                'description': 'Partly cloudy'
            },
            'forecast': [
                {
                    'date': '2025-08-02',
                    'temp_max': 28,
                    'temp_min': 18,
                    'precipitation_prob': 10
                }
            ]
        }
        mock_service.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_openai_service():
    """Mock do serviço OpenAI"""
    with patch('openai.ChatCompletion.create') as mock_openai:
        mock_openai.return_value = {
            'choices': [{
                'message': {
                    'content': 'Recomendação de teste gerada pela IA'
                }
            }]
        }
        yield mock_openai

@pytest.fixture
def mock_current_user(sample_user):
    """Mock do usuário atual para testes"""
    with patch('flask_login.current_user', sample_user):
        yield sample_user

@pytest.fixture
def temp_upload_folder():
    """Pasta temporária para uploads em testes"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

# Fixtures para testes de performance
@pytest.fixture
def performance_data():
    """Dados para testes de performance"""
    return {
        'users_count': 10,
        'cultures_per_user': 3,
        'alerts_per_user': 5,
        'products_per_user': 2
    }

# Fixtures para testes de integração
@pytest.fixture(scope='session')
def integration_db():
    """Banco de dados para testes de integração"""
    # Usar banco PostgreSQL de teste se disponível
    test_db_url = os.environ.get('TEST_DATABASE_URL', 'sqlite:///test_integration.db')
    return test_db_url
    user.username = 'test_user'
    user.email = 'test@example.com'
    return user

@pytest.fixture
def mock_farm():
    """Mock de uma fazenda para testes"""
    farm = MagicMock()
    farm.id = 1
    farm.name = 'Fazenda Teste'
    farm.user_id = 1
    return farm

@pytest.fixture
def mock_user_model():
    """Mock do modelo User para testes de banco de dados"""
    user_mock = MagicMock()
    user_mock.query.filter_by.return_value.first.return_value = None
    return user_mock

@pytest.fixture
def mock_farm_model():
    """Mock do modelo Farm para testes de banco de dados"""
    farm_mock = MagicMock()
    farm_instance = MagicMock()
    farm_instance.id = 1
    farm_instance.user_id = 1
    farm_mock.query.filter_by.return_value.first.return_value = farm_instance
    return farm_mock

@pytest.fixture
def portuguese_test_data():
    """Dados específicos portugueses para testes"""
    return {
        'districts': [
            'Aveiro', 'Beja', 'Braga', 'Bragança', 'Castelo Branco',
            'Coimbra', 'Évora', 'Faro', 'Guarda', 'Leiria',
            'Lisboa', 'Portalegre', 'Porto', 'Santarém', 'Setúbal',
            'Viana do Castelo', 'Vila Real', 'Viseu',
            'Região Autónoma dos Açores', 'Região Autónoma da Madeira'
        ],
        'coordinates': {
            'lisboa': {'lat': 38.7223, 'lng': -9.1393},
            'porto': {'lat': 41.1579, 'lng': -8.6291},
            'coimbra': {'lat': 40.2033, 'lng': -8.4103},
            'evora': {'lat': 38.5667, 'lng': -7.9000},
            'faro': {'lat': 37.0194, 'lng': -7.9322},
            'funchal': {'lat': 32.6669, 'lng': -16.9241},
            'ponta_delgada': {'lat': 37.7412, 'lng': -25.6756}
        },
        'cultures': {
            'oliveira': ['Galega Vulgar', 'Cobrançosa', 'Picual'],
            'vinha': ['Touriga Nacional', 'Touriga Franca', 'Alvarinho'],
            'tomate': ['Heinz 9553', 'San Marzano', 'Coração de Boi'],
            'trigo': ['Antequera', 'Almansor', 'Claudio']
        }
    }

@pytest.fixture
def security_test_vectors():
    """Vetores de teste para segurança"""
    return {
        'sql_injection': [
            "'; DROP TABLE users; --",
            "admin'--",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'pass'); --"
        ],
        'xss': [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "'>><script>alert('xss')</script>"
        ]
    }

# Markers personalizados para categorizar testes
def pytest_configure(config):
    """Configuração de markers personalizados"""
    config.addinivalue_line(
        "markers", "auth: marca testes relacionados à autenticação"
    )
    config.addinivalue_line(
        "markers", "culture: marca testes relacionados às culturas"
    )
    config.addinivalue_line(
        "markers", "dashboard: marca testes relacionados ao dashboard"
    )
    config.addinivalue_line(
        "markers", "agent: marca testes relacionados ao agente IA"
    )
    config.addinivalue_line(
        "markers", "marketplace: marca testes relacionados ao marketplace"
    )
    config.addinivalue_line(
        "markers", "performance: marca testes de performance"
    )
    config.addinivalue_line(
        "markers", "security: marca testes de segurança"
    )
    # PROMPT 4 - Novos markers para sistema de alertas
    config.addinivalue_line(
        "markers", "alerts: marca testes do sistema de alertas"
    )
    config.addinivalue_line(
        "markers", "alerts_api: marca testes da API de alertas"
    )
    config.addinivalue_line(
        "markers", "alerts_integration: marca testes de integração de alertas"
    )


# PROMPT 4 - Fixtures específicas para testes de alertas
@pytest.fixture
def sample_user_for_alerts(init_database):
    """Criar usuário específico para testes de alertas"""
    from app.models.user import User
    from app import db
    
    user = User(
        email='alerts_test@example.com',
        nome_completo='Alerts Test User',
        password_hash=generate_password_hash('alerts123'),
        ativo=True,
        onboarding_completed=True
    )
    
    db.session.add(user)
    db.session.commit()
    
    return user


@pytest.fixture
def authenticated_client_alerts(client, sample_user_for_alerts):
    """Cliente autenticado específico para testes de alertas"""
    # Fazer login
    login_data = {
        'email': 'alerts_test@example.com',
        'password': 'alerts123'
    }
    
    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    
    return client


@pytest.fixture
def sample_alerts_comprehensive(init_database, sample_user_for_alerts):
    """Criar conjunto abrangente de alertas para testes"""
    from app.models.alerts import Alert, AlertType, AlertPriority, AlertStatus
    from app import db
    
    alerts = [
        # Alerta crítico ativo
        Alert(
            user_id=sample_user_for_alerts.id,
            type=AlertType.WEATHER,
            priority=AlertPriority.CRITICAL,
            status=AlertStatus.ACTIVE,
            title='Tempestade Severa Aproximando',
            message='Alerta meteorológico crítico: tempestade severa prevista nas próximas 2 horas.',
            created_at=datetime.now(timezone.utc)
        ),
        # Alerta médio ativo
        Alert(
            user_id=sample_user_for_alerts.id,
            type=AlertType.IRRIGATION,
            priority=AlertPriority.MEDIUM,
            status=AlertStatus.ACTIVE,
            title='Sistema de Irrigação',
            message='Nível de água no reservatório abaixo do recomendado.',
            created_at=datetime.now(timezone.utc)
        ),
        # Alerta lido
        Alert(
            user_id=sample_user_for_alerts.id,
            type=AlertType.DISEASE,
            priority=AlertPriority.MEDIUM,
            status=AlertStatus.READ,
            title='Monitoramento de Pragas',
            message='Detectada presença de insetos nas culturas de tomate.',
            read_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        ),
        # Alerta dispensado
        Alert(
            user_id=sample_user_for_alerts.id,
            type=AlertType.GENERAL,
            priority=AlertPriority.LOW,
            status=AlertStatus.DISMISSED,
            title='Manutenção Programada',
            message='Lembrete: manutenção do equipamento agendada para amanhã.',
            dismissed_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
    ]
    
    for alert in alerts:
        db.session.add(alert)
    
    db.session.commit()
    
    return alerts


@pytest.fixture
def valid_alert_data_comprehensive():
    """Dados completos válidos para criação de alerta"""
    return {
        'type': 'weather',
        'priority': 'high',
        'title': 'Teste de Alerta Automatizado',
        'message': 'Esta é uma mensagem de teste criada automaticamente durante a validação do sistema.',
        'action_text': 'Ver Detalhes',
        'action_url': '/weather/details'
    }


@pytest.fixture
def invalid_alert_data_comprehensive():
    """Conjunto abrangente de dados inválidos para teste"""
    return [
        # Tipo inválido
        {
            'type': 'invalid_type',
            'priority': 'high',
            'title': 'Teste',
            'message': 'Mensagem'
        },
        # Prioridade inválida
        {
            'type': 'weather',
            'priority': 'invalid_priority',
            'title': 'Teste',
            'message': 'Mensagem'
        },
        # Título vazio
        {
            'type': 'weather',
            'priority': 'high',
            'title': '',
            'message': 'Mensagem'
        },
        # Mensagem vazia
        {
            'type': 'weather',
            'priority': 'high',
            'title': 'Teste',
            'message': ''
        },
        # Título muito longo
        {
            'type': 'weather',
            'priority': 'high',
            'title': 'A' * 201,  # Máximo 200 caracteres
            'message': 'Mensagem'
        }
    ]


@pytest.fixture
def api_headers_alerts():
    """Headers específicos para API de alertas"""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'AlertsTestClient/1.0'
    }


# Helper functions para testes de alertas
def create_test_alert_helper(user_id, **kwargs):
    """Helper para criar alerta de teste"""
    from app.models.alerts import Alert, AlertType, AlertPriority, AlertStatus
    from app import db
    
    default_data = {
        'user_id': user_id,
        'type': AlertType.GENERAL,
        'priority': AlertPriority.MEDIUM,
        'status': AlertStatus.ACTIVE,
        'title': 'Alerta de Teste Automatizado',
        'message': 'Mensagem gerada automaticamente para teste',
        'created_at': datetime.now(timezone.utc)
    }
    
    default_data.update(kwargs)
    
    alert = Alert(**default_data)
    db.session.add(alert)
    db.session.commit()
    
    return alert


def login_alerts_user(client, email='alerts_test@example.com', password='alerts123'):
    """Helper específico para login de usuário de testes de alertas"""
    return client.post('/auth/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)

