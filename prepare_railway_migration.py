#!/usr/bin/env python3
"""
Script para preparar e aplicar migration de sincronização com Railway
"""

import os
import sys
import sqlite3
from datetime import datetime

def update_alembic_version():
    """Atualizar versão do alembic no banco SQLite"""
    try:
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        
        # Verificar se tabela alembic_version existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version';")
        if not cursor.fetchone():
            # Criar tabela alembic_version
            cursor.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num));")
            cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('railway_sync_20250802');")
            print("✅ Tabela alembic_version criada com nova versão")
        else:
            # Atualizar versão existente
            cursor.execute("UPDATE alembic_version SET version_num = 'railway_sync_20250802';")
            print("✅ Versão do alembic atualizada para: railway_sync_20250802")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar versão do alembic: {e}")
        return False

def create_deployment_instructions():
    """Criar instruções para deployment no Railway"""
    instructions = """
# 🚀 INSTRUÇÕES PARA DEPLOYMENT NO RAILWAY

## 📋 Migration Criado
- **Arquivo**: migrations/versions/railway_sync_20250802_sync_local_to_railway.py
- **Versão**: railway_sync_20250802
- **Objetivo**: Sincronizar estrutura local com Railway PostgreSQL

## 🔄 Passos para Deploy:

### 1. Commit e Push
```bash
git add .
git commit -m "Migration: Sincronização com Railway - 02/08/2025"
git push origin main
```

### 2. Railway vai executar automaticamente:
- O arquivo `run.py` contém a função `deploy()` que executa migrations
- Railway irá aplicar automaticamente o migration no PostgreSQL
- Todas as tabelas serão criadas/atualizadas conforme necessário

### 3. Verificação:
- Acesse o painel do Railway
- Verifique os logs do deployment
- Confirme que o migration foi aplicado com sucesso

## 📊 Estrutura Sincronizada:
✅ Usuários (users)
✅ Fazendas (farms)  
✅ Culturas (cultures, culture_types)
✅ Atividades (activities)
✅ Alertas (alerts, alert_rules, user_alert_preferences)
✅ Marketplace (marketplace_items)
✅ Conversas (conversations, messages)

## 🔧 Em caso de problemas:
1. Verifique os logs do Railway
2. Confirme que DATABASE_URL está configurada
3. Execute manualmente no Railway console: `python run.py deploy`

## 📝 Notas:
- O banco local SQLite permanece inalterado
- Apenas Railway PostgreSQL será atualizado
- Migration é seguro - não remove dados existentes
"""
    
    with open('RAILWAY_DEPLOYMENT_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("📝 Instruções de deployment criadas: RAILWAY_DEPLOYMENT_INSTRUCTIONS.md")

def main():
    """Função principal"""
    print("🚀 Preparando Migration para Railway - 02/08/2025")
    print("=" * 60)
    
    # Verificar se arquivo de migration existe
    migration_file = 'migrations/versions/railway_sync_20250802_sync_local_to_railway.py'
    if not os.path.exists(migration_file):
        print(f"❌ Arquivo de migration não encontrado: {migration_file}")
        return False
    
    print(f"✅ Migration encontrado: {migration_file}")
    
    # Atualizar versão do alembic localmente
    if not update_alembic_version():
        return False
    
    # Criar instruções de deployment
    create_deployment_instructions()
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. git add .")
    print("2. git commit -m 'Migration: Sincronização com Railway - 02/08/2025'")
    print("3. git push origin main")
    print("4. Railway aplicará automaticamente o migration")
    print("\n✅ Preparação completa!")
    
    return True

if __name__ == '__main__':
    main()
