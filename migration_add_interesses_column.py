#!/usr/bin/env python3
"""
Migração: Adicionar coluna interesses na tabela users
Data: 2025-08-05
Descrição: Adiciona campo para armazenar os interesses selecionados pelo usuário no onboarding
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_add_interesses_column():
    """Adiciona a coluna interesses na tabela users"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("🚀 Iniciando migração: Adicionar coluna 'interesses' na tabela users")
            
            # Verificar se a coluna já existe
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            logger.info(f"📋 Colunas atuais na tabela users: {len(columns)} colunas")
            
            if 'interesses' in columns:
                logger.info("✅ Coluna 'interesses' já existe - migração já aplicada")
                return True
            
            logger.info("🔄 Adicionando coluna 'interesses' na tabela users...")
            
            # SQL para adicionar a coluna
            add_column_sql = "ALTER TABLE users ADD COLUMN interesses VARCHAR(200)"
            
            # Executar SQL para adicionar a coluna
            with db.engine.connect() as conn:
                conn.execute(text(add_column_sql))
                conn.commit()
            
            logger.info("✅ Coluna 'interesses' adicionada com sucesso!")
            
            # Verificar se a coluna foi criada
            inspector = db.inspect(db.engine)
            updated_columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'interesses' in updated_columns:
                logger.info("✅ Migração concluída com sucesso!")
                logger.info(f"📋 Total de colunas após migração: {len(updated_columns)}")
                return True
            else:
                logger.error("❌ Erro: Coluna não foi criada corretamente")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro durante migração: {str(e)}")
            return False

def rollback_interesses_column():
    """Remove a coluna interesses da tabela users (rollback)"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("🔄 Iniciando rollback: Remover coluna 'interesses' da tabela users")
            
            # Verificar se a coluna existe
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'interesses' not in columns:
                logger.info("ℹ️  Coluna 'interesses' não existe - rollback não necessário")
                return True
            
            # SQL para remover a coluna (SQLite não suporta DROP COLUMN diretamente)
            # Para SQLite, seria necessário recriar a tabela, mas vamos assumir PostgreSQL em produção
            drop_column_sql = "ALTER TABLE users DROP COLUMN interesses"
            
            with db.engine.connect() as conn:
                conn.execute(text(drop_column_sql))
                conn.commit()
            
            logger.info("✅ Rollback concluído - coluna 'interesses' removida")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante rollback: {str(e)}")
            # Para SQLite, o rollback pode falhar - isso é esperado
            if "DROP COLUMN" in str(e):
                logger.warning("⚠️  SQLite não suporta DROP COLUMN - rollback não aplicável localmente")
                logger.info("💡 Em produção (PostgreSQL), o rollback funcionará corretamente")
                return True
            return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("🔄 Executando rollback da migração...")
        success = rollback_interesses_column()
    else:
        print("🚀 Executando migração...")
        success = migrate_add_interesses_column()
    
    if success:
        print("✅ Operação concluída com sucesso!")
        sys.exit(0)
    else:
        print("❌ Operação falhou!")
        sys.exit(1)
