# Prompts Claude Sonnet 4 - Correções Críticas AgroTech Portugal

**Documento Técnico Especializado**  
**Autor:** Gerente de Tecnologia  
**Data:** 2 de agosto de 2025  
**Objetivo:** Implementar correções críticas do sistema de registro  
**Prioridade:** CRÍTICA - EXECUÇÃO IMEDIATA

---

## 🎯 CONTEXTO GERAL PARA TODOS OS PROMPTS

### Situação do Projeto
O AgroTech Portugal é uma plataforma de agricultura familiar que está enfrentando um problema crítico no sistema de registro. Após investigação técnica profunda, identificamos que a causa raiz é a falta de inicialização automática das tabelas do banco de dados em produção.

### Arquitetura Atual
- **Framework:** Flask (Python)
- **Banco de Dados:** PostgreSQL (Railway)
- **ORM:** SQLAlchemy
- **Autenticação:** Flask-Login
- **Deploy:** Automático via GitHub Actions
- **Produção:** www.agenteagricola.com

### Problema Identificado
O sistema está falhando com "Erro interno do servidor" durante o registro de novos usuários porque as tabelas não estão sendo criadas automaticamente no banco de produção.

---

## 🔧 PROMPT 1: CORREÇÃO CRÍTICA - INICIALIZAÇÃO DO BANCO DE DADOS

### Contexto Específico
Você é um desenvolvedor Python especialista em Flask e SQLAlchemy trabalhando no projeto AgroTech Portugal. O sistema está falhando no registro de usuários porque as tabelas do banco não estão sendo criadas automaticamente em produção.

### Problema Técnico
O arquivo `app/__init__.py` não possui inicialização automática de tabelas, causando falha na operação `db.session.add(user)` durante o registro.

### Tarefa
Corrija o arquivo `app/__init__.py` adicionando inicialização automática e robusta das tabelas do banco de dados.

### Código Atual (Parcial)
```python
# app/__init__.py - VERSÃO ATUAL COM PROBLEMA
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    
    # Registrar blueprints
    from app.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app
```

### Especificações da Correção

1. **Inicialização Robusta de Tabelas**
   - Verificar se tabelas já existem antes de criar
   - Usar `db.create_all()` dentro do contexto da aplicação
   - Implementar tratamento de exceções adequado
   - Adicionar logs informativos

2. **Verificação de Schema**
   - Usar SQLAlchemy Inspector para verificar tabelas existentes
   - Verificar especificamente a tabela 'users'
   - Criar tabelas apenas se necessário

3. **Tratamento de Erros**
   - Capturar exceções durante criação de tabelas
   - Implementar fallback para tentar criar tabelas mesmo com erros
   - Não falhar a aplicação por problemas de banco

4. **Logging Adequado**
   - Logs informativos sobre criação de tabelas
   - Logs de erro com detalhes técnicos
   - Mensagens claras para debugging

### Modelos Existentes
```python
# app/models/user.py - MODELO EXISTENTE
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nome_completo = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    onboarding_completed = db.Column(db.Boolean, default=False)
    # ... outros campos
```

### Requisitos Técnicos

1. **Compatibilidade**
   - Funcionar com PostgreSQL (Railway)
   - Compatível com SQLite (desenvolvimento)
   - Suportar múltiplos ambientes

2. **Performance**
   - Verificação rápida de tabelas existentes
   - Não impactar tempo de inicialização
   - Operação idempotente

3. **Segurança**
   - Não expor informações sensíveis nos logs
   - Tratamento seguro de conexões de banco
   - Validação de contexto de aplicação

### Resultado Esperado
Arquivo `app/__init__.py` corrigido que:
- Cria tabelas automaticamente se não existirem
- Funciona em produção (Railway PostgreSQL)
- Possui logging adequado
- Trata exceções robustamente
- Não quebra funcionalidades existentes

### Validação
Após implementação, o sistema deve:
- Permitir registro de novos usuários
- Criar tabelas automaticamente no primeiro acesso
- Funcionar em www.agenteagricola.com
- Não gerar erros de "tabela não existe"

---

## 🏥 PROMPT 2: IMPLEMENTAÇÃO DE HEALTH CHECK

### Contexto Específico
Você é um desenvolvedor Flask especialista em monitoramento e observabilidade. Precisa criar um sistema de health check para o AgroTech Portugal que permita monitorar a saúde do banco de dados e do sistema de registro.

### Problema
O sistema não possui endpoints de monitoramento, dificultando o diagnóstico de problemas em produção.

### Tarefa
Criar um controller completo de health check com endpoints especializados para monitoramento do sistema.

### Especificações dos Endpoints

1. **`/health` - Health Check Básico**
   - Verificar conectividade com banco
   - Verificar se tabelas existem
   - Retornar status geral do sistema
   - Tempo de resposta < 1 segundo

2. **`/health/db` - Health Check de Banco**
   - Testar conexão com PostgreSQL
   - Verificar existência de tabelas críticas
   - Contar registros na tabela users
   - Listar colunas da tabela users
   - Validar estrutura do schema

3. **`/health/registration` - Health Check de Registro**
   - Testar validadores de registro
   - Verificar estrutura da tabela users
   - Simular processo de validação
   - Identificar problemas específicos

### Estrutura Esperada
```python
# app/controllers/health_controller.py - ARQUIVO A CRIAR
from datetime import datetime
from flask import Blueprint, jsonify
from app import db
from app.models.user import User

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    # Implementar verificação básica
    pass

@health_bp.route('/health/db')
def database_health():
    # Implementar verificação detalhada de banco
    pass

@health_bp.route('/health/registration')
def registration_health():
    # Implementar verificação específica de registro
    pass
```

### Requisitos Técnicos

1. **Respostas JSON Padronizadas**
   - Status: "healthy" ou "unhealthy"
   - Timestamp ISO 8601
   - Detalhes técnicos quando necessário
   - Códigos HTTP apropriados (200, 503)

2. **Verificações Robustas**
   - Timeout de 5 segundos para operações de banco
   - Tratamento de exceções completo
   - Não falhar por problemas temporários
   - Logs detalhados para debugging

3. **Informações Úteis**
   - Versão do sistema
   - Contagem de usuários
   - Estrutura de tabelas
   - Status de conexão

### Integração
O health check deve ser registrado no `app/__init__.py`:
```python
# Adicionar no create_app()
try:
    from app.controllers.health_controller import health_bp
    app.register_blueprint(health_bp, url_prefix='/')
except ImportError:
    pass  # Health check opcional
```

### Validação
Endpoints devem responder:
- `GET /health` → Status 200 com JSON
- `GET /health/db` → Detalhes do banco
- `GET /health/registration` → Status do registro

---

## 🔍 PROMPT 3: VALIDAÇÃO E TESTES DAS CORREÇÕES

### Contexto Específico
Você é um especialista em QA e testes automatizados. Precisa criar scripts de validação para verificar se as correções do sistema de registro foram implementadas corretamente.

### Tarefa
Criar scripts Python para validar automaticamente as correções implementadas.

### Especificações dos Testes

1. **Teste de Inicialização de Banco**
   - Verificar se `db.create_all()` foi adicionado
   - Testar criação de tabelas em ambiente limpo
   - Validar logs de inicialização
   - Confirmar estrutura das tabelas

2. **Teste de Health Checks**
   - Verificar se endpoints respondem
   - Validar formato das respostas JSON
   - Testar cenários de erro
   - Confirmar códigos HTTP corretos

3. **Teste de Registro de Usuário**
   - Simular registro completo
   - Verificar criação no banco
   - Testar login após registro
   - Validar redirecionamento

### Script de Validação
```python
#!/usr/bin/env python3
"""
Script de validação das correções críticas
Executa testes automatizados para verificar implementação
"""

import requests
import json
from datetime import datetime

class CorrectionsValidator:
    def __init__(self, base_url="https://www.agenteagricola.com"):
        self.base_url = base_url
        self.results = []
    
    def test_health_endpoints(self):
        # Implementar testes de health check
        pass
    
    def test_registration_flow(self):
        # Implementar teste de registro
        pass
    
    def generate_report(self):
        # Gerar relatório de validação
        pass

if __name__ == "__main__":
    validator = CorrectionsValidator()
    validator.run_all_tests()
```

### Critérios de Aprovação

1. **Health Checks**
   - `/health` retorna status 200
   - `/health/db` mostra tabelas existentes
   - `/health/registration` confirma sistema OK

2. **Sistema de Registro**
   - Formulário carrega corretamente
   - Submissão não gera erro interno
   - Usuário é criado no banco
   - Redirecionamento funciona

3. **Logs e Monitoramento**
   - Logs de inicialização presentes
   - Mensagens de erro específicas
   - Timestamps corretos

### Validação Final
Script deve gerar relatório confirmando:
- ✅ Correções implementadas
- ✅ Sistema funcionando
- ✅ Registro operacional
- ✅ Health checks ativos

---

## 📋 INSTRUÇÕES DE USO DOS PROMPTS

### Para Claude Sonnet 4

1. **Execute os prompts em sequência**
   - Prompt 1: Correção do `__init__.py`
   - Prompt 2: Criação do health check
   - Prompt 3: Scripts de validação

2. **Contexto Completo**
   - Cada prompt inclui contexto específico
   - Especificações técnicas detalhadas
   - Exemplos de código quando necessário

3. **Validação Obrigatória**
   - Testar código antes de entregar
   - Verificar compatibilidade com Flask
   - Confirmar funcionamento com PostgreSQL

### Para a Equipe de Desenvolvimento

1. **Implementação Sequencial**
   - Aplicar correções na ordem especificada
   - Testar cada correção individualmente
   - Validar em ambiente de desenvolvimento

2. **Deploy Cuidadoso**
   - Fazer backup antes das alterações
   - Deploy em horário de baixo tráfego
   - Monitorar logs após implementação

3. **Validação Completa**
   - Executar scripts de teste
   - Verificar health checks
   - Testar registro manual

---

## ✅ RESULTADOS ESPERADOS

### Após Implementação das Correções

1. **Sistema de Registro**
   - 95%+ de registros bem-sucedidos
   - Erro "interno do servidor" eliminado
   - Redirecionamento para onboarding funcionando

2. **Monitoramento**
   - Health checks ativos e funcionais
   - Logs detalhados disponíveis
   - Diagnóstico proativo de problemas

3. **Qualidade Técnica**
   - Score de conformidade 85%+
   - Código robusto e bem documentado
   - Tratamento de exceções adequado

### Aprovação do Sprint 1
Com as correções implementadas, o Sprint 1 poderá ser aprovado e o projeto seguirá para o Sprint 2 conforme cronograma original.

---

**PROMPTS PRONTOS PARA EXECUÇÃO COM CLAUDE SONNET 4**  
**IMPLEMENTAÇÃO IMEDIATA RECOMENDADA**

