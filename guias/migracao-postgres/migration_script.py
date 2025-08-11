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
        print("💡 Execute: export DATABASE_URL='postgresql://...'")
        return False
    
    print(f"🔗 Conectando ao banco: {database_url[:50]}...")
    
    try:
        # Conexão direta com PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Conexão estabelecida com sucesso!")
        
        # Verificar se a tabela alerts existe
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alerts');")
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ Tabela 'alerts' não encontrada!")
            return False
        
        print("✅ Tabela 'alerts' encontrada")
        
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
        
        print(f"\n📊 Executando {len(migrations)} migrações...")
        print("=" * 60)
        
        successful_migrations = 0
        
        for i, (column_name, query) in enumerate(migrations, 1):
            try:
                cursor.execute(query)
                conn.commit()
                print(f"✅ {i:2d}/{len(migrations)} - Coluna '{column_name}' processada")
                successful_migrations += 1
            except Exception as e:
                if "already exists" in str(e):
                    print(f"ℹ️ {i:2d}/{len(migrations)} - Coluna '{column_name}' já existe")
                    successful_migrations += 1
                else:
                    print(f"❌ {i:2d}/{len(migrations)} - Coluna '{column_name}': {e}")
                conn.rollback()
        
        # Verificação final
        print(f"\n🔍 Verificação final...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'alerts' 
            ORDER BY column_name;
        """)
        columns = cursor.fetchall()
        
        print(f"✅ Colunas atuais na tabela alerts: {len(columns)}")
        print("=" * 60)
        for col_name, col_type, nullable, default in sorted(columns):
            nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default}" if default else ""
            print(f"   • {col_name:<20} {col_type:<15} {nullable_str}{default_str}")
        
        # Estatísticas finais
        cursor.execute("SELECT COUNT(*) FROM alerts;")
        total_alerts = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\n📈 RESUMO DA MIGRAÇÃO:")
        print(f"   • Migrações executadas: {successful_migrations}/{len(migrations)}")
        print(f"   • Total de colunas: {len(columns)}")
        print(f"   • Registros na tabela: {total_alerts}")
        print(f"   • Timestamp: {datetime.now().isoformat()}")
        
        if successful_migrations == len(migrations):
            print("\n🎉 Migração concluída com 100% de sucesso!")
            return True
        else:
            print(f"\n⚠️ Migração parcial: {successful_migrations}/{len(migrations)} sucessos")
            return False
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False

def verify_migration():
    """Verifica se a migração foi bem-sucedida"""
    
    print("\n🧪 VERIFICAÇÃO PÓS-MIGRAÇÃO")
    print("=" * 40)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada!")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Lista de colunas que devem existir
        required_columns = [
            'id', 'user_id', 'type', 'priority', 'status', 'title', 'message',
            'culture_id', 'created_at', 'updated_at',
            # Colunas adicionadas na migração
            'action_text', 'action_url', 'location_data', 'weather_data', 
            'alert_metadata', 'scheduled_for', 'expires_at', 'sent_at', 
            'read_at', 'dismissed_at', 'delivery_channels', 'retry_count', 
            'last_retry_at'
        ]
        
        # Verificar colunas existentes
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'alerts' 
            ORDER BY column_name;
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Verificar colunas faltantes
        missing_columns = [col for col in required_columns if col not in existing_columns]
        extra_columns = [col for col in existing_columns if col not in required_columns]
        
        print(f"✅ Colunas encontradas: {len(existing_columns)}")
        print(f"✅ Colunas esperadas: {len(required_columns)}")
        
        if missing_columns:
            print(f"❌ Colunas faltantes ({len(missing_columns)}):")
            for col in missing_columns:
                print(f"   • {col}")
        else:
            print("✅ Todas as colunas necessárias estão presentes!")
        
        if extra_columns:
            print(f"ℹ️ Colunas extras ({len(extra_columns)}):")
            for col in extra_columns:
                print(f"   • {col}")
        
        cursor.close()
        conn.close()
        
        return len(missing_columns) == 0
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SCRIPT DE MIGRAÇÃO POSTGRESQL")
    print("=" * 50)
    print(f"Início: {datetime.now().isoformat()}")
    print()
    
    # Executar migração
    migration_success = execute_migration()
    
    if migration_success:
        # Verificar migração
        verification_success = verify_migration()
        
        if verification_success:
            print("\n🎉 MIGRAÇÃO COMPLETAMENTE VALIDADA!")
            exit(0)
        else:
            print("\n⚠️ MIGRAÇÃO EXECUTADA MAS VERIFICAÇÃO FALHOU")
            exit(1)
    else:
        print("\n❌ FALHA NA EXECUÇÃO DA MIGRAÇÃO")
        exit(1)
