#!/usr/bin/env python3
"""
Script para consultar a estrutura do banco de dados SQLite
"""
import sqlite3
import os

def consultar_banco():
    db_path = 'C:/agente_agricola_fresh/instance/agente_agricola.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return
    
    print(f"✅ Conectando ao banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        print("\n📋 TABELAS ENCONTRADAS:")
        print("=" * 50)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            print(f"• {table[0]}")
        
        print(f"\nTotal: {len(tables)} tabelas\n")
        
        # Para cada tabela, mostrar a estrutura
        for table in tables:
            table_name = table[0]
            print(f"\n🗂️  ESTRUTURA DA TABELA: {table_name}")
            print("=" * 60)
            
            # Obter informações das colunas
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("Colunas:")
            for col in columns:
                cid, name, col_type, notnull, default_value, pk = col
                null_text = "NOT NULL" if notnull else "NULL"
                pk_text = " (PRIMARY KEY)" if pk else ""
                default_text = f" DEFAULT {default_value}" if default_value else ""
                print(f"  - {name}: {col_type} {null_text}{default_text}{pk_text}")
            
            # Obter chaves estrangeiras
            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            foreign_keys = cursor.fetchall()
            
            if foreign_keys:
                print("Chaves Estrangeiras:")
                for fk in foreign_keys:
                    id_fk, seq, table_ref, from_col, to_col, on_update, on_delete, match = fk
                    print(f"  - {from_col} -> {table_ref}.{to_col}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"Registros: {count}")
            
            print("-" * 60)
        
        conn.close()
        print("\n✅ Consulta concluída!")
        
    except Exception as e:
        print(f"❌ Erro ao consultar banco: {e}")

if __name__ == "__main__":
    consultar_banco()
