#!/usr/bin/env python3
"""
Migração para adicionar colunas de agendamento automático na tabela user_alert_preferences
"""
from app import create_app, db
from sqlalchemy import text

def migrate_user_alert_preferences():
    """Adicionar colunas de agendamento automático"""
    
    app = create_app()
    with app.app_context():
        try:
            print("🔧 Iniciando migração da tabela user_alert_preferences...")
            
            # Lista de colunas para adicionar
            columns_to_add = [
                "auto_generation_enabled BOOLEAN DEFAULT 1",
                "auto_frequency VARCHAR(20) DEFAULT 'daily'",
                "auto_time TIME DEFAULT '08:00:00'",
                "auto_weekday INTEGER",
                "auto_day_of_month INTEGER", 
                "last_auto_generation DATETIME"
            ]
            
            # Verificar quais colunas já existem
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('user_alert_preferences')]
            
            print(f"✓ Colunas existentes: {existing_columns}")
            
            # Adicionar colunas que não existem
            for column_def in columns_to_add:
                column_name = column_def.split()[0]
                
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE user_alert_preferences ADD COLUMN {column_def}"
                        db.session.execute(text(sql))
                        db.session.commit()
                        print(f"✓ Coluna '{column_name}' adicionada com sucesso")
                    except Exception as e:
                        print(f"✗ Erro ao adicionar coluna '{column_name}': {str(e)}")
                        db.session.rollback()
                else:
                    print(f"ℹ Coluna '{column_name}' já existe")
            
            print("✅ Migração concluída com sucesso!")
            
        except Exception as e:
            print(f"✗ Erro na migração: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_user_alert_preferences()
