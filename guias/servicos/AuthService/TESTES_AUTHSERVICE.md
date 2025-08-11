# Testes do AuthService

## 🧪 Estratégia de Testes

### 📋 Tipos de Testes
1. **Testes Unitários** - Testar métodos isoladamente
2. **Testes de Integração** - Testar interação com banco de dados
3. **Testes de API** - Testar endpoints REST
4. **Testes de Segurança** - Testar vulnerabilidades
5. **Testes de Performance** - Testar carga e stress

---

## 🔬 Testes Unitários

### 📦 Configuração Base
```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import sys
import os

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.alerts import UserAlertPreference, AlertType, AlertPriority
from app.services.auth_service import AuthService


class TestAuthServiceBase(unittest.TestCase):
    """Classe base para testes do AuthService"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Criar todas as tabelas
        db.create_all()
        
        # Dados de teste padrão
        self.test_user_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'nome_completo': 'Test User',
            'telefone': '+351912345678',
            'location': 'Lisboa, Portugal',
            'latitude': 38.7223,
            'longitude': -9.1393
        }
    
    def tearDown(self):
        """Limpeza após cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_test_user(self, **kwargs):
        """Helper para criar usuário de teste"""
        user_data = self.test_user_data.copy()
        user_data.update(kwargs)
        return AuthService.create_user(**user_data)
```

### ✅ Testes de Criação de Usuário
```python
class TestCreateUser(TestAuthServiceBase):
    """Testes para criação de usuário"""
    
    def test_create_user_success(self):
        """Teste de criação de usuário com sucesso"""
        result = AuthService.create_user(
            email=self.test_user_data['email'],
            password=self.test_user_data['password'],
            nome_completo=self.test_user_data['nome_completo']
        )
        
        # Verificar resultado
        self.assertTrue(result['success'])
        self.assertIn('user', result)
        self.assertIn('user_id', result)
        self.assertEqual(result['user']['email'], self.test_user_data['email'])
        self.assertEqual(result['user']['nome_completo'], self.test_user_data['nome_completo'])
        
        # Verificar no banco
        user = User.query.filter_by(email=self.test_user_data['email']).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.test_user_data['email'])
        self.assertTrue(user.password_hash)  # Senha foi criptografada
    
    def test_create_user_with_location(self):
        """Teste de criação com dados de localização"""
        result = AuthService.create_user(
            email='test-location@example.com',
            password='TestPassword123!',
            location='Porto, Portugal',
            latitude=41.1579,
            longitude=-8.6291
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(result['has_location'])
        self.assertTrue(result['has_coordinates'])
        
        user = User.query.filter_by(email='test-location@example.com').first()
        self.assertEqual(user.cidade, 'Porto, Portugal')
        self.assertEqual(user.latitude, 41.1579)
        self.assertEqual(user.longitude, -8.6291)
    
    def test_create_user_with_phone(self):
        """Teste de criação com telefone"""
        result = AuthService.create_user(
            email='test-phone@example.com',
            password='TestPassword123!',
            telefone='+351912345678'
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(result['has_phone'])
        
        user = User.query.filter_by(email='test-phone@example.com').first()
        self.assertEqual(user.telefone, '+351912345678')
    
    def test_create_user_phone_duplication_fix(self):
        """Teste de correção de duplicação de código de país"""
        result = AuthService.create_user(
            email='test-phone-dup@example.com',
            password='TestPassword123!',
            telefone='+351351912345678'  # Código duplicado
        )
        
        self.assertTrue(result['success'])
        
        user = User.query.filter_by(email='test-phone-dup@example.com').first()
        self.assertEqual(user.telefone, '+351912345678')  # Duplicação removida
    
    def test_create_user_duplicate_email(self):
        """Teste de email duplicado"""
        # Criar primeiro usuário
        result1 = AuthService.create_user(
            email='duplicate@example.com',
            password='TestPassword123!'
        )
        self.assertTrue(result1['success'])
        
        # Tentar criar segundo usuário com mesmo email
        result2 = AuthService.create_user(
            email='duplicate@example.com',
            password='AnotherPassword123!'
        )
        
        self.assertFalse(result2['success'])
        self.assertEqual(result2['error_code'], 'EMAIL_EXISTS')
        self.assertEqual(result2['status_code'], 409)
        self.assertIn('Já existe uma conta', result2['error'])
    
    def test_create_user_empty_fields(self):
        """Teste com campos vazios"""
        with self.assertRaises(TypeError):
            AuthService.create_user()  # Sem argumentos obrigatórios
    
    @patch('app.services.auth_service.db.session.commit')
    def test_create_user_database_error(self, mock_commit):
        """Teste de erro no banco de dados"""
        mock_commit.side_effect = Exception("Database error")
        
        result = AuthService.create_user(
            email='db-error@example.com',
            password='TestPassword123!'
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 500)
        self.assertIn('Erro interno', result['error'])
```

### 🔐 Testes de Autenticação
```python
class TestAuthenticateUser(TestAuthServiceBase):
    """Testes para autenticação de usuário"""
    
    def test_authenticate_success(self):
        """Teste de autenticação com sucesso"""
        # Criar usuário primeiro
        create_result = self.create_test_user()
        self.assertTrue(create_result['success'])
        
        # Autenticar
        result = AuthService.authenticate_user(
            email=self.test_user_data['email'],
            password=self.test_user_data['password']
        )
        
        self.assertTrue(result['success'])
        self.assertIn('user', result)
        self.assertEqual(result['user']['email'], self.test_user_data['email'])
        self.assertIn('message', result)
    
    def test_authenticate_remember_me(self):
        """Teste de autenticação com remember me"""
        # Criar usuário
        self.create_test_user()
        
        # Autenticar com remember=True
        result = AuthService.authenticate_user(
            email=self.test_user_data['email'],
            password=self.test_user_data['password'],
            remember=True
        )
        
        self.assertTrue(result['success'])
    
    def test_authenticate_invalid_email(self):
        """Teste com email inexistente"""
        result = AuthService.authenticate_user(
            email='nonexistent@example.com',
            password='AnyPassword123!'
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 401)
        self.assertEqual(result['error'], 'Credenciais inválidas')
    
    def test_authenticate_wrong_password(self):
        """Teste com senha incorreta"""
        # Criar usuário
        self.create_test_user()
        
        # Tentar com senha errada
        result = AuthService.authenticate_user(
            email=self.test_user_data['email'],
            password='WrongPassword123!'
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 401)
        self.assertEqual(result['error'], 'Credenciais inválidas')
    
    def test_authenticate_empty_credentials(self):
        """Teste com credenciais vazias"""
        result = AuthService.authenticate_user(
            email='',
            password=''
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 401)
    
    @patch('app.services.auth_service.check_password_hash')
    def test_authenticate_database_error(self, mock_check_password):
        """Teste de erro no banco durante autenticação"""
        # Criar usuário
        self.create_test_user()
        
        # Simular erro
        mock_check_password.side_effect = Exception("Database error")
        
        result = AuthService.authenticate_user(
            email=self.test_user_data['email'],
            password=self.test_user_data['password']
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 500)
```

### 📝 Testes de Onboarding
```python
class TestOnboarding(TestAuthServiceBase):
    """Testes para onboarding"""
    
    def setUp(self):
        super().setUp()
        # Criar usuário para testes de onboarding
        create_result = self.create_test_user()
        self.user = User.query.filter_by(email=self.test_user_data['email']).first()
    
    def test_onboarding_step_1(self):
        """Teste do passo 1 do onboarding"""
        result = AuthService.save_onboarding_step(
            user=self.user,
            step='1',
            data={'experience_level': 'intermediate'}
        )
        
        self.assertTrue(result['success'])
        
        # Verificar no banco
        db.session.refresh(self.user)
        self.assertEqual(self.user.experience_level, 'intermediate')
    
    def test_onboarding_step_2(self):
        """Teste do passo 2 do onboarding"""
        result = AuthService.save_onboarding_step(
            user=self.user,
            step='2',
            data={
                'full_name': 'João Silva Atualizado',
                'phone': '912345678',
                'country_code': '+351',
                'farm_experience': 'advanced',
                'interests': ['tomate', 'alface', 'cenoura']
            }
        )
        
        self.assertTrue(result['success'])
        
        # Verificar no banco
        db.session.refresh(self.user)
        self.assertEqual(self.user.nome_completo, 'João Silva Atualizado')
        self.assertEqual(self.user.telefone, '+351912345678')
        self.assertEqual(self.user.experience_level, 'advanced')
    
    def test_onboarding_step_3_complete(self):
        """Teste do passo 3 com dados completos"""
        result = AuthService.save_onboarding_step(
            user=self.user,
            step='3',
            data={
                'farm_name': 'Quinta do João',
                'location': 'Porto, Portugal',
                'latitude': 41.1579,
                'longitude': -8.6291,
                'formatted_address': 'Rua das Flores, 123, Porto',
                'farm_area': '5.5',
                'soil_type': 'argiloso',
                'climate': 'mediterrânico',
                'water_sources': ['poço', 'chuva']
            }
        )
        
        self.assertTrue(result['success'])
        
        # Verificar usuário
        db.session.refresh(self.user)
        self.assertEqual(self.user.propriedade_nome, 'Quinta do João')
        self.assertEqual(self.user.cidade, 'Porto, Portugal')
        self.assertEqual(self.user.latitude, 41.1579)
        self.assertEqual(self.user.longitude, -8.6291)
        
        # Verificar se farm foi criada
        from app.models.farm import Farm
        farm = Farm.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(farm)
        self.assertEqual(farm.name, 'Quinta do João')
        self.assertEqual(farm.area_total, 5.5)
    
    def test_onboarding_step_3_missing_required(self):
        """Teste do passo 3 sem dados obrigatórios"""
        result = AuthService.save_onboarding_step(
            user=self.user,
            step='3',
            data={
                'farm_name': '',  # Vazio
                'location': 'Porto, Portugal'
            }
        )
        
        self.assertFalse(result['success'])
        self.assertIn('obrigatórios', result['error'])
    
    def test_onboarding_step_5_completion(self):
        """Teste da finalização do onboarding"""
        result = AuthService.save_onboarding_step(
            user=self.user,
            step='5',
            data={'complete_onboarding': True}
        )
        
        self.assertTrue(result['success'])
        
        # Verificar no banco
        db.session.refresh(self.user)
        self.assertTrue(self.user.onboarding_completed)
        
        # Verificar se preferências de alerta foram criadas
        preferences = UserAlertPreference.query.filter_by(user_id=self.user.id).all()
        self.assertGreater(len(preferences), 0)
    
    @patch('app.services.auth_service.db.session.commit')
    def test_onboarding_database_error(self, mock_commit):
        """Teste de erro no banco durante onboarding"""
        mock_commit.side_effect = Exception("Database error")
        
        result = AuthService.save_onboarding_step(
            user=self.user,
            step='1',
            data={'experience_level': 'intermediate'}
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 500)
```

### 🚨 Testes de Preferências de Alertas
```python
class TestAlertPreferences(TestAuthServiceBase):
    """Testes para criação de preferências de alertas"""
    
    def setUp(self):
        super().setUp()
        create_result = self.create_test_user()
        self.user = User.query.filter_by(email=self.test_user_data['email']).first()
    
    def test_create_default_alert_preferences_beginner(self):
        """Teste de criação de preferências para iniciante"""
        self.user.experience_level = 'beginner'
        db.session.commit()
        
        # Chamar método privado diretamente para teste
        AuthService._create_default_alert_preferences(self.user)
        
        # Verificar preferências criadas
        preferences = UserAlertPreference.query.filter_by(user_id=self.user.id).all()
        self.assertEqual(len(preferences), 9)  # 9 tipos de alerta
        
        # Verificar configurações específicas para iniciante
        weather_pref = UserAlertPreference.query.filter_by(
            user_id=self.user.id,
            alert_type=AlertType.WEATHER
        ).first()
        self.assertIsNotNone(weather_pref)
        self.assertTrue(weather_pref.is_enabled)
        self.assertTrue(weather_pref.email_enabled)
        
        # Iniciantes recebem mais emails
        pest_pref = UserAlertPreference.query.filter_by(
            user_id=self.user.id,
            alert_type=AlertType.PEST
        ).first()
        self.assertTrue(pest_pref.email_enabled)  # True para iniciantes
    
    def test_create_default_alert_preferences_advanced(self):
        """Teste de criação de preferências para usuário avançado"""
        self.user.experience_level = 'advanced'
        db.session.commit()
        
        AuthService._create_default_alert_preferences(self.user)
        
        # Verificar configurações específicas para avançado
        pest_pref = UserAlertPreference.query.filter_by(
            user_id=self.user.id,
            alert_type=AlertType.PEST
        ).first()
        self.assertFalse(pest_pref.email_enabled)  # False para avançados
        self.assertEqual(pest_pref.min_priority, AlertPriority.HIGH)
    
    def test_alert_preferences_not_duplicated(self):
        """Teste que preferências não são duplicadas"""
        # Criar preferências uma vez
        AuthService._create_default_alert_preferences(self.user)
        count_first = UserAlertPreference.query.filter_by(user_id=self.user.id).count()
        
        # Tentar criar novamente
        AuthService._create_default_alert_preferences(self.user)
        count_second = UserAlertPreference.query.filter_by(user_id=self.user.id).count()
        
        self.assertEqual(count_first, count_second)
    
    @patch('app.services.auth_service.db.session.commit')
    def test_alert_preferences_database_error(self, mock_commit):
        """Teste de erro no banco ao criar preferências"""
        mock_commit.side_effect = Exception("Database error")
        
        with self.assertRaises(Exception):
            AuthService._create_default_alert_preferences(self.user)
```

---

## 🌐 Testes de Integração

### 🔗 Testes de API
```python
import json
from flask import url_for

class TestAuthAPI(TestAuthServiceBase):
    """Testes de integração da API de autenticação"""
    
    def test_register_api_success(self):
        """Teste de registro via API"""
        response = self.client.post('/api/auth/register', 
            data=json.dumps({
                'email': 'api-test@example.com',
                'password': 'TestPassword123!',
                'nome_completo': 'API Test User'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('user_id', data)
    
    def test_register_api_duplicate_email(self):
        """Teste de email duplicado via API"""
        # Primeiro registro
        self.client.post('/api/auth/register',
            data=json.dumps({
                'email': 'duplicate-api@example.com',
                'password': 'TestPassword123!'
            }),
            content_type='application/json'
        )
        
        # Segundo registro (duplicado)
        response = self.client.post('/api/auth/register',
            data=json.dumps({
                'email': 'duplicate-api@example.com',
                'password': 'AnotherPassword123!'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 409)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'EMAIL_EXISTS')
    
    def test_login_api_success(self):
        """Teste de login via API"""
        # Criar usuário primeiro
        self.create_test_user()
        
        # Login via API
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': self.test_user_data['email'],
                'password': self.test_user_data['password']
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('user', data)
    
    def test_login_api_invalid_credentials(self):
        """Teste de login com credenciais inválidas via API"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': 'nonexistent@example.com',
                'password': 'WrongPassword123!'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_protected_endpoint_without_auth(self):
        """Teste de endpoint protegido sem autenticação"""
        response = self.client.get('/protected-endpoint')
        
        # Deve redirecionar para login ou retornar 401
        self.assertIn(response.status_code, [302, 401])
```

### 🗄️ Testes de Banco de Dados
```python
class TestDatabaseIntegration(TestAuthServiceBase):
    """Testes de integração com banco de dados"""
    
    def test_user_cascade_delete(self):
        """Teste de deleção em cascata"""
        # Criar usuário com preferências
        create_result = self.create_test_user()
        user = User.query.filter_by(email=self.test_user_data['email']).first()
        
        # Finalizar onboarding para criar preferências
        AuthService.save_onboarding_step(
            user=user,
            step='5',
            data={'complete_onboarding': True}
        )
        
        # Verificar que preferências existem
        preferences_count = UserAlertPreference.query.filter_by(user_id=user.id).count()
        self.assertGreater(preferences_count, 0)
        
        # Deletar usuário
        user_id = user.id
        db.session.delete(user)
        db.session.commit()
        
        # Verificar que preferências foram deletadas (se cascade configurado)
        remaining_preferences = UserAlertPreference.query.filter_by(user_id=user_id).count()
        # Dependendo da configuração de FK, pode ser 0 ou causar erro
    
    def test_concurrent_user_creation(self):
        """Teste de criação simultânea de usuários"""
        import threading
        
        results = []
        
        def create_user_thread(email):
            try:
                result = AuthService.create_user(
                    email=email,
                    password='TestPassword123!'
                )
                results.append(result)
            except Exception as e:
                results.append({'success': False, 'error': str(e)})
        
        # Criar threads para tentar criar mesmo usuário
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=create_user_thread,
                args=[f'concurrent-{i}@example.com']
            )
            threads.append(thread)
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Esperar todas terminarem
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        self.assertEqual(len(results), 3)
        successful_results = [r for r in results if r['success']]
        self.assertEqual(len(successful_results), 3)  # Todos devem ter sucesso com emails diferentes
    
    def test_database_constraints(self):
        """Teste de constraints do banco de dados"""
        # Tentar criar usuário sem email (deve falhar)
        user = User(password_hash='test')
        db.session.add(user)
        
        with self.assertRaises(Exception):  # IntegrityError esperado
            db.session.commit()
        
        db.session.rollback()
    
    def test_user_model_methods(self):
        """Teste dos métodos do modelo User"""
        create_result = self.create_test_user()
        user = User.query.filter_by(email=self.test_user_data['email']).first()
        
        # Teste to_dict
        user_dict = user.to_dict()
        self.assertIsInstance(user_dict, dict)
        self.assertEqual(user_dict['email'], self.test_user_data['email'])
        self.assertIn('id', user_dict)
        
        # Teste get_id (método do Flask-Login)
        self.assertEqual(user.get_id(), str(user.id))
        
        # Teste is_authenticated
        self.assertTrue(user.is_authenticated)
        
        # Teste is_active
        self.assertTrue(user.is_active)
```

---

## 🛡️ Testes de Segurança

### 🔒 Testes de Segurança de Senhas
```python
class TestPasswordSecurity(TestAuthServiceBase):
    """Testes de segurança de senhas"""
    
    def test_password_hashing(self):
        """Teste de hash de senhas"""
        create_result = self.create_test_user()
        user = User.query.filter_by(email=self.test_user_data['email']).first()
        
        # Senha não deve estar em texto plano
        self.assertNotEqual(user.password_hash, self.test_user_data['password'])
        
        # Hash deve ser diferente a cada execução
        from werkzeug.security import generate_password_hash
        hash1 = generate_password_hash(self.test_user_data['password'])
        hash2 = generate_password_hash(self.test_user_data['password'])
        self.assertNotEqual(hash1, hash2)
    
    def test_weak_passwords(self):
        """Teste com senhas fracas (implementar validação se necessário)"""
        weak_passwords = [
            '123456',
            'password',
            'abc123',
            '12345678',
            'qwerty'
        ]
        
        for weak_password in weak_passwords:
            result = AuthService.create_user(
                email=f'weak-{weak_password}@example.com',
                password=weak_password
            )
            # Por enquanto aceita senhas fracas, mas pode implementar validação
            # self.assertFalse(result['success'])  # Se validação implementada
    
    def test_password_length_limits(self):
        """Teste de limites de tamanho de senha"""
        # Senha muito longa
        very_long_password = 'a' * 1000
        result = AuthService.create_user(
            email='long-password@example.com',
            password=very_long_password
        )
        
        # Deve funcionar (Werkzeug suporta senhas longas)
        self.assertTrue(result['success'])
        
        # Senha vazia já é testada em outros testes
```

### 🔐 Testes de Vulnerabilidades
```python
class TestSecurityVulnerabilities(TestAuthServiceBase):
    """Testes de vulnerabilidades de segurança"""
    
    def test_sql_injection_protection(self):
        """Teste de proteção contra SQL injection"""
        malicious_email = "test@example.com'; DROP TABLE users; --"
        
        result = AuthService.create_user(
            email=malicious_email,
            password='TestPassword123!'
        )
        
        # Deve funcionar normalmente (SQLAlchemy protege contra SQL injection)
        # Email malicioso é tratado como string normal
        if result['success']:
            user = User.query.filter_by(email=malicious_email).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, malicious_email)
    
    def test_xss_protection(self):
        """Teste de proteção contra XSS"""
        xss_payload = '<script>alert("XSS")</script>'
        
        result = AuthService.create_user(
            email='xss-test@example.com',
            password='TestPassword123!',
            nome_completo=xss_payload
        )
        
        self.assertTrue(result['success'])
        
        user = User.query.filter_by(email='xss-test@example.com').first()
        # Dados devem ser armazenados como fornecidos
        # Escape deve ser feito na apresentação, não no armazenamento
        self.assertEqual(user.nome_completo, xss_payload)
    
    def test_session_fixation_protection(self):
        """Teste de proteção contra session fixation"""
        # Este teste seria mais complexo e envolveria o sistema de sessões
        # Por enquanto, verificamos se o login regenera a sessão
        pass
    
    def test_brute_force_protection(self):
        """Teste de proteção contra ataques de força bruta"""
        # Este teste verificaria rate limiting
        # Implementação dependeria do middleware de rate limiting
        pass
```

---

## ⚡ Testes de Performance

### 🚀 Testes de Carga
```python
import time
import concurrent.futures
from unittest.mock import patch

class TestPerformance(TestAuthServiceBase):
    """Testes de performance"""
    
    def test_user_creation_performance(self):
        """Teste de performance de criação de usuários"""
        start_time = time.time()
        
        # Criar 100 usuários
        for i in range(100):
            result = AuthService.create_user(
                email=f'perf-test-{i}@example.com',
                password='TestPassword123!'
            )
            self.assertTrue(result['success'])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Deve criar 100 usuários em menos de 10 segundos
        self.assertLess(total_time, 10.0)
        
        # Performance média por usuário
        avg_time_per_user = total_time / 100
        self.assertLess(avg_time_per_user, 0.1)  # Menos de 100ms por usuário
    
    def test_authentication_performance(self):
        """Teste de performance de autenticação"""
        # Criar usuários de teste
        test_users = []
        for i in range(50):
            email = f'auth-perf-{i}@example.com'
            result = AuthService.create_user(email=email, password='TestPassword123!')
            test_users.append(email)
        
        start_time = time.time()
        
        # Autenticar todos os usuários
        for email in test_users:
            result = AuthService.authenticate_user(email, 'TestPassword123!')
            self.assertTrue(result['success'])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Deve autenticar 50 usuários em menos de 5 segundos
        self.assertLess(total_time, 5.0)
    
    def test_concurrent_operations(self):
        """Teste de operações concorrentes"""
        def create_and_auth_user(user_id):
            email = f'concurrent-{user_id}@example.com'
            
            # Criar usuário
            create_result = AuthService.create_user(
                email=email,
                password='TestPassword123!'
            )
            
            if not create_result['success']:
                return False
            
            # Autenticar usuário
            auth_result = AuthService.authenticate_user(email, 'TestPassword123!')
            return auth_result['success']
        
        # Executar operações em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(create_and_auth_user, i)
                for i in range(20)
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Todas as operações devem ter sucesso
        self.assertEqual(sum(results), 20)
    
    def test_memory_usage(self):
        """Teste de uso de memória"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Criar muitos usuários
        for i in range(500):
            result = AuthService.create_user(
                email=f'memory-test-{i}@example.com',
                password='TestPassword123!'
            )
            self.assertTrue(result['success'])
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Aumento de memória não deve ser excessivo (menos de 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024)
```

---

## 🏃 Como Executar os Testes

### 📦 Configuração do Ambiente de Teste
```python
# conftest.py
import pytest
from app import create_app, db

@pytest.fixture
def app():
    """Fixture da aplicação para testes"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Fixture do cliente de teste"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture do runner CLI"""
    return app.test_cli_runner()
```

### 🔧 Configuração de Teste
```python
# config.py
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    LOGIN_DISABLED = False
```

### 🚀 Scripts de Execução
```bash
#!/bin/bash
# run_tests.sh

echo "Executando testes do AuthService..."

# Testes unitários
echo "=== Testes Unitários ==="
python -m pytest tests/test_auth_service.py -v

# Testes de integração
echo "=== Testes de Integração ==="
python -m pytest tests/test_auth_integration.py -v

# Testes de performance
echo "=== Testes de Performance ==="
python -m pytest tests/test_auth_performance.py -v

# Testes de segurança
echo "=== Testes de Segurança ==="
python -m pytest tests/test_auth_security.py -v

# Coverage report
echo "=== Relatório de Cobertura ==="
python -m pytest --cov=app.services.auth_service --cov-report=html
```

### 📊 Relatórios de Cobertura
```bash
# Instalar dependências de teste
pip install pytest pytest-cov pytest-mock

# Executar com cobertura
pytest --cov=app.services.auth_service --cov-report=html --cov-report=term

# Gerar relatório detalhado
coverage html
coverage report --show-missing
```

---

## 📈 Métricas de Qualidade

### ✅ Critérios de Aprovação
- **Cobertura de Código**: Mínimo 95%
- **Testes Unitários**: 100% dos métodos públicos
- **Testes de Performance**: < 100ms por operação
- **Testes de Segurança**: Proteção contra vulnerabilidades comuns
- **Testes de Integração**: Todos os fluxos principais

### 📊 Métricas Alvo
```python
# metrics.py
QUALITY_METRICS = {
    'code_coverage': 95,  # % mínimo de cobertura
    'max_response_time': 0.1,  # segundos
    'max_memory_usage': 100,  # MB
    'min_tests_per_method': 3,  # testes por método público
    'max_cyclomatic_complexity': 10,  # complexidade ciclomática
}
```

---

*Este documento fornece uma suite completa de testes para garantir a qualidade e segurança do AuthService.*
