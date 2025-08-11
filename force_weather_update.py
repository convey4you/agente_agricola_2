#!/usr/bin/env python3
"""
Forçar atualização dos dados de clima e verificar logs
"""
import requests
import json

def force_weather_update():
    """Forçar atualização do clima e verificar logs"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("=== FORÇAR ATUALIZAÇÃO CLIMA ===\n")
    
    # 1. Login
    print("1. Fazendo login...")
    login_data = {
        'email': 'francismarquesrosa@gmail.com',
        'password': 'f100676'
    }
    
    response = session.post(f"{base_url}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"✗ Erro no login: {response.status_code}")
        return
    print("✓ Login OK!")
    
    # 2. Forçar refresh
    print("\n2. Forçando refresh dos dados...")
    headers = {'Accept': 'application/json'}
    
    refresh_response = session.get(f"{base_url}/weather/refresh", headers=headers)
    print(f"Status refresh: {refresh_response.status_code}")
    print(f"Content-Type: {refresh_response.headers.get('content-type')}")
    
    if refresh_response.status_code == 200:
        try:
            refresh_data = refresh_response.json()
            print(f"Refresh result: {refresh_data}")
        except Exception as e:
            print(f"Refresh HTML response: {refresh_response.text[:200]}")
    
    # 3. Testar endpoint de teste de API
    print("\n3. Testando endpoint de teste...")
    
    test_response = session.get(f"{base_url}/weather/test", headers=headers)
    print(f"Status test: {test_response.status_code}")
    
    if test_response.status_code == 200:
        try:
            test_data = test_response.json()
            print(f"Test result: {json.dumps(test_data, indent=2)}")
            
            if test_data.get('success'):
                print("✅ API teste funcionou")
                if test_data.get('data'):
                    data = test_data['data']
                    print(f"Dados obtidos: {data.get('name')}, {data['main']['temp']}°C")
            else:
                print(f"❌ API teste falhou: {test_data.get('error')}")
                
        except Exception as e:
            print(f"Erro no teste: {e}")
    
    # 4. Verificar dados após refresh
    print("\n4. Verificando dados após operações...")
    
    weather_response = session.get(f"{base_url}/api/dashboard/weather", headers=headers)
    if weather_response.status_code == 200:
        try:
            weather_data = weather_response.json()
            weather = weather_data.get('weather', {})
            current = weather.get('current', {})
            
            print(f"Temperatura atual: {current.get('temperature')}°C")
            print(f"Condição: {current.get('condition')}")
            print(f"É mock? {current.get('mock', False)}")
            print(f"Cached? {current.get('cached', False)}")
            
        except Exception as e:
            print(f"Erro ao verificar dados: {e}")

if __name__ == "__main__":
    force_weather_update()
