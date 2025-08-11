# 🗄️ GUIA COMPLETO: MIGRAÇÃO DE BANCO DE DADOS POSTGRESQL EM PRODUÇÃO

**Versão:** 1.0  
**Data:** 06 de Agosto de 2025  
**Autor:** Sistema AgroTech  
**Ambiente:** Railway + PostgreSQL

---

## 📋 **ÍNDICE**

1. [Visão Geral](#visão-geral)
2. [Preparação Pré-Migração](#preparação-pré-migração)
3. [Estratégias de Migração](#estratégias-de-migração)
4. [Execução da Migração](#execução-da-migração)
5. [Validação Pós-Migração](#validação-pós-migração)
6. [Resolução de Problemas](#resolução-de-problemas)
7. [Checklist Completo](#checklist-completo)

---

## 🎯 **VISÃO GERAL**

Este guia documenta o processo completo para realizar migrações de banco de dados PostgreSQL em produção no Railway, baseado nas lições aprendidas durante a correção crítica do schema da tabela `alerts`.

### **Contexto Histórico:**
- **Problema:** Colunas faltantes na tabela `alerts` causando erros 500
- **Solução:** Migração forçada com múltiplas estratégias
- **Resultado:** 100% de sucesso após 3 tentativas iterativas

---

## 🛠️ **PREPARAÇÃO PRÉ-MIGRAÇÃO**

### **1. Análise do Problema**

```bash
# 1.1 Identificar erros nos logs
curl -s https://www.agenteagricola.com/api/alerts/health
# Verificar se retorna erro de coluna inexistente

# 1.2 Comparar modelo Python vs Schema PostgreSQL
python -c "from app.models.alerts import Alert; print([c.name for c in Alert.__table__.columns])"
```

### **2. Backup de Segurança**

```bash
# 2.1 Backup via Railway CLI (se disponível)
railway db backup

# 2.2 Backup via psql (alternativa)
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

### **3. Análise de Dependências**

```python
# 3.1 Verificar modelos que dependem da tabela
# Executar no terminal Python local
from app.models import *
from sqlalchemy import inspect

inspector = inspect(db.engine)
print("Tabelas existentes:", inspector.get_table_names())
print("Colunas alerts:", [c['name'] for c in inspector.get_columns('alerts')])
```

---

## 🚀 **ESTRATÉGIAS DE MIGRAÇÃO**

### **Estratégia 1: Migração Automática via run.py (RECOMENDADA)**

```python
# Arquivo: run.py
def deploy():
    """Executar tarefas de deploy com migração automática"""
    app = create_app(os.getenv('FLASK_CONFIG') or 'production')
    
    with app.app_context():
        try:
            print("🔧 Aplicando migração crítica...")
            from sqlalchemy import text
            
            # IMPORTANTE: Lista completa de colunas a adicionar
            migration_queries = [
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS action_text VARCHAR(100);",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS action_url VARCHAR(500);", 
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS location_data TEXT;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS weather_data TEXT;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS alert_metadata TEXT;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS scheduled_for TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS sent_at TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS read_at TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS dismissed_at TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS delivery_channels VARCHAR(100) DEFAULT 'web';",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS last_retry_at TIMESTAMP;"
            ]
            
            for i, query in enumerate(migration_queries, 1):
                try:
                    db.session.execute(text(query))
                    db.session.commit()
                    print(f"✅ Coluna {i}/{len(migration_queries)} adicionada")
                except Exception as e:
                    print(f"ℹ️ Coluna {i} já existe ou erro: {e}")
                    db.session.rollback()
            
            print("✅ Migração concluída!")
            
        except Exception as e:
            print(f"⚠️ Erro na migração: {e}")
```

### **Estratégia 2: Script de Migração Independente**

```python
# Arquivo: guias/migration_script.py
#!/usr/bin/env python3
"""
Script de Migração PostgreSQL Independente
Execute este script quando precisar forçar migrações em produção
"""

import os
import psycopg2
from datetime import datetime

def execute_migration():
    """Executa migração diretamente no PostgreSQL"""
    
    # URL do banco (Railway)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada!")
        return False
    
    print(f"🔗 Conectando ao banco: {database_url[:50]}...")
    
    try:
        # Conexão direta com PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Queries de migração
        migrations = [
            ("action_text", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS action_text VARCHAR(100);"),
            ("action_url", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS action_url VARCHAR(500);"),
            ("location_data", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS location_data TEXT;"),
            ("weather_data", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS weather_data TEXT;"),
            ("alert_metadata", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS alert_metadata TEXT;"),
            ("scheduled_for", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS scheduled_for TIMESTAMP;"),
            ("expires_at", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;"),
            ("sent_at", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS sent_at TIMESTAMP;"),
            ("read_at", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS read_at TIMESTAMP;"),
            ("dismissed_at", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS dismissed_at TIMESTAMP;"),
            ("delivery_channels", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS delivery_channels VARCHAR(100) DEFAULT 'web';"),
            ("retry_count", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;"),
            ("last_retry_at", "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS last_retry_at TIMESTAMP;")
        ]
        
        print(f"📊 Executando {len(migrations)} migrações...")
        
        for i, (column_name, query) in enumerate(migrations, 1):
            try:
                cursor.execute(query)
                conn.commit()
                print(f"✅ {i:2d}/{len(migrations)} - Coluna '{column_name}' processada")
            except Exception as e:
                print(f"ℹ️ {i:2d}/{len(migrations)} - Coluna '{column_name}': {e}")
                conn.rollback()
        
        # Verificação final
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'alerts' ORDER BY column_name;")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"\n✅ Colunas atuais na tabela alerts: {len(columns)}")
        for col in sorted(columns):
            print(f"   • {col}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False

if __name__ == "__main__":
    success = execute_migration()
    exit(0 if success else 1)
```

### **Estratégia 3: Migração via Flask-Migrate (Tradicional)**

```bash
# 3.1 Gerar migração
export FLASK_APP=run.py
export FLASK_ENV=production
flask db migrate -m "Adicionar colunas faltantes tabela alerts"

# 3.2 Aplicar migração
flask db upgrade

# 3.3 Se falhar, forçar criação
flask db stamp head
flask db migrate -m "Force migration alerts"
flask db upgrade
```

---

## ⚡ **EXECUÇÃO DA MIGRAÇÃO**

### **Processo Passo-a-Passo**

```bash
# PASSO 1: Preparar ambiente
cd /path/to/project
git pull origin main
git status

# PASSO 2: Verificar status atual
python -c "
from app import create_app, db
app = create_app('production')
with app.app_context():
    try:
        from app.models.alerts import Alert
        alerts = Alert.query.count()
        print(f'✅ Tabela alerts acessível: {alerts} registros')
    except Exception as e:
        print(f'❌ Erro ao acessar alerts: {e}')
"

# PASSO 3: Executar migração (escolher uma estratégia)

# Opção A: Via deploy automático
git add .
git commit -m "MIGRATION: Forçar atualização schema alerts"
git push origin main
# Railway fará deploy automático

# Opção B: Via script direto
export DATABASE_URL="postgresql://..."
python guias/migration_script.py

# Opção C: Via Flask-Migrate
flask db upgrade

# PASSO 4: Validar resultado
curl -s https://www.agenteagricola.com/api/alerts/health | jq
```

### **Monitoramento Durante Migração**

```bash
# Terminal 1: Logs do Railway
railway logs --follow

# Terminal 2: Testes de API
watch -n 5 'curl -s https://www.agenteagricola.com/api/alerts/health | jq .status'

# Terminal 3: Verificação de banco
psql $DATABASE_URL -c "SELECT count(*) FROM alerts;"
```

---

## ✅ **VALIDAÇÃO PÓS-MIGRAÇÃO**

### **1. Testes Automáticos**

```python
# Arquivo: guias/validation_script.py
#!/usr/bin/env python3
"""Script de validação pós-migração"""

import requests
import json
from datetime import datetime

def validate_migration():
    """Valida se a migração foi bem-sucedida"""
    
    base_url = "https://www.agenteagricola.com"
    
    tests = [
        ("Health Check Geral", "/health"),
        ("API Alerts Health", "/api/alerts/health"),
        ("API Alerts Widget", "/api/alerts/widget"),
    ]
    
    print("🧪 VALIDAÇÃO PÓS-MIGRAÇÃO")
    print("=" * 50)
    
    all_passed = True
    
    for name, endpoint in tests:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            elif response.status_code == 401 and "alerts" in endpoint:
                print(f"✅ {name}: OK (autenticação requerida)")
            else:
                print(f"❌ {name}: Status {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {name}: Erro {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    success = validate_migration()
    print(f"\n{'🎉 MIGRAÇÃO VALIDADA!' if success else '⚠️ PROBLEMAS DETECTADOS'}")
    exit(0 if success else 1)
```

### **2. Validação Manual**

```bash
# 2.1 Verificar estrutura da tabela
psql $DATABASE_URL -c "
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'alerts' 
ORDER BY ordinal_position;
"

# 2.2 Testar criação de alerta (via API ou código)
curl -X POST https://www.agenteagricola.com/api/alerts/create \
  -H "Content-Type: application/json" \
  -d '{"type":"weather","priority":"low","title":"Teste","message":"Teste migração"}'

# 2.3 Verificar logs de aplicação
railway logs --tail=100
```

---

## 🚨 **RESOLUÇÃO DE PROBLEMAS**

### **Problemas Comuns e Soluções**

#### **1. Erro: "column does not exist"**
```sql
-- Solução: Adicionar coluna manualmente
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS read_at TIMESTAMP;
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS dismissed_at TIMESTAMP;
```

#### **2. Migração parcialmente aplicada**
```python
# Solução: Verificar colunas existentes e aplicar apenas as faltantes
from sqlalchemy import inspect, text

inspector = inspect(db.engine)
existing_columns = [c['name'] for c in inspector.get_columns('alerts')]
required_columns = ['action_text', 'action_url', 'read_at', 'dismissed_at', ...]

missing_columns = [col for col in required_columns if col not in existing_columns]
print(f"Colunas faltantes: {missing_columns}")
```

#### **3. Aplicação não reinicia automaticamente**
```bash
# Forçar restart no Railway
railway service restart

# Ou fazer commit vazio para triggerar deploy
git commit --allow-empty -m "Force Railway restart"
git push origin main
```

#### **4. Erro de conexão com banco**
```bash
# Verificar variável de ambiente
echo $DATABASE_URL

# Testar conexão direta
psql $DATABASE_URL -c "SELECT version();"

# Verificar status do Railway
railway status
```

### **Script de Diagnóstico**

```python
# Arquivo: guias/diagnostic_script.py
#!/usr/bin/env python3
"""Script de diagnóstico para problemas de migração"""

import os
import psycopg2
import requests
from datetime import datetime

def run_diagnostics():
    """Executa diagnósticos completos"""
    
    print("🔍 DIAGNÓSTICO DE MIGRAÇÃO")
    print("=" * 50)
    
    # 1. Verificar variáveis de ambiente
    print("1. Variáveis de ambiente:")
    env_vars = ['DATABASE_URL', 'FLASK_ENV', 'FLASK_CONFIG']
    for var in env_vars:
        value = os.getenv(var, 'NÃO DEFINIDA')
        masked_value = value[:20] + '...' if len(value) > 20 else value
        print(f"   {var}: {masked_value}")
    
    # 2. Testar conexão com banco
    print("\n2. Conexão com banco:")
    try:
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✅ PostgreSQL conectado: {version[:50]}...")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 3. Verificar estrutura da tabela alerts
    print("\n3. Estrutura da tabela alerts:")
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'alerts' 
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print(f"   ✅ {len(columns)} colunas encontradas:")
        for col_name, col_type in columns:
            print(f"      • {col_name} ({col_type})")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"   ❌ Erro ao verificar tabela: {e}")
    
    # 4. Testar endpoints da API
    print("\n4. Status da API:")
    endpoints = [
        "/health",
        "/api/alerts/health",
        "/api/alerts/widget"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"https://www.agenteagricola.com{endpoint}", timeout=5)
            status = "OK" if response.status_code in [200, 401] else f"ERRO {response.status_code}"
            print(f"   {endpoint}: {status}")
        except Exception as e:
            print(f"   {endpoint}: ERRO - {e}")

if __name__ == "__main__":
    run_diagnostics()
```

---

## 📋 **CHECKLIST COMPLETO**

### **PRÉ-MIGRAÇÃO**
- [ ] Backup do banco de dados realizado
- [ ] Análise do modelo Python vs Schema PostgreSQL
- [ ] Identificação das colunas faltantes
- [ ] Teste em ambiente de desenvolvimento
- [ ] Verificação de dependências

### **MIGRAÇÃO**
- [ ] Escolha da estratégia de migração
- [ ] Execução da migração (automática ou manual)
- [ ] Monitoramento dos logs durante o processo
- [ ] Verificação de erros em tempo real

### **PÓS-MIGRAÇÃO**
- [ ] Validação automática executada
- [ ] Testes manuais dos endpoints críticos
- [ ] Verificação da estrutura da tabela
- [ ] Teste de criação/leitura de registros
- [ ] Monitoramento por 24h após a migração

### **DOCUMENTAÇÃO**
- [ ] Atualização do guia com lições aprendidas
- [ ] Commit das alterações no repositório
- [ ] Comunicação à equipe sobre status da migração

---

## 📝 **COMANDOS ÚTEIS DE REFERÊNCIA**

```bash
# Verificar status da aplicação
curl -s https://www.agenteagricola.com/health | jq

# Conectar ao banco PostgreSQL
psql $DATABASE_URL

# Ver logs do Railway
railway logs --tail=100

# Executar migração Flask
flask db upgrade

# Forçar restart no Railway
railway service restart

# Backup do banco
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Verificar colunas da tabela
psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'alerts';"
```

---

## 🔗 **REFERÊNCIAS E RECURSOS**

- [Railway Documentation](https://docs.railway.app/)
- [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [SQLAlchemy Column Types](https://docs.sqlalchemy.org/en/14/core/type_basics.html)

---

## 📞 **SUPORTE**

Em caso de problemas durante a migração:

1. **Execute o script de diagnóstico:** `python guias/diagnostic_script.py`
2. **Verifique os logs:** `railway logs --tail=200`
3. **Teste os endpoints:** `python guias/validation_script.py`
4. **Documente o problema** e as tentativas de solução

---

**Última atualização:** 06 de Agosto de 2025  
**Status:** Testado em produção com 100% de sucesso  
**Próxima revisão:** Após próxima migração crítica
