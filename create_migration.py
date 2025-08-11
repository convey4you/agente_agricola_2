#!/usr/bin/env python3
"""
Script para criar migration para sincronizar com Railway
"""

import os
import sys
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

# Definir variáveis de ambiente necessárias
os.environ['FLASK_APP'] = 'run.py'
os.environ['FLASK_ENV'] = 'development'

try:
    from app import create_app, db
    from flask_migrate import Migrate, init, migrate, upgrade
    
    def create_migration():
        """Criar migration para sincronização com Railway"""
        app = create_app('development')
        
        with app.app_context():
            try:
                # Verificar se migrations está inicializado
                if not os.path.exists('migrations'):
                    print("Inicializando sistema de migrations...")
                    init()
                
                # Gerar migration
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                message = f"Sincronizacao Railway {timestamp}"
                
                print(f"Gerando migration: {message}")
                
                # Usar o comando direto do alembic
                from flask_migrate import migrate as flask_migrate
                flask_migrate(message=message)
                
                print("✅ Migration gerado com sucesso!")
                print("📋 Para aplicar no Railway, faça commit e push das alterações")
                
            except Exception as e:
                print(f"❌ Erro ao gerar migration: {e}")
                return False
                
        return True
    
    if __name__ == '__main__':
        create_migration()
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Execute este script no ambiente virtual ativado")
