# 🗃️ Sistema de Gerenciamento do Banco de Dados

## 📖 Visão Geral

O sistema de gerenciamento do banco de dados oferece funcionalidades completas para manutenção e atualização do schema, funcionando tanto em **SQLite** (desenvolvimento) quanto **PostgreSQL** (produção). As principais funcionalidades incluem:

- ✅ **Sincronização Segura**: Atualiza schema sem perder dados existentes
- ✅ **Reset Completo**: Limpar e recriar todas as tabelas (desenvolvimento)
- ✅ **Migração**: Aplicar novos campos/modelos sem conflitos
- ✅ **Validação**: Verificar integridade e saúde do banco
- ✅ **Backup**: Proteção automática dos dados

## 🔒 Segurança

- **Acesso restrito**: Apenas admins (`admin@agrotech.pt`)
- **Confirmação dupla**: Confirmação de texto + confirmação visual (reset)
- **Auditoria completa**: Todas as operações são logadas
- **Backup automático**: SQLite é salvo antes de operações destrutivas

## 🖥️ Interface Web

### Acesso
```
http://localhost:5000/monitoring/dashboard-status
```

### Funcionalidades
1. **📊 Informações do Banco**
   - Tipo de banco (SQLite/PostgreSQL)
   - Número de tabelas e registros
   - Tamanho do arquivo (SQLite)
   - Status de saúde do banco

2. **🔍 Validação de Integridade**
   - Verificação de tabelas esperadas
   - Teste de conectividade
   - Score de saúde (0-100)
   - Lista de problemas encontrados

3. **🔄 Sincronização do Schema (NOVA FUNCIONALIDADE)**
   - **Operação 100% segura** - não remove dados existentes
   - Cria tabelas ausentes definidas no código
   - Adiciona campos novos às tabelas existentes
   - Preserva todos os dados atuais
   - Ideal para atualizações do sistema

4. **🗑️ Reset Completo**
   - Formulário com confirmação de segurança
   - Opção de backup automático
   - Feedback em tempo real
   - Log de auditoria

## 🔧 API REST

### Endpoints Disponíveis

#### 1. Informações do Banco
```http
GET /monitoring/database/info
Authorization: Required (Admin only)
```

**Resposta:**
```json
{
  "success": true,
  "database_type": "SQLite",
  "total_tables": 10,
  "total_records": 1250,
  "database_size_mb": 15.2,
  "tables": ["user", "farm", "culture", ...],
  "table_counts": {
    "user": 5,
    "farm": 3,
    "culture": 12
  }
}
```

#### 2. Validação de Integridade
```http
GET /monitoring/database/validate
Authorization: Required (Admin only)
```

**Resposta:**
```json
{
  "success": true,
  "status": "healthy",
  "health_score": 95,
  "issues": [],
  "warnings": ["Tabela X com poucos registros"]
}
```

#### 3. Criar Backup
```http
POST /monitoring/database/backup
Authorization: Required (Admin only)
Content-Type: application/json

{
  "backup_name": "backup_antes_reset"
}
```

**Resposta:**
```json
{
  "success": true,
  "backup_file": "/path/to/backup_antes_reset.db",
  "backup_size_mb": 15.2,
  "created_at": "2025-08-02T10:30:00"
}
```

#### 4. Sincronização do Schema (NOVA - OPERAÇÃO SEGURA)
```http
POST /monitoring/database/sync-schema
Authorization: Required (Admin only)
Content-Type: application/json
```

**Resposta de Sucesso:**
```json
{
  "success": true,
  "message": "Schema sincronizado com sucesso",
  "report": {
    "timestamp": "2025-08-02T10:35:00",
    "database_type": "SQLite",
    "tables_before": 12,
    "tables_after": 14,
    "new_tables": ["new_features", "audit_logs"],
    "updated_tables": [
      {
        "table": "users",
        "new_columns": ["avatar_url", "last_login_ip"]
      }
    ],
    "data_preserved": true,
    "safe_operation": true
  }
}
```

**Resposta quando Schema já Atualizado:**
```json
{
  "success": true,
  "message": "Schema já está atualizado - nenhuma alteração necessária",
  "report": {
    "timestamp": "2025-08-02T10:35:00",
    "database_type": "SQLite",
    "tables_before": 12,
    "tables_after": 12,
    "new_tables": [],
    "updated_tables": [],
    "data_preserved": true,
    "safe_operation": true
  }
}
```

#### 5. Reset Completo (CRÍTICO)
```http
POST /monitoring/database/reset
Authorization: Required (Admin only)
Content-Type: application/json

{
  "confirmation": "RESET_DATABASE_CONFIRM",
  "create_backup": true
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Banco resetado com sucesso",
  "before": {"tables": 10, "records": 1250},
  "after": {"tables": 10, "records": 0},
  "tables_created": ["user", "farm", "culture", ...],
  "database_type": "SQLite",
  "backup": {
    "backup_name": "pre_reset_20250802_103000",
    "backup_file": "/path/to/backup.db"
  }
}
```

## 💻 CLI (Linha de Comando)

### Instalação das Dependências
```bash
pip install requests
```

### Uso Básico
```bash
# Informações do banco
python database_cli.py info

# Validar integridade
python database_cli.py validate

# Criar backup
python database_cli.py backup

# Sincronizar schema (operação segura)
python database_cli.py sync

# Reset completo (com confirmações)
python database_cli.py reset
```

### Exemplo de Sincronização Segura
```bash
$ python database_cli.py sync
🔐 Fazendo login...
Email: admin@agrotech.pt
Senha: ********
✅ Login realizado com sucesso!

🔄 Sincronizando schema do banco de dados...
ℹ️ Operação segura - não remove dados existentes
Continuar com a sincronização? (s/N): s
✅ Schema sincronizado com sucesso!
📋 Tabelas criadas: audit_logs, user_preferences
🔄 Tabela 'users': adicionados 2 campos (avatar_url, last_login_ip)
🔄 Tabela 'cultures': adicionados 1 campos (harvest_notes)
```

### Exemplo de Output - Info
```bash
$ python database_cli.py info
🔐 Fazendo login...
Email: admin@agrotech.pt
Senha: ********
✅ Login realizado com sucesso!

📊 Obtendo informações do banco...
{
  "success": true,
  "database_type": "SQLite",
  "total_tables": 10,
  "total_records": 1250,
  "database_size_mb": 15.2
}
```

## ⚙️ Implementação Técnica

### Arquitetura
```
app/
├── services/
│   └── database_manager.py     # Lógica principal
├── controllers/
│   └── monitoring_controller.py  # Rotas da API
└── templates/
    └── monitoring/
        └── dashboard.html      # Interface web
```

### Fluxo do Reset
1. **Verificação de Permissões** → Admin only
2. **Confirmação de Segurança** → Texto específico obrigatório
3. **Backup Opcional** → Criar cópia (SQLite apenas)
4. **DROP ALL TABLES** → Remove tudo existente
5. **CREATE ALL TABLES** → Recria estrutura limpa
6. **Validação Final** → Confirma sucesso
7. **Log de Auditoria** → Registra operação

### Compatibilidade

#### SQLite (Desenvolvimento)
- ✅ Backup automático antes do reset
- ✅ Verificação de integridade com PRAGMA
- ✅ Drop/Create usando SQLAlchemy metadata
- ✅ Cálculo de tamanho do arquivo

#### PostgreSQL (Produção)
- ✅ DROP CASCADE para foreign keys
- ✅ Transações para atomicidade
- ⚠️ Backup manual necessário (usar pg_dump)
- ✅ Todas as outras funcionalidades

## 🚨 Cenários de Uso

### 1. Desenvolvimento Local
```bash
# Limpar dados de teste
curl -X POST http://localhost:5000/monitoring/database/reset \
  -H "Content-Type: application/json" \
  -d '{"confirmation": "RESET_DATABASE_CONFIRM", "create_backup": true}'
```

### 2. Deploy em Produção
```bash
# Recrear estrutura após mudanças nos models
python database_cli.py reset
```

### 3. Migração de Schema
```bash
# 1. Backup manual (PostgreSQL)
pg_dump database_url > backup.sql

# 2. Reset via API
python database_cli.py reset

# 3. Aplicar dados essenciais se necessário
```

## 🔍 Logs e Auditoria

Todas as operações são registradas:

```python
LoggingHelper.log_user_action(
    'admin@agrotech.pt',
    'DATABASE_RESET_SUCCESS',
    'Reset concluído. Antes: 10 tabelas/1250 registros. Depois: 10 tabelas/0 registros'
)
```

### Tipos de Log
- `DATABASE_RESET_START` - Início do reset
- `DATABASE_RESET_SUCCESS` - Reset bem-sucedido
- `DATABASE_RESET_FAILED` - Falha no reset
- `DATABASE_BACKUP_CREATED` - Backup criado
- `DATABASE_VALIDATION_RUN` - Validação executada

## ⚠️ Considerações Importantes

1. **BACKUP CRÍTICO**: Sempre faça backup manual antes de reset em produção
2. **DOWNTIME**: O reset causa indisponibilidade temporária
3. **DADOS PERDIDOS**: Todos os dados são perdidos permanentemente
4. **PERMISSÕES**: Apenas admins podem executar operações
5. **CONEXÕES**: Certifique-se de que não há conexões ativas durante o reset

## 🆘 Recuperação de Emergência

### SQLite
```bash
# Restaurar do backup automático
cp /path/to/backup.db /path/to/main.db
```

### PostgreSQL
```bash
# Restaurar do backup manual
psql database_url < backup.sql
```

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs em `/app/logs/`
2. Executar validação: `python database_cli.py validate`
3. Verificar conectividade com o banco
4. Contatar equipe de desenvolvimento

---

**⚠️ AVISO FINAL**: Este sistema é uma ferramenta poderosa. Use com responsabilidade e sempre mantenha backups atualizados!
