# 🚨 INSTRUÇÕES DE EXECUÇÃO CRÍTICA - Migration Status Column

**PRIORIDADE:** CRÍTICA  
**PROBLEMA:** Sistema de alertas inacessível em produção  
**SOLUÇÃO:** Migration para adicionar coluna `status`

---

## 📋 PRÉ-REQUISITOS OBRIGATÓRIOS

### ✅ Checklist Antes da Execução
- [ ] **Backup realizado** (OBRIGATÓRIO)
- [ ] **Acesso ao Railway/Produção confirmado**
- [ ] **Migration testada em desenvolvimento**
- [ ] **Script de validação preparado**
- [ ] **Plano de rollback definido**

---

## 🚀 PASSOS DE EXECUÇÃO EM PRODUÇÃO

### 1️⃣ BACKUP CRÍTICO (OBRIGATÓRIO)
```bash
# No Railway CLI ou diretamente no PostgreSQL
pg_dump $DATABASE_URL > backup_pre_status_migration_$(date +%Y%m%d_%H%M%S).sql

# Verificar que backup foi criado
ls -la backup_pre_status_migration_*.sql
```

### 2️⃣ VALIDAÇÃO PRÉ-MIGRATION
```bash
# Verificar estado atual do banco
python -c "
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    result = db.session.execute(text('SELECT column_name FROM information_schema.columns WHERE table_name = \'alerts\' AND column_name = \'status\''))
    if result.fetchone():
        print('✅ Coluna status JÁ existe - migration desnecessária')
    else:
        print('❌ Coluna status NÃO existe - migration necessária')
"
```

### 3️⃣ EXECUTAR MIGRATION
```bash
# Executar migration específica
flask db upgrade

# OU se houver problemas, forçar a migration específica:
flask db upgrade fix_alerts_status_column
```

### 4️⃣ VALIDAÇÃO PÓS-MIGRATION
```bash
# Executar script de validação completa
python scripts/validate_alerts_schema.py

# Resultado esperado:
# 🎉 VALIDAÇÃO COMPLETA: SCHEMA DA TABELA ALERTS OK!
# ✅ Sistema de alertas pronto para produção
```

### 5️⃣ TESTE DA API DE ALERTAS
```bash
# Testar endpoint principal que estava falhando
curl -X GET "https://agente-agricola-production.up.railway.app/api/alerts/" \
     -H "Cookie: session=..." \
     -H "Content-Type: application/json"

# Resultado esperado: JSON válido, não erro SQL
```

### 6️⃣ VERIFICAÇÃO DE HEALTH CHECK
```bash
# Verificar health check do banco
curl https://agente-agricola-production.up.railway.app/health/db

# Resultado esperado: "missing_columns": 0
```

---

## 🔧 COMANDOS DE EMERGÊNCIA

### 🚨 Se Migration Falhar
```bash
# Verificar logs de erro
flask db history

# Marcar migration como executada manualmente (se necessário)
flask db stamp fix_alerts_status_column

# Tentar upgrade novamente
flask db upgrade
```

### 🔄 ROLLBACK (Se Necessário)
```bash
# Voltar à migration anterior
flask db downgrade

# Restaurar backup
psql $DATABASE_URL < backup_pre_status_migration_[timestamp].sql
```

---

## ✅ CRITÉRIOS DE VALIDAÇÃO OBRIGATÓRIOS

### 🎯 Validações Técnicas que DEVEM Passar:

1. **Query SQL Original (que estava falhando):**
```sql
SELECT alerts.id, alerts.user_id, alerts.type, alerts.priority, alerts.status, 
       alerts.title, alerts.message 
FROM alerts 
WHERE alerts.user_id = 42 AND alerts.status != 'EXPIRED' 
ORDER BY alerts.created_at DESC 
LIMIT 50;
```

2. **API de Alertas Funcional:**
```bash
# Deve retornar JSON válido
GET /api/alerts/
```

3. **Health Check do Banco:**
```json
{
  "status": "healthy",
  "missing_columns": 0
}
```

### 📊 Métricas de Sucesso:
- [ ] **Migration executada sem erros**
- [ ] **Coluna `status` criada com tipo VARCHAR(20)**
- [ ] **Index `ix_alerts_status` criado**
- [ ] **Constraint `check_alert_status` funcionando**
- [ ] **Query SQL original funciona**
- [ ] **API de alertas responde corretamente**
- [ ] **Health checks passam**
- [ ] **Zero perda de dados**

---

## 🎯 RESULTADO ESPERADO

### ✅ Após Execução Bem-Sucedida:
- **Sistema de alertas 100% funcional**
- **API respondendo corretamente**
- **Dashboard carregando alertas**
- **Score de validação: 26% → 80%+**
- **Sprint 2 aprovado para produção**

### 📈 Impacto no Negócio:
- **Agricultura Portuguesa**: Alertas funcionais novamente
- **Usuários**: Sistema de notificações ativo
- **Negócio**: Funcionalidade crítica restaurada

---

## 📞 CONTATOS DE EMERGÊNCIA

**Desenvolvedores**: GitHub Copilot AI Team  
**Plataforma**: Railway.app  
**Repositório**: https://github.com/convey4you/agente_agricola  
**Branch**: main  
**Migration**: fix_alerts_status_column  

---

## ⚠️ NOTAS IMPORTANTES

1. **Esta migration é IDEMPOTENTE** - pode ser executada múltiplas vezes sem problemas
2. **Compatível com SQLite (dev) e PostgreSQL (prod)**
3. **Zero downtime** - adição de coluna não requer parada do sistema
4. **Backup é OBRIGATÓRIO** - não executar sem backup
5. **Validação é CRÍTICA** - confirmar funcionamento antes de considerar completa

---

**🚨 Esta é a correção mais crítica para aprovação do Sprint 2**
