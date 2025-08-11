#!/usr/bin/env python3
"""
Servidor Flask em modo desenvolvimento limpo
"""
import os
import sys

# Configurar ambiente ANTES de importar a aplicação
os.environ['FLASK_ENV'] = 'development_clean'
os.environ['FLASK_DEBUG'] = '1'
os.environ['DISABLE_PERFORMANCE_MONITORING'] = 'true'
os.environ['DISABLE_METRICS_COLLECTION'] = 'true'
os.environ['DISABLE_HEALTH_CHECKS'] = 'true'

def create_clean_app():
    """Criar aplicação com configuração limpa"""
    from app import create_app
    
    # Usar configuração limpa
    app = create_app('development_clean')
    
    return app

if __name__ == '__main__':
    print("🧹 Iniciando servidor Flask em modo DESENVOLVIMENTO LIMPO...")
    print("📍 Logs reduzidos, monitoramento desabilitado")
    print("🚀 Servidor será executado em http://localhost:5000")
    print("=" * 60)
    
    try:
        app = create_clean_app()
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Evitar processos duplicados
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar servidor: {e}")
        sys.exit(1)
