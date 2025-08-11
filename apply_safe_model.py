#!/usr/bin/env python3
"""
Script para aplicar modelo User temporário enquanto a migração não é executada
Permite que a aplicação inicie no Railway mesmo sem a coluna interesses
"""

import os
import shutil
from datetime import datetime

def apply_safe_user_model():
    """
    Substitui temporariamente o modelo User por uma versão segura
    """
    print("🔄 Aplicando modelo User temporário...")
    
    try:
        # Fazer backup do modelo original
        original_path = "app/models/user.py"
        backup_path = f"app/models/user_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        safe_path = "app/models/user_safe.py"
        
        if os.path.exists(original_path):
            shutil.copy2(original_path, backup_path)
            print(f"✅ Backup criado: {backup_path}")
        
        if os.path.exists(safe_path):
            shutil.copy2(safe_path, original_path)
            print(f"✅ Modelo seguro aplicado: {original_path}")
            return True
        else:
            print(f"❌ Arquivo {safe_path} não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao aplicar modelo seguro: {e}")
        return False

def restore_original_model():
    """
    Restaura o modelo User original após a migração
    """
    print("🔄 Restaurando modelo User original...")
    
    try:
        # Encontrar o backup mais recente
        backup_files = [f for f in os.listdir("app/models/") if f.startswith("user_backup_")]
        if not backup_files:
            print("❌ Nenhum backup encontrado")
            return False
        
        latest_backup = sorted(backup_files)[-1]
        backup_path = f"app/models/{latest_backup}"
        original_path = "app/models/user.py"
        
        shutil.copy2(backup_path, original_path)
        print(f"✅ Modelo original restaurado de: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao restaurar modelo: {e}")
        return False

def main():
    """Função principal"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        success = restore_original_model()
    else:
        success = apply_safe_user_model()
    
    if success:
        print("✅ Operação concluída com sucesso!")
    else:
        print("❌ Operação falhou")
        sys.exit(1)

if __name__ == "__main__":
    main()
