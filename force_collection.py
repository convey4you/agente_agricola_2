#!/usr/bin/env python3
"""
Script para forçar coleta imediata de dados climáticos
"""
from app import create_app
from app.services.weather_scheduler import force_collection

def force_weather_collection():
    app = create_app()
    with app.app_context():
        print('=== FORÇANDO COLETA IMEDIATA ===')
        print('🌤️ Iniciando coleta de dados climáticos...')
        
        # Forçar coleta imediata
        result = force_collection()
        
        print(f'\n📊 Resultado da Coleta:')
        print(f'   ✅ Sucesso: {result.get("success", False)}')
        print(f'   📍 Localizações processadas: {result.get("locations_processed", 0)}')
        print(f'   ❌ Localizações falharam: {result.get("locations_failed", 0)}')
        
        if result.get('errors'):
            print(f'   🚨 Erros encontrados:')
            for error in result['errors']:
                print(f'      - {error}')
        
        # Verificar dados coletados
        from app.models.weather_history import WeatherData
        from datetime import datetime, timedelta
        
        print('\n📋 Verificando dados coletados:')
        recent_data = WeatherData.query.order_by(WeatherData.api_timestamp.desc()).limit(10).all()
        
        if recent_data:
            print(f'   ✅ {len(recent_data)} registros encontrados:')
            for data in recent_data:
                time_ago = datetime.utcnow() - data.api_timestamp
                minutes_ago = time_ago.total_seconds() / 60
                temp = f"{data.temperature}°C" if data.temperature else "N/A"
                print(f'      📍 {data.location_name}: {temp} - {minutes_ago:.0f}min atrás')
        else:
            print('   ⚠️ Nenhum dado encontrado após coleta')
        
        print(f'\n🕐 Timestamp da coleta: {result.get("timestamp", "N/A")}')

if __name__ == '__main__':
    force_weather_collection()
