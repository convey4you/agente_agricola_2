#!/usr/bin/env python3
"""
MIGRAÇÃO COMPLETA POSTGRESQL - TODAS AS TABELAS
Baseado no GUIA_MIGRACAO_POSTGRESQL_PRODUCAO.md

Este script garante que todas as tabelas tenham todas as colunas necessárias
para evitar erros como "column users.country does not exist"
"""

import os
import psycopg2
from datetime import datetime

def log_message(level, message):
    """Log formatado com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def get_all_table_migrations():
    """Retorna todas as migrações necessárias para todas as tabelas"""
    
    migrations = {
        'users': [
            # Colunas básicas (existem)
            # "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY);",
            # "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(120) UNIQUE NOT NULL;",
            
            # Colunas que podem estar faltando
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'Portugal';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Europe/Lisbon';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS ultimo_acesso TIMESTAMP;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS nome_completo VARCHAR(200);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS telefone VARCHAR(20);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS experience_level VARCHAR(20) DEFAULT 'beginner';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS propriedade_nome VARCHAR(120);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS latitude FLOAT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS longitude FLOAT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS cidade VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS estado VARCHAR(50);"
        ],
        
        'alerts': [
            # Todas as colunas da tabela alerts baseadas no modelo
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
            "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS last_retry_at TIMESTAMP;",
            "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS severity_level INTEGER DEFAULT 1;",
            "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
            "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;"
        ],
        
        'cultures': [
            "ALTER TABLE cultures ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
            "ALTER TABLE cultures ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;",
            "ALTER TABLE cultures ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE cultures ADD COLUMN IF NOT EXISTS description TEXT;",
            "ALTER TABLE cultures ADD COLUMN IF NOT EXISTS season VARCHAR(20);",
            "ALTER TABLE cultures ADD COLUMN IF NOT EXISTS planting_date DATE;",
            "ALTER TABLE cultures ADD COLUMN IF NOT EXISTS harvest_date DATE;"
        ],
        
        'farms': [
            "ALTER TABLE farms ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
            "ALTER TABLE farms ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;",
            "ALTER TABLE farms ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE farms ADD COLUMN IF NOT EXISTS description TEXT;",
            "ALTER TABLE farms ADD COLUMN IF NOT EXISTS total_area FLOAT;",
            "ALTER TABLE farms ADD COLUMN IF NOT EXISTS latitude FLOAT;",
            "ALTER TABLE farms ADD COLUMN IF NOT EXISTS longitude FLOAT;"
        ],
        
        'activities': [
            "ALTER TABLE activities ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
            "ALTER TABLE activities ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;",
            "ALTER TABLE activities ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;",
            "ALTER TABLE activities ADD COLUMN IF NOT EXISTS is_completed BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE activities ADD COLUMN IF NOT EXISTS notes TEXT;",
            "ALTER TABLE activities ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium';"
        ]
    }
    
    return migrations

def verify_environment():
    """Verifica variáveis de ambiente essenciais"""
    log_message("INFO", "🔍 Verificando ambiente...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        log_message("ERROR", "❌ DATABASE_URL não encontrada!")
        return None
    
    # Mascarar URL para log seguro
    masked_url = database_url[:30] + "..." if len(database_url) > 30 else database_url
    log_message("INFO", f"✅ DATABASE_URL encontrada: {masked_url}")
    
    return database_url

def test_database_connection(database_url):
    """Testa conexão com PostgreSQL"""
    log_message("INFO", "🔗 Testando conexão com PostgreSQL...")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar versão do PostgreSQL
        cursor.execute("SELECT version();")
        version_result = cursor.fetchone()
        if version_result:
            version = version_result[0]
            log_message("INFO", f"✅ PostgreSQL conectado: {version[:80]}...")
        else:
            log_message("WARNING", "⚠️ Não foi possível obter versão do PostgreSQL")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        log_message("ERROR", f"❌ Erro de conexão: {e}")
        return False

def get_existing_tables(database_url):
    """Lista todas as tabelas existentes"""
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        return tables
        
    except Exception as e:
        log_message("ERROR", f"❌ Erro ao listar tabelas: {e}")
        return []

def execute_complete_migration(database_url):
    """Executa migração completa de todas as tabelas"""
    log_message("INFO", "🚀 Iniciando migração completa...")
    
    migrations = get_all_table_migrations()
    existing_tables = get_existing_tables(database_url)
    
    if not existing_tables:
        log_message("ERROR", "❌ Não foi possível listar tabelas existentes")
        return False
    
    log_message("INFO", f"📋 Tabelas encontradas: {existing_tables}")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        total_migrations = sum(len(table_migrations) for table_migrations in migrations.values())
        successful_migrations = 0
        skipped_migrations = 0
        failed_migrations = 0
        
        log_message("INFO", f"📊 Total de migrações a executar: {total_migrations}")
        log_message("INFO", "=" * 60)
        
        for table_name, table_migrations in migrations.items():
            log_message("INFO", f"🔧 Processando tabela '{table_name}'...")
            
            # Verificar se tabela existe
            if table_name not in existing_tables:
                log_message("WARNING", f"⚠️ Tabela '{table_name}' não existe - pulando migrações")
                skipped_migrations += len(table_migrations)
                continue
            
            for i, query in enumerate(table_migrations, 1):
                try:
                    cursor.execute(query)
                    conn.commit()
                    successful_migrations += 1
                    
                    # Extrair nome da coluna do query para log
                    if "ADD COLUMN" in query:
                        parts = query.split("ADD COLUMN IF NOT EXISTS ")
                        if len(parts) > 1:
                            column_info = parts[1].split()[0]
                            log_message("INFO", f"  ✅ {i:2d}/{len(table_migrations)} - Coluna '{column_info}' processada")
                    else:
                        log_message("INFO", f"  ✅ {i:2d}/{len(table_migrations)} - Migração aplicada")
                        
                except Exception as e:
                    if "already exists" in str(e):
                        successful_migrations += 1
                        if "ADD COLUMN" in query:
                            parts = query.split("ADD COLUMN IF NOT EXISTS ")
                            if len(parts) > 1:
                                column_info = parts[1].split()[0]
                                log_message("INFO", f"  ℹ️ {i:2d}/{len(table_migrations)} - Coluna '{column_info}' já existe")
                    else:
                        failed_migrations += 1
                        log_message("ERROR", f"  ❌ {i:2d}/{len(table_migrations)} - Erro: {e}")
                    conn.rollback()
            
            log_message("INFO", f"✅ Tabela '{table_name}' processada")
        
        cursor.close()
        conn.close()
        
        # Estatísticas finais
        log_message("INFO", "=" * 60)
        log_message("INFO", f"📈 RESUMO DA MIGRAÇÃO COMPLETA:")
        log_message("INFO", f"   • Total de migrações: {total_migrations}")
        log_message("INFO", f"   • Sucessos: {successful_migrations}")
        log_message("INFO", f"   • Puladas: {skipped_migrations}")
        log_message("INFO", f"   • Falhas: {failed_migrations}")
        
        success_rate = (successful_migrations / total_migrations) * 100 if total_migrations > 0 else 0
        log_message("INFO", f"   • Taxa de sucesso: {success_rate:.1f}%")
        
        if failed_migrations == 0:
            log_message("INFO", "🎉 Migração completa executada com sucesso!")
            return True
        else:
            log_message("WARNING", f"⚠️ Migração executada com {failed_migrations} falhas")
            return False
        
    except Exception as e:
        log_message("ERROR", f"❌ Erro na execução da migração: {e}")
        return False

def validate_migration_results(database_url):
    """Valida resultados da migração"""
    log_message("INFO", "🧪 Validando resultados da migração...")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar colunas críticas da tabela users
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY column_name;
        """)
        user_columns = [row[0] for row in cursor.fetchall()]
        
        critical_user_columns = ['country', 'timezone', 'postal_code', 'is_active']
        missing_user_columns = [col for col in critical_user_columns if col not in user_columns]
        
        if missing_user_columns:
            log_message("ERROR", f"❌ Colunas críticas faltantes em users: {missing_user_columns}")
            return False
        else:
            log_message("INFO", f"✅ Tabela users: {len(user_columns)} colunas - Todas críticas presentes")
        
        # Verificar colunas críticas da tabela alerts
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'alerts' 
            ORDER BY column_name;
        """)
        alert_columns = [row[0] for row in cursor.fetchall()]
        
        critical_alert_columns = ['action_text', 'action_url', 'read_at', 'dismissed_at']
        missing_alert_columns = [col for col in critical_alert_columns if col not in alert_columns]
        
        if missing_alert_columns:
            log_message("WARNING", f"⚠️ Colunas faltantes em alerts: {missing_alert_columns}")
        else:
            log_message("INFO", f"✅ Tabela alerts: {len(alert_columns)} colunas - Todas críticas presentes")
        
        cursor.close()
        conn.close()
        
        return len(missing_user_columns) == 0
        
    except Exception as e:
        log_message("ERROR", f"❌ Erro na validação: {e}")
        return False

def main():
    """Função principal da migração completa"""
    log_message("INFO", "🗄️ MIGRAÇÃO COMPLETA POSTGRESQL - TODAS AS TABELAS")
    log_message("INFO", "=" * 60)
    log_message("INFO", "Baseado no GUIA_MIGRACAO_POSTGRESQL_PRODUCAO.md")
    log_message("INFO", "=" * 60)
    
    # Etapa 1: Verificar ambiente
    database_url = verify_environment()
    if not database_url:
        return False
    
    # Etapa 2: Testar conexão
    if not test_database_connection(database_url):
        return False
    
    # Etapa 3: Executar migração completa
    if not execute_complete_migration(database_url):
        log_message("ERROR", "❌ Falha na execução da migração")
        return False
    
    # Etapa 4: Validar resultados
    if not validate_migration_results(database_url):
        log_message("WARNING", "⚠️ Algumas validações falharam")
        return False
    
    log_message("INFO", "=" * 60)
    log_message("INFO", "🎉 MIGRAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!")
    log_message("INFO", "✅ Todas as tabelas atualizadas")
    log_message("INFO", "✅ Erro 'column users.country does not exist' deve estar resolvido")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
