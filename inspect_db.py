#!/usr/bin/env python3
"""Script para inspecionar estrutura das tabelas do banco"""

import os
from dotenv import load_dotenv
import sqlite3

# Carregar .env
load_dotenv()

# Conectar diretamente ao SQLite para ver a estrutura
db_path = "C:/agente_agricola_fresh/instance/agente_agricola.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== ESTRUTURA DAS TABELAS ===\n")
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"📋 TABELA: {table_name}")
        
        # Ver estrutura da tabela
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        for col in columns:
            col_id, name, type_name, not_null, default, pk = col
            pk_mark = " (PK)" if pk else ""
            null_mark = " NOT NULL" if not_null else ""
            default_mark = f" DEFAULT {default}" if default else ""
            print(f"  - {name}: {type_name}{pk_mark}{null_mark}{default_mark}")
        
        # Ver dados de exemplo se existirem
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"  📊 Registros: {count}")
        
        if count > 0 and table_name in ['users', 'farms', 'cultures']:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 2;")
            rows = cursor.fetchall()
            if rows:
                print("  🔍 Exemplo de dados:")
                for i, row in enumerate(rows, 1):
                    print(f"    {i}. {row}")
        
        print()
    
    conn.close()
    
except Exception as e:
    print(f"Erro ao conectar ao banco: {e}")
    import traceback
    traceback.print_exc()
