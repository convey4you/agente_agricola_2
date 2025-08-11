#!/usr/bin/env python3
"""
Script de Migração da Tabela Users - PostgreSQL
Corrige erro: column users.country does not exist
"""

import os
import psycopg2
from datetime import datetime

def log_message(level, message):
    """Log formatado com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def migrate_users_table():
    """Aplica migração na tabela users"""
    
    log_message("INFO", "🔧 Iniciando migração da tabela users...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        log_message("ERROR", "❌ DATABASE_URL não encontrada!")
        return False
    
    try:
        # Conexão com PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        log_message("INFO", "✅ Conectado ao PostgreSQL")
        
        # Verificar se tabela users existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            );
        """)
        result = cursor.fetchone()
        table_exists = result[0] if result else False
        
        if not table_exists:
            log_message("ERROR", "❌ Tabela 'users' não encontrada!")
            return False
        
        # Verificar colunas existentes
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY column_name;
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        log_message("INFO", f"📋 Colunas existentes: {len(existing_columns)}")
        
        # Migrações da tabela users
        migrations = [
            ("country", "ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'Portugal';"),
            ("timezone", "ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Europe/Lisbon';"),
            ("postal_code", "ALTER TABLE users ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20);")
        ]
        
        log_message("INFO", f"🚀 Aplicando {len(migrations)} migrações na tabela users...")
        
        successful_migrations = 0
        
        for i, (column_name, query) in enumerate(migrations, 1):
            try:
                cursor.execute(query)
                conn.commit()
                log_message("INFO", f"✅ {i}/{len(migrations)} - Coluna '{column_name}' processada")
                successful_migrations += 1
            except Exception as e:
                if "already exists" in str(e):
                    log_message("INFO", f"ℹ️ {i}/{len(migrations)} - Coluna '{column_name}' já existe")
                    successful_migrations += 1
                else:
                    log_message("ERROR", f"❌ {i}/{len(migrations)} - Coluna '{column_name}': {e}")
                conn.rollback()
        
        # Verificação final
        cursor.execute("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY column_name;
        """)
        final_columns = cursor.fetchall()
        
        log_message("INFO", f"📊 Verificação final: {len(final_columns)} colunas na tabela users")
        
        # Verificar se colunas críticas existem
        critical_columns = ['country', 'timezone', 'postal_code']
        final_column_names = [col[0] for col in final_columns]
        missing_critical = [col for col in critical_columns if col not in final_column_names]
        
        if missing_critical:
            log_message("ERROR", f"❌ Colunas críticas ainda faltantes: {missing_critical}")
            return False
        else:
            log_message("INFO", "✅ Todas as colunas críticas estão presentes!")
        
        # Estatísticas
        cursor.execute("SELECT COUNT(*) FROM users;")
        result = cursor.fetchone()
        total_users = result[0] if result else 0
        
        cursor.close()
        conn.close()
        
        log_message("INFO", f"📈 Resumo: {successful_migrations}/{len(migrations)} migrações, {total_users} usuários")
        
        return successful_migrations == len(migrations)
        
    except Exception as e:
        log_message("ERROR", f"❌ Erro na migração: {e}")
        return False

if __name__ == "__main__":
    log_message("INFO", "🗄️ MIGRAÇÃO TABELA USERS - POSTGRESQL")
    log_message("INFO", "=" * 50)
    
    success = migrate_users_table()
    
    if success:
        log_message("INFO", "🎉 Migração da tabela users concluída com sucesso!")
    else:
        log_message("ERROR", "❌ Falha na migração da tabela users")
    
    exit(0 if success else 1)
