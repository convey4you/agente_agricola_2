#!/usr/bin/env python3
"""
Migração para adicionar campo interesses na tabela users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User

def add_interesses_column():
    """Adiciona a coluna interesses na tabela users"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar se a coluna já existe
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            print(f"📋 Colunas atuais na tabela users: {columns}")
            
            if 'interesses' in columns:
                print("✅ Coluna 'interesses' já existe!")
                return
            
            print("🔄 Adicionando coluna 'interesses' na tabela users...")
            
            # Executar SQL para adicionar a coluna
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE users ADD COLUMN interesses VARCHAR(200)"))
                conn.commit()
            
            print("✅ Coluna 'interesses' adicionada com sucesso!")
            
            # Verificar novamente
            columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"📋 Colunas após migração: {columns}")
            
            if 'interesses' in columns:
                print("✅ Migração concluída com sucesso!")
            else:
                print("❌ Erro: Coluna não foi adicionada")
            
        except Exception as e:
            print(f"❌ Erro durante migração: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando migração para adicionar campo interesses...")
    add_interesses_column()
    print("\n🔚 Migração concluída!")
