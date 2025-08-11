#!/usr/bin/env python3
"""
Script de Migração - Remover campo username da tabela users
Remove inconsistência entre modelo e banco de produção
Autor: Gerente de Tecnologia
Data: 1 de agosto de 2025
"""

import os
import sys
from sqlalchemy import text
from app import create_app, db

def remove_username_column():
    """Remove a coluna username da tabela users"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Verificando se coluna username existe...")
            
            # Detectar tipo de banco
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            is_sqlite = 'sqlite' in db_url.lower()
            is_postgresql = 'postgresql' in db_url.lower()
            
            print(f"🔍 Tipo de banco detectado: {'SQLite' if is_sqlite else 'PostgreSQL' if is_postgresql else 'Desconhecido'}")
            
            # Verificar se a coluna existe (método compatível)
            column_exists = False
            try:
                if is_sqlite:
                    # Para SQLite, usar PRAGMA
                    result = db.session.execute(text("PRAGMA table_info(users)"))
                    columns = [row[1] for row in result.fetchall()]  # row[1] é o nome da coluna
                    column_exists = 'username' in columns
                else:
                    # Para PostgreSQL, usar information_schema
                    result = db.session.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'username'
                    """))
                    column_exists = result.fetchone() is not None
                    
            except Exception as e:
                print(f"⚠️ Erro ao verificar coluna: {e}")
                # Tentar método alternativo - criar tabela temporária
                try:
                    from app.models.user import User
                    # Se o modelo não tem username mas a query falha, provavelmente a coluna existe
                    db.session.execute(text("SELECT username FROM users LIMIT 1"))
                    column_exists = True
                    print("🔍 Coluna username detectada via query direta")
                except:
                    column_exists = False
                    print("🔍 Coluna username não detectada")
            
            if column_exists:
                print("⚠️ Coluna username encontrada. Removendo...")
                
                if is_sqlite:
                    print("⚠️ SQLite não suporta DROP COLUMN diretamente")
                    print("🔄 Recriando tabela sem username...")
                    
                    # Para SQLite, precisamos recriar a tabela
                    # Primeiro, obter dados existentes
                    existing_users = db.session.execute(text("""
                        SELECT id, email, password_hash, nome_completo, telefone, 
                               experience_level, propriedade_nome, latitude, longitude, 
                               cidade, estado, data_criacao, ultimo_acesso, ativo, 
                               onboarding_completed
                        FROM users
                    """)).fetchall()
                    
                    print(f"📋 Backup de {len(existing_users)} usuários criado")
                    
                    # Renomear tabela atual
                    db.session.execute(text("ALTER TABLE users RENAME TO users_backup"))
                    db.session.commit()
                    
                    # Recriar tabela com novo schema (sem username)
                    from app.models.user import User
                    User.__table__.create(db.engine)
                    
                    # Restaurar dados
                    for user_data in existing_users:
                        db.session.execute(text("""
                            INSERT INTO users (id, email, password_hash, nome_completo, telefone,
                                             experience_level, propriedade_nome, latitude, longitude,
                                             cidade, estado, data_criacao, ultimo_acesso, ativo,
                                             onboarding_completed)
                            VALUES (:id, :email, :password_hash, :nome_completo, :telefone,
                                   :experience_level, :propriedade_nome, :latitude, :longitude,
                                   :cidade, :estado, :data_criacao, :ultimo_acesso, :ativo,
                                   :onboarding_completed)
                        """), {
                            'id': user_data[0],
                            'email': user_data[1],
                            'password_hash': user_data[2],
                            'nome_completo': user_data[3],
                            'telefone': user_data[4],
                            'experience_level': user_data[5],
                            'propriedade_nome': user_data[6],
                            'latitude': user_data[7],
                            'longitude': user_data[8],
                            'cidade': user_data[9],
                            'estado': user_data[10],
                            'data_criacao': user_data[11],
                            'ultimo_acesso': user_data[12],
                            'ativo': user_data[13],
                            'onboarding_completed': user_data[14]
                        })
                    
                    db.session.commit()
                    
                    # Remover tabela backup
                    db.session.execute(text("DROP TABLE users_backup"))
                    db.session.commit()
                    
                    print("✅ Tabela SQLite recriada sem username")
                    
                else:
                    # PostgreSQL - pode usar DROP COLUMN
                    # Verificar se há dados na coluna username
                    result = db.session.execute(text("""
                        SELECT COUNT(*) 
                        FROM users 
                        WHERE username IS NOT NULL
                    """))
                    count_with_username = result.scalar()
                    
                    if count_with_username > 0:
                        print(f"⚠️ {count_with_username} usuários têm username definido")
                        print("🔄 Limpando dados da coluna username...")
                        
                        # Limpar dados da coluna primeiro
                        db.session.execute(text("UPDATE users SET username = NULL"))
                        db.session.commit()
                        print("✅ Dados da coluna username limpos")
                    
                    # Remover constraint unique se existir
                    try:
                        db.session.execute(text("""
                            ALTER TABLE users 
                            DROP CONSTRAINT IF EXISTS users_username_key
                        """))
                        db.session.commit()
                        print("✅ Constraint unique removida")
                    except Exception as e:
                        print(f"ℹ️ Constraint unique não encontrada: {e}")
                    
                    # Remover a coluna
                    db.session.execute(text("ALTER TABLE users DROP COLUMN username"))
                    db.session.commit()
                    
                    print("✅ Coluna username removida do PostgreSQL")
                
                return True
                    
            else:
                print("✅ Coluna username já não existe no banco")
                return True
                
        except Exception as e:
            print(f"❌ Erro durante migração: {e}")
            db.session.rollback()
            return False

def verify_model_consistency():
    """Verifica se o modelo está consistente com o banco"""
    app = create_app()
    
    with app.app_context():
        try:
            from app.models.user import User
            
            # Verificar se o modelo ainda tem username
            model_columns = [col.name for col in User.__table__.columns]
            has_username_in_model = 'username' in model_columns
            
            print(f"🔍 Modelo User tem username: {has_username_in_model}")
            
            # Verificar se o banco tem username
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            is_sqlite = 'sqlite' in db_url.lower()
            
            has_username_in_db = False
            try:
                if is_sqlite:
                    result = db.session.execute(text("PRAGMA table_info(users)"))
                    columns = [row[1] for row in result.fetchall()]
                    has_username_in_db = 'username' in columns
                else:
                    result = db.session.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'username'
                    """))
                    has_username_in_db = result.fetchone() is not None
            except Exception as e:
                print(f"⚠️ Erro na verificação do banco: {e}")
                # Método alternativo
                try:
                    db.session.execute(text("SELECT username FROM users LIMIT 1"))
                    has_username_in_db = True
                except:
                    has_username_in_db = False
            
            print(f"🔍 Banco users tem username: {has_username_in_db}")
            
            if has_username_in_model == has_username_in_db == False:
                print("✅ Modelo e banco consistentes (sem username)")
                return True
            else:
                print("⚠️ Inconsistência entre modelo e banco")
                return False
                
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            return False

def test_user_creation():
    """Testa criação de usuário após migração"""
    app = create_app()
    
    with app.app_context():
        try:
            from app.models.user import User
            
            # Criar usuário de teste
            test_user = User(
                email='migration_test@example.com',
                password_hash='test_hash',
                nome_completo='Migration Test'
            )
            
            db.session.add(test_user)
            db.session.flush()  # Testa sem commit permanente
            
            print("✅ Criação de usuário funcionando após migração")
            
            db.session.rollback()  # Remove usuário de teste
            return True
            
        except Exception as e:
            print(f"❌ Erro na criação de usuário: {e}")
            db.session.rollback()
            return False

def main():
    """Função principal da migração"""
    print("🚀 MIGRAÇÃO: REMOÇÃO DA COLUNA USERNAME")
    print("=" * 50)
    
    # Passo 1: Verificar estado inicial
    print("\n1. VERIFICAÇÃO INICIAL:")
    verify_model_consistency()
    
    # Passo 2: Remover coluna username
    print("\n2. REMOÇÃO DA COLUNA:")
    if remove_username_column():
        print("✅ Migração da coluna bem-sucedida")
    else:
        print("❌ Falha na migração da coluna")
        sys.exit(1)
    
    # Passo 3: Verificar consistência
    print("\n3. VERIFICAÇÃO FINAL:")
    if verify_model_consistency():
        print("✅ Modelo e banco consistentes")
    else:
        print("❌ Ainda há inconsistências")
        sys.exit(1)
    
    # Passo 4: Testar funcionalidade
    print("\n4. TESTE DE FUNCIONALIDADE:")
    if test_user_creation():
        print("✅ Sistema funcionando corretamente")
    else:
        print("❌ Problemas na funcionalidade")
        sys.exit(1)
    
    print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 50)

if __name__ == "__main__":
    main()
