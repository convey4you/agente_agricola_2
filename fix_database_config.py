#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir problema de duplicação de banco de dados
"""
import os
import sys
from pathlib import Path

def check_database_configuration():
    """Verificar configuração do banco de dados"""
    
    print("🔍 DIAGNÓSTICO - Configuração do Banco de Dados")
    print("=" * 60)
    
    # 1. Verificar variável de ambiente
    print("1. Verificando variável DATABASE_URL:")
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print(f"   ✅ DATABASE_URL encontrada: {database_url}")
    else:
        print("   ❌ DATABASE_URL NÃO encontrada no ambiente")
    
    # 2. Verificar arquivo .env
    print("\n2. Verificando arquivo .env:")
    env_file = Path('.env')
    if env_file.exists():
        print("   ✅ Arquivo .env existe")
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
            if 'DATABASE_URL=' in env_content:
                env_lines = [line for line in env_content.split('\n') if line.startswith('DATABASE_URL=')]
                for line in env_lines:
                    print(f"   📄 {line}")
            else:
                print("   ❌ DATABASE_URL não encontrada no .env")
    else:
        print("   ❌ Arquivo .env não existe")
    
    # 3. Verificar arquivos de banco existentes
    print("\n3. Verificando arquivos de banco existentes:")
    
    # Banco na raiz
    root_db = Path('agente_agricola.db')
    if root_db.exists():
        size = root_db.stat().st_size
        print(f"   ⚠️  BANCO NA RAIZ encontrado: {root_db} ({size} bytes)")
    else:
        print("   ✅ Nenhum banco na raiz")
    
    # Banco na instance
    instance_db = Path('instance/agente_agricola.db')
    if instance_db.exists():
        size = instance_db.stat().st_size
        print(f"   ✅ Banco na instance encontrado: {instance_db} ({size} bytes)")
    else:
        print("   ❌ Banco na instance NÃO encontrado")
    
    # 4. Verificar configuração do Flask
    print("\n4. Verificando configuração do Flask:")
    try:
        # Configurar ambiente primeiro
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_CONFIG'] = 'development'
        
        sys.path.insert(0, os.path.abspath('.'))
        from app import create_app
        
        app = create_app()
        with app.app_context():
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
            print(f"   📊 SQLALCHEMY_DATABASE_URI: {db_uri}")
            
            if 'instance' in db_uri:
                print("   ✅ Configuração aponta para pasta instance")
            else:
                print("   ❌ Configuração NÃO aponta para pasta instance")
                
    except Exception as e:
        print(f"   ❌ Erro ao verificar configuração Flask: {e}")
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DO PROBLEMA:")
    print()
    
    # Análise do problema
    if not database_url and root_db.exists():
        print("🔍 CAUSA PROVÁVEL:")
        print("   - DATABASE_URL não está sendo carregada do .env")
        print("   - Flask usa fallback que cria banco na raiz")
        print("   - Scripts criam banco onde a configuração manda")
        
        print("\n💡 SOLUÇÕES RECOMENDADAS:")
        print("   1. Verificar se python-dotenv está instalado")
        print("   2. Garantir que .env é carregado antes de create_app()")
        print("   3. Usar caminho absoluto no DATABASE_URL")
        print("   4. Remover banco duplicado da raiz (após backup)")
    
    return database_url, root_db.exists(), instance_db.exists()

def fix_database_configuration():
    """Corrigir configuração do banco"""
    
    print("\n🔧 APLICANDO CORREÇÕES...")
    
    # 1. Garantir que .env tem a configuração correta
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Garantir que DATABASE_URL está correto
        instance_path = os.path.abspath('instance/agente_agricola.db')
        correct_db_url = f"sqlite:///{instance_path}"
        
        if 'DATABASE_URL=' in content:
            # Substituir DATABASE_URL existente
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('DATABASE_URL='):
                    lines[i] = f"DATABASE_URL={correct_db_url}"
                    break
            content = '\n'.join(lines)
        else:
            # Adicionar DATABASE_URL
            content += f"\nDATABASE_URL={correct_db_url}\n"
        
        # Salvar .env corrigido
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ .env atualizado com DATABASE_URL correto")
        print(f"   📍 Novo DATABASE_URL: {correct_db_url}")
    
    # 2. Garantir que pasta instance existe
    instance_dir = Path('instance')
    if not instance_dir.exists():
        instance_dir.mkdir(exist_ok=True)
        print("   ✅ Pasta instance criada")
    
    print("\n✅ Correções aplicadas!")
    print("\n📝 PRÓXIMOS PASSOS:")
    print("   1. Reiniciar aplicação Flask")
    print("   2. Verificar se novos scripts usam banco correto")
    print("   3. Remover banco da raiz (após confirmar que instance funciona)")

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de configuração do banco...")
    
    database_url, has_root_db, has_instance_db = check_database_configuration()
    
    if not database_url or has_root_db:
        print("\n❓ Deseja aplicar correções automáticas? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes', 's', 'sim']:
                fix_database_configuration()
            else:
                print("   ℹ️  Correções não aplicadas")
        except KeyboardInterrupt:
            print("\n   ℹ️  Operação cancelada")
    else:
        print("\n✅ Configuração parece estar correta!")
    
    print("\n🎉 Diagnóstico concluído!")
