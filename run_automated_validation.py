#!/usr/bin/env python3
"""
Script de Validação Automatizada Completa - AgroTech Portugal
Executa todos os scripts de validação em sequência e gera relatório final
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class AutomatedValidationRunner:
    """Executor automatizado de todos os testes de validação"""
    
    def __init__(self, base_url: str = "https://www.agenteagricola.com"):
        self.base_url = base_url
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            'timestamp': datetime.utcnow().isoformat(),
            'base_url': base_url,
            'execution_summary': {},
            'individual_results': {},
            'final_assessment': {}
        }
        
    def run_script(self, script_name: str, args: List[str] = None) -> Dict[str, Any]:
        """Executa um script de validação individual"""
        if args is None:
            args = []
            
        print(f"🚀 Executando {script_name}...")
        
        start_time = time.time()
        
        try:
            # Construir comando
            cmd = [sys.executable, script_name] + args
            
            # Executar script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos de timeout
            )
            
            duration = round((time.time() - start_time) * 1000, 2)
            
            execution_result = {
                'script': script_name,
                'exit_code': result.returncode,
                'duration_ms': duration,
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            # Tentar carregar resultado JSON se gerado
            json_output = None
            for line in result.stdout.split('\n'):
                if '.json' in line and ('salvo' in line or 'saved' in line):
                    # Extrair nome do arquivo JSON
                    json_file = line.split()[-1]
                    if os.path.exists(json_file):
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                json_output = json.load(f)
                            execution_result['json_output'] = json_output
                            execution_result['json_file'] = json_file
                        except:
                            pass
            
            if execution_result['success']:
                print(f"  ✅ {script_name} - Concluído ({duration:.0f}ms)")
            else:
                print(f"  ❌ {script_name} - Falhou (código: {result.returncode})")
                
            return execution_result
            
        except subprocess.TimeoutExpired:
            print(f"  ⏰ {script_name} - Timeout (>5min)")
            return {
                'script': script_name,
                'exit_code': -1,
                'duration_ms': round((time.time() - start_time) * 1000, 2),
                'success': False,
                'error': 'Timeout - script executou por mais de 5 minutos'
            }
            
        except Exception as e:
            print(f"  💥 {script_name} - Erro: {e}")
            return {
                'script': script_name,
                'exit_code': -2,
                'duration_ms': round((time.time() - start_time) * 1000, 2),
                'success': False,
                'error': str(e)
            }
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Executa toda a bateria de validações"""
        print("🎯 INICIANDO VALIDAÇÃO AUTOMATIZADA COMPLETA")
        print("="*60)
        print(f"URL: {self.base_url}")
        print(f"Timestamp: {self.timestamp}")
        print("="*60)
        
        # Scripts para executar em ordem
        validation_scripts = [
            {
                'name': 'validate_corrections.py',
                'args': ['--url', self.base_url, '--output', f'validation_main_{self.timestamp}.json'],
                'description': 'Validação principal das correções'
            },
            {
                'name': 'test_health_endpoints_new.py',
                'args': [self.base_url],
                'description': 'Testes específicos de health check'
            },
            {
                'name': 'test_registration_flow.py',
                'args': [self.base_url],
                'description': 'Testes do fluxo de registro'
            }
        ]
        
        # Executar cada script
        for script_config in validation_scripts:
            script_name = script_config['name']
            script_args = script_config['args']
            
            print(f"\n📋 {script_config['description']}")
            
            if not os.path.exists(script_name):
                print(f"  ⚠️ Script não encontrado: {script_name}")
                self.results['individual_results'][script_name] = {
                    'success': False,
                    'error': 'Script file not found'
                }
                continue
            
            result = self.run_script(script_name, script_args)
            self.results['individual_results'][script_name] = result
        
        # Gerar assessment final
        self._generate_final_assessment()
        
        # Gerar relatório consolidado
        self._generate_consolidated_report()
        
        return self.results
    
    def _generate_final_assessment(self):
        """Gera assessment final baseado em todos os resultados"""
        individual_results = self.results['individual_results']
        
        total_scripts = len(individual_results)
        successful_scripts = sum(1 for r in individual_results.values() if r.get('success', False))
        
        # Extrair dados do validador principal
        main_validation = individual_results.get('validate_corrections.py', {})
        main_json = main_validation.get('json_output', {})
        main_summary = main_json.get('summary', {})
        
        # Determinar status geral
        main_score = main_summary.get('overall_score', 0)
        main_status = main_summary.get('overall_status', 'UNKNOWN')
        
        if successful_scripts == total_scripts and main_score >= 90:
            final_status = 'APPROVED'
            final_emoji = '✅'
            final_decision = 'Sprint 1 APROVADO - Sistema funcionando corretamente'
        elif successful_scripts >= total_scripts * 0.8 and main_score >= 70:
            final_status = 'CONDITIONAL'
            final_emoji = '⚠️'
            final_decision = 'Sprint 1 APROVADO CONDICIONALMENTE - Melhorias recomendadas'
        else:
            final_status = 'REJECTED'
            final_emoji = '❌'
            final_decision = 'Sprint 1 NÃO APROVADO - Correções obrigatórias necessárias'
        
        self.results['final_assessment'] = {
            'final_status': final_status,
            'final_emoji': final_emoji,
            'final_decision': final_decision,
            'main_score': main_score,
            'main_status': main_status,
            'scripts_successful': successful_scripts,
            'scripts_total': total_scripts,
            'success_rate': (successful_scripts / total_scripts * 100) if total_scripts > 0 else 0
        }
        
        self.results['execution_summary'] = {
            'total_scripts_executed': total_scripts,
            'successful_executions': successful_scripts,
            'failed_executions': total_scripts - successful_scripts,
            'execution_success_rate': (successful_scripts / total_scripts * 100) if total_scripts > 0 else 0
        }
    
    def _generate_consolidated_report(self):
        """Gera relatório consolidado final"""
        # Buscar arquivo de validação principal
        main_validation = self.results['individual_results'].get('validate_corrections.py', {})
        main_json_file = main_validation.get('json_file')
        
        if main_json_file and os.path.exists(main_json_file):
            print(f"\n📊 Gerando relatório consolidado...")
            
            try:
                # Executar gerador de relatório
                report_result = self.run_script(
                    'generate_validation_report.py',
                    [main_json_file, '--csv']
                )
                
                self.results['individual_results']['generate_validation_report.py'] = report_result
                
                if report_result.get('success'):
                    print("  ✅ Relatório consolidado gerado com sucesso")
                else:
                    print("  ❌ Falha na geração do relatório consolidado")
                    
            except Exception as e:
                print(f"  ❌ Erro na geração do relatório: {e}")
    
    def save_execution_summary(self) -> str:
        """Salva resumo da execução"""
        filename = f"automated_validation_{self.timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def print_final_summary(self):
        """Imprime resumo final"""
        assessment = self.results['final_assessment']
        execution = self.results['execution_summary']
        
        print("\n" + "="*80)
        print("RESUMO FINAL - VALIDAÇÃO AUTOMATIZADA AGROTECH PORTUGAL")
        print("="*80)
        
        print(f"{assessment['final_emoji']} DECISÃO FINAL: {assessment['final_decision']}")
        print(f"📊 Score Principal: {assessment['main_score']}%")
        print(f"🎯 Status Principal: {assessment['main_status']}")
        
        print(f"\n📋 EXECUÇÃO DOS SCRIPTS:")
        print(f"  ✅ Scripts Executados com Sucesso: {execution['successful_executions']}")
        print(f"  ❌ Scripts com Falha: {execution['failed_executions']}")
        print(f"  📈 Taxa de Sucesso: {execution['execution_success_rate']:.1f}%")
        
        print(f"\n🕐 Timestamp: {self.results['timestamp']}")
        print(f"🌐 URL Testada: {self.results['base_url']}")
        
        print("\n" + "="*80)

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validação Automatizada Completa - AgroTech Portugal')
    parser.add_argument('--url', default='https://www.agenteagricola.com',
                       help='URL base do sistema (padrão: https://www.agenteagricola.com)')
    
    args = parser.parse_args()
    
    # Executar validação automatizada
    runner = AutomatedValidationRunner(args.url)
    results = runner.run_all_validations()
    
    # Salvar resumo da execução
    summary_file = runner.save_execution_summary()
    print(f"\n📄 Resumo da execução salvo em: {summary_file}")
    
    # Imprimir resumo final
    runner.print_final_summary()
    
    # Exit code baseado no resultado final
    final_status = results['final_assessment']['final_status']
    if final_status == 'APPROVED':
        sys.exit(0)
    elif final_status == 'CONDITIONAL':
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
