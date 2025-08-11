#!/usr/bin/env python3
"""
Script para inicializar o banco de dados PostgreSQL no Railway
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from flask_migrate import upgrade, init, migrate

def init_database():
    """Inicializar banco de dados"""
    # Configurar para produção
    os.environ.setdefault('FLASK_ENV', 'production')
    
    app = create_app('production')
    
    with app.app_context():
        try:
            # Tentar executar migrações
            print("🔄 Executando migrações...")
            upgrade()
            print("✅ Migrações executadas com sucesso!")
            
        except Exception as e:
            print(f"⚠️  Erro nas migrações: {e}")
            print("🔄 Criando tabelas diretamente...")
            
            try:
                # Criar todas as tabelas
                db.create_all()
                print("✅ Tabelas criadas com sucesso!")
                
            except Exception as e2:
                print(f"❌ Erro ao criar tabelas: {e2}")
                sys.exit(1)
        
        # Verificar conexão
        try:
            result = db.engine.execute("SELECT 1")
            print("✅ Conexão com PostgreSQL verificada!")
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            sys.exit(1)

if __name__ == '__main__':
    print("🚀 Inicializando banco de dados PostgreSQL...")
    init_database()
    print("🎉 Inicialização concluída!")
