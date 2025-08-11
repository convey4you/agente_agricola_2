# 🚨 PROMPT CRÍTICO 1: CORREÇÃO URGENTE DO SCHEMA DO BANCO

**Prioridade:** CRÍTICA (24 horas)  
**Problema:** Sistema de alertas completamente inacessível  
**Erro:** `column alerts.status does not exist`

---

## 📋 CONTEXTO COMPLETO PARA CLAUDE SONNET 4

### Situação Crítica
Você é um desenvolvedor backend sênior especializado em Flask e SQLAlchemy trabalhando no projeto **AgroTech Portugal**. O sistema está em produção mas a funcionalidade principal (Sistema de Alertas Inteligentes) está completamente quebrada devido a um erro de schema do banco de dados.

### Erro Específico Identificado
```sql
psycopg2.errors.UndefinedColumn: column alerts.status does not exist
LINE 1: ... alerts_type, alerts.priority AS alerts_priority, alerts.sta...
                                                             ^

[SQL: SELECT alerts.id AS alerts_id, alerts.user_id AS alerts_user_id, 
     alerts.type AS alerts_type, alerts.priority AS alerts_priority, 
     alerts.status AS alerts_status, alerts.title AS alerts_title, 
     alerts.message AS alerts_message, alerts.action_text AS alerts_action_text, 
     alerts.action_url AS alerts_action_url, alerts.culture_id AS alerts_culture_id, 
     alerts.location_data AS alerts_location_data, alerts.weather_data AS alerts_weather_data, 
     alerts.alert_metadata AS alerts_alert_metadata, alerts.created_at AS alerts_created_at, 
     alerts.scheduled_for AS alerts_scheduled_for, alerts.expires_at AS alerts_expires_at, 
     alerts.sent_at AS alerts_sent_at, alerts.read_at AS alerts_read_at, 
     alerts.dismissed_at AS alerts_dismissed_at, alerts.delivery_channels AS alerts_delivery_channels, 
     alerts.retry_count AS alerts_retry_count, alerts.last_retry_at AS alerts_last_retry_at 
FROM alerts 
WHERE alerts.user_id = %(user_id_1)s AND alerts.status != %(status_1)s 
ORDER BY alerts.created_at DESC 
LIMIT %(param_1)s]

[parameters: {'user_id_1': 42, 'status_1': 'EXPIRED', 'param_1': 50}]
```

### Arquitetura Técnica
- **Backend:** Flask 3.1.1
- **ORM:** SQLAlchemy 2.0.41 (versão moderna)
- **Banco:** PostgreSQL (Railway.app)
- **Deploy:** Git-based automatizado
- **Repositório:** https://github.com/convey4you/agente_agricola
- **Branch:** main
- **Commit atual:** da162dd

### Análise do Health Check
O health check do banco mostra que a tabela `alerts` existe, mas há "missing_columns": 1, confirmando que a coluna `status` não foi criada.

---

## 🎯 TAREFA URGENTE E ESPECÍFICA

### Objetivo Principal
Criar e executar migration SQLAlchemy para adicionar a coluna `status` na tabela `alerts` de forma segura, sem quebrar dados existentes e seguindo as melhores práticas.

### Especificações Técnicas da Coluna

**Nome:** `status`  
**Tipo:** ENUM ou VARCHAR com constraint  
**Valores Permitidos:** 
- `'PENDING'` (padrão para novos alertas)
- `'SENT'` (alerta enviado ao usuário)
- `'READ'` (usuário visualizou o alerta)
- `'DISMISSED'` (usuário dispensou o alerta)
- `'EXPIRED'` (alerta expirou automaticamente)

**Propriedades:**
- `nullable=False` (obrigatório)
- `default='PENDING'` (valor padrão)
- `index=True` (para performance em queries)

### Estrutura Esperada do Modelo Alert

Com base no erro SQL, o modelo Alert deve ter estas colunas:
```python
class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # weather, pest, disease, etc.
    priority = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    status = db.Column(db.String(20), nullable=False, default='PENDING')  # ← ESTA COLUNA FALTA
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    action_text = db.Column(db.String(100))
    action_url = db.Column(db.String(200))
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id'))
    location_data = db.Column(db.JSON)
    weather_data = db.Column(db.JSON)
    alert_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_for = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    dismissed_at = db.Column(db.DateTime)
    delivery_channels = db.Column(db.JSON)
    retry_count = db.Column(db.Integer, default=0)
    last_retry_at = db.Column(db.DateTime)
```

---

## 📝 ENTREGÁVEIS OBRIGATÓRIOS

### 1. Arquivo de Migration
Criar arquivo `migrations/versions/add_status_column_to_alerts.py` com:

```python
"""Add status column to alerts table

Revision ID: [auto-generated]
Revises: [previous-revision]
Create Date: 2025-08-01 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '[auto-generated]'
down_revision = '[previous-revision]'
branch_labels = None
depends_on = None

def upgrade():
    # Adicionar coluna status com valor padrão
    op.add_column('alerts', sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'))
    
    # Criar index para performance
    op.create_index('ix_alerts_status', 'alerts', ['status'])
    
    # Adicionar constraint para valores válidos (PostgreSQL)
    op.execute("ALTER TABLE alerts ADD CONSTRAINT check_alert_status CHECK (status IN ('PENDING', 'SENT', 'READ', 'DISMISSED', 'EXPIRED'))")

def downgrade():
    # Remover constraint
    op.execute("ALTER TABLE alerts DROP CONSTRAINT IF EXISTS check_alert_status")
    
    # Remover index
    op.drop_index('ix_alerts_status', table_name='alerts')
    
    # Remover coluna
    op.drop_column('alerts', 'status')
```

### 2. Script de Validação
Criar `scripts/validate_alerts_schema.py`:

```python
#!/usr/bin/env python3
"""
Script de validação do schema da tabela alerts
Executa após migration para confirmar que tudo funcionou
"""

import sys
from app import create_app, db
from sqlalchemy import text

def validate_schema():
    app = create_app()
    with app.app_context():
        try:
            # Testar se coluna status existe
            result = db.session.execute(text("SELECT status FROM alerts LIMIT 1"))
            print("✅ Coluna 'status' existe e é acessível")
            
            # Testar query completa que estava falhando
            query = text("""
                SELECT alerts.id AS alerts_id, alerts.user_id AS alerts_user_id, 
                       alerts.type AS alerts_type, alerts.priority AS alerts_priority, 
                       alerts.status AS alerts_status, alerts.title AS alerts_title, 
                       alerts.message AS alerts_message
                FROM alerts 
                WHERE alerts.status != :status_val 
                ORDER BY alerts.created_at DESC 
                LIMIT 5
            """)
            
            result = db.session.execute(query, {'status_val': 'EXPIRED'})
            alerts = result.fetchall()
            print(f"✅ Query completa funciona - {len(alerts)} alertas encontrados")
            
            # Testar constraint de valores
            try:
                db.session.execute(text("INSERT INTO alerts (user_id, type, priority, status, title, message) VALUES (1, 'test', 'low', 'INVALID_STATUS', 'Test', 'Test')"))
                db.session.commit()
                print("❌ ERRO: Constraint de status não está funcionando")
                return False
            except Exception:
                print("✅ Constraint de status funcionando corretamente")
                db.session.rollback()
            
            print("✅ Schema da tabela alerts validado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ ERRO na validação: {e}")
            return False

if __name__ == "__main__":
    success = validate_schema()
    sys.exit(0 if success else 1)
```

### 3. Instruções de Execução em Produção

Criar `MIGRATION_INSTRUCTIONS.md`:

```markdown
# Instruções de Execução da Migration - Status Column

## Pré-requisitos
1. Backup do banco de dados realizado
2. Acesso ao ambiente de produção
3. Aplicação em modo de manutenção (opcional)

## Passos de Execução

### 1. Backup (OBRIGATÓRIO)
```bash
# No Railway ou localmente
pg_dump $DATABASE_URL > backup_pre_status_migration_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Executar Migration
```bash
# No ambiente de produção
flask db upgrade
```

### 3. Validar Migration
```bash
python3 scripts/validate_alerts_schema.py
```

### 4. Testar API
```bash
curl -X GET "https://www.agenteagricola.com/api/alerts/" \
     -H "Cookie: session=..." \
     -H "Content-Type: application/json"
```

### 5. Verificar Health Check
```bash
curl https://www.agenteagricola.com/health/db
```

## Rollback (Se Necessário)
```bash
flask db downgrade
```

## Validação Final
- [ ] Query SQL funciona sem erros
- [ ] API de alertas responde corretamente
- [ ] Health checks passam
- [ ] Dashboard carrega alertas
- [ ] Logs sem erros relacionados a alerts
```

### 4. Modelo Alert Atualizado (Se Necessário)

Se o modelo atual não tiver a coluna definida, atualizar `app/models/alert.py`:

```python
from app import db
from datetime import datetime
from enum import Enum

class AlertStatus(Enum):
    PENDING = 'PENDING'
    SENT = 'SENT'
    READ = 'READ'
    DISMISSED = 'DISMISSED'
    EXPIRED = 'EXPIRED'

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    priority = db.Column(db.String(20), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='PENDING', index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    action_text = db.Column(db.String(100))
    action_url = db.Column(db.String(200))
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id'))
    location_data = db.Column(db.JSON)
    weather_data = db.Column(db.JSON)
    alert_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    scheduled_for = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    dismissed_at = db.Column(db.DateTime)
    delivery_channels = db.Column(db.JSON)
    retry_count = db.Column(db.Integer, default=0)
    last_retry_at = db.Column(db.DateTime)
    
    # Relacionamentos
    user = db.relationship('User', backref='alerts')
    culture = db.relationship('Culture', backref='alerts')
    
    def __repr__(self):
        return f'<Alert {self.id}: {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'priority': self.priority,
            'status': self.status,
            'title': self.title,
            'message': self.message,
            'action_text': self.action_text,
            'action_url': self.action_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'dismissed_at': self.dismissed_at.isoformat() if self.dismissed_at else None
        }
```

---

## ✅ CRITÉRIOS DE VALIDAÇÃO

### Validação Técnica Obrigatória
Após implementação, estas validações DEVEM passar:

1. **Query SQL Original:**
```sql
SELECT alerts.id, alerts.user_id, alerts.type, alerts.priority, alerts.status, 
       alerts.title, alerts.message 
FROM alerts 
WHERE alerts.user_id = 42 AND alerts.status != 'EXPIRED' 
ORDER BY alerts.created_at DESC 
LIMIT 50;
```

2. **Health Check do Banco:**
```bash
curl https://www.agenteagricola.com/health/db
# Deve retornar "missing_columns": 0
```

3. **API de Alertas:**
```bash
curl https://www.agenteagricola.com/api/alerts/
# Deve retornar JSON válido, não erro de SQL
```

### Critérios de Sucesso
- [ ] Migration executa sem erros
- [ ] Coluna `status` criada com tipo correto
- [ ] Constraint de valores funcionando
- [ ] Index criado para performance
- [ ] Query original funciona
- [ ] API de alertas responde
- [ ] Health checks passam
- [ ] Rollback funciona se necessário

---

## 🚨 CONSIDERAÇÕES CRÍTICAS

### Segurança
- **SEMPRE** fazer backup antes da migration
- Testar migration em ambiente de desenvolvimento primeiro
- Validar que dados existentes não são perdidos
- Implementar rollback testado

### Performance
- Adicionar index na coluna `status` para queries rápidas
- Usar `server_default` para evitar lock de tabela
- Considerar execução em horário de baixo tráfego

### Compatibilidade
- Garantir compatibilidade com SQLAlchemy 2.0.41
- Usar sintaxe PostgreSQL apropriada
- Testar com dados existentes na tabela

---

## 🎯 RESULTADO ESPERADO

Após implementação desta correção:
- ✅ Sistema de alertas 100% funcional
- ✅ API de alertas respondendo corretamente
- ✅ Dashboard carregando alertas
- ✅ Score de validação passando de 26% para >80%
- ✅ Sprint 2 pronto para aprovação

**Esta é a correção mais crítica e deve ser implementada PRIMEIRO antes de qualquer outra correção.**

---

**Ferramentas:** VS Code + GitHub Copilot  
**Prazo:** 24 horas (URGENTE)  
**Validação:** Gerente de Tecnologia

