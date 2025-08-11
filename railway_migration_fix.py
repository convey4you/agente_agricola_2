#!/usr/bin/env python3
"""
Script para executar migração da coluna interesses no Railway PostgreSQL
Deve ser executado no Railway Console
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def execute_railway_migration():
    """
    Executa a migração da coluna interesses no PostgreSQL do Railway
    """
    try:
        # Verificar se estamos no Railway (tem DATABASE_URL)
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL não encontrada. Este script deve ser executado no Railway.")
            return False
            
        logger.info("🚀 Iniciando migração no Railway PostgreSQL...")
        
        # Importar SQLAlchemy
        try:
            from sqlalchemy import create_engine, text, inspect
        except ImportError:
            logger.error("SQLAlchemy não disponível. Instalando...")
            os.system("pip install sqlalchemy psycopg2-binary")
            from sqlalchemy import create_engine, text, inspect
        
        # Conectar ao banco
        engine = create_engine(database_url)
        logger.info("✅ Conectado ao PostgreSQL do Railway")
        
        with engine.connect() as conn:
            # Verificar se a coluna já existe
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'interesses' in columns:
                logger.info("✅ Coluna 'interesses' já existe - migração já aplicada")
                return True
            
            logger.info(f"📋 Colunas atuais: {len(columns)} colunas")
            logger.info("⚙️ Executando migração: ADD COLUMN interesses...")
            
            # Executar a migração
            migration_sql = "ALTER TABLE users ADD COLUMN interesses VARCHAR(200);"
            conn.execute(text(migration_sql))
            conn.commit()
            
            logger.info("✅ Migração executada com sucesso!")
            
            # Verificar se a coluna foi criada
            inspector = inspect(engine)
            columns_after = [col['name'] for col in inspector.get_columns('users')]
            
            if 'interesses' in columns_after:
                logger.info("✅ Coluna 'interesses' criada e verificada!")
                return True
            else:
                logger.error("❌ Erro: Coluna não foi criada corretamente")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro na migração: {str(e)}")
        return False

def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info("MIGRAÇÃO RAILWAY - COLUNA INTERESSES")
    logger.info("=" * 60)
    
    success = execute_railway_migration()
    
    if success:
        logger.info("🎉 Migração concluída com sucesso!")
        logger.info("✅ A aplicação agora pode ser reiniciada")
    else:
        logger.error("❌ Migração falhou")
        sys.exit(1)

if __name__ == "__main__":
    main()
