#!/usr/bin/env python3
"""
SUPER MIGRAÇÃO AUTOMÁTICA - FORÇA ABSOLUTA
Aplica migração via SQLAlchemy usando conexão da própria aplicação
"""

from app import create_app, db
from sqlalchemy import text
import os

def force_migration():
    """Força migração usando a própria aplicação"""
    
    print("🚨 SUPER MIGRAÇÃO AUTOMÁTICA - FORÇA ABSOLUTA")
    print("=" * 60)
    
    # Criar aplicação
    app = create_app(os.getenv('FLASK_CONFIG') or 'production')
    
    with app.app_context():
        try:
            print("🔧 Forçando migração da tabela users...")
            
            # Listar tabelas existentes
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tabelas existentes: {tables}")
            
            if 'users' not in tables:
                print("❌ Tabela 'users' não existe! Criando todas as tabelas...")
                db.create_all()
                print("✅ Tabelas criadas com db.create_all()")
            
            # Lista de TODAS as colunas que devem existir
            user_migrations = [
                # Colunas básicas
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(120);",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);",
                
                # Colunas de perfil
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS nome_completo VARCHAR(200);",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS telefone VARCHAR(20);",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS experience_level VARCHAR(20) DEFAULT 'beginner';",
                
                # Colunas de localização
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS propriedade_nome VARCHAR(120);",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS latitude FLOAT;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS longitude FLOAT;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS cidade VARCHAR(100);",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS estado VARCHAR(50);",
                
                # COLUNAS CRÍTICAS QUE ESTÃO FALTANDO
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'Portugal';",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Europe/Lisbon';",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20);",
                
                # Colunas de controle
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS ultimo_acesso TIMESTAMP;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;"
            ]
            
            print(f"🚀 Aplicando {len(user_migrations)} migrações...")
            
            success_count = 0
            for i, query in enumerate(user_migrations, 1):
                try:
                    result = db.session.execute(text(query))
                    db.session.commit()
                    success_count += 1
                    print(f"✅ {i:2d}/{len(user_migrations)} - Migração aplicada")
                except Exception as e:
                    db.session.rollback()
                    if "already exists" in str(e) or "duplicate column" in str(e):
                        success_count += 1
                        print(f"ℹ️ {i:2d}/{len(user_migrations)} - Já existe")
                    else:
                        print(f"❌ {i:2d}/{len(user_migrations)} - Erro: {e}")
            
            print(f"\n📊 Resultado: {success_count}/{len(user_migrations)} migrações")
            
            # Verificação final crítica
            print("\n🧪 VERIFICAÇÃO FINAL...")
            
            # Listar colunas da tabela users
            user_columns = inspector.get_columns('users')
            column_names = [col['name'] for col in user_columns]
            print(f"📋 Colunas na tabela users: {column_names}")
            
            # Verificar colunas críticas
            critical_columns = ['country', 'timezone', 'postal_code', 'is_active']
            missing_critical = [col for col in critical_columns if col not in column_names]
            
            if missing_critical:
                print(f"❌ AINDA FALTAM COLUNAS CRÍTICAS: {missing_critical}")
                
                # Tentar de forma individual e mais agressiva
                for col in missing_critical:
                    try:
                        if col == 'country':
                            query = "ALTER TABLE users ADD COLUMN country VARCHAR(100) DEFAULT 'Portugal';"
                        elif col == 'timezone':
                            query = "ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'Europe/Lisbon';"
                        elif col == 'postal_code':
                            query = "ALTER TABLE users ADD COLUMN postal_code VARCHAR(20);"
                        elif col == 'is_active':
                            query = "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;"
                        
                        db.session.execute(text(query))
                        db.session.commit()
                        print(f"✅ Coluna '{col}' adicionada individualmente")
                    except Exception as e:
                        db.session.rollback()
                        print(f"❌ Falha ao adicionar '{col}': {e}")
            else:
                print(f"✅ TODAS AS COLUNAS CRÍTICAS PRESENTES!")
            
            # Teste da query que estava falhando
            print("\n🎯 TESTANDO QUERY QUE FALHA...")
            try:
                test_query = """
                SELECT users.id, users.email, users.country, users.timezone, 
                       users.postal_code, users.is_active, users.onboarding_completed
                FROM users 
                WHERE users.is_active = true 
                LIMIT 1
                """
                result = db.session.execute(text(test_query))
                print("✅ QUERY DE TESTE PASSOU! Problema resolvido!")
                return True
            except Exception as e:
                print(f"❌ QUERY DE TESTE FALHOU: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Erro crítico na super migração: {e}")
            return False

if __name__ == "__main__":
    success = force_migration()
    if success:
        print("\n🎉 SUPER MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    else:
        print("\n❌ SUPER MIGRAÇÃO FALHOU")
    exit(0 if success else 1)
