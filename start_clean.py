#!/usr/bin/env python3
"""
Script para reiniciar o servidor Flask de forma limpa
"""
import os
import sys
import subprocess
import time

def kill_python_processes():
    """Finalizar todos os processos Python em execução"""
    try:
        # No Windows, usar taskkill
        result = subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                              capture_output=True, text=True)
        print(f"Processos Python finalizados: {result.returncode}")
        time.sleep(2)
    except Exception as e:
        print(f"Erro ao finalizar processos: {e}")

def start_clean_server():
    """Iniciar servidor com configuração limpa"""
    print("🧹 Limpando processos anteriores...")
    kill_python_processes()
    
    print("🚀 Iniciando servidor Flask limpo...")
    
    # Configurar ambiente para desenvolvimento
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    os.environ['DISABLE_PERFORMANCE_MONITORING'] = 'true'
    
    # Executar servidor
    try:
        subprocess.run([
            sys.executable, 'run.py'
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar servidor: {e}")

if __name__ == "__main__":
    start_clean_server()
