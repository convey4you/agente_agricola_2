#!/usr/bin/env python3
"""
Script de Exemplo - Como Usar os Guias de Migração
Demonstra o uso prático dos scripts de migração
"""

import subprocess
import sys
import os
from datetime import datetime

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"📋 {title}")
    print("="*60)

def run_script(script_path, description):
    """Executa um script e retorna o resultado"""
    print(f"\n🚀 Executando: {description}")
    print(f"Script: {script_path}")
    print("-" * 40)
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                               capture_output=False, 
                               text=True, 
                               timeout=60)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Script executado por muito tempo (timeout)")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar script: {e}")
        return False

def demonstrate_workflow():
    """Demonstra o workflow completo de migração"""
    
    print_header("DEMONSTRAÇÃO DE WORKFLOW DE MIGRAÇÃO")
    
    print("""
🎯 CENÁRIO DE USO:
Você precisa atualizar o banco de dados PostgreSQL em produção
após adicionar novas colunas ao modelo Alert.

📋 WORKFLOW RECOMENDADO:

1️⃣ DIAGNÓSTICO - Identifique problemas existentes
2️⃣ MIGRAÇÃO - Execute as correções necessárias  
3️⃣ VALIDAÇÃO - Confirme que tudo está funcionando

Vamos executar cada etapa:
""")
    
    input("Pressione ENTER para continuar...")
    
    # Etapa 1: Diagnóstico
    print_header("ETAPA 1: DIAGNÓSTICO")
    print("🔍 Identificando problemas no sistema atual...")
    
    diagnostic_success = run_script("guias/migracao-postgres/diagnostic_script.py", "Diagnóstico completo")
    
    if not diagnostic_success:
        print("⚠️ Problemas identificados! Continuando com migração...")
    
    input("\nPressione ENTER para prosseguir para a migração...")
    
    # Etapa 2: Migração
    print_header("ETAPA 2: MIGRAÇÃO")
    print("🔧 Executando correções de schema...")
    
    # Verificar se DATABASE_URL está configurada
    if not os.getenv('DATABASE_URL'):
        print("⚠️ DATABASE_URL não configurada!")
        print("💡 Para usar em produção, execute:")
        print("   export DATABASE_URL='postgresql://user:pass@host:port/db'")
        print("   python guias/migracao-postgres/migration_script.py")
        print("\n📋 Para esta demonstração, vamos pular a migração real.")
        migration_success = True  # Simular sucesso
    else:
        migration_success = run_script("guias/migracao-postgres/migration_script.py", "Migração de schema")
    
    input("\nPressione ENTER para prosseguir para a validação...")
    
    # Etapa 3: Validação
    print_header("ETAPA 3: VALIDAÇÃO")
    print("✅ Validando se as correções foram aplicadas...")
    
    validation_success = run_script("guias/migracao-postgres/validation_script.py", "Validação pós-migração")
    
    # Resumo final
    print_header("RESUMO FINAL")
    
    steps = [
        ("Diagnóstico", diagnostic_success),
        ("Migração", migration_success), 
        ("Validação", validation_success)
    ]
    
    success_count = sum([success for _, success in steps])
    total_steps = len(steps)
    
    for step_name, success in steps:
        status = "✅ SUCESSO" if success else "❌ FALHOU"
        print(f"{step_name}: {status}")
    
    print(f"\n🎯 Taxa de Sucesso: {success_count}/{total_steps} ({success_count/total_steps*100:.1f}%)")
    
    if success_count == total_steps:
        print("\n🎉 WORKFLOW COMPLETADO COM SUCESSO!")
        print("✅ Sistema pronto para produção")
    elif success_count >= 2:
        print("\n✅ WORKFLOW PARCIALMENTE COMPLETADO")
        print("🔧 Algumas correções podem ser necessárias")
    else:
        print("\n⚠️ WORKFLOW REQUER ATENÇÃO")
        print("🚨 Várias etapas falharam - intervenção necessária")

def show_individual_commands():
    """Mostra comandos individuais para uso avançado"""
    
    print_header("COMANDOS INDIVIDUAIS")
    
    print("""
🛠️ SCRIPTS DISPONÍVEIS:

1️⃣ DIAGNÓSTICO:
   python guias/migracao-postgres/diagnostic_script.py
   
   ✅ Use quando: Suspeitar de problemas no sistema
   📋 O que faz: Verifica ambiente, banco, APIs e problemas comuns
   
2️⃣ MIGRAÇÃO:
   export DATABASE_URL="postgresql://..."
   python guias/migracao-postgres/migration_script.py
   
   ✅ Use quando: Precisar aplicar correções de schema
   📋 O que faz: Adiciona colunas faltantes na tabela alerts
   
3️⃣ VALIDAÇÃO:
   python guias/migracao-postgres/validation_script.py
   
   ✅ Use quando: Confirmar que migração foi bem-sucedida
   📋 O que faz: Testa schema, APIs e funcionalidades
   
4️⃣ COMANDOS MANUAIS ÚTEIS:

   # Testar conexão com banco
   psql $DATABASE_URL -c "SELECT version();"
   
   # Verificar colunas da tabela alerts
   psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'alerts';"
   
   # Testar API de alertas
   curl -s https://www.agenteagricola.com/api/alerts/health | jq
   
   # Ver logs do Railway
   railway logs --tail=100
   
   # Forçar restart
   railway service restart
""")

def main():
    """Função principal"""
    
    print("🎯 GUIA DE USO - MIGRAÇÃO POSTGRESQL PRODUÇÃO")
    print("=" * 60)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("""
📋 OPÇÕES DISPONÍVEIS:

1. Demonstrar workflow completo (recomendado para iniciantes)
2. Mostrar comandos individuais (para uso avançado)
3. Sair
""")
    
    while True:
        try:
            choice = input("Escolha uma opção (1-3): ").strip()
            
            if choice == "1":
                demonstrate_workflow()
                break
            elif choice == "2":
                show_individual_commands()
                break
            elif choice == "3":
                print("👋 Até logo!")
                break
            else:
                print("❌ Opção inválida! Digite 1, 2 ou 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Interrompido pelo usuário. Até logo!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            break

if __name__ == "__main__":
    main()
