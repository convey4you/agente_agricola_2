"""
Ponto de entrada da aplicação Flask - AgroTech 1.0
Configurado para deployment em Railway e desenvolvimento local
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar logs reduzidos para desenvolvimento
if os.getenv('FLASK_ENV') == 'development' or os.getenv('FLASK_DEBUG') == '1':
    from dev_logging_config import setup_dev_logging
    setup_dev_logging()

from app import create_app, db
from flask_migrate import upgrade


def deploy():
    """Executar tarefas de deploy"""
    # Criar aplicação
    app = create_app(os.getenv('FLASK_CONFIG') or 'production')
    
    with app.app_context():
        # CORREÇÃO CRÍTICA: Adicionar colunas faltantes na tabela alerts
        try:
            print("🔧 Aplicando correção crítica da tabela alerts...")
            from sqlalchemy import text
            
            migration_queries = [
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS action_text VARCHAR(100);",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS action_url VARCHAR(500);", 
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS location_data TEXT;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS weather_data TEXT;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS alert_metadata TEXT;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS scheduled_for TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS sent_at TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS read_at TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS dismissed_at TIMESTAMP;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS delivery_channels VARCHAR(100) DEFAULT 'web';",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;",
                "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS last_retry_at TIMESTAMP;"
            ]
            
            for i, query in enumerate(migration_queries, 1):
                try:
                    db.session.execute(text(query))
                    db.session.commit()
                    print(f"✅ Coluna {i}/13 adicionada com sucesso")
                except Exception as e:
                    print(f"ℹ️ Coluna {i}/13 já existe ou erro: {e}")
                    db.session.rollback()
            
            print("✅ Correção da tabela alerts concluída!")
            
        except Exception as e:
            print(f"⚠️ Erro na correção da tabela alerts: {e}")
        
        # SQLite: Inicialização simples sem migrações complexas
        try:
            print("🔧 Inicializando banco SQLite...")
            db.create_all()
            print("✅ Banco SQLite inicializado com sucesso!")
            
        except Exception as e:
            print(f"⚠️ Erro na inicialização SQLite: {e}")
        
        # CORREÇÃO: Forçar estrutura completa do banco
        try:
            from fix_railway_structure import create_complete_migration
            if create_complete_migration():
                print("✅ Estrutura do banco corrigida")
            else:
                print("⚠️  Falha ao corrigir estrutura - tentando alternativas")
        except Exception as e:
            print(f"⚠️  Erro no fix de estrutura: {e}")
        
        # Executar migrações se existirem
        try:
            upgrade()
            print("✅ Migrações aplicadas com sucesso")
        except Exception as e:
            print(f"⚠️  Migrações não aplicadas: {e}")
            # Criar tabelas se migrações falharem
            try:
                db.create_all()
                print("✅ Tabelas criadas com db.create_all()")
            except Exception as e2:
                print(f"❌ Erro ao criar tabelas: {e2}")


if __name__ == '__main__':
    # Determinar configuração baseada no ambiente
    config_name = os.getenv('FLASK_ENV', 'development')
    if config_name == 'production':
        config_name = 'production'
    
    app = create_app(config_name)
    
    with app.app_context():
        # CORREÇÃO CRÍTICA PARA PRODUÇÃO: Adicionar colunas faltantes
        if config_name == 'production':
            try:
                print("🔧 Aplicando correção crítica para produção...")
                from sqlalchemy import text
                
                critical_fixes = [
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS action_text VARCHAR(100);",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS action_url VARCHAR(500);",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS location_data TEXT;",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS weather_data TEXT;",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS alert_metadata TEXT;",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS scheduled_for TIMESTAMP;",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS sent_at TIMESTAMP;",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS read_at TIMESTAMP;",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS dismissed_at TIMESTAMP;",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS delivery_channels VARCHAR(100) DEFAULT 'web';",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;",
                    "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS last_retry_at TIMESTAMP;"
                ]
                
                for query in critical_fixes:
                    try:
                        db.session.execute(text(query))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
                        
                print("✅ Correção crítica aplicada com sucesso!")
                
            except Exception as e:
                print(f"⚠️ Erro na correção crítica: {e}")
        
        # Inicializar banco de dados
        db.create_all()
        
        if config_name == 'development':
            print("🚀 Iniciando Agente Agrícola...")
            print("✅ Banco de dados inicializado")
            print("🌐 Servidor rodando em: http://localhost:5000")
            print("📋 Acesse o dashboard em: http://localhost:5000/")
            print("📡 API disponível em: http://localhost:5000/api/")
            print("⚠️  Para parar: Ctrl+C")
            print("=" * 50)
        else:
            print("🐘 Ambiente de produção - PostgreSQL")
            print("✅ Banco de dados inicializado")
    
    # Configurações de servidor
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = config_name == 'development'
    
    app.run(host=host, port=port, debug=debug)
