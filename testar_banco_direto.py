#!/usr/bin/env python3
"""
Teste direto no banco SQLite
"""

import sqlite3
import os

def testar_banco_direto():
    """Teste direto no banco SQLite"""
    print("🔍 TESTE DIRETO NO BANCO SQLite")
    print("=" * 50)
    
    # Caminho do banco conforme .env
    db_path = "instance/agente_agricola.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    print(f"✅ Banco encontrado: {db_path}")
    print(f"📊 Tamanho: {os.path.getsize(db_path)} bytes")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(culture_types)")
        columns = cursor.fetchall()
        print(f"\n📋 Colunas da tabela culture_types:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Contar total de registros
        cursor.execute("SELECT COUNT(*) FROM culture_types")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total de registros: {total}")
        
        # Listar todos os registros
        cursor.execute("SELECT id, name, category FROM culture_types")
        all_records = cursor.fetchall()
        print(f"\n🌱 Todos os registros:")
        for record in all_records:
            print(f"   ID {record[0]}: '{record[1]}' ({record[2]})")
        
        # Buscar especificamente por espinafre
        print(f"\n🔍 Buscando 'espinafre':")
        
        # Busca exata
        cursor.execute("SELECT * FROM culture_types WHERE name = 'Espinafre'")
        exact = cursor.fetchone()
        print(f"   Busca exata 'Espinafre': {exact[1] if exact else 'Não encontrado'}")
        
        # Busca case insensitive
        cursor.execute("SELECT * FROM culture_types WHERE LOWER(name) = LOWER('espinafre')")
        case_insensitive = cursor.fetchone()
        print(f"   Busca case insensitive: {case_insensitive[1] if case_insensitive else 'Não encontrado'}")
        
        # Busca parcial
        cursor.execute("SELECT * FROM culture_types WHERE LOWER(name) LIKE LOWER('%espinafre%')")
        partial = cursor.fetchone()
        print(f"   Busca parcial '%espinafre%': {partial[1] if partial else 'Não encontrado'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_banco_direto()
