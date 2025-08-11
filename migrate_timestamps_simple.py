#!/usr/bin/env python3
"""
Migração simplificada para adicionar colunas timestamp
"""

from app import create_app, db
from datetime import datetime

def migrate_timestamps():
    """Adiciona colunas timestamp às tabelas weather"""
    
    app = create_app()
    with app.app_context():
        try:
            print("🔄 Iniciando migração de timestamps...")
            
            # Verificar estrutura atual
            inspector = db.inspect(db.engine)
            weather_data_columns = [col['name'] for col in inspector.get_columns('weather_data')]
            weather_stats_columns = [col['name'] for col in inspector.get_columns('weather_stats')]
            
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
            with db.engine.connect() as conn:
                # weather_data: adicionar created_at
                if 'created_at' not in weather_data_columns:
                    print("➕ Adicionando created_at em weather_data...")
                    conn.execute(db.text('ALTER TABLE weather_data ADD COLUMN created_at DATETIME'))
                    conn.execute(db.text('UPDATE weather_data SET created_at = :time'), {'time': current_time})
                    conn.commit()
                    print("✅ created_at adicionada e preenchida")
                else:
                    print("✅ created_at já existe em weather_data")
                
                # weather_data: adicionar updated_at
                if 'updated_at' not in weather_data_columns:
                    print("➕ Adicionando updated_at em weather_data...")
                    conn.execute(db.text('ALTER TABLE weather_data ADD COLUMN updated_at DATETIME'))
                    conn.execute(db.text('UPDATE weather_data SET updated_at = :time'), {'time': current_time})
                    conn.commit()
                    print("✅ updated_at adicionada e preenchida")
                else:
                    print("✅ updated_at já existe em weather_data")
                
                # weather_stats: adicionar updated_at (created_at já existe)
                if 'updated_at' not in weather_stats_columns:
                    print("➕ Adicionando updated_at em weather_stats...")
                    conn.execute(db.text('ALTER TABLE weather_stats ADD COLUMN updated_at DATETIME'))
                    conn.execute(db.text('UPDATE weather_stats SET updated_at = :time'), {'time': current_time})
                    conn.commit()
                    print("✅ updated_at adicionada e preenchida")
                else:
                    print("✅ updated_at já existe em weather_stats")
            
            # Verificar resultado
            inspector = db.inspect(db.engine)
            weather_data_final = [col['name'] for col in inspector.get_columns('weather_data')]
            weather_stats_final = [col['name'] for col in inspector.get_columns('weather_stats')]
            
            print(f"\n🎉 Migração concluída!")
            print(f"📊 weather_data: {len(weather_data_final)} colunas")
            print(f"📊 weather_stats: {len(weather_stats_final)} colunas")
            
            print(f"\n✅ Verificação final:")
            print(f"   weather_data.created_at: {'created_at' in weather_data_final}")
            print(f"   weather_data.updated_at: {'updated_at' in weather_data_final}")
            print(f"   weather_stats.created_at: {'created_at' in weather_stats_final}")
            print(f"   weather_stats.updated_at: {'updated_at' in weather_stats_final}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    migrate_timestamps()
