# Prompts Claude Sonnet 4 - Sprint 1 Correções Críticas
## AgroTech Portugal - Diagnóstico e Correção de Problemas Bloqueadores

**Documento**: Prompts Específicos para Claude Sonnet 4  
**Projeto**: Sistema de Agente Agrícola Inteligente  
**Sprint**: 1 - Correções Críticas  
**Período**: 29 de julho - 02 de agosto de 2025  
**Autor**: Gerente de Tecnologia  
**Baseado em**: Relatório QA + Análise de Problemas

---

## 📋 INSTRUÇÕES PARA USO DOS PROMPTS

### Como Utilizar Este Documento
Este documento contém prompts específicos e detalhados para Claude Sonnet 4, organizados por tarefa crítica. Cada prompt inclui contexto completo, código existente, problema específico e instruções detalhadas para resolução.

### Estrutura dos Prompts
Cada prompt segue o padrão:
- **Contexto do Projeto**: Informações sobre o AgroTech Portugal
- **Problema Específico**: Descrição detalhada do issue
- **Código Atual**: Trechos relevantes do código existente
- **Objetivo**: O que precisa ser alcançado
- **Instruções Detalhadas**: Passos específicos para implementação
- **Critérios de Aceitação**: Como validar o sucesso

### Ordem de Execução
Os prompts devem ser executados na ordem apresentada, pois há dependências entre as correções.

---

## 🚨 PROMPT 1: DIAGNÓSTICO COMPLETO DO SISTEMA DE SESSÕES

### Contexto do Projeto
Você está trabalhando no AgroTech Portugal, um sistema de agente agrícola inteligente desenvolvido em Flask para o mercado português. O sistema utiliza Flask-Login para autenticação e tem uma arquitetura MVC bem estruturada.

### Problema Identificado
Durante testes de QA, foi identificado um problema crítico: usuários conseguem fazer login com sucesso e acessar o dashboard principal, mas ao tentar navegar para outras seções protegidas (como /culturas), são automaticamente redirecionados para a tela de login, indicando falha na persistência de sessão.

### Sintomas Observados
- Login funciona corretamente no dashboard principal
- Redirecionamento automático para `/auth/login` ao acessar `/culturas`
- Perda de contexto de autenticação entre rotas
- Middleware `@login_required` não reconhece usuário logado
- Cookies de sessão aparentam estar sendo criados

### Código Atual Relevante

**app/__init__.py (configuração Flask-Login):**
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    from app.routes import auth, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    
    return app
```

**app/config.py:**
```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///agrotech.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

**app/routes/main.py (rotas protegidas):**
```python
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/culturas')
@login_required
def culturas():
    return render_template('culturas/index.html')
```

**app/routes/auth.py (autenticação):**
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.models import User
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Email ou senha inválidos')
    
    return render_template('auth/login.html')
```

### Objetivo
Realizar diagnóstico completo e sistemático do sistema de autenticação Flask-Login para identificar a causa raiz do problema de persistência de sessão, fornecendo análise detalhada e plano de correção específico.

### Instruções Detalhadas

**ETAPA 1: Análise de Configuração**
Analise minuciosamente a configuração atual e identifique possíveis problemas em:

1. **Configuração do SECRET_KEY**: Verifique se está sendo definida corretamente e se é consistente entre requests
2. **Configuração de Cookies**: Analise se as configurações de cookie estão adequadas para o ambiente
3. **LoginManager**: Verifique se está sendo inicializado corretamente
4. **User Loader**: Confirme se o callback está funcionando adequadamente

**ETAPA 2: Análise de Middleware**
Examine o middleware de autenticação e identifique problemas em:

1. **Decorators @login_required**: Verifique se estão sendo aplicados corretamente
2. **current_user**: Analise se está sendo carregado adequadamente
3. **Imports**: Confirme se todos os imports estão corretos
4. **Ordem de decorators**: Verifique se a ordem está adequada

**ETAPA 3: Análise de Sessão**
Investigue o funcionamento das sessões:

1. **Criação de sessão**: Como e quando as sessões são criadas
2. **Persistência**: Se as sessões estão sendo mantidas entre requests
3. **Cookies**: Se os cookies estão sendo enviados/recebidos corretamente
4. **Expiração**: Se há problemas de timeout ou expiração

**ETAPA 4: Análise de Banco de Dados**
Verifique questões relacionadas ao banco:

1. **Queries de usuário**: Se User.query.get() está funcionando
2. **Conexões**: Se não há problemas de conexão com o banco
3. **Concorrência**: Se há problemas de concorrência em SQLite
4. **Integridade de dados**: Se os dados de usuário estão íntegros

**ETAPA 5: Implementação de Logging**
Implemente logging detalhado para debugging:

```python
import logging

# Configure logging para debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Adicione logs em pontos críticos:
# - Login/logout events
# - Session creation/destruction  
# - User loading attempts
# - Authentication checks
```

### Entregáveis Esperados

1. **Relatório de Diagnóstico Detalhado** contendo:
   - Identificação precisa da causa raiz
   - Análise de cada componente do sistema de autenticação
   - Evidências técnicas dos problemas encontrados
   - Impacto de cada problema identificado

2. **Código de Logging Implementado** para:
   - Monitoramento de eventos de login/logout
   - Tracking de criação/destruição de sessões
   - Debugging de carregamento de usuários
   - Verificação de autenticação

3. **Plano de Correção Específico** incluindo:
   - Passos detalhados para correção
   - Código específico a ser alterado
   - Ordem de implementação das correções
   - Testes necessários para validação

### Critérios de Aceitação
- Causa raiz identificada com evidências técnicas
- Logging implementado em pontos críticos
- Plano de correção detalhado e específico
- Código pronto para implementação das correções

### Informações Adicionais
- O sistema está em ambiente de desenvolvimento local
- Utiliza SQLite como banco de dados
- Flask versão 2.x com Flask-Login
- Problema afeta 100% dos usuários
- Prioridade máxima para resolução

---

## 🚨 PROMPT 2: IMPLEMENTAÇÃO DA CORREÇÃO DE SESSÕES

### Contexto do Projeto
Você está implementando a correção para o problema de persistência de sessão no AgroTech Portugal, baseado no diagnóstico realizado anteriormente. O sistema precisa manter usuários logados durante a navegação entre diferentes seções protegidas.

### Problema a Resolver
Implementar correção completa do sistema de autenticação Flask-Login para garantir que usuários permaneçam autenticados durante toda a sessão de navegação, eliminando redirecionamentos inesperados para a tela de login.

### Diagnóstico Prévio (Assumindo Resultados Típicos)
Com base em problemas comuns em sistemas Flask-Login, as principais causas prováveis são:
- Configuração inadequada de SECRET_KEY
- Problemas na configuração de cookies de sessão
- Middleware de autenticação com falhas
- User loader callback com problemas

### Objetivo
Implementar correção robusta e segura do sistema de autenticação, garantindo persistência adequada de sessão e funcionamento correto de todas as rotas protegidas.

### Instruções Detalhadas

**CORREÇÃO 1: Configuração Flask Aprimorada**

Atualize o arquivo `app/config.py` com configurações robustas:

```python
import os
from datetime import timedelta

class Config:
    # SECRET_KEY mais robusta
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'agrotech-portugal-secret-key-2025-dev'
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = False  # True em produção HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configurações de banco
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///agrotech.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
```

**CORREÇÃO 2: LoginManager Aprimorado**

Atualize `app/__init__.py` com configuração robusta do LoginManager:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import logging

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    
    # Inicializar extensões
    db.init_app(app)
    
    # Configuração robusta do LoginManager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            from app.models import User
            app.logger.info(f'Loading user: {user_id}')
            user = User.query.get(int(user_id))
            if user:
                app.logger.info(f'User loaded successfully: {user.email}')
            else:
                app.logger.warning(f'User not found: {user_id}')
            return user
        except (ValueError, TypeError) as e:
            app.logger.error(f'Error loading user {user_id}: {str(e)}')
            return None
        except Exception as e:
            app.logger.error(f'Unexpected error loading user {user_id}: {str(e)}')
            return None
    
    # Registrar blueprints
    from app.routes import auth, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    
    return app
```

**CORREÇÃO 3: Middleware de Autenticação Robusto**

Crie `app/middleware/auth.py`:

```python
from functools import wraps
from flask import session, request, redirect, url_for, flash, current_app
from flask_login import current_user

def ensure_session_valid(f):
    """Middleware para garantir validade da sessão"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log da tentativa de acesso
        current_app.logger.info(f'Accessing {request.endpoint} - User authenticated: {current_user.is_authenticated}')
        
        # Verificar se há inconsistência na sessão
        if 'user_id' in session and not current_user.is_authenticated:
            current_app.logger.warning('Session inconsistency detected - clearing session')
            session.clear()
            flash('Sua sessão expirou. Por favor, faça login novamente.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Verificar se usuário está realmente autenticado
        if not current_user.is_authenticated:
            current_app.logger.info('User not authenticated - redirecting to login')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def log_auth_event(event_type, user_id=None, details=None):
    """Função para logging de eventos de autenticação"""
    current_app.logger.info(f'AUTH_EVENT: {event_type} - User: {user_id} - Details: {details}')
```

**CORREÇÃO 4: Rotas Protegidas Atualizadas**

Atualize `app/routes/main.py`:

```python
from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.middleware.auth import ensure_session_valid, log_auth_event

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/dashboard')
@login_required
@ensure_session_valid
def dashboard():
    log_auth_event('DASHBOARD_ACCESS', current_user.id)
    current_app.logger.info(f'Dashboard accessed by user: {current_user.email}')
    
    # Verificação adicional de segurança
    if not current_user.is_authenticated:
        current_app.logger.error('User not authenticated in dashboard - this should not happen')
        return redirect(url_for('auth.login'))
    
    return render_template('dashboard.html', user=current_user)

@bp.route('/culturas')
@login_required
@ensure_session_valid
def culturas():
    log_auth_event('CULTURAS_ACCESS', current_user.id)
    current_app.logger.info(f'Culturas accessed by user: {current_user.email}')
    
    # Verificação adicional de segurança
    if not current_user.is_authenticated:
        current_app.logger.error('User not authenticated in culturas - this should not happen')
        flash('Sessão expirada. Por favor, faça login novamente.', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('culturas/index.html', user=current_user)

@bp.route('/agente')
@login_required
@ensure_session_valid
def agente():
    log_auth_event('AGENTE_ACCESS', current_user.id)
    return render_template('agente/chat.html', user=current_user)

@bp.route('/marketplace')
@login_required
@ensure_session_valid
def marketplace():
    log_auth_event('MARKETPLACE_ACCESS', current_user.id)
    return render_template('marketplace/index.html', user=current_user)
```

**CORREÇÃO 5: Processo de Login Aprimorado**

Atualize `app/routes/auth.py`:

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, current_user
from app.models import User
from app import db
from app.middleware.auth import log_auth_event
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se já está logado, redirecionar
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        current_app.logger.info(f'Login attempt for email: {email}')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Login bem-sucedido
            login_user(user, remember=remember)
            
            # Atualizar último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log do evento
            log_auth_event('LOGIN_SUCCESS', user.id, f'IP: {request.remote_addr}')
            current_app.logger.info(f'User {user.email} logged in successfully')
            
            # Verificar se há next page
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            flash(f'Bem-vindo de volta, {user.nome or user.email}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            # Login falhado
            log_auth_event('LOGIN_FAILED', None, f'Email: {email}, IP: {request.remote_addr}')
            current_app.logger.warning(f'Failed login attempt for email: {email}')
            flash('Email ou senha inválidos', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    user_id = current_user.id
    user_email = current_user.email
    
    log_auth_event('LOGOUT', user_id)
    current_app.logger.info(f'User {user_email} logged out')
    
    logout_user()
    session.clear()  # Limpar completamente a sessão
    
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('auth.login'))
```

**CORREÇÃO 6: Modelo de Usuário Atualizado**

Certifique-se de que o modelo User em `app/models.py` está adequado:

```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def __repr__(self):
        return f'<User {self.email}>'
```

### Testes de Validação

**TESTE 1: Fluxo Básico de Autenticação**
```python
# Teste manual:
# 1. Acessar /auth/login
# 2. Fazer login com credenciais válidas
# 3. Verificar redirecionamento para dashboard
# 4. Navegar para /culturas
# 5. Verificar que NÃO há redirecionamento para login
# 6. Verificar logs para confirmação
```

**TESTE 2: Persistência de Sessão**
```python
# Teste manual:
# 1. Fazer login
# 2. Navegar entre diferentes seções (dashboard, culturas, agente)
# 3. Verificar que usuário permanece logado
# 4. Refresh da página
# 5. Verificar que sessão persiste
```

**TESTE 3: Timeout de Sessão**
```python
# Teste manual:
# 1. Fazer login
# 2. Aguardar 31 minutos (timeout + 1)
# 3. Tentar acessar rota protegida
# 4. Verificar redirecionamento para login com mensagem adequada
```

### Critérios de Aceitação
- Login funciona e mantém sessão entre todas as rotas
- Todas as seções protegidas são acessíveis após login
- Logout limpa sessão completamente
- Timeout de sessão funciona adequadamente (30 minutos)
- Não há redirecionamentos inesperados
- Logs mostram comportamento correto
- Performance não foi degradada

### Entregáveis Esperados
1. **Código Completo Atualizado** para todos os arquivos modificados
2. **Logs Detalhados** implementados para debugging
3. **Testes de Validação** executados com sucesso
4. **Documentação** das alterações realizadas

### Informações Importantes
- Mantenha compatibilidade com código existente
- Implemente logging adequado para debugging futuro
- Considere segurança em todas as implementações
- Teste thoroughly antes de considerar concluído

---

## 🚨 PROMPT 3: DIAGNÓSTICO DO PROBLEMA DE ONBOARDING

### Contexto do Projeto
Você está trabalhando no diagnóstico do segundo problema crítico do AgroTech Portugal: o onboarding está travando no Passo 2. O sistema tem um processo de onboarding em 5 etapas para novos usuários, mas o segundo passo não avança após preenchimento correto do formulário.

### Problema Identificado
Durante o processo de onboarding, especificamente no Passo 2 (Configuração de Perfil), o formulário aceita os dados de entrada corretamente, mas ao clicar em "Próximo", o botão fica em estado de loading ("A processar...") indefinidamente sem progresso ou mensagem de erro.

### Sintomas Observados
- Formulário aceita dados de entrada corretamente
- Validação client-side aparenta funcionar
- Botão "Próximo" fica em estado de loading permanente
- Nenhuma mensagem de erro é exibida ao usuário
- Dados não são persistidos no backend
- Network requests podem estar falhando silenciosamente

### Código Atual Relevante

**templates/auth/onboarding_step2.html:**
```html
<div class="onboarding-container">
    <div class="progress-bar">
        <div class="progress" style="width: 40%"></div>
        <span class="progress-text">Passo 2 de 5 - 40%</span>
    </div>
    
    <div class="onboarding-content">
        <h2>Configure seu Perfil</h2>
        <p>Conte-nos um pouco sobre você para personalizarmos sua experiência.</p>
        
        <form id="onboarding-step-2" class="onboarding-form">
            <div class="form-group">
                <label for="nome_completo">Nome Completo *</label>
                <input type="text" id="nome_completo" name="nome_completo" required>
            </div>
            
            <div class="form-group">
                <label for="telefone">Telefone</label>
                <input type="tel" id="telefone" name="telefone" placeholder="(11) 99999-9999">
            </div>
            
            <div class="form-group">
                <label for="experiencia">Experiência na Agricultura *</label>
                <select id="experiencia" name="experiencia" required>
                    <option value="">Selecione...</option>
                    <option value="iniciante">Iniciante (0-1 anos)</option>
                    <option value="basico">Básico (2-5 anos)</option>
                    <option value="intermediario">Intermediário (6-10 anos)</option>
                    <option value="avancado">Avançado (11-20 anos)</option>
                    <option value="especialista">Especialista (20+ anos)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="tipo_produtor">Tipo de Produtor *</label>
                <select id="tipo_produtor" name="tipo_produtor" required>
                    <option value="">Selecione...</option>
                    <option value="familiar">Agricultura Familiar</option>
                    <option value="comercial">Agricultura Comercial</option>
                    <option value="organico">Agricultura Orgânica</option>
                    <option value="cooperativa">Membro de Cooperativa</option>
                    <option value="hobby">Hobby/Subsistência</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Principais Interesses (máximo 3) *</label>
                <div class="checkbox-group">
                    <label class="checkbox-item">
                        <input type="checkbox" name="interesses" value="cereais">
                        <span>Cereais</span>
                    </label>
                    <label class="checkbox-item">
                        <input type="checkbox" name="interesses" value="horticultura">
                        <span>Horticultura</span>
                    </label>
                    <label class="checkbox-item">
                        <input type="checkbox" name="interesses" value="fruticultura">
                        <span>Fruticultura</span>
                    </label>
                    <label class="checkbox-item">
                        <input type="checkbox" name="interesses" value="olivicultura">
                        <span>Olivicultura</span>
                    </label>
                    <label class="checkbox-item">
                        <input type="checkbox" name="interesses" value="viticultura">
                        <span>Viticultura</span>
                    </label>
                    <label class="checkbox-item">
                        <input type="checkbox" name="interesses" value="pecuaria">
                        <span>Pecuária</span>
                    </label>
                </div>
            </div>
            
            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="previousStep()">Anterior</button>
                <button type="submit" class="btn btn-primary" id="next-button">
                    <span class="button-text">Próximo</span>
                    <span class="loading-spinner" style="display: none;">A processar...</span>
                </button>
            </div>
        </form>
    </div>
</div>
```

**static/js/onboarding.js:**
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('onboarding-step-2');
    const nextButton = document.getElementById('next-button');
    
    if (form) {
        form.addEventListener('submit', handleStep2Submit);
    }
});

function handleStep2Submit(event) {
    event.preventDefault();
    
    const form = event.target;
    const nextButton = document.getElementById('next-button');
    const buttonText = nextButton.querySelector('.button-text');
    const loadingSpinner = nextButton.querySelector('.loading-spinner');
    
    // Validar formulário
    if (!validateStep2Form()) {
        return false;
    }
    
    // Mostrar loading
    buttonText.style.display = 'none';
    loadingSpinner.style.display = 'inline';
    nextButton.disabled = true;
    
    // Coletar dados
    const formData = new FormData(form);
    
    // Enviar dados
    fetch('/auth/onboarding?step=2', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/auth/onboarding?step=3';
        } else {
            showError(data.message || 'Erro ao processar dados');
            resetButton();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Erro de conexão. Tente novamente.');
        resetButton();
    });
}

function validateStep2Form() {
    const nomeCompleto = document.getElementById('nome_completo').value.trim();
    const experiencia = document.getElementById('experiencia').value;
    const tipoProdutor = document.getElementById('tipo_produtor').value;
    const interesses = document.querySelectorAll('input[name="interesses"]:checked');
    
    if (!nomeCompleto) {
        showError('Nome completo é obrigatório');
        return false;
    }
    
    if (!experiencia) {
        showError('Experiência é obrigatória');
        return false;
    }
    
    if (!tipoProdutor) {
        showError('Tipo de produtor é obrigatório');
        return false;
    }
    
    if (interesses.length === 0) {
        showError('Selecione pelo menos um interesse');
        return false;
    }
    
    if (interesses.length > 3) {
        showError('Selecione no máximo 3 interesses');
        return false;
    }
    
    return true;
}

function resetButton() {
    const nextButton = document.getElementById('next-button');
    const buttonText = nextButton.querySelector('.button-text');
    const loadingSpinner = nextButton.querySelector('.loading-spinner');
    
    buttonText.style.display = 'inline';
    loadingSpinner.style.display = 'none';
    nextButton.disabled = false;
}

function showError(message) {
    // Implementar exibição de erro
    alert(message); // Temporário
}
```

**app/routes/auth.py (rota de onboarding):**
```python
@bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    step = request.args.get('step', 1, type=int)
    
    if request.method == 'POST':
        if step == 2:
            # Processar dados do step 2
            nome_completo = request.form.get('nome_completo')
            telefone = request.form.get('telefone')
            experiencia = request.form.get('experiencia')
            tipo_produtor = request.form.get('tipo_produtor')
            interesses = request.form.getlist('interesses')
            
            # Validação básica
            if not nome_completo or not experiencia or not tipo_produtor:
                return jsonify({'success': False, 'message': 'Campos obrigatórios não preenchidos'})
            
            if len(interesses) == 0 or len(interesses) > 3:
                return jsonify({'success': False, 'message': 'Selecione entre 1 e 3 interesses'})
            
            # Salvar dados
            try:
                current_user.nome_completo = nome_completo
                current_user.telefone = telefone
                current_user.experiencia = experiencia
                current_user.tipo_produtor = tipo_produtor
                # interesses precisa ser salvo em tabela relacionada
                
                db.session.commit()
                return jsonify({'success': True, 'next_step': 3})
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': 'Erro interno'})
    
    # GET request - mostrar formulário
    if step < 1 or step > 5:
        step = 1
    
    return render_template(f'auth/onboarding_step{step}.html', step=step)
```

### Objetivo
Realizar diagnóstico completo e sistemático do problema de onboarding no Passo 2, identificando se o problema está no frontend (JavaScript), backend (Python), ou na comunicação entre eles.

### Instruções Detalhadas

**ETAPA 1: Análise Frontend (JavaScript)**

Analise minuciosamente o código JavaScript e identifique possíveis problemas:

1. **Validação de Formulário**:
   - Verifique se a função `validateStep2Form()` está funcionando corretamente
   - Confirme se todos os campos obrigatórios estão sendo validados
   - Teste a validação de checkboxes múltiplos (máximo 3)
   - Verifique se a validação não está bloqueando o envio

2. **Serialização de Dados**:
   - Confirme se `FormData` está sendo criado corretamente
   - Verifique se campos de checkbox estão sendo incluídos
   - Teste se caracteres especiais portugueses estão sendo codificados adequadamente
   - Valide se todos os campos do formulário estão sendo capturados

3. **Requisição AJAX/Fetch**:
   - Verifique se a URL `/auth/onboarding?step=2` está correta
   - Confirme se o método POST está sendo usado
   - Verifique se headers necessários estão sendo enviados (CSRF token, Content-Type)
   - Analise se há problemas de CORS ou outras restrições

4. **Tratamento de Resposta**:
   - Confirme se o código está esperando JSON como resposta
   - Verifique se o tratamento de erro está adequado
   - Analise se há problemas na verificação de `data.success`
   - Teste se o redirecionamento está funcionando

**ETAPA 2: Análise Backend (Python)**

Examine o código Python e identifique problemas:

1. **Rota de Processamento**:
   - Verifique se a rota `/auth/onboarding` aceita POST com step=2
   - Confirme se o decorator `@login_required` não está causando problemas
   - Analise se há conflitos de rotas
   - Verifique se a rota está sendo registrada corretamente

2. **Processamento de Dados**:
   - Confirme se `request.form.get()` está capturando os dados
   - Verifique se `request.form.getlist('interesses')` funciona para checkboxes
   - Analise se há problemas de encoding de caracteres
   - Teste se a validação server-side está passando

3. **Persistência de Dados**:
   - Verifique se o modelo User tem os campos necessários
   - Confirme se não há problemas de foreign keys ou constraints
   - Analise se há problemas de concorrência no SQLite
   - Teste se o commit está funcionando adequadamente

4. **Response Handling**:
   - Confirme se está retornando JSON válido
   - Verifique se os status codes estão corretos
   - Analise se não há exceptions não tratadas
   - Teste se não há problemas de timeout

**ETAPA 3: Análise de Comunicação**

Investigue a comunicação frontend-backend:

1. **Network Requests**:
   - Use DevTools para analisar requests HTTP
   - Verifique se a requisição está sendo enviada
   - Confirme se a resposta está sendo recebida
   - Analise headers de request e response

2. **CSRF Protection**:
   - Verifique se há proteção CSRF ativa
   - Confirme se token CSRF está sendo enviado
   - Analise se há problemas de validação de token

3. **Session Management**:
   - Confirme se a sessão está válida durante o onboarding
   - Verifique se não há problemas de autenticação
   - Analise se há conflitos com o sistema de login

**ETAPA 4: Implementação de Debugging**

Implemente logging e debugging detalhado:

```python
# No backend (app/routes/auth.py)
import logging
logger = logging.getLogger(__name__)

@bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    step = request.args.get('step', 1, type=int)
    logger.info(f'Onboarding step {step} requested by user {current_user.id}')
    
    if request.method == 'POST':
        logger.info(f'POST data received: {request.form.to_dict()}')
        
        if step == 2:
            # Log detalhado de cada campo
            nome_completo = request.form.get('nome_completo')
            logger.info(f'Nome completo: {nome_completo}')
            
            # ... resto da implementação com logs
```

```javascript
// No frontend (static/js/onboarding.js)
function handleStep2Submit(event) {
    console.log('Step 2 form submitted');
    event.preventDefault();
    
    const form = event.target;
    console.log('Form element:', form);
    
    // Validar formulário
    if (!validateStep2Form()) {
        console.log('Form validation failed');
        return false;
    }
    
    console.log('Form validation passed');
    
    // Coletar dados
    const formData = new FormData(form);
    console.log('FormData created:', formData);
    
    // Log dos dados coletados
    for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }
    
    // ... resto da implementação com logs
}
```

### Cenários de Teste

**CENÁRIO 1: Teste de Validação**
- Enviar formulário com campos vazios
- Verificar se validação impede envio
- Testar com mais de 3 interesses selecionados
- Confirmar mensagens de erro

**CENÁRIO 2: Teste de Dados Válidos**
- Preencher todos os campos corretamente
- Selecionar 2-3 interesses
- Verificar se dados são enviados
- Confirmar se resposta é recebida

**CENÁRIO 3: Teste de Network**
- Usar DevTools para monitorar requests
- Verificar se request é enviado para URL correta
- Analisar response status e body
- Confirmar headers enviados/recebidos

### Critérios de Aceitação
- Causa específica do problema identificada (frontend ou backend)
- Logs implementados para debugging contínuo
- Evidências técnicas coletadas (network requests, logs, etc.)
- Plano de correção específico elaborado
- Testes de validação documentados

### Entregáveis Esperados
1. **Relatório de Diagnóstico** identificando a causa raiz
2. **Código de Debugging** implementado em frontend e backend
3. **Evidências Técnicas** (screenshots, logs, network analysis)
4. **Plano de Correção** detalhado e específico

### Informações Adicionais
- Problema afeta 100% dos novos usuários
- Onboarding é crítico para experiência inicial
- Prioridade máxima após correção de sessões
- Testar em diferentes browsers se necessário



---

## 🚨 PROMPT 4: CORREÇÃO DO FORMULÁRIO DE ONBOARDING

### Contexto do Projeto
Você está implementando a correção para o problema de onboarding no Passo 2 do AgroTech Portugal, baseado no diagnóstico realizado anteriormente. O objetivo é garantir que o formulário funcione corretamente e permita que usuários avancem para o Passo 3.

### Problema a Resolver
Implementar correção completa do formulário de onboarding Passo 2, garantindo que dados sejam validados, enviados, processados e persistidos corretamente, permitindo progressão natural para o Passo 3.

### Diagnóstico Prévio (Assumindo Resultados Típicos)
Com base em problemas comuns em formulários AJAX, as principais causas prováveis são:
- Problemas na validação JavaScript
- Falhas na serialização de dados FormData
- Problemas no endpoint backend
- Falta de CSRF token
- Problemas na validação server-side

### Objetivo
Implementar correção robusta e completa do formulário de onboarding, garantindo fluxo suave e confiável para todos os usuários.

### Instruções Detalhadas

**CORREÇÃO 1: JavaScript Aprimorado**

Substitua completamente o arquivo `static/js/onboarding.js`:

```javascript
/**
 * Sistema de Onboarding - AgroTech Portugal
 * Gerenciamento completo do processo de onboarding em 5 etapas
 */

class OnboardingManager {
    constructor() {
        this.currentStep = this.getCurrentStep();
        this.initializeEventListeners();
        this.setupFormValidation();
    }
    
    getCurrentStep() {
        const urlParams = new URLSearchParams(window.location.search);
        return parseInt(urlParams.get('step')) || 1;
    }
    
    initializeEventListeners() {
        // Event listener para formulário do step 2
        const step2Form = document.getElementById('onboarding-step-2');
        if (step2Form) {
            step2Form.addEventListener('submit', (e) => this.handleStep2Submit(e));
            
            // Validação em tempo real para checkboxes
            const checkboxes = step2Form.querySelectorAll('input[name="interesses"]');
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', () => this.validateInteresses());
            });
        }
        
        // Event listeners para outros steps (futuro)
        this.setupNavigationButtons();
    }
    
    setupNavigationButtons() {
        const prevButton = document.querySelector('.btn-secondary');
        if (prevButton) {
            prevButton.addEventListener('click', () => this.previousStep());
        }
    }
    
    setupFormValidation() {
        // Configurar validação em tempo real
        const requiredFields = document.querySelectorAll('input[required], select[required]');
        requiredFields.forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => this.clearFieldError(field));
        });
    }
    
    async handleStep2Submit(event) {
        event.preventDefault();
        console.log('🚀 Iniciando submissão do Step 2');
        
        const form = event.target;
        const submitButton = document.getElementById('next-button');
        
        try {
            // 1. Validar formulário
            if (!this.validateStep2Form()) {
                console.log('❌ Validação do formulário falhou');
                return false;
            }
            
            console.log('✅ Validação do formulário passou');
            
            // 2. Mostrar loading state
            this.setLoadingState(submitButton, true);
            
            // 3. Coletar e preparar dados
            const formData = this.collectFormData(form);
            console.log('📋 Dados coletados:', this.formDataToObject(formData));
            
            // 4. Enviar dados
            const response = await this.submitFormData(formData);
            console.log('📡 Resposta recebida:', response);
            
            // 5. Processar resposta
            if (response.success) {
                console.log('✅ Submissão bem-sucedida');
                this.handleSuccess(response);
            } else {
                console.log('❌ Erro na submissão:', response.message);
                this.handleError(response.message || 'Erro ao processar dados');
            }
            
        } catch (error) {
            console.error('💥 Erro na submissão:', error);
            this.handleError('Erro de conexão. Verifique sua internet e tente novamente.');
        } finally {
            this.setLoadingState(submitButton, false);
        }
    }
    
    validateStep2Form() {
        console.log('🔍 Iniciando validação do formulário');
        
        let isValid = true;
        const errors = [];
        
        // Validar nome completo
        const nomeCompleto = document.getElementById('nome_completo').value.trim();
        if (!nomeCompleto) {
            errors.push('Nome completo é obrigatório');
            this.setFieldError('nome_completo', 'Nome completo é obrigatório');
            isValid = false;
        } else if (nomeCompleto.length < 2) {
            errors.push('Nome deve ter pelo menos 2 caracteres');
            this.setFieldError('nome_completo', 'Nome deve ter pelo menos 2 caracteres');
            isValid = false;
        } else {
            this.clearFieldError('nome_completo');
        }
        
        // Validar telefone (opcional, mas se preenchido deve ser válido)
        const telefone = document.getElementById('telefone').value.trim();
        if (telefone && !this.isValidPortuguesePhone(telefone)) {
            errors.push('Formato de telefone inválido');
            this.setFieldError('telefone', 'Use o formato +351 9XX XXX XXX');
            isValid = false;
        } else {
            this.clearFieldError('telefone');
        }
        
        // Validar experiência
        const experiencia = document.getElementById('experiencia').value;
        if (!experiencia) {
            errors.push('Experiência é obrigatória');
            this.setFieldError('experiencia', 'Selecione sua experiência');
            isValid = false;
        } else {
            this.clearFieldError('experiencia');
        }
        
        // Validar tipo de produtor
        const tipoProdutor = document.getElementById('tipo_produtor').value;
        if (!tipoProdutor) {
            errors.push('Tipo de produtor é obrigatório');
            this.setFieldError('tipo_produtor', 'Selecione o tipo de produtor');
            isValid = false;
        } else {
            this.clearFieldError('tipo_produtor');
        }
        
        // Validar interesses
        const interessesValid = this.validateInteresses();
        if (!interessesValid) {
            isValid = false;
        }
        
        console.log(`🔍 Validação concluída: ${isValid ? 'PASSOU' : 'FALHOU'}`);
        if (!isValid) {
            console.log('❌ Erros encontrados:', errors);
        }
        
        return isValid;
    }
    
    validateInteresses() {
        const checkboxes = document.querySelectorAll('input[name="interesses"]:checked');
        const interessesContainer = document.querySelector('.checkbox-group');
        
        if (checkboxes.length === 0) {
            this.setFieldError('interesses', 'Selecione pelo menos um interesse');
            return false;
        } else if (checkboxes.length > 3) {
            this.setFieldError('interesses', 'Selecione no máximo 3 interesses');
            return false;
        } else {
            this.clearFieldError('interesses');
            return true;
        }
    }
    
    isValidPortuguesePhone(phone) {
        // Formato português: +351 9XX XXX XXX
        const phoneRegex = /^\+351\s?9\d{8}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
    }
    
    collectFormData(form) {
        const formData = new FormData(form);
        
        // Adicionar CSRF token se disponível
        const csrfToken = this.getCSRFToken();
        if (csrfToken) {
            formData.append('csrf_token', csrfToken);
        }
        
        // Garantir que interesses são incluídos mesmo se vazios
        const interessesCheckboxes = form.querySelectorAll('input[name="interesses"]:checked');
        if (interessesCheckboxes.length === 0) {
            formData.append('interesses', ''); // Campo vazio para validação backend
        }
        
        return formData;
    }
    
    formDataToObject(formData) {
        // Função auxiliar para logging
        const obj = {};
        for (let [key, value] of formData.entries()) {
            if (obj[key]) {
                if (Array.isArray(obj[key])) {
                    obj[key].push(value);
                } else {
                    obj[key] = [obj[key], value];
                }
            } else {
                obj[key] = value;
            }
        }
        return obj;
    }
    
    async submitFormData(formData) {
        const response = await fetch('/auth/onboarding?step=2', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Resposta não é JSON válido');
        }
        
        return await response.json();
    }
    
    handleSuccess(response) {
        // Mostrar mensagem de sucesso
        this.showSuccessMessage('Perfil configurado com sucesso!');
        
        // Aguardar um pouco para UX e redirecionar
        setTimeout(() => {
            window.location.href = `/auth/onboarding?step=${response.next_step || 3}`;
        }, 1000);
    }
    
    handleError(message) {
        this.showErrorMessage(message);
        
        // Scroll para o topo para mostrar erro
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    setLoadingState(button, isLoading) {
        const buttonText = button.querySelector('.button-text');
        const loadingSpinner = button.querySelector('.loading-spinner');
        
        if (isLoading) {
            buttonText.style.display = 'none';
            loadingSpinner.style.display = 'inline';
            button.disabled = true;
        } else {
            buttonText.style.display = 'inline';
            loadingSpinner.style.display = 'none';
            button.disabled = false;
        }
    }
    
    validateField(field) {
        // Validação individual de campo
        if (field.hasAttribute('required') && !field.value.trim()) {
            this.setFieldError(field.id, `${field.previousElementSibling.textContent} é obrigatório`);
            return false;
        }
        
        this.clearFieldError(field.id);
        return true;
    }
    
    setFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        const formGroup = field.closest('.form-group') || field.closest('.checkbox-group');
        
        // Remover erro existente
        const existingError = formGroup.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Adicionar novo erro
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.textContent = message;
        errorElement.style.color = '#dc3545';
        errorElement.style.fontSize = '0.875rem';
        errorElement.style.marginTop = '0.25rem';
        
        formGroup.appendChild(errorElement);
        field.classList.add('is-invalid');
    }
    
    clearFieldError(fieldId) {
        const field = document.getElementById(fieldId);
        const formGroup = field.closest('.form-group') || field.closest('.checkbox-group');
        
        const errorElement = formGroup.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
        
        field.classList.remove('is-invalid');
    }
    
    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }
    
    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }
    
    showMessage(message, type) {
        // Remover mensagem existente
        const existingMessage = document.querySelector('.onboarding-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Criar nova mensagem
        const messageElement = document.createElement('div');
        messageElement.className = `onboarding-message alert alert-${type === 'success' ? 'success' : 'danger'}`;
        messageElement.textContent = message;
        messageElement.style.marginBottom = '1rem';
        
        // Inserir no início do container
        const container = document.querySelector('.onboarding-content');
        container.insertBefore(messageElement, container.firstChild);
        
        // Auto-remover após 5 segundos se for sucesso
        if (type === 'success') {
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.remove();
                }
            }, 5000);
        }
    }
    
    getCSRFToken() {
        // Tentar obter CSRF token de diferentes fontes
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }
        
        const hiddenInput = document.querySelector('input[name="csrf_token"]');
        if (hiddenInput) {
            return hiddenInput.value;
        }
        
        return null;
    }
    
    previousStep() {
        if (this.currentStep > 1) {
            window.location.href = `/auth/onboarding?step=${this.currentStep - 1}`;
        }
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Inicializando OnboardingManager');
    new OnboardingManager();
});
```

**CORREÇÃO 2: Backend Aprimorado**

Substitua a rota de onboarding em `app/routes/auth.py`:

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, UserInteresse, Interesse, db
from app.validators.auth_validators import OnboardingStep2Validator
from datetime import datetime
import logging

bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    step = request.args.get('step', 1, type=int)
    
    # Log da requisição
    logger.info(f'Onboarding step {step} requested by user {current_user.id} - Method: {request.method}')
    
    if request.method == 'POST':
        return handle_onboarding_post(step)
    else:
        return handle_onboarding_get(step)

def handle_onboarding_post(step):
    """Processar dados POST do onboarding"""
    
    if step == 2:
        return process_onboarding_step2()
    elif step == 3:
        return process_onboarding_step3()
    elif step == 4:
        return process_onboarding_step4()
    elif step == 5:
        return process_onboarding_step5()
    else:
        logger.warning(f'Invalid onboarding step: {step}')
        return jsonify({'success': False, 'message': 'Passo inválido'}), 400

def process_onboarding_step2():
    """Processar especificamente o Step 2 do onboarding"""
    
    try:
        # Log dos dados recebidos
        form_data = request.form.to_dict()
        logger.info(f'Step 2 form data received: {form_data}')
        
        # Coletar dados do formulário
        nome_completo = request.form.get('nome_completo', '').strip()
        telefone = request.form.get('telefone', '').strip()
        experiencia = request.form.get('experiencia', '').strip()
        tipo_produtor = request.form.get('tipo_produtor', '').strip()
        interesses_list = request.form.getlist('interesses')
        
        logger.info(f'Parsed data - Nome: {nome_completo}, Telefone: {telefone}, '
                   f'Experiencia: {experiencia}, Tipo: {tipo_produtor}, '
                   f'Interesses: {interesses_list}')
        
        # Validação server-side
        validation_result = validate_step2_data(
            nome_completo, telefone, experiencia, tipo_produtor, interesses_list
        )
        
        if not validation_result['is_valid']:
            logger.warning(f'Step 2 validation failed: {validation_result["errors"]}')
            return jsonify({
                'success': False,
                'message': validation_result['message'],
                'errors': validation_result['errors']
            }), 400
        
        # Salvar dados no banco
        save_result = save_step2_data(
            current_user, nome_completo, telefone, experiencia, tipo_produtor, interesses_list
        )
        
        if not save_result['success']:
            logger.error(f'Failed to save step 2 data: {save_result["error"]}')
            return jsonify({
                'success': False,
                'message': 'Erro ao salvar dados. Tente novamente.'
            }), 500
        
        logger.info(f'Step 2 completed successfully for user {current_user.id}')
        
        return jsonify({
            'success': True,
            'message': 'Perfil configurado com sucesso!',
            'next_step': 3
        })
        
    except Exception as e:
        logger.error(f'Unexpected error in step 2: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor. Tente novamente.'
        }), 500

def validate_step2_data(nome_completo, telefone, experiencia, tipo_produtor, interesses_list):
    """Validar dados do Step 2"""
    
    errors = []
    
    # Validar nome completo
    if not nome_completo:
        errors.append('Nome completo é obrigatório')
    elif len(nome_completo) < 2:
        errors.append('Nome deve ter pelo menos 2 caracteres')
    elif len(nome_completo) > 100:
        errors.append('Nome deve ter no máximo 100 caracteres')
    
    # Validar telefone (opcional)
    if telefone and not validate_portuguese_phone(telefone):
        errors.append('Formato de telefone inválido. Use +351 9XX XXX XXX')
    
    # Validar experiência
    valid_experiencias = ['iniciante', 'basico', 'intermediario', 'avancado', 'especialista']
    if not experiencia:
        errors.append('Experiência é obrigatória')
    elif experiencia not in valid_experiencias:
        errors.append('Experiência inválida')
    
    # Validar tipo de produtor
    valid_tipos = ['familiar', 'comercial', 'organico', 'cooperativa', 'hobby']
    if not tipo_produtor:
        errors.append('Tipo de produtor é obrigatório')
    elif tipo_produtor not in valid_tipos:
        errors.append('Tipo de produtor inválido')
    
    # Validar interesses
    if not interesses_list or len(interesses_list) == 0:
        errors.append('Selecione pelo menos um interesse')
    elif len(interesses_list) > 3:
        errors.append('Selecione no máximo 3 interesses')
    else:
        valid_interesses = ['cereais', 'horticultura', 'fruticultura', 'olivicultura', 
                           'viticultura', 'pecuaria', 'organicos', 'tecnologia']
        for interesse in interesses_list:
            if interesse not in valid_interesses:
                errors.append(f'Interesse inválido: {interesse}')
    
    is_valid = len(errors) == 0
    message = 'Dados válidos' if is_valid else 'Dados inválidos: ' + ', '.join(errors)
    
    return {
        'is_valid': is_valid,
        'errors': errors,
        'message': message
    }

def validate_portuguese_phone(phone):
    """Validar formato de telefone português"""
    import re
    # Formato: +351 9XX XXX XXX
    pattern = r'^\+351\s?9\d{8}$'
    return re.match(pattern, phone.replace(' ', '')) is not None

def save_step2_data(user, nome_completo, telefone, experiencia, tipo_produtor, interesses_list):
    """Salvar dados do Step 2 no banco"""
    
    try:
        # Atualizar dados do usuário
        user.nome_completo = nome_completo
        user.telefone = telefone if telefone else None
        user.experiencia = experiencia
        user.tipo_produtor = tipo_produtor
        user.onboarding_step = 2  # Marcar progresso
        user.updated_at = datetime.utcnow()
        
        # Limpar interesses existentes
        UserInteresse.query.filter_by(user_id=user.id).delete()
        
        # Adicionar novos interesses
        for interesse_nome in interesses_list:
            # Buscar ou criar interesse
            interesse = Interesse.query.filter_by(nome=interesse_nome).first()
            if not interesse:
                interesse = Interesse(nome=interesse_nome)
                db.session.add(interesse)
                db.session.flush()  # Para obter o ID
            
            # Criar relacionamento
            user_interesse = UserInteresse(
                user_id=user.id,
                interesse_id=interesse.id
            )
            db.session.add(user_interesse)
        
        # Commit das alterações
        db.session.commit()
        
        logger.info(f'Step 2 data saved successfully for user {user.id}')
        
        return {'success': True}
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error saving step 2 data: {str(e)}', exc_info=True)
        return {'success': False, 'error': str(e)}

def handle_onboarding_get(step):
    """Processar requisições GET do onboarding"""
    
    # Validar step
    if step < 1 or step > 5:
        logger.warning(f'Invalid onboarding step requested: {step}')
        return redirect(url_for('auth.onboarding', step=1))
    
    # Verificar se usuário pode acessar este step
    if step > 1 and (not hasattr(current_user, 'onboarding_step') or 
                     current_user.onboarding_step < step - 1):
        logger.warning(f'User {current_user.id} trying to access step {step} '
                      f'but is only at step {getattr(current_user, "onboarding_step", 0)}')
        return redirect(url_for('auth.onboarding', step=1))
    
    # Preparar contexto para o template
    context = {
        'step': step,
        'total_steps': 5,
        'progress': (step / 5) * 100,
        'user': current_user
    }
    
    # Contexto específico para cada step
    if step == 2:
        context.update({
            'experiencias': [
                ('iniciante', 'Iniciante (0-1 anos)'),
                ('basico', 'Básico (2-5 anos)'),
                ('intermediario', 'Intermediário (6-10 anos)'),
                ('avancado', 'Avançado (11-20 anos)'),
                ('especialista', 'Especialista (20+ anos)')
            ],
            'tipos_produtor': [
                ('familiar', 'Agricultura Familiar'),
                ('comercial', 'Agricultura Comercial'),
                ('organico', 'Agricultura Orgânica'),
                ('cooperativa', 'Membro de Cooperativa'),
                ('hobby', 'Hobby/Subsistência')
            ],
            'interesses_disponiveis': [
                ('cereais', 'Cereais'),
                ('horticultura', 'Horticultura'),
                ('fruticultura', 'Fruticultura'),
                ('olivicultura', 'Olivicultura'),
                ('viticultura', 'Viticultura'),
                ('pecuaria', 'Pecuária'),
                ('organicos', 'Produtos Orgânicos'),
                ('tecnologia', 'Tecnologia Agrícola')
            ]
        })
    
    try:
        return render_template(f'auth/onboarding_step{step}.html', **context)
    except Exception as e:
        logger.error(f'Error rendering onboarding step {step}: {str(e)}')
        flash('Erro ao carregar página. Tente novamente.', 'error')
        return redirect(url_for('main.dashboard'))
```

**CORREÇÃO 3: Modelo de Dados Atualizado**

Atualize `app/models.py` para suportar os dados do onboarding:

```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Dados básicos
    nome_completo = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    
    # Dados do onboarding
    experiencia = db.Column(db.String(20))  # iniciante, basico, intermediario, avancado, especialista
    tipo_produtor = db.Column(db.String(20))  # familiar, comercial, organico, cooperativa, hobby
    onboarding_step = db.Column(db.Integer, default=0)  # Progresso do onboarding
    onboarding_completed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    interesses = db.relationship('UserInteresse', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    def get_interesses_list(self):
        """Retorna lista de nomes dos interesses do usuário"""
        return [ui.interesse.nome for ui in self.interesses]
    
    def __repr__(self):
        return f'<User {self.email}>'

class Interesse(db.Model):
    __tablename__ = 'interesses'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Interesse {self.nome}>'

class UserInteresse(db.Model):
    __tablename__ = 'user_interesses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    interesse_id = db.Column(db.Integer, db.ForeignKey('interesses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    interesse = db.relationship('Interesse', backref='user_interesses')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'interesse_id'),)
    
    def __repr__(self):
        return f'<UserInteresse {self.user_id}-{self.interesse_id}>'
```

**CORREÇÃO 4: Template HTML Atualizado**

Atualize `templates/auth/onboarding_step2.html`:

```html
{% extends "base.html" %}

{% block title %}Configurar Perfil - AgroTech Portugal{% endblock %}

{% block content %}
<div class="onboarding-container">
    <div class="progress-bar">
        <div class="progress" style="width: {{ progress }}%"></div>
        <span class="progress-text">Passo {{ step }} de {{ total_steps }} - {{ progress|int }}%</span>
    </div>
    
    <div class="onboarding-content">
        <h2>Configure seu Perfil</h2>
        <p>Conte-nos um pouco sobre você para personalizarmos sua experiência no AgroTech Portugal.</p>
        
        <form id="onboarding-step-2" class="onboarding-form" novalidate>
            <div class="form-group">
                <label for="nome_completo">Nome Completo *</label>
                <input type="text" 
                       id="nome_completo" 
                       name="nome_completo" 
                       value="{{ user.nome_completo or '' }}"
                       required
                       maxlength="100"
                       placeholder="Seu nome completo">
            </div>
            
            <div class="form-group">
                <label for="telefone">Telefone</label>
                <input type="tel" 
                       id="telefone" 
                       name="telefone"
                       value="{{ user.telefone or '' }}"
                       placeholder="+351 9XX XXX XXX"
                       pattern="^\+351\s?9\d{8}$"
                       title="Formato: +351 9XX XXX XXX">
                <small class="form-text text-muted">
                    Formato português: +351 seguido do número de telemóvel
                </small>
            </div>
            
            <div class="form-group">
                <label for="experiencia">Experiência na Agricultura *</label>
                <select id="experiencia" name="experiencia" required>
                    <option value="">Selecione sua experiência...</option>
                    {% for value, label in experiencias %}
                    <option value="{{ value }}" 
                            {% if user.experiencia == value %}selected{% endif %}>
                        {{ label }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label for="tipo_produtor">Tipo de Produtor *</label>
                <select id="tipo_produtor" name="tipo_produtor" required>
                    <option value="">Selecione o tipo...</option>
                    {% for value, label in tipos_produtor %}
                    <option value="{{ value }}"
                            {% if user.tipo_produtor == value %}selected{% endif %}>
                        {{ label }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label>Principais Interesses (selecione 1-3) *</label>
                <div class="checkbox-group" id="interesses">
                    {% set user_interesses = user.get_interesses_list() %}
                    {% for value, label in interesses_disponiveis %}
                    <label class="checkbox-item">
                        <input type="checkbox" 
                               name="interesses" 
                               value="{{ value }}"
                               {% if value in user_interesses %}checked{% endif %}>
                        <span class="checkmark"></span>
                        <span class="label-text">{{ label }}</span>
                    </label>
                    {% endfor %}
                </div>
                <small class="form-text text-muted">
                    Selecione entre 1 e 3 áreas do seu interesse
                </small>
            </div>
            
            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="window.history.back()">
                    Anterior
                </button>
                <button type="submit" class="btn btn-primary" id="next-button">
                    <span class="button-text">Próximo</span>
                    <span class="loading-spinner" style="display: none;">
                        <i class="fas fa-spinner fa-spin"></i> A processar...
                    </span>
                </button>
            </div>
        </form>
    </div>
</div>

<style>
.onboarding-container {
    max-width: 600px;
    margin: 2rem auto;
    padding: 2rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
    margin-bottom: 2rem;
    position: relative;
}

.progress {
    height: 100%;
    background: linear-gradient(90deg, #28a745, #20c997);
    border-radius: 4px;
    transition: width 0.3s ease;
}

.progress-text {
    position: absolute;
    top: 15px;
    right: 0;
    font-size: 0.875rem;
    color: #6c757d;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #333;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
    outline: none;
    border-color: #28a745;
    box-shadow: 0 0 0 2px rgba(40, 167, 69, 0.25);
}

.form-group input.is-invalid,
.form-group select.is-invalid {
    border-color: #dc3545;
}

.checkbox-group {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.75rem;
    margin-top: 0.5rem;
}

.checkbox-item {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.checkbox-item:hover {
    border-color: #28a745;
    background-color: #f8f9fa;
}

.checkbox-item input[type="checkbox"] {
    width: auto;
    margin-right: 0.5rem;
}

.checkbox-item input[type="checkbox"]:checked + .checkmark + .label-text {
    color: #28a745;
    font-weight: 500;
}

.form-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e9ecef;
}

.btn {
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.btn-primary {
    background: linear-gradient(90deg, #28a745, #20c997);
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background: linear-gradient(90deg, #218838, #1ea085);
    transform: translateY(-1px);
}

.btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background: #5a6268;
}

.field-error {
    color: #dc3545;
    font-size: 0.875rem;
    margin-top: 0.25rem;
}

.alert {
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}

.alert-success {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
}

.alert-danger {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}

.form-text {
    font-size: 0.875rem;
    color: #6c757d;
    margin-top: 0.25rem;
}

@media (max-width: 768px) {
    .onboarding-container {
        margin: 1rem;
        padding: 1rem;
    }
    
    .checkbox-group {
        grid-template-columns: 1fr;
    }
    
    .form-actions {
        flex-direction: column;
        gap: 1rem;
    }
}
</style>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/onboarding.js') }}"></script>
{% endblock %}
```

### Testes de Validação

**TESTE 1: Fluxo Completo**
1. Acessar `/auth/onboarding?step=2`
2. Preencher todos os campos corretamente
3. Selecionar 2-3 interesses
4. Clicar em "Próximo"
5. Verificar redirecionamento para step 3

**TESTE 2: Validação de Erros**
1. Tentar enviar formulário vazio
2. Verificar mensagens de erro
3. Selecionar mais de 3 interesses
4. Verificar validação de limite

**TESTE 3: Persistência de Dados**
1. Preencher formulário
2. Verificar se dados são salvos no banco
3. Voltar ao step 2
4. Verificar se dados são mantidos

### Critérios de Aceitação
- Formulário avança para Passo 3 após preenchimento correto
- Dados são salvos corretamente no banco de dados
- Validação de erros funciona e exibe mensagens claras
- Interface responsiva funciona em mobile
- Não há travamentos ou timeouts
- Logs mostram comportamento correto

### Entregáveis Esperados
1. **JavaScript Completo** com classe OnboardingManager
2. **Backend Robusto** com validação e persistência
3. **Template Atualizado** com melhor UX
4. **Modelo de Dados** adequado para onboarding
5. **Testes de Validação** executados com sucesso

---

## 🧪 PROMPT 5: VALIDAÇÃO E TESTES DAS CORREÇÕES

### Contexto do Projeto
Você está na fase final do Sprint 1 do AgroTech Portugal, responsável por validar e testar todas as correções críticas implementadas (sistema de sessões e onboarding). O objetivo é garantir que ambos os problemas foram resolvidos completamente e que o sistema está estável para a próxima sprint.

### Problemas Corrigidos
1. **Sistema de Sessões**: Correção da persistência de sessão entre rotas
2. **Onboarding Passo 2**: Correção do formulário que travava em "A processar..."

### Objetivo
Criar e executar um plano de testes abrangente para validar que todas as correções funcionam corretamente, identificar possíveis regressões e garantir que o sistema está pronto para desenvolvimento das funcionalidades core.

### Instruções Detalhadas

**FASE 1: TESTES DO SISTEMA DE SESSÕES**

Crie um script de teste automatizado para validar o sistema de autenticação:

```python
# tests/test_auth_sessions.py
import pytest
from flask import url_for
from app import create_app, db
from app.models import User
import time

class TestAuthSessions:
    """Testes para validar correção do sistema de sessões"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def test_user(self, app):
        with app.app_context():
            user = User(email='test@agrotech.pt')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            return user
    
    def test_login_creates_session(self, client, test_user):
        """Teste: Login cria sessão válida"""
        response = client.post('/auth/login', data={
            'email': 'test@agrotech.pt',
            'password': 'password123'
        })
        
        assert response.status_code == 302  # Redirect após login
        assert '/dashboard' in response.location
        
        # Verificar se sessão foi criada
        with client.session_transaction() as sess:
            assert 'user_id' in sess
    
    def test_session_persists_between_routes(self, client, test_user):
        """Teste: Sessão persiste entre diferentes rotas"""
        # Login
        client.post('/auth/login', data={
            'email': 'test@agrotech.pt',
            'password': 'password123'
        })
        
        # Testar acesso a diferentes rotas protegidas
        routes_to_test = ['/dashboard', '/culturas', '/agente', '/marketplace']
        
        for route in routes_to_test:
            response = client.get(route)
            assert response.status_code == 200, f'Falha ao acessar {route}'
            assert b'login' not in response.data.lower(), f'Redirecionado para login em {route}'
    
    def test_logout_clears_session(self, client, test_user):
        """Teste: Logout limpa sessão completamente"""
        # Login
        client.post('/auth/login', data={
            'email': 'test@agrotech.pt',
            'password': 'password123'
        })
        
        # Logout
        response = client.get('/auth/logout')
        assert response.status_code == 302
        
        # Verificar se sessão foi limpa
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
        
        # Tentar acessar rota protegida
        response = client.get('/culturas')
        assert response.status_code == 302  # Redirect para login
        assert '/auth/login' in response.location
    
    def test_session_timeout(self, client, test_user, app):
        """Teste: Timeout de sessão funciona adequadamente"""
        # Configurar timeout muito baixo para teste
        with app.app_context():
            app.config['PERMANENT_SESSION_LIFETIME'] = 1  # 1 segundo
        
        # Login
        client.post('/auth/login', data={
            'email': 'test@agrotech.pt',
            'password': 'password123'
        })
        
        # Aguardar timeout
        time.sleep(2)
        
        # Tentar acessar rota protegida
        response = client.get('/culturas')
        # Deve redirecionar para login devido ao timeout
        assert response.status_code == 302
    
    def test_multiple_tabs_simulation(self, client, test_user):
        """Teste: Simular múltiplas abas do mesmo usuário"""
        # Login
        client.post('/auth/login', data={
            'email': 'test@agrotech.pt',
            'password': 'password123'
        })
        
        # Simular acessos simultâneos (como múltiplas abas)
        responses = []
        for _ in range(5):
            response = client.get('/dashboard')
            responses.append(response)
        
        # Todos os acessos devem ser bem-sucedidos
        for response in responses:
            assert response.status_code == 200
    
    def test_invalid_session_handling(self, client, test_user):
        """Teste: Tratamento de sessão inválida"""
        # Simular sessão corrompida
        with client.session_transaction() as sess:
            sess['user_id'] = '999999'  # ID inexistente
        
        # Tentar acessar rota protegida
        response = client.get('/culturas')
        
        # Deve redirecionar para login e limpar sessão
        assert response.status_code == 302
        assert '/auth/login' in response.location

# Script para executar testes
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

**FASE 2: TESTES DO ONBOARDING**

Crie testes específicos para o onboarding:

```python
# tests/test_onboarding.py
import pytest
import json
from flask import url_for
from app import create_app, db
from app.models import User, Interesse, UserInteresse

class TestOnboarding:
    """Testes para validar correção do onboarding"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Criar interesses padrão
            interesses = [
                'cereais', 'horticultura', 'fruticultura', 
                'olivicultura', 'viticultura', 'pecuaria'
            ]
            for nome in interesses:
                interesse = Interesse(nome=nome)
                db.session.add(interesse)
            
            db.session.commit()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def logged_user(self, app, client):
        with app.app_context():
            user = User(email='test@agrotech.pt')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Login
            client.post('/auth/login', data={
                'email': 'test@agrotech.pt',
                'password': 'password123'
            })
            
            return user
    
    def test_onboarding_step2_get(self, client, logged_user):
        """Teste: GET do step 2 carrega corretamente"""
        response = client.get('/auth/onboarding?step=2')
        
        assert response.status_code == 200
        assert b'Configure seu Perfil' in response.data
        assert b'onboarding-step-2' in response.data
    
    def test_onboarding_step2_valid_data(self, client, logged_user, app):
        """Teste: POST com dados válidos funciona"""
        data = {
            'nome_completo': 'João Silva',
            'telefone': '+351 912345678',
            'experiencia': 'intermediario',
            'tipo_produtor': 'familiar',
            'interesses': ['cereais', 'horticultura']
        }
        
        response = client.post('/auth/onboarding?step=2', data=data)
        
        assert response.status_code == 200
        
        # Verificar resposta JSON
        json_data = json.loads(response.data)
        assert json_data['success'] is True
        assert json_data['next_step'] == 3
        
        # Verificar se dados foram salvos
        with app.app_context():
            user = User.query.filter_by(email='test@agrotech.pt').first()
            assert user.nome_completo == 'João Silva'
            assert user.telefone == '+351 912345678'
            assert user.experiencia == 'intermediario'
            assert user.tipo_produtor == 'familiar'
            assert len(user.interesses) == 2
    
    def test_onboarding_step2_missing_required_fields(self, client, logged_user):
        """Teste: Campos obrigatórios faltando"""
        data = {
            'telefone': '+351 912345678',
            # nome_completo ausente
            # experiencia ausente
            # tipo_produtor ausente
            # interesses ausente
        }
        
        response = client.post('/auth/onboarding?step=2', data=data)
        
        assert response.status_code == 400
        
        json_data = json.loads(response.data)
        assert json_data['success'] is False
        assert 'obrigatório' in json_data['message'].lower()
    
    def test_onboarding_step2_invalid_phone(self, client, logged_user):
        """Teste: Formato de telefone inválido"""
        data = {
            'nome_completo': 'João Silva',
            'telefone': '123456789',  # Formato inválido
            'experiencia': 'intermediario',
            'tipo_produtor': 'familiar',
            'interesses': ['cereais']
        }
        
        response = client.post('/auth/onboarding?step=2', data=data)
        
        assert response.status_code == 400
        
        json_data = json.loads(response.data)
        assert json_data['success'] is False
        assert 'telefone' in json_data['message'].lower()
    
    def test_onboarding_step2_too_many_interests(self, client, logged_user):
        """Teste: Mais de 3 interesses selecionados"""
        data = {
            'nome_completo': 'João Silva',
            'experiencia': 'intermediario',
            'tipo_produtor': 'familiar',
            'interesses': ['cereais', 'horticultura', 'fruticultura', 'olivicultura']  # 4 interesses
        }
        
        response = client.post('/auth/onboarding?step=2', data=data)
        
        assert response.status_code == 400
        
        json_data = json.loads(response.data)
        assert json_data['success'] is False
        assert 'máximo 3' in json_data['message']
    
    def test_onboarding_step2_no_interests(self, client, logged_user):
        """Teste: Nenhum interesse selecionado"""
        data = {
            'nome_completo': 'João Silva',
            'experiencia': 'intermediario',
            'tipo_produtor': 'familiar',
            'interesses': []  # Sem interesses
        }
        
        response = client.post('/auth/onboarding?step=2', data=data)
        
        assert response.status_code == 400
        
        json_data = json.loads(response.data)
        assert json_data['success'] is False
        assert 'pelo menos um' in json_data['message']
    
    def test_onboarding_step2_database_error_handling(self, client, logged_user, app):
        """Teste: Tratamento de erro de banco de dados"""
        data = {
            'nome_completo': 'João Silva',
            'experiencia': 'intermediario',
            'tipo_produtor': 'familiar',
            'interesses': ['cereais']
        }
        
        # Simular erro fechando conexão
        with app.app_context():
            db.session.close()
        
        response = client.post('/auth/onboarding?step=2', data=data)
        
        # Deve retornar erro 500 mas não quebrar
        assert response.status_code == 500
        
        json_data = json.loads(response.data)
        assert json_data['success'] is False

# Script para executar testes
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

**FASE 3: TESTES DE INTEGRAÇÃO**

Crie testes de fluxo completo:

```python
# tests/test_integration_flow.py
import pytest
from app import create_app, db
from app.models import User, Interesse

class TestIntegrationFlow:
    """Testes de integração do fluxo completo"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Setup inicial
            interesses = ['cereais', 'horticultura', 'fruticultura']
            for nome in interesses:
                interesse = Interesse(nome=nome)
                db.session.add(interesse)
            
            db.session.commit()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_complete_user_flow(self, client, app):
        """Teste: Fluxo completo do usuário novo"""
        
        # 1. Criar usuário
        with app.app_context():
            user = User(email='newuser@agrotech.pt')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # 2. Login
        response = client.post('/auth/login', data={
            'email': 'newuser@agrotech.pt',
            'password': 'password123'
        })
        assert response.status_code == 302
        
        # 3. Acessar dashboard
        response = client.get('/dashboard')
        assert response.status_code == 200
        
        # 4. Acessar onboarding step 2
        response = client.get('/auth/onboarding?step=2')
        assert response.status_code == 200
        
        # 5. Completar onboarding step 2
        response = client.post('/auth/onboarding?step=2', data={
            'nome_completo': 'Novo Usuário',
            'experiencia': 'basico',
            'tipo_produtor': 'familiar',
            'interesses': ['cereais', 'horticultura']
        })
        assert response.status_code == 200
        
        # 6. Verificar redirecionamento para step 3
        import json
        json_data = json.loads(response.data)
        assert json_data['success'] is True
        assert json_data['next_step'] == 3
        
        # 7. Navegar entre seções
        sections = ['/dashboard', '/culturas', '/agente']
        for section in sections:
            response = client.get(section)
            assert response.status_code == 200
        
        # 8. Logout
        response = client.get('/auth/logout')
        assert response.status_code == 302
        
        # 9. Verificar que não consegue acessar seções protegidas
        response = client.get('/culturas')
        assert response.status_code == 302
        assert '/auth/login' in response.location

# Script para executar testes
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

**FASE 4: TESTES MANUAIS ESTRUTURADOS**

Crie um checklist de testes manuais:

```markdown
# Checklist de Testes Manuais - Sprint 1

## TESTES DE SISTEMA DE SESSÕES

### ✅ Teste 1: Login e Navegação Básica
- [ ] Acessar /auth/login
- [ ] Fazer login com credenciais válidas
- [ ] Verificar redirecionamento para dashboard
- [ ] Navegar para /culturas
- [ ] Verificar que NÃO há redirecionamento para login
- [ ] Navegar para /agente
- [ ] Verificar que NÃO há redirecionamento para login
- [ ] Navegar para /marketplace
- [ ] Verificar que NÃO há redirecionamento para login

### ✅ Teste 2: Persistência de Sessão
- [ ] Fazer login
- [ ] Navegar entre diferentes seções
- [ ] Fazer refresh da página (F5)
- [ ] Verificar que usuário continua logado
- [ ] Fechar aba e reabrir
- [ ] Verificar que usuário continua logado (se dentro do timeout)

### ✅ Teste 3: Logout
- [ ] Fazer login
- [ ] Clicar em logout
- [ ] Verificar redirecionamento para login
- [ ] Tentar acessar /culturas diretamente
- [ ] Verificar redirecionamento para login

### ✅ Teste 4: Múltiplas Abas
- [ ] Fazer login em aba A
- [ ] Abrir nova aba B no mesmo browser
- [ ] Acessar /culturas na aba B
- [ ] Verificar que funciona sem novo login
- [ ] Fazer logout na aba A
- [ ] Tentar acessar seção protegida na aba B
- [ ] Verificar comportamento adequado

## TESTES DE ONBOARDING

### ✅ Teste 5: Onboarding Step 2 - Dados Válidos
- [ ] Fazer login
- [ ] Acessar /auth/onboarding?step=2
- [ ] Preencher nome completo: "João Silva"
- [ ] Preencher telefone: "+351 912345678"
- [ ] Selecionar experiência: "Intermediário"
- [ ] Selecionar tipo: "Agricultura Familiar"
- [ ] Selecionar 2 interesses
- [ ] Clicar "Próximo"
- [ ] Verificar que avança para step 3

### ✅ Teste 6: Onboarding Step 2 - Validação de Erros
- [ ] Acessar step 2
- [ ] Deixar nome vazio
- [ ] Clicar "Próximo"
- [ ] Verificar mensagem de erro
- [ ] Preencher nome
- [ ] Deixar experiência vazia
- [ ] Clicar "Próximo"
- [ ] Verificar mensagem de erro
- [ ] Preencher todos os campos
- [ ] Selecionar 4 interesses
- [ ] Clicar "Próximo"
- [ ] Verificar erro "máximo 3 interesses"

### ✅ Teste 7: Onboarding Step 2 - Telefone Português
- [ ] Acessar step 2
- [ ] Preencher telefone: "123456789"
- [ ] Completar outros campos
- [ ] Clicar "Próximo"
- [ ] Verificar erro de formato
- [ ] Corrigir para "+351 912345678"
- [ ] Clicar "Próximo"
- [ ] Verificar que aceita

### ✅ Teste 8: Onboarding Step 2 - Loading State
- [ ] Acessar step 2
- [ ] Preencher todos os campos
- [ ] Clicar "Próximo"
- [ ] Verificar que botão mostra "A processar..."
- [ ] Verificar que botão fica desabilitado
- [ ] Aguardar resposta
- [ ] Verificar que volta ao normal ou redireciona

## TESTES DE REGRESSÃO

### ✅ Teste 9: Funcionalidades Existentes
- [ ] Dashboard carrega corretamente
- [ ] Widgets do dashboard funcionam
- [ ] Dados climáticos são exibidos
- [ ] Menu lateral funciona
- [ ] Responsividade mobile funciona

### ✅ Teste 10: Performance
- [ ] Login em < 2 segundos
- [ ] Navegação entre seções em < 1 segundo
- [ ] Onboarding step 2 processa em < 3 segundos
- [ ] Sem travamentos ou timeouts

## TESTES EM DIFERENTES BROWSERS

### ✅ Teste 11: Chrome
- [ ] Repetir testes principais no Chrome
- [ ] Verificar console para erros JavaScript
- [ ] Testar responsividade

### ✅ Teste 12: Firefox
- [ ] Repetir testes principais no Firefox
- [ ] Verificar compatibilidade

### ✅ Teste 13: Safari (se disponível)
- [ ] Repetir testes principais no Safari
- [ ] Verificar compatibilidade

## TESTES DE LOGS E DEBUGGING

### ✅ Teste 14: Logs do Sistema
- [ ] Verificar logs de login/logout
- [ ] Verificar logs de onboarding
- [ ] Verificar logs de erro (se houver)
- [ ] Confirmar que logs são informativos

### ✅ Teste 15: Network Requests
- [ ] Usar DevTools para monitorar requests
- [ ] Verificar que requests são enviados corretamente
- [ ] Verificar que responses são recebidos
- [ ] Verificar headers e status codes
```

**FASE 5: SCRIPT DE VALIDAÇÃO AUTOMATIZADA**

Crie um script para executar todos os testes:

```bash
#!/bin/bash
# validate_sprint1.sh

echo "🚀 Iniciando validação do Sprint 1 - AgroTech Portugal"
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 1. Verificar ambiente
log "Verificando ambiente..."
if [ ! -f "app.py" ]; then
    error "app.py não encontrado. Execute no diretório raiz do projeto."
    exit 1
fi

# 2. Instalar dependências de teste
log "Instalando dependências de teste..."
pip install pytest pytest-flask > /dev/null 2>&1

# 3. Executar testes de sessões
log "Executando testes de sistema de sessões..."
python -m pytest tests/test_auth_sessions.py -v
if [ $? -ne 0 ]; then
    error "Testes de sessões falharam!"
    exit 1
fi

# 4. Executar testes de onboarding
log "Executando testes de onboarding..."
python -m pytest tests/test_onboarding.py -v
if [ $? -ne 0 ]; then
    error "Testes de onboarding falharam!"
    exit 1
fi

# 5. Executar testes de integração
log "Executando testes de integração..."
python -m pytest tests/test_integration_flow.py -v
if [ $? -ne 0 ]; then
    error "Testes de integração falharam!"
    exit 1
fi

# 6. Verificar logs
log "Verificando sistema de logs..."
if [ ! -d "logs" ]; then
    warning "Diretório de logs não encontrado"
fi

# 7. Testar servidor local
log "Testando servidor local..."
python app.py &
SERVER_PID=$!
sleep 5

# Testar se servidor está respondendo
curl -s http://localhost:5000 > /dev/null
if [ $? -eq 0 ]; then
    log "Servidor local funcionando ✅"
else
    error "Servidor local não está respondendo"
fi

# Parar servidor
kill $SERVER_PID 2>/dev/null

# 8. Relatório final
echo ""
echo "=================================================="
echo -e "${GREEN}✅ VALIDAÇÃO DO SPRINT 1 CONCLUÍDA${NC}"
echo "=================================================="
echo ""
echo "Próximos passos:"
echo "1. Executar testes manuais do checklist"
echo "2. Testar em diferentes browsers"
echo "3. Validar com stakeholders"
echo "4. Deploy para staging"
echo ""
echo "🎉 Sprint 1 pronto para aprovação!"
```

### Critérios de Aceitação Final

**SISTEMA DE SESSÕES**:
- ✅ Login funciona e mantém sessão entre todas as rotas
- ✅ Todas as seções protegidas são acessíveis após login
- ✅ Logout limpa sessão completamente
- ✅ Timeout de sessão funciona adequadamente
- ✅ Não há redirecionamentos inesperados
- ✅ Logs mostram comportamento correto

**ONBOARDING**:
- ✅ Formulário avança para Passo 3 após preenchimento correto
- ✅ Dados são salvos corretamente no banco de dados
- ✅ Validação de erros funciona e exibe mensagens claras
- ✅ Interface responsiva funciona em mobile
- ✅ Não há travamentos ou timeouts
- ✅ Loading states funcionam adequadamente

**QUALIDADE GERAL**:
- ✅ Todos os testes automatizados passam
- ✅ Performance não foi degradada
- ✅ Não há regressões em funcionalidades existentes
- ✅ Logs implementados adequadamente
- ✅ Código segue padrões de qualidade

### Entregáveis Esperados
1. **Suite de Testes Automatizados** completa e funcional
2. **Checklist de Testes Manuais** executado
3. **Script de Validação** automatizado
4. **Relatório de Testes** com resultados
5. **Sistema Validado** pronto para próxima sprint

### Informações Importantes
- Execute todos os testes antes de considerar o Sprint 1 concluído
- Documente qualquer problema encontrado
- Valide em múltiplos browsers se possível
- Confirme que logs estão funcionando adequadamente
- Prepare ambiente para Sprint 2

---

## 📋 RESUMO DOS PROMPTS PARA CLAUDE SONNET 4

### Ordem de Execução Recomendada

1. **PROMPT 1**: Diagnóstico Completo do Sistema de Sessões
2. **PROMPT 2**: Implementação da Correção de Sessões
3. **PROMPT 3**: Diagnóstico do Problema de Onboarding
4. **PROMPT 4**: Correção do Formulário de Onboarding
5. **PROMPT 5**: Validação e Testes das Correções

### Tempo Estimado Total
- **Diagnósticos**: 4-6 horas
- **Implementações**: 12-16 horas
- **Testes e Validação**: 6-8 horas
- **Total**: 22-30 horas (3-4 dias de trabalho)

### Recursos Necessários
- Acesso ao código fonte do AgroTech Portugal
- Ambiente de desenvolvimento configurado
- Ferramentas de teste (pytest, browser DevTools)
- Acesso ao banco de dados de desenvolvimento

### Critérios de Sucesso
- Ambos os problemas críticos resolvidos
- Todos os testes passando
- Sistema estável e pronto para Sprint 2
- Documentação e logs implementados

**Estes prompts fornecem um guia completo e detalhado para resolver os problemas críticos do Sprint 1 do AgroTech Portugal usando Claude Sonnet 4.**

