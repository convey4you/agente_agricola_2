#!/usr/bin/env python3
"""
Script de exemplo para gerenciamento do banco de dados via API
Pode ser usado para automação ou operações em lote
"""
import requests
import json
import sys
import getpass
from datetime import datetime

class DatabaseManagerCLI:
    """Cliente CLI para gerenciamento do banco de dados"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.logged_in = False
    
    def login(self, email=None, password=None):
        """Fazer login na aplicação"""
        if not email:
            email = input("Email: ")
        if not password:
            password = getpass.getpass("Senha: ")
        
        try:
            # Primeiro, obter o token CSRF
            response = self.session.get(f"{self.base_url}/auth/login")
            
            # Fazer login
            login_data = {
                'email': email,
                'password': password
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", data=login_data)
            
            if response.status_code == 200:
                self.logged_in = True
                print("✅ Login realizado com sucesso!")
                return True
            else:
                print(f"❌ Erro no login: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    def get_database_info(self):
        """Obter informações do banco de dados"""
        if not self.logged_in:
            print("❌ Faça login primeiro")
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/monitoring/database/info")
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"❌ Erro ao obter informações: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return None
    
    def validate_database(self):
        """Validar integridade do banco"""
        if not self.logged_in:
            print("❌ Faça login primeiro")
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/monitoring/database/validate")
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"❌ Erro na validação: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return None
    
    def create_backup(self, backup_name=None):
        """Criar backup do banco"""
        if not self.logged_in:
            print("❌ Faça login primeiro")
            return None
        
        try:
            data = {}
            if backup_name:
                data['backup_name'] = backup_name
            
            response = self.session.post(
                f"{self.base_url}/monitoring/database/backup",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                print(f"❌ Erro no backup: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return None
    
    def reset_database(self, create_backup=True):
        """OPERAÇÃO CRÍTICA: Reset completo do banco"""
        if not self.logged_in:
            print("❌ Faça login primeiro")
            return None
        
        # Confirmação de segurança
        print("\n" + "="*60)
        print("🚨 OPERAÇÃO CRÍTICA: RESET COMPLETO DO BANCO DE DADOS")
        print("="*60)
        print("⚠️  ESTA OPERAÇÃO IRÁ:")
        print("   • Remover TODAS as tabelas")
        print("   • Apagar TODOS os dados")
        print("   • Recriar estrutura vazia")
        print("   • NÃO PODE SER DESFEITA")
        print("="*60)
        
        confirmation = input("\nDigite 'CONFIRMO_RESET_COMPLETO' para continuar: ")
        if confirmation != 'CONFIRMO_RESET_COMPLETO':
            print("❌ Operação cancelada")
            return None
        
        final_confirm = input("\nTem certeza absoluta? Digite 'SIM': ")
        if final_confirm != 'SIM':
            print("❌ Operação cancelada")
            return None
        
        try:
            data = {
                'confirmation': 'RESET_DATABASE_CONFIRM',
                'create_backup': create_backup
            }
            
            print(f"\n⏳ Iniciando reset do banco... (backup: {'sim' if create_backup else 'não'})")
            
            response = self.session.post(
                f"{self.base_url}/monitoring/database/reset",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                print(f"❌ Erro no reset: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Detalhes: {error_data.get('error', 'Erro desconhecido')}")
                except:
                    pass
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return None
    
    def sync_schema(self):
        """Sincronizar schema do banco - operação segura"""
        if not self.logged_in:
            print("❌ É necessário fazer login primeiro")
            return
        
        try:
            print("🔄 Sincronizando schema do banco de dados...")
            print("ℹ️ Operação segura - não remove dados existentes")
            
            # Confirmar operação
            confirm = input("Continuar com a sincronização? (s/N): ").strip().lower()
            if confirm not in ['s', 'sim', 'y', 'yes']:
                print("❌ Operação cancelada")
                return
            
            response = self.session.post(f"{self.base_url}/monitoring/database/sync-schema")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Schema sincronizado com sucesso!")
                    
                    # Mostrar detalhes
                    report = data.get('data', {}).get('report', {})
                    new_tables = report.get('new_tables', [])
                    updated_tables = report.get('updated_tables', [])
                    
                    if new_tables:
                        print(f"📋 Tabelas criadas: {', '.join(new_tables)}")
                    
                    if updated_tables:
                        for table_info in updated_tables:
                            table_name = table_info['table']
                            new_columns = table_info['new_columns']
                            print(f"🔄 Tabela '{table_name}': adicionados {len(new_columns)} campos ({', '.join(new_columns)})")
                    
                    if not new_tables and not updated_tables:
                        print("ℹ️ Schema já estava atualizado - nenhuma alteração necessária")
                        
                else:
                    error_msg = data.get('message', 'Erro desconhecido')
                    print(f"❌ Erro na sincronização: {error_msg}")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro na sincronização: {e}")


def main():
    """Função principal do CLI"""
    if len(sys.argv) < 2:
        print("Uso: python database_cli.py <comando> [opções]")
        print("\nComandos disponíveis:")
        print("  info          - Informações do banco")
        print("  validate      - Validar integridade")
        print("  backup        - Criar backup")
        print("  sync          - Sincronizar schema (seguro)")
        print("  reset         - Reset completo (CUIDADO!)")
        print("\nExemplos:")
        print("  python database_cli.py info")
        print("  python database_cli.py sync")
        print("  python database_cli.py backup")
        print("  python database_cli.py reset")
        return
    
    command = sys.argv[1].lower()
    
    # Inicializar cliente
    client = DatabaseManagerCLI()
    
    # Fazer login
    print("🔐 Fazendo login...")
    if not client.login(email="admin@agrotech.pt"):
        print("❌ Falha no login. Verifique as credenciais.")
        return
    
    # Executar comando
    if command == "info":
        print("\n📊 Obtendo informações do banco...")
        result = client.get_database_info()
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "validate":
        print("\n🔍 Validando banco de dados...")
        result = client.validate_database()
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "backup":
        backup_name = f"cli_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n💾 Criando backup: {backup_name}...")
        result = client.create_backup(backup_name)
        if result:
            print("✅ Backup criado com sucesso!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "sync":
        print("\n🔄 Sincronizando schema do banco...")
        client.sync_schema()
    
    elif command == "reset":
        print("\n🗑️ Iniciando reset do banco...")
        result = client.reset_database(create_backup=True)
        if result:
            print("✅ Reset concluído!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"❌ Comando desconhecido: {command}")


if __name__ == "__main__":
    main()
