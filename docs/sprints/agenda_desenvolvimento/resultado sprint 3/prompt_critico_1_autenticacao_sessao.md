# 🔐 PROMPT CRÍTICO 1: CORREÇÃO DO SISTEMA DE AUTENTICAÇÃO/SESSÃO

**URGÊNCIA:** CRÍTICA - 24-48 HORAS  
**PROBLEMA:** Sistema de autenticação/sessão quebrado  
**IMPACTO:** 100% das funcionalidades principais inacessíveis  
**PRIORIDADE:** MÁXIMA (Bloqueia todo o Sprint 3)

---

## 🎯 CONTEXTO EXECUTIVO

Você é um desenvolvedor especialista em Flask trabalhando no projeto **AgroTech Portugal**. O sistema está com um problema crítico: usuários conseguem fazer login no dashboard principal, mas ao tentar acessar qualquer funcionalidade específica (`/cultures`, `/agent`, `/marketplace`, `/monitoring`), são **redirecionados automaticamente para a página de login**.

Este problema foi identificado em validação automatizada que reprovou o Sprint 3 com score de **10%** devido a **5 problemas críticos**, sendo este o mais grave.

### 📊 EVIDÊNCIAS DO PROBLEMA

**Funcionando:**
- ✅ Login em `/auth/login` - Usuário consegue autenticar
- ✅ Dashboard em `/` - Carrega normalmente após login
- ✅ Navegação visual - Menu lateral aparece corretamente

**Quebrado:**
- ❌ `/cultures` - Redirecionamento para login
- ❌ `/agent` - Redirecionamento para login
- ❌ `/marketplace` - Redirecionamento para login
- ❌ `/monitoring` - Redirecionamento para login

### 🔍 ANÁLISE TÉCNICA INICIAL

**Hipóteses da Causa Raiz:**
1. **Middleware de autenticação mal configurado** - `@login_required` não reconhece sessão
2. **Configuração de sessão incorreta** - Cookies não persistem entre rotas
3. **Rotas não implementadas** - URLs podem não existir no sistema
4. **Problema de domínio/path** - Sessão não compartilhada entre rotas

---

## 🛠️ ESPECIFICAÇÕES TÉCNICAS

### Ambiente de Desenvolvimento
- **Framework:** Flask 3.1.1
- **Autenticação:** Flask-Login
- **Sessões:** Flask-Session  
- **Banco de Dados:** PostgreSQL (Railway)
- **Deploy:** Railway (automático via GitHub)
- **Repositório:** https://github.com/convey4you/agente_agricola

### Ferramentas Obrigatórias
- **VS Code** com GitHub Copilot
- **Python 3.11+**
- **Git** para versionamento

---

## 📋 TAREFA ESPECÍFICA

### OBJETIVO PRINCIPAL
Corrigir o sistema de autenticação/sessão para que usuários logados possam acessar **todas as funcionalidades** sem redirecionamento para login.

### ESCOPO DA CORREÇÃO

#### 1. INVESTIGAÇÃO OBRIGATÓRIA (30-60 min)

**Verificar Arquivos Críticos:**
```bash
# Arquivos que DEVEM ser analisados
app/__init__.py          # Configuração principal
app/auth/routes.py       # Rotas de autenticação  
app/main/routes.py       # Rotas principais
app/models/user.py       # Modelo de usuário
requirements.txt         # Dependências
```

**Pontos de Investigação:**
- [ ] Configuração do Flask-Login está correta?
- [ ] SECRET_KEY está definida adequadamente?
- [ ] Login manager está inicializado?
- [ ] User loader está implementado?
- [ ] Decoradores @login_required estão corretos?
- [ ] Rotas `/cultures`, `/agent`, `/marketplace`, `/monitoring` existem?

#### 2. CORREÇÃO DA CONFIGURAÇÃO (60-120 min)

**app/__init__.py - Configuração Principal:**
```python
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Configuração obrigatória
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-segura'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

# Inicialização do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Faça login para acessar esta página.'

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))
```

**Configurações de Sessão Necessárias:**
```python
# Configurações de sessão para produção
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
```

#### 3. IMPLEMENTAÇÃO DAS ROTAS FALTANTES (120-180 min)

**Criar/Corrigir Rotas Principais:**

```python
# app/main/routes.py
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@main.route('/cultures')
@login_required
def cultures():
    # Implementar lógica de culturas
    return render_template('cultures/index.html', user=current_user)

@main.route('/agent')
@login_required
def agent():
    # Implementar lógica do agente IA
    return render_template('agent/index.html', user=current_user)

@main.route('/marketplace')
@login_required
def marketplace():
    # Implementar lógica do marketplace
    return render_template('marketplace/index.html', user=current_user)

@main.route('/monitoring')
@login_required
def monitoring():
    # Implementar lógica de monitoramento
    return render_template('monitoring/index.html', user=current_user)
```

#### 4. CRIAÇÃO DE TEMPLATES BÁSICOS (60-90 min)

**Templates Mínimos Necessários:**

```html
<!-- templates/cultures/index.html -->
{% extends "base.html" %}
{% block title %}Culturas - AgTech Portugal{% endblock %}
{% block content %}
<div class="container-fluid">
    <h1>Gestão de Culturas</h1>
    <p>Bem-vindo à seção de culturas, {{ current_user.email }}!</p>
    <div class="alert alert-info">
        <strong>Funcionalidade em desenvolvimento.</strong>
        Esta página confirma que a autenticação está funcionando corretamente.
    </div>
</div>
{% endblock %}
```

**Criar templates similares para:**
- `templates/agent/index.html`
- `templates/marketplace/index.html`  
- `templates/monitoring/index.html`

#### 5. VALIDAÇÃO E TESTES (30-60 min)

**Script de Teste Local:**
```python
# test_authentication.py
import requests

def test_authentication_flow():
    base_url = "http://localhost:5000"
    
    # Teste 1: Login
    login_data = {
        'email': 'teste.final.sprint1@agrotech.pt',
        'password': 'TesteFinalSprint2025!'
    }
    
    session = requests.Session()
    response = session.post(f"{base_url}/auth/login", data=login_data)
    
    # Teste 2: Acessar funcionalidades
    routes = ['/cultures', '/agent', '/marketplace', '/monitoring']
    
    for route in routes:
        response = session.get(f"{base_url}{route}")
        if response.status_code == 200:
            print(f"✅ {route}: OK")
        else:
            print(f"❌ {route}: FALHOU ({response.status_code})")

if __name__ == "__main__":
    test_authentication_flow()
```

---

## ✅ CRITÉRIOS DE VALIDAÇÃO

### TESTES OBRIGATÓRIOS

**1. Teste Manual (Browser):**
- [ ] Login em `/auth/login` funciona
- [ ] Dashboard `/` carrega após login
- [ ] `/cultures` carrega sem redirecionamento
- [ ] `/agent` carrega sem redirecionamento
- [ ] `/marketplace` carrega sem redirecionamento
- [ ] `/monitoring` carrega sem redirecionamento
- [ ] Logout funciona corretamente
- [ ] Sessão persiste entre navegações

**2. Teste Automatizado:**
```bash
# Executar script de validação
python3 validacao_automatizada_sprint3.py
```

**Resultado esperado:**
- Score: 10% → ≥50% (mínimo após esta correção)
- Testes de funcionalidades: 0% → 100%
- Problemas críticos: 5 → ≤2

### CRITÉRIOS DE APROVAÇÃO

**Mínimos Obrigatórios:**
- ✅ Todas as 4 funcionalidades acessíveis
- ✅ Nenhum redirecionamento indevido para login
- ✅ Sessão persiste corretamente
- ✅ Templates básicos carregando
- ✅ Navegação fluida entre seções

**Desejáveis:**
- ✅ Mensagens de erro claras
- ✅ Loading states adequados
- ✅ Design responsivo básico
- ✅ Logs de debug implementados

---

## 📦 ENTREGÁVEIS OBRIGATÓRIOS

### 1. CÓDIGO CORRIGIDO
- [ ] `app/__init__.py` - Configuração corrigida
- [ ] `app/main/routes.py` - Rotas implementadas
- [ ] `app/auth/routes.py` - Autenticação validada
- [ ] `app/models/user.py` - Modelo atualizado (se necessário)

### 2. TEMPLATES BÁSICOS
- [ ] `templates/cultures/index.html`
- [ ] `templates/agent/index.html`
- [ ] `templates/marketplace/index.html`
- [ ] `templates/monitoring/index.html`

### 3. TESTES E VALIDAÇÃO
- [ ] Script de teste local
- [ ] Documentação das correções
- [ ] Logs de debug implementados
- [ ] Validação automatizada passando

### 4. DOCUMENTAÇÃO
- [ ] README atualizado
- [ ] Changelog das correções
- [ ] Instruções de deploy
- [ ] Troubleshooting guide

---

## 🚀 INSTRUÇÕES DE EXECUÇÃO

### PASSO 1: SETUP DO AMBIENTE
```bash
# Clonar repositório
git clone https://github.com/convey4you/agente_agricola.git
cd agente_agricola

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export FLASK_APP=app
export FLASK_ENV=development
export DATABASE_URL="sua-url-do-banco"
export SECRET_KEY="sua-chave-secreta"
```

### PASSO 2: INVESTIGAÇÃO
```bash
# Analisar estrutura atual
find . -name "*.py" | grep -E "(auth|main|routes)" | head -10
grep -r "login_required" app/
grep -r "Flask-Login" .
```

### PASSO 3: IMPLEMENTAÇÃO
1. Corrigir `app/__init__.py`
2. Implementar rotas em `app/main/routes.py`
3. Criar templates básicos
4. Testar localmente

### PASSO 4: VALIDAÇÃO
```bash
# Teste local
python test_authentication.py

# Deploy para produção
git add .
git commit -m "fix: correção crítica do sistema de autenticação/sessão"
git push origin main

# Aguardar deploy automático (Railway)
# Testar em produção: https://www.agenteagricola.com
```

### PASSO 5: CONFIRMAÇÃO
```bash
# Executar validação automatizada
python3 validacao_automatizada_sprint3.py

# Verificar resultado:
# - Score deve subir de 10% para ≥50%
# - Funcionalidades devem estar acessíveis
# - Problemas críticos devem diminuir
```

---

## ⚠️ PONTOS DE ATENÇÃO CRÍTICOS

### ERROS COMUNS A EVITAR

**1. Configuração de Sessão:**
```python
# ❌ ERRADO
app.config['SECRET_KEY'] = None

# ✅ CORRETO  
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')
```

**2. User Loader:**
```python
# ❌ ERRADO - Sem user loader
@login_manager.user_loader
def load_user(user_id):
    return None

# ✅ CORRETO
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

**3. Decoradores:**
```python
# ❌ ERRADO - Decorador faltando
@app.route('/cultures')
def cultures():
    return render_template('cultures.html')

# ✅ CORRETO
@app.route('/cultures')
@login_required
def cultures():
    return render_template('cultures.html')
```

### DEBUGGING OBRIGATÓRIO

**Adicionar logs de debug:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/cultures')
@login_required
def cultures():
    app.logger.debug(f"Usuário {current_user.id} acessou /cultures")
    return render_template('cultures/index.html')
```

---

## 🎯 RESULTADO ESPERADO

### ANTES DA CORREÇÃO
- Score: 10%
- Funcionalidades acessíveis: 0/4
- Problemas críticos: 5
- Status: REPROVADO

### APÓS A CORREÇÃO
- Score: ≥50%
- Funcionalidades acessíveis: 4/4
- Problemas críticos: ≤2
- Status: PROGRESSO SIGNIFICATIVO

### VALIDAÇÃO FINAL
```bash
# Teste manual
1. Login em https://www.agenteagricola.com/auth/login
2. Navegar para https://www.agenteagricola.com/cultures
3. Verificar se carrega sem redirecionamento
4. Repetir para /agent, /marketplace, /monitoring

# Teste automatizado
python3 validacao_automatizada_sprint3.py
```

---

## 🏆 CRITÉRIO DE SUCESSO

**Esta correção será considerada SUCESSO se:**

1. **Todas as 4 funcionalidades** (`/cultures`, `/agent`, `/marketplace`, `/monitoring`) **carregarem sem redirecionamento**
2. **Score da validação automatizada** subir de 10% para **≥50%**
3. **Usuário logado** conseguir navegar livremente entre todas as seções
4. **Nenhum problema crítico** relacionado à autenticação persistir

**Tempo estimado:** 4-8 horas de desenvolvimento focado  
**Impacto:** Desbloqueio completo das funcionalidades do Sprint 3  
**Prioridade:** MÁXIMA - Sem esta correção, Sprint 3 permanece reprovado

---

**🚨 URGENTE: Esta correção é CRÍTICA e deve ser implementada IMEDIATAMENTE. Todo o Sprint 3 depende desta funcionalidade básica funcionando corretamente!**

