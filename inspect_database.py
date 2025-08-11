#!/usr/bin/env python3
"""
Script para inspecionar a estrutura do banco de dados
Verifica tabelas, campos e dados existentes
"""
import os
import sys
import sqlite3
from datetime import datetime

# Configurar variáveis de ambiente
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_CONFIG'] = 'development'

# Adicionar o diretório da aplicação ao Python path
sys.path.insert(0, os.path.abspath('.'))

def inspect_database():
    """Inspecionar estrutura do banco de dados"""
    
    try:
        from app import create_app, db
        
        print("🔍 Inspecionando estrutura do banco de dados...")
        print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Criar aplicação Flask
        app = create_app()
        
        with app.app_context():
            database_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
            print(f"📊 Banco: {database_uri}")
            
            # Conectar diretamente ao SQLite para inspeção
            if 'sqlite:///' in database_uri:
                db_path = database_uri.replace('sqlite:///', '')
                print(f"📁 Caminho do arquivo: {db_path}")
                
                if not os.path.exists(db_path):
                    print("❌ Arquivo do banco não existe!")
                    return False
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Listar todas as tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"\n📋 Tabelas encontradas ({len(tables)}):")
                for table in tables:
                    print(f"  - {table[0]}")
                
                # Inspecionar tabela users
                print("\n👥 ESTRUTURA DA TABELA 'users':")
                try:
                    cursor.execute("PRAGMA table_info(users);")
                    columns = cursor.fetchall()
                    for col in columns:
                        print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
                    
                    # Contar usuários
                    cursor.execute("SELECT COUNT(*) FROM users;")
                    user_count = cursor.fetchone()[0]
                    print(f"  📊 Total de usuários: {user_count}")
                    
                    if user_count > 0:
                        cursor.execute("SELECT id, email FROM users LIMIT 3;")
                        users = cursor.fetchall()
                        print("  📝 Usuários encontrados:")
                        for user in users:
                            print(f"    ID: {user[0]}, Email: {user[1]}")
                except Exception as e:
                    print(f"  ❌ Erro ao inspecionar users: {e}")
                
                # Inspecionar tabela cultures
                print("\n🌱 ESTRUTURA DA TABELA 'cultures':")
                try:
                    cursor.execute("PRAGMA table_info(cultures);")
                    columns = cursor.fetchall()
                    for col in columns:
                        print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
                    
                    # Contar culturas
                    cursor.execute("SELECT COUNT(*) FROM cultures;")
                    culture_count = cursor.fetchone()[0]
                    print(f"  📊 Total de culturas: {culture_count}")
                    
                    if culture_count > 0:
                        cursor.execute("SELECT id, nome, user_id FROM cultures LIMIT 3;")
                        cultures = cursor.fetchall()
                        print("  📝 Culturas encontradas:")
                        for culture in cultures:
                            print(f"    ID: {culture[0]}, Nome: {culture[1]}, User ID: {culture[2]}")
                except Exception as e:
                    print(f"  ❌ Erro ao inspecionar cultures: {e}")
                
                # Inspecionar tabela alerts
                print("\n🔔 ESTRUTURA DA TABELA 'alerts':")
                try:
                    cursor.execute("PRAGMA table_info(alerts);")
                    columns = cursor.fetchall()
                    for col in columns:
                        print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
                    
                    # Contar alertas
                    cursor.execute("SELECT COUNT(*) FROM alerts;")
                    alert_count = cursor.fetchone()[0]
                    print(f"  📊 Total de alertas: {alert_count}")
                    
                    if alert_count > 0:
                        cursor.execute("SELECT id, type, title, user_id FROM alerts LIMIT 3;")
                        alerts = cursor.fetchall()
                        print("  📝 Alertas encontrados:")
                        for alert in alerts:
                            print(f"    ID: {alert[0]}, Tipo: {alert[1]}, Título: {alert[2]}, User ID: {alert[3]}")
                except Exception as e:
                    print(f"  ❌ Erro ao inspecionar alerts: {e}")
                
                conn.close()
                
            print("\n✅ Inspeção concluída!")
            return True
            
    except Exception as e:
        print(f"❌ Erro durante inspeção: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando inspeção do banco de dados...")
    success = inspect_database()
    
    if success:
        print("\n🎉 Inspeção executada com sucesso!")
    else:
        print("\n💥 Inspeção falhou!")
        sys.exit(1)
