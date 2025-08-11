"""
Script para inicializar Redis localmente para desenvolvimento
"""

import subprocess
import sys
import os
import time

def check_redis_running():
    """Verifica se Redis está rodando"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis está rodando")
        return True
    except:
        print("❌ Redis não está rodando")
        return False

def install_redis_windows():
    """Instala Redis no Windows via Chocolatey ou manual"""
    print("📦 Tentando instalar Redis no Windows...")
    
    # Tentar via Chocolatey primeiro
    try:
        result = subprocess.run(['choco', 'install', 'redis-64', '-y'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Redis instalado via Chocolatey")
            return True
    except FileNotFoundError:
        print("⚠️ Chocolatey não encontrado")
    
    # Instruções manuais
    print("""
    📋 Para instalar Redis manualmente no Windows:
    
    1. Baixe Redis para Windows:
       https://github.com/tporadowski/redis/releases
    
    2. Extraia e execute redis-server.exe
    
    3. Ou use Docker:
       docker run --name redis -p 6379:6379 -d redis:alpine
    
    4. Ou use WSL:
       sudo apt update && sudo apt install redis-server
       sudo service redis-server start
    """)
    return False

def start_redis_service():
    """Tenta iniciar o serviço Redis"""
    print("🚀 Tentando iniciar Redis...")
    
    # Tentar iniciar serviço Windows
    try:
        result = subprocess.run(['net', 'start', 'Redis'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Serviço Redis iniciado")
            return True
    except:
        pass
    
    # Tentar executar redis-server diretamente
    try:
        # Verificar se redis-server está no PATH
        result = subprocess.run(['redis-server', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("🔄 Iniciando redis-server...")
            # Iniciar em background
            subprocess.Popen(['redis-server'])
            time.sleep(2)
            return check_redis_running()
    except FileNotFoundError:
        print("❌ redis-server não encontrado no PATH")
    
    return False

def setup_redis_for_development():
    """Configura Redis para desenvolvimento"""
    print("🔧 Configurando Redis para desenvolvimento AgroTech Portugal...")
    
    # Verificar se já está rodando
    if check_redis_running():
        return True
    
    # Tentar iniciar serviço
    if start_redis_service():
        return True
    
    # Tentar instalar se não encontrado
    if sys.platform == "win32":
        install_redis_windows()
    
    # Verificar novamente
    if check_redis_running():
        return True
    
    print("""
    ⚠️ Redis não pôde ser iniciado automaticamente.
    
    🐳 SOLUÇÃO RÁPIDA - Use Docker:
    docker run --name redis-agrotech -p 6379:6379 -d redis:alpine
    
    🔄 Para continuar sem Redis:
    A aplicação funcionará com cache em memória (menos eficiente)
    """)
    
    return False

if __name__ == "__main__":
    setup_redis_for_development()
