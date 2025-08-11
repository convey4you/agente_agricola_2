#!/usr/bin/env python3
"""
Script para aplicar migração usando Flask-Migrate em produção
Força a aplicação da migração que adiciona colunas faltantes
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Criar aplicação Flask para executar migração"""
    app = Flask(__name__)
    
    # Configurações de produção
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    return app

def execute_migration_via_sql():
    """Executar migração via SQL direto"""
    
    try:
        app = create_app()
        db = SQLAlchemy()
        db.init_app(app)
        
        with app.app_context():
            # SQL para adicionar colunas
            migration_queries = [
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS action_text VARCHAR(100);",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS action_url VARCHAR(500);", 
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS location_data TEXT;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS weather_data TEXT;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS alert_metadata TEXT;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS scheduled_for TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS sent_at TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS delivery_channels VARCHAR(100) DEFAULT 'web';",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS last_retry_at TIMESTAMP;",
                "CREATE INDEX IF NOT EXISTS ix_alerts_scheduled_for ON alerts(scheduled_for);",
                "CREATE INDEX IF NOT EXISTS ix_alerts_expires_at ON alerts(expires_at);"
            ]
            
            logger.info("🚀 Executando migração de colunas...")
            
            from sqlalchemy import text
            
            for i, query in enumerate(migration_queries, 1):
                try:
                    db.session.execute(text(query))
                    db.session.commit()
                    logger.info(f"✅ Query {i}/{len(migration_queries)} executada com sucesso")
                except Exception as e:
                    logger.warning(f"⚠️ Query {i} falhou (pode já existir): {e}")
                    db.session.rollback()
            
            # Verificar resultado
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'alerts' 
                ORDER BY ordinal_position;
            """)).fetchall()
            
            columns = [row[0] for row in result]
            logger.info(f"📋 Colunas na tabela alerts: {len(columns)}")
            
            required_columns = [
                'action_text', 'action_url', 'location_data', 'weather_data', 
                'alert_metadata', 'scheduled_for', 'expires_at', 'sent_at',
                'delivery_channels', 'retry_count', 'last_retry_at'
            ]
            
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                logger.error(f"❌ Colunas ainda faltantes: {missing_columns}")
                return False
            else:
                logger.info("✅ Todas as colunas necessárias estão presentes!")
                return True
                
    except Exception as e:
        logger.error(f"❌ Erro durante migração: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 MIGRAÇÃO FORÇADA - PRODUÇÃO")
    print("=" * 60)
    
    success = execute_migration_via_sql()
    
    if success:
        print("\n🎉 Migração executada com sucesso!")
        print("🔄 Reinicie o serviço para aplicar as mudanças.")
    else:
        print("\n❌ Falha na migração")
    
    sys.exit(0 if success else 1)
