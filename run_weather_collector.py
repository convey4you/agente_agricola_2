#!/usr/bin/env python3
"""
Script para executar coleta de dados climáticos
"""
from app import create_app
from app.services.weather_collector import WeatherCollectorService
import os

app = create_app()
with app.app_context():
    # Verificar se há chave de API configurada
    api_key = app.config.get('WEATHER_API_KEY')
    print(f'🔑 Chave API configurada: {"Sim" if api_key else "Não"}')
    
    if api_key:
        print(f'🔍 Chave API (primeiros 8 chars): {api_key[:8]}...')
    
    # Verificar variáveis de ambiente
    env_key = os.getenv('WEATHER_API_KEY')
    print(f'🌍 Variável de ambiente WEATHER_API_KEY: {"Sim" if env_key else "Não"}')
    
    print("\n" + "="*50)
    print("🌤️ EXECUTANDO COLETA DE DADOS CLIMÁTICOS")
    print("="*50)
    
    # Verificar status atual
    print("\n📊 Status atual da coleta:")
    status = WeatherCollectorService.get_collection_status()
    print(f"   Status: {status['status']}")
    print(f"   Mensagem: {status['message']}")
    print(f"   Última coleta: {status.get('last_collection', 'Nunca')}")
    print(f"   Localizações com dados: {status.get('locations_with_data', 0)}")
    
    # Executar coleta forçada
    print("\n🔄 Iniciando coleta forçada...")
    try:
        result = WeatherCollectorService.force_collection_now()
        
        print(f"\n✅ Resultado da coleta:")
        print(f"   Sucesso: {result['success']}")
        print(f"   Localizações processadas: {result['locations_processed']}")
        print(f"   Localizações com falha: {result['locations_failed']}")
        print(f"   Timestamp: {result['timestamp']}")
        
        if result['errors']:
            print(f"\n❌ Erros encontrados:")
            for error in result['errors']:
                print(f"   - {error}")
        
        # Status após coleta
        print("\n📊 Status após coleta:")
        status_after = WeatherCollectorService.get_collection_status()
        print(f"   Status: {status_after['status']}")
        print(f"   Mensagem: {status_after['message']}")
        print(f"   Última coleta: {status_after.get('last_collection', 'Nunca')}")
        print(f"   Localizações com dados: {status_after.get('locations_with_data', 0)}")
        
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        import traceback
        traceback.print_exc()
