#!/usr/bin/env python3
"""
Migração para adicionar colunas created_at e updated_at às tabelas weather
"""

from app import create_app, db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def add_timestamp_columns():
    """Adiciona colunas de timestamp às tabelas weather"""
    
    app = create_app()
    with app.app_context():
        try:
            print("🔄 Iniciando migração das tabelas weather...")
            
            # Verificar se as colunas já existem
            inspector = db.inspect(db.engine)
            weather_data_columns = [col['name'] for col in inspector.get_columns('weather_data')]
            weather_stats_columns = [col['name'] for col in inspector.get_columns('weather_stats')]
            
            print(f"📋 Colunas atuais em weather_data: {len(weather_data_columns)}")
            print(f"📋 Colunas atuais em weather_stats: {len(weather_stats_columns)}")
            
            # Adicionar colunas à tabela weather_data
            if 'created_at' not in weather_data_columns:
                print("➕ Adicionando coluna created_at à tabela weather_data...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE weather_data ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP'))
                    conn.commit()
                print("✅ Coluna created_at adicionada à weather_data")
            else:
                print("✅ Coluna created_at já existe em weather_data")
                
            if 'updated_at' not in weather_data_columns:
                print("➕ Adicionando coluna updated_at à tabela weather_data...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE weather_data ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP'))
                    conn.commit()
                print("✅ Coluna updated_at adicionada à weather_data")
            else:
                print("✅ Coluna updated_at já existe em weather_data")
            
            # Adicionar coluna updated_at à tabela weather_stats (created_at já existe)
            if 'updated_at' not in weather_stats_columns:
                print("➕ Adicionando coluna updated_at à tabela weather_stats...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE weather_stats ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP'))
                    conn.commit()
                print("✅ Coluna updated_at adicionada à weather_stats")
            else:
                print("✅ Coluna updated_at já existe em weather_stats")
            
            # Atualizar registros existentes com timestamps atuais
            current_time = datetime.utcnow()
            
            print("🔄 Atualizando registros existentes...")
            
            # Atualizar weather_data onde created_at é NULL
            with db.engine.connect() as conn:
                if 'created_at' not in weather_data_columns:  # Se acabou de ser adicionada
                    result = conn.execute(
                        db.text('UPDATE weather_data SET created_at = :time WHERE created_at IS NULL'),
                        {'time': current_time}
                    )
                    print(f"✅ Atualizados {result.rowcount} registros em weather_data com created_at")
                
                if 'updated_at' not in weather_data_columns:  # Se acabou de ser adicionada
                    result = conn.execute(
                        db.text('UPDATE weather_data SET updated_at = :time WHERE updated_at IS NULL'),
                        {'time': current_time}
                    )
                    print(f"✅ Atualizados {result.rowcount} registros em weather_data com updated_at")
                
                # Atualizar weather_stats onde updated_at é NULL
                if 'updated_at' not in weather_stats_columns:  # Se acabou de ser adicionada
                    result = conn.execute(
                        db.text('UPDATE weather_stats SET updated_at = :time WHERE updated_at IS NULL'),
                        {'time': current_time}
                    )
                    print(f"✅ Atualizados {result.rowcount} registros em weather_stats com updated_at")
                
                conn.commit()
            
            print("\n🎉 Migração concluída com sucesso!")
            
            # Verificar resultado final
            inspector = db.inspect(db.engine)
            weather_data_columns_final = [col['name'] for col in inspector.get_columns('weather_data')]
            weather_stats_columns_final = [col['name'] for col in inspector.get_columns('weather_stats')]
            
            print(f"\n📊 RESULTADO FINAL:")
            print(f"   weather_data: {len(weather_data_columns_final)} colunas")
            print(f"   weather_stats: {len(weather_stats_columns_final)} colunas")
            
            print(f"\n✅ weather_data tem created_at: {'created_at' in weather_data_columns_final}")
            print(f"✅ weather_data tem updated_at: {'updated_at' in weather_data_columns_final}")
            print(f"✅ weather_stats tem created_at: {'created_at' in weather_stats_columns_final}")
            print(f"✅ weather_stats tem updated_at: {'updated_at' in weather_stats_columns_final}")
            
        except Exception as e:
            print(f"❌ Erro durante migração: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_timestamp_columns()
