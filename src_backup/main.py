#!/usr/bin/env python3
"""
Ponto de entrada principal da aplicação
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar e executar a aplicação
from run import *

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'development')
    
    with app.app_context():
        # Inicializar banco de dados
        db.create_all()
        
        print("🚀 Iniciando Agente Agrícola...")
        print("✅ Banco de dados inicializado")
        print("🌐 Servidor rodando em: http://localhost:5000")
        print("📋 Acesse o dashboard em: http://localhost:5000/")
        print("📡 API disponível em: http://localhost:5000/api/")
        print("⚠️  Para parar: Ctrl+C")
        print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
