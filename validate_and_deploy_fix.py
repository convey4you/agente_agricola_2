#!/usr/bin/env python3
"""
Script para validar e fazer deploy do fix da coluna location
"""

import os
import sqlite3

def validate_migration_fix():
    """Validar que o migration fix está correto"""
    print("🔍 Validando migration fix da coluna location...")
    
    # 1. Verificar se o arquivo de migration existe
    migration_file = 'migrations/versions/fix_user_location_20250802_add_missing_user_location_column.py'
    if not os.path.exists(migration_file):
        print(f"❌ Migration fix não encontrado: {migration_file}")
        return False
    
    print(f"✅ Migration fix encontrado: {migration_file}")
    
    # 2. Verificar versão do alembic
    try:
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT version_num FROM alembic_version LIMIT 1;")
        version = cursor.fetchone()
        
        if version and version[0] == 'fix_user_location_20250802':
            print(f"✅ Versão do alembic correta: {version[0]}")
        else:
            print(f"❌ Versão do alembic incorreta: {version[0] if version else 'Nenhuma'}")
            return False
            
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao verificar versão: {e}")
        return False
    
    # 3. Verificar se coluna location existe localmente
    try:
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        
        location_exists = any(col[1] == 'location' for col in columns)
        if location_exists:
            print("✅ Coluna 'location' existe no SQLite local")
        else:
            print("❌ Coluna 'location' não existe no SQLite local")
            return False
            
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao verificar coluna: {e}")
        return False
    
    return True

def create_deploy_summary():
    """Criar resumo do que será deployado"""
    print("\n📋 RESUMO DO DEPLOY:")
    print("=" * 50)
    print("🎯 Problema: Coluna 'users.location' não existe no PostgreSQL Railway")
    print("🔧 Solução: Migration para adicionar coluna faltante")
    print("📄 Migration: fix_user_location_20250802_add_missing_user_location_column.py")
    print("⚡ Versão: fix_user_location_20250802")
    print("\n🚀 O que acontecerá no Railway:")
    print("  1. Executa deploy() automaticamente")
    print("  2. Aplica migration fix_user_location_20250802")
    print("  3. Adiciona coluna 'location VARCHAR(200)' na tabela users")
    print("  4. Aplicação funciona corretamente")
    print("=" * 50)

def main():
    """Função principal"""
    print("🚀 VALIDAÇÃO E DEPLOY - FIX COLUNA LOCATION")
    print("=" * 60)
    
    if validate_migration_fix():
        print("\n✅ TODAS AS VALIDAÇÕES PASSARAM!")
        create_deploy_summary()
        
        print("\n🎯 COMANDOS PARA DEPLOY:")
        print("git add .")
        print('git commit -m "fix: Adicionar coluna location faltante na tabela users"')
        print("git push origin main")
        
        print("\n🎉 Após o push, Railway irá:")
        print("  ✅ Aplicar o migration automaticamente")
        print("  ✅ Adicionar a coluna location")
        print("  ✅ Resolver o erro 503")
        print("  ✅ Aplicação funcionará corretamente")
        
    else:
        print("\n❌ VALIDAÇÕES FALHARAM!")
        print("🔧 Corrija os problemas antes do deploy")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
