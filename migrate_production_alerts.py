#!/usr/bin/env python3
"""
Script para aplicar migração em produção PostgreSQL
Resolve o problema das colunas faltantes na tabela alerts
"""

import os
import sys
import psycopg2
from datetime import datetime

# Configurações de conexão com PostgreSQL (Railway)
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada nas variáveis de ambiente")
    sys.exit(1)

def execute_migration():
    """Executa a migração na produção PostgreSQL"""
    
    # SQL para adicionar colunas que estão faltando
    migration_sql = """
    -- Verificar e adicionar colunas que estão faltando na tabela alerts
    DO $$ 
    BEGIN 
        -- action_text
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'alerts' AND column_name = 'action_text') THEN
            ALTER TABLE alerts ADD COLUMN action_text VARCHAR(100);
            RAISE NOTICE 'Coluna action_text adicionada';
        ELSE
            RAISE NOTICE 'Coluna action_text já existe';
        END IF;

        -- action_url
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'alerts' AND column_name = 'action_url') THEN
            ALTER TABLE alerts ADD COLUMN action_url VARCHAR(500);
            RAISE NOTICE 'Coluna action_url adicionada';
        ELSE
            RAISE NOTICE 'Coluna action_url já existe';
        END IF;

        -- location_data
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'alerts' AND column_name = 'location_data') THEN
            ALTER TABLE alerts ADD COLUMN location_data TEXT;
            RAISE NOTICE 'Coluna location_data adicionada';
        ELSE
            RAISE NOTICE 'Coluna location_data já existe';
        END IF;

        -- weather_data
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'alerts' AND column_name = 'weather_data') THEN
            ALTER TABLE alerts ADD COLUMN weather_data TEXT;
            RAISE NOTICE 'Coluna weather_data adicionada';
        ELSE
            RAISE NOTICE 'Coluna weather_data já existe';
        END IF;

        -- alert_metadata
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'alerts' AND column_name = 'alert_metadata') THEN
            ALTER TABLE alerts ADD COLUMN alert_metadata TEXT;
            RAISE NOTICE 'Coluna alert_metadata adicionada';
        ELSE
            RAISE NOTICE 'Coluna alert_metadata já existe';
        END IF;

        -- scheduled_for
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'alerts' AND column_name = 'scheduled_for') THEN
            ALTER TABLE alerts ADD COLUMN scheduled_for TIMESTAMP;
            RAISE NOTICE 'Coluna scheduled_for adicionada';
        ELSE
            RAISE NOTICE 'Coluna scheduled_for já existe';
        END IF;

        -- expires_at
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'alerts' AND column_name = 'expires_at') THEN
            ALTER TABLE alerts ADD COLUMN expires_at TIMESTAMP;
            RAISE NOTICE 'Coluna expires_at adicionada';
        ELSE
            RAISE NOTICE 'Coluna expires_at já existe';
        END IF;

        -- sent_at
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'alerts' AND column_name = 'sent_at') THEN
            ALTER TABLE alerts ADD COLUMN sent_at TIMESTAMP;
            RAISE NOTICE 'Coluna sent_at adicionada';
        ELSE
            RAISE NOTICE 'Coluna sent_at já existe';
        END IF;

        -- delivery_channels
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'alerts' AND column_name = 'delivery_channels') THEN
            ALTER TABLE alerts ADD COLUMN delivery_channels VARCHAR(100) DEFAULT 'web';
            RAISE NOTICE 'Coluna delivery_channels adicionada';
        ELSE
            RAISE NOTICE 'Coluna delivery_channels já existe';
        END IF;

        -- retry_count
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'alerts' AND column_name = 'retry_count') THEN
            ALTER TABLE alerts ADD COLUMN retry_count INTEGER DEFAULT 0;
            RAISE NOTICE 'Coluna retry_count adicionada';
        ELSE
            RAISE NOTICE 'Coluna retry_count já existe';
        END IF;

        -- last_retry_at
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'alerts' AND column_name = 'last_retry_at') THEN
            ALTER TABLE alerts ADD COLUMN last_retry_at TIMESTAMP;
            RAISE NOTICE 'Coluna last_retry_at adicionada';
        ELSE
            RAISE NOTICE 'Coluna last_retry_at já existe';
        END IF;

        RAISE NOTICE 'Migração de alertas concluída com sucesso!';
    END $$;
    
    -- Criar índices para performance (se não existirem)
    CREATE INDEX IF NOT EXISTS ix_alerts_scheduled_for ON alerts(scheduled_for);
    CREATE INDEX IF NOT EXISTS ix_alerts_expires_at ON alerts(expires_at);
    """

    try:
        print("🔧 Conectando ao PostgreSQL...")
        
        # Conectar ao banco de dados
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Conectado ao PostgreSQL")
        print("🚀 Executando migração...")
        
        # Executar a migração
        cursor.execute(migration_sql)
        
        print("✅ Migração executada com sucesso!")
        
        # Verificar as colunas existentes
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'alerts' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 Colunas na tabela alerts ({len(columns)} total):")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
        cursor.close()
        conn.close()
        
        print("\n🎉 Migração de produção concluída com sucesso!")
        print(f"⏰ Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 MIGRAÇÃO DE PRODUÇÃO - TABELA ALERTS")
    print("=" * 60)
    
    success = execute_migration()
    
    if success:
        print("\n✅ A API de alertas agora deve funcionar corretamente!")
        sys.exit(0)
    else:
        print("\n❌ Falha na migração - verifique os logs acima")
        sys.exit(1)
