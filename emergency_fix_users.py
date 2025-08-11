#!/usr/bin/env python3
"""
MIGRAÇÃO EMERGENCIAL - FIX CRÍTICO users.country
Resolve especificamente o erro: column users.country does not exist
"""

import os
import psycopg2
from datetime import datetime

def log_message(level, message):
    """Log formatado com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def emergency_fix():
    """Aplica fix emergencial para o erro users.country"""
    
    log_message("INFO", "🚨 MIGRAÇÃO EMERGENCIAL - FIX users.country")
    log_message("INFO", "=" * 50)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        log_message("ERROR", "❌ DATABASE_URL não encontrada!")
        print("💡 Para Railway: DATABASE_URL é configurada automaticamente")
        print("💡 Para local: export DATABASE_URL='postgresql://...'")
        return False
    
    try:
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
            log_message("INFO", "💡 Execute db.create_all() primeiro")
            return False
        
        # Verificar colunas que existem
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY column_name;
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        log_message("INFO", f"📋 Colunas existentes: {existing_columns}")
        
        # Colunas críticas que DEVEM existir
        critical_columns = {
            'country': "ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'Portugal';",
            'timezone': "ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Europe/Lisbon';",
            'postal_code': "ALTER TABLE users ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20);",
            'is_active': "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
            'onboarding_completed': "ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;"
        }
        
        missing_columns = [col for col in critical_columns.keys() if col not in existing_columns]
        
        if missing_columns:
            log_message("WARNING", f"⚠️ Colunas faltantes: {missing_columns}")
            
            for column_name, query in critical_columns.items():
                if column_name in missing_columns:
                    try:
                        log_message("INFO", f"🔧 Adicionando coluna '{column_name}'...")
                        cursor.execute(query)
                        conn.commit()
                        log_message("INFO", f"✅ Coluna '{column_name}' adicionada com sucesso")
                    except Exception as e:
                        log_message("ERROR", f"❌ Erro ao adicionar '{column_name}': {e}")
                        conn.rollback()
                        return False
        else:
            log_message("INFO", "✅ Todas as colunas críticas já existem!")
        
        # Verificação final
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY column_name;
        """)
        final_columns = [row[0] for row in cursor.fetchall()]
        
        # Verificar se todas as críticas estão presentes
        still_missing = [col for col in critical_columns.keys() if col not in final_columns]
        
        if still_missing:
            log_message("ERROR", f"❌ Colunas ainda faltantes: {still_missing}")
            return False
        
        log_message("INFO", f"✅ Verificação final: {len(final_columns)} colunas na tabela users")
        log_message("INFO", "✅ Todas as colunas críticas estão presentes!")
        
        # Testar query que estava falhando
        try:
            log_message("INFO", "🧪 Testando query que estava falhando...")
            cursor.execute("""
                SELECT users.country, users.timezone, users.postal_code, users.is_active 
                FROM users 
                LIMIT 1;
            """)
            log_message("INFO", "✅ Query de teste executada com sucesso!")
        except Exception as e:
            log_message("ERROR", f"❌ Query de teste ainda falha: {e}")
            return False
        
        cursor.close()
        conn.close()
        
        log_message("INFO", "🎉 MIGRAÇÃO EMERGENCIAL CONCLUÍDA COM SUCESSO!")
        log_message("INFO", "✅ Erro 'column users.country does not exist' deve estar resolvido")
        
        return True
        
    except Exception as e:
        log_message("ERROR", f"❌ Erro na migração emergencial: {e}")
        return False

if __name__ == "__main__":
    success = emergency_fix()
    exit(0 if success else 1)
