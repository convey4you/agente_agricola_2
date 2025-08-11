# 🔧 PROMPTS CLAUDE SONNET 4 - CORREÇÕES CRÍTICAS SPRINT 2

**Projeto:** AgroTech Portugal - Sistema de Alertas Inteligentes  
**Data:** 1 de agosto de 2025  
**Gerente de Tecnologia:** Prompts para correções críticas  
**Objetivo:** Resolver problemas bloqueantes identificados na validação

## 📋 CONTEXTO TÉCNICO PARA CLAUDE SONNET 4

### Situação Atual
O Sprint 2 do AgroTech Portugal implementou um Sistema de Alertas Inteligentes, mas falhou na validação técnica com score de apenas 26%. O problema principal é um erro crítico de schema do banco de dados que torna toda a funcionalidade inacessível.

### Problema Crítico Identificado
```sql
psycopg2.errors.UndefinedColumn: column alerts.status does not exist
```

### Arquitetura do Projeto
- **Backend:** Flask 3.1.1 + SQLAlchemy 2.0.41
- **Banco:** PostgreSQL (Railway)
- **Deploy:** Git-based automatizado
- **Estrutura:** Clean Architecture com separação de responsabilidades

### Repositório
- **URL:** https://github.com/convey4you/agente_agricola
- **Branch:** main
- **Último commit:** da162dd

---

## 🚨 PROMPT 1: CORREÇÃO CRÍTICA DO SCHEMA DO BANCO

### Para Claude Sonnet 4:

```
Você é um desenvolvedor backend sênior especializado em Flask e SQLAlchemy trabalhando no projeto AgroTech Portugal. 

PROBLEMA CRÍTICO IDENTIFICADO:
A API de alertas está falhando com erro "column alerts.status does not exist". O sistema foi implementado assumindo que a coluna existe, mas ela não foi criada no banco de produção.

ERRO ESPECÍFICO:
```sql
psycopg2.errors.UndefinedColumn: column alerts.status does not exist
LINE 1: ... alerts_type, alerts.priority AS alerts_priority, alerts.sta...
```

CONTEXTO DO PROJETO:
- Flask 3.1.1 + SQLAlchemy 2.0.41
- PostgreSQL no Railway
- Sistema de alertas para agricultura portuguesa
- Deploy via Git (commit da162dd)

TAREFA URGENTE:
1. Analisar o modelo Alert atual no código
2. Identificar exatamente qual coluna 'status' está faltando
3. Criar migration SQLAlchemy para adicionar a coluna
4. Definir valores ENUM apropriados: PENDING, SENT, READ, DISMISSED, EXPIRED
5. Executar migration segura em produção
6. Validar que todas as queries funcionam

ESTRUTURA ESPERADA DA COLUNA:
- Nome: status
- Tipo: ENUM ou VARCHAR com constraint
- Valores: 'PENDING', 'SENT', 'READ', 'DISMISSED', 'EXPIRED'
- Default: 'PENDING'
- Nullable: False

REQUISITOS ESPECÍFICOS:
- Migration deve ser reversível
- Não pode quebrar dados existentes
- Deve funcionar com PostgreSQL
- Seguir padrões SQLAlchemy 2.0+
- Incluir validação pós-migration

ENTREGÁVEIS:
1. Arquivo de migration completo
2. Modelo Alert atualizado (se necessário)
3. Script de validação da migration
4. Instruções de execução em produção
5. Rollback procedure

VALIDAÇÃO OBRIGATÓRIA:
Após implementação, a query abaixo deve funcionar:
```sql
SELECT id, user_id, type, priority, status, title, message 
FROM alerts 
WHERE user_id = 42 AND status != 'EXPIRED' 
ORDER BY created_at DESC 
LIMIT 50
```

Use VS Code + GitHub Copilot para desenvolvimento. Priorize segurança e não quebre funcionalidades existentes.
```

---

## 🔧 PROMPT 2: CORREÇÃO DA API DE ALERTAS

### Para Claude Sonnet 4:

```
Você é um desenvolvedor backend especialista em APIs REST com Flask trabalhando no AgroTech Portugal.

CONTEXTO:
Após correção do schema do banco, precisa validar e corrigir todos os endpoints da API de alertas que estavam falhando.

ENDPOINTS PARA CORRIGIR:
1. GET /api/alerts/ - Listagem de alertas
2. POST /api/alerts/create - Criação de alertas  
3. POST /api/alerts/{id}/read - Marcar como lido
4. POST /api/alerts/{id}/dismiss - Dispensar alerta

PROBLEMAS IDENTIFICADOS:
- Erro de schema resolvido, mas podem existir outros bugs
- Integração com Flask-Login precisa funcionar
- Respostas JSON devem ser consistentes
- Tratamento de erros inadequado

REQUISITOS TÉCNICOS:
- Flask 3.1.1 + SQLAlchemy 2.0.41
- Autenticação via Flask-Login
- Respostas JSON padronizadas
- Status HTTP corretos
- Validação de entrada
- Logs apropriados

ESTRUTURA DE RESPOSTA ESPERADA:
```json
// GET /api/alerts/
{
  "alerts": [...],
  "total": 10,
  "status": "success"
}

// POST /api/alerts/create
{
  "id": 123,
  "message": "Alerta criado com sucesso",
  "status": "success"
}

// Erro
{
  "message": "Descrição do erro",
  "status": "error",
  "code": "VALIDATION_ERROR"
}
```

VALIDAÇÕES NECESSÁRIAS:
1. Usuário autenticado (Flask-Login)
2. Dados de entrada válidos
3. Permissões corretas (usuário só acessa seus alertas)
4. Tratamento de exceções SQL
5. Logs de auditoria

TESTES OBRIGATÓRIOS:
Criar testes para cada endpoint que validem:
- Autenticação requerida
- Dados válidos/inválidos
- Permissões de usuário
- Respostas JSON corretas
- Status HTTP apropriados

ENTREGÁVEIS:
1. Controllers/routes corrigidos
2. Modelos atualizados (se necessário)
3. Testes unitários para cada endpoint
4. Documentação da API
5. Script de validação manual

Use padrões REST, implemente tratamento robusto de erros e garanta segurança.
```

---

## 📊 PROMPT 3: CORREÇÃO DA INTEGRAÇÃO COM DASHBOARD

### Para Claude Sonnet 4:

```
Você é um desenvolvedor frontend especializado em JavaScript/AJAX trabalhando no AgroTech Portugal.

PROBLEMA IDENTIFICADO:
O dashboard está mostrando "Carregando alertas..." indefinidamente. A integração entre frontend e API de alertas não está funcionando.

CONTEXTO TÉCNICO:
- Dashboard em HTML/CSS/JavaScript
- API de alertas corrigida e funcionando
- Autenticação via Flask-Login (session-based)
- Precisa carregar alertas do usuário logado

PROBLEMAS POSSÍVEIS:
1. Chamada AJAX incorreta para /api/alerts/
2. Tratamento de erro inadequado
3. Parsing de JSON falhando
4. Loading state não sendo removido
5. Autenticação não sendo enviada

REQUISITOS:
- Carregar alertas via AJAX/fetch
- Mostrar loading state apropriado
- Tratar erros graciosamente
- Exibir alertas em formato amigável
- Atualizar em tempo real (opcional)

ESTRUTURA ESPERADA NO DASHBOARD:
```html
<div id="alerts-section">
  <h3>Alertas Recentes</h3>
  <div id="alerts-loading">Carregando alertas...</div>
  <div id="alerts-container" style="display:none;">
    <!-- Alertas serão inseridos aqui -->
  </div>
  <div id="alerts-empty" style="display:none;">
    Nenhum alerta no momento
  </div>
  <div id="alerts-error" style="display:none;">
    Erro ao carregar alertas
  </div>
</div>
```

FUNCIONALIDADES NECESSÁRIAS:
1. Carregar alertas na inicialização da página
2. Exibir cada alerta com: título, mensagem, prioridade, data
3. Permitir marcar como lido
4. Permitir dispensar alerta
5. Atualizar contador de alertas não lidos

TRATAMENTO DE ESTADOS:
- Loading: Mostrar spinner/mensagem
- Success: Exibir alertas ou mensagem de vazio
- Error: Mostrar mensagem de erro amigável
- Empty: Mensagem quando não há alertas

VALIDAÇÃO:
Testar com:
- Usuário com alertas
- Usuário sem alertas  
- Erro de rede
- Erro de autenticação
- Diferentes tipos de alertas

ENTREGÁVEIS:
1. JavaScript para carregamento de alertas
2. HTML/CSS para exibição
3. Tratamento de todos os estados
4. Funcionalidades de interação (ler/dispensar)
5. Testes manuais documentados

Use fetch() moderno, implemente UX responsiva e garanta acessibilidade.
```

---

## 🧪 PROMPT 4: IMPLEMENTAÇÃO DE TESTES AUTOMATIZADOS

### Para Claude Sonnet 4:

```
Você é um especialista em testes automatizados para aplicações Flask trabalhando no AgroTech Portugal.

CONTEXTO:
O Sprint 2 falhou na validação porque não havia testes adequados. Precisa implementar suite completa de testes automatizados para o sistema de alertas.

OBJETIVO:
Criar testes que validem todas as funcionalidades em ambiente de produção e detectem problemas antes do deploy.

TIPOS DE TESTES NECESSÁRIOS:
1. Testes unitários (modelos, services)
2. Testes de integração (API endpoints)
3. Testes de banco de dados (schema, queries)
4. Testes de autenticação
5. Testes end-to-end (fluxo completo)

FRAMEWORK RECOMENDADO:
- pytest para testes Python
- requests para testes de API
- SQLAlchemy testing utilities
- Factory Boy para dados de teste

ESTRUTURA DE TESTES:
```
tests/
├── conftest.py              # Configuração pytest
├── test_models.py           # Testes de modelos
├── test_alerts_api.py       # Testes da API de alertas
├── test_database.py         # Testes de banco
├── test_auth.py             # Testes de autenticação
├── test_integration.py      # Testes de integração
└── test_production.py       # Testes em produção
```

TESTES CRÍTICOS PARA ALERTAS:
1. Criação de alerta com dados válidos
2. Listagem de alertas por usuário
3. Marcar alerta como lido
4. Dispensar alerta
5. Validação de permissões
6. Tratamento de erros

TESTES DE BANCO DE DADOS:
1. Schema da tabela alerts
2. Todas as colunas existem
3. Constraints funcionam
4. Indexes estão criados
5. Migrations são reversíveis

TESTES DE PRODUÇÃO:
Criar script que rode em produção e valide:
- Conectividade com banco
- API endpoints funcionando
- Autenticação funcionando
- Performance adequada
- Logs sem erros

CONFIGURAÇÃO DE CI/CD:
- Testes devem rodar automaticamente
- Falha de teste bloqueia deploy
- Relatórios de cobertura
- Notificações de falhas

ENTREGÁVEIS:
1. Suite completa de testes
2. Configuração pytest
3. Script de testes de produção
4. Documentação de como executar
5. Integração com CI/CD

VALIDAÇÃO:
- Cobertura de código > 80%
- Todos os testes passam
- Testes detectam problemas conhecidos
- Execução rápida (< 2 minutos)

Use pytest, implemente fixtures reutilizáveis e garanta testes determinísticos.
```

---

## 🏥 PROMPT 5: MELHORIA DOS HEALTH CHECKS

### Para Claude Sonnet 4:

```
Você é um especialista em monitoramento e observabilidade para aplicações Flask trabalhando no AgroTech Portugal.

PROBLEMA:
Os health checks atuais não detectaram o problema crítico do Sprint 2. Precisa implementar health checks mais robustos que validem funcionalidades específicas.

HEALTH CHECKS ATUAIS:
- /health - Status básico
- /health/db - Conexão com banco
- /health/registration - Sistema de registro

NOVOS HEALTH CHECKS NECESSÁRIOS:
1. /health/alerts - Sistema de alertas específico
2. /health/schema - Validação de schema do banco
3. /health/api - Todos os endpoints críticos
4. /health/dependencies - Serviços externos

VALIDAÇÕES PARA /health/alerts:
```python
{
  "status": "healthy|degraded|unhealthy",
  "checks": {
    "database_schema": "pass|fail",
    "api_endpoints": "pass|fail", 
    "alert_creation": "pass|fail",
    "alert_listing": "pass|fail"
  },
  "details": {
    "alerts_table_exists": true,
    "required_columns": ["id", "user_id", "type", "priority", "status", "title", "message"],
    "missing_columns": [],
    "api_response_time_ms": 150,
    "last_alert_created": "2025-08-01T15:30:00Z"
  },
  "recommendations": []
}
```

VALIDAÇÕES DE SCHEMA:
- Verificar se tabela alerts existe
- Validar todas as colunas necessárias
- Verificar tipos de dados corretos
- Validar constraints e indexes
- Testar queries críticas

VALIDAÇÕES DE API:
- Testar GET /api/alerts/ com usuário de teste
- Testar POST /api/alerts/create
- Validar tempos de resposta
- Verificar autenticação
- Testar tratamento de erros

ALERTAS AUTOMÁTICOS:
- Notificar quando health checks falham
- Logs detalhados de problemas
- Métricas de disponibilidade
- Dashboard de status

CONFIGURAÇÃO:
- Health checks devem ser rápidos (< 5s)
- Não devem impactar performance
- Devem funcionar sem autenticação
- Logs estruturados

ENTREGÁVEIS:
1. Novos endpoints de health check
2. Validações específicas para alertas
3. Sistema de alertas automáticos
4. Dashboard de monitoramento
5. Documentação completa

INTEGRAÇÃO:
- Monitoramento externo (Uptime Robot, etc.)
- Logs centralizados
- Métricas para Grafana/similar
- Alertas via email/Slack

Use Flask-HealthCheck ou similar, implemente checks específicos e garanta observabilidade completa.
```

---

## 📚 PROMPT 6: DOCUMENTAÇÃO E PROCESSO DE DEPLOY

### Para Claude Sonnet 4:

```
Você é um especialista em DevOps e documentação técnica trabalhando no AgroTech Portugal.

CONTEXTO:
O Sprint 2 falhou porque o processo de deploy não incluiu migrations do banco. Precisa documentar e automatizar o processo para evitar problemas futuros.

PROBLEMAS IDENTIFICADOS:
1. Migrations não executadas automaticamente
2. Falta de validação pós-deploy
3. Ausência de checklist pré-deploy
4. Rollback procedures não documentados

DOCUMENTAÇÃO NECESSÁRIA:

### 1. CHECKLIST PRÉ-DEPLOY
```markdown
## Checklist Obrigatório Pré-Deploy

### Código
- [ ] Todos os testes passam localmente
- [ ] Code review aprovado
- [ ] Sem conflitos de merge
- [ ] Versão atualizada

### Banco de Dados
- [ ] Migrations criadas e testadas
- [ ] Backup do banco realizado
- [ ] Schema validado localmente
- [ ] Rollback procedure documentado

### Testes
- [ ] Testes unitários passam (100%)
- [ ] Testes de integração passam
- [ ] Testes de API validados
- [ ] Performance testada

### Infraestrutura
- [ ] Variáveis de ambiente configuradas
- [ ] Dependências atualizadas
- [ ] Logs configurados
- [ ] Monitoramento ativo
```

### 2. PROCESSO DE DEPLOY AUTOMATIZADO
Criar scripts que:
- Executem migrations automaticamente
- Validem schema pós-deploy
- Testem endpoints críticos
- Façam rollback em caso de falha

### 3. VALIDAÇÃO PÓS-DEPLOY
Script que execute após deploy:
```bash
#!/bin/bash
# Validação pós-deploy obrigatória

echo "Validando deploy..."

# 1. Health checks
curl -f https://www.agenteagricola.com/health || exit 1

# 2. API de alertas
curl -f https://www.agenteagricola.com/api/alerts/ || exit 1

# 3. Testes automatizados
python3 validacao_automatizada_sprint2.py || exit 1

echo "Deploy validado com sucesso!"
```

### 4. ROLLBACK PROCEDURES
Documentar como reverter:
- Código (git revert)
- Banco de dados (restore backup)
- Configurações (versões anteriores)
- Validação pós-rollback

AUTOMAÇÃO RAILWAY:
- Configurar deploy hooks
- Executar migrations automaticamente
- Validação pós-deploy obrigatória
- Notificações de status

ENTREGÁVEIS:
1. Checklist pré-deploy completo
2. Scripts de deploy automatizado
3. Validação pós-deploy
4. Procedures de rollback
5. Configuração Railway atualizada
6. Documentação para equipe

TREINAMENTO:
- Documentar processo para equipe
- Criar vídeos explicativos
- Estabelecer responsabilidades
- Definir aprovações necessárias

Use GitHub Actions ou similar, implemente validações robustas e garanta processo à prova de falhas.
```

---

## 🎯 SEQUÊNCIA DE EXECUÇÃO RECOMENDADA

### Ordem dos Prompts:
1. **PROMPT 1** - Correção do schema (URGENTE - 24h)
2. **PROMPT 2** - Correção da API (CRÍTICO - 48h)  
3. **PROMPT 3** - Correção do dashboard (ALTA - 48h)
4. **PROMPT 4** - Testes automatizados (ALTA - 72h)
5. **PROMPT 5** - Health checks melhorados (MÉDIA - 72h)
6. **PROMPT 6** - Documentação e processo (MÉDIA - 72h)

### Validação Entre Prompts:
- Após PROMPT 1: Testar query SQL básica
- Após PROMPT 2: Testar todos os endpoints da API
- Após PROMPT 3: Validar dashboard funcionando
- Após PROMPT 4: Executar suite de testes
- Após PROMPT 5: Verificar health checks
- Após PROMPT 6: Validar processo completo

### Critério de Sucesso:
- Score de validação ≥ 80%
- 0 problemas críticos
- Todos os testes passando
- Documentação completa

---

**Responsável:** Claude Sonnet 4  
**Supervisão:** Gerente de Tecnologia  
**Meta:** Sprint 2 aprovado em máximo 5 dias úteis

