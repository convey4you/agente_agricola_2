# 🚨 INSTRUÇÕES URGENTES - RAILWAY CONSOLE

## ❌ ERRO ATUAL:
```
column users.interesses does not exist
```

## ✅ SOLUÇÃO RÁPIDA:

### 1. Acessar Railway Console:
- Vá para o painel do Railway
- Selecione o projeto "agente_agricola"
- Clique em "Console" ou "Shell"

### 2. Executar UMA das opções abaixo:

#### 🎯 OPÇÃO 1 - Script Automático (RECOMENDADO):
```bash
python railway_migration_fix.py
```

#### 🎯 OPÇÃO 2 - SQL Direto:
```bash
railway connect
```
Depois no prompt SQL:
```sql
ALTER TABLE users ADD COLUMN interesses VARCHAR(200);
```

#### 🎯 OPÇÃO 3 - Python Inline:
```python
import os
from sqlalchemy import create_engine, text
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    conn.execute(text("ALTER TABLE users ADD COLUMN interesses VARCHAR(200);"))
    conn.commit()
print("✅ Migração concluída!")
```

### 3. Após a migração:
- Reiniciar o serviço Railway
- Verificar se a aplicação inicia sem erros
- Testar o onboarding step 2

## 🔍 Como verificar se funcionou:
```sql
\d users
```
Deve mostrar: `interesses | character varying(200)`

## 📞 Se precisar de ajuda:
- Verifique os logs do Railway após cada comando
- Se a migração falhar, tente novamente
- A coluna deve aceitar valores como: "vegetables,fruits,herbs"

---
**⏰ TEMPO ESTIMADO: 2-3 minutos**
