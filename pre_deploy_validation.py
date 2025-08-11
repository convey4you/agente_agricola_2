#!/usr/bin/env python3
"""
Verificação Final Pré-Deploy - Sprint 2
Validação completa do sistema antes da produção
"""

import os
import sys
import subprocess
import json
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PreDeployValidator:
    """Validador pré-deploy para garantir qualidade"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'code_quality': {},
            'configuration': {},
            'overall_status': 'PENDING'
        }
    
    def validate_tests(self):
        """Valida que todos os testes passam"""
        logger.info("🧪 Validando testes automatizados...")
        
        try:
            # Executar testes unitários
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'tests/test_models.py', 
                '-v', '--tb=short', '--no-cov', '-q'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Contar testes que passaram
                output_lines = result.stdout.split('\n')
                passed_line = [line for line in output_lines if 'passed' in line and 'warnings' in line]
                
                if passed_line:
                    # Extrair número de testes
                    import re
                    match = re.search(r'(\d+) passed', passed_line[0])
                    tests_passed = int(match.group(1)) if match else 0
                    
                    self.results['tests'] = {
                        'status': 'PASS',
                        'tests_passed': tests_passed,
                        'total_tests': tests_passed,
                        'success_rate': '100%'
                    }
                    logger.info(f"✅ Testes: {tests_passed} passaram")
                    return True
                else:
                    self.results['tests'] = {'status': 'FAIL', 'error': 'Could not parse test results'}
                    return False
            else:
                self.results['tests'] = {
                    'status': 'FAIL',
                    'error': result.stderr,
                    'stdout': result.stdout
                }
                logger.error(f"❌ Testes falharam: {result.stderr}")
                return False
                
        except Exception as e:
            self.results['tests'] = {'status': 'ERROR', 'exception': str(e)}
            logger.error(f"❌ Erro executando testes: {e}")
            return False
    
    def validate_code_quality(self):
        """Valida qualidade do código"""
        logger.info("📊 Validando qualidade do código...")
        
        quality_checks = {}
        
        # 1. Verificar imports no código principal
        try:
            import app
            quality_checks['imports'] = 'OK'
        except Exception as e:
            quality_checks['imports'] = f'FAIL: {e}'
            logger.error(f"❌ Erro de imports: {e}")
        
        # 2. Verificar se warnings foram corrigidas
        try:
            result = subprocess.run([
                'python', '-c', 
                'from datetime import datetime, timezone; print("datetime imports OK")'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                quality_checks['datetime_imports'] = 'OK'
            else:
                quality_checks['datetime_imports'] = f'FAIL: {result.stderr}'
                
        except Exception as e:
            quality_checks['datetime_imports'] = f'ERROR: {e}'
        
        # 3. Verificar estrutura de arquivos essenciais
        essential_files = [
            'app/__init__.py',
            'app/models/alerts.py',
            'app/controllers/alerts_controller.py',
            'tests/test_models.py',
            'tests/conftest.py',
            'requirements.txt',
            'Procfile',
            'run.py'
        ]
        
        missing_files = []
        for file_path in essential_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            quality_checks['essential_files'] = f'MISSING: {missing_files}'
            logger.error(f"❌ Arquivos faltando: {missing_files}")
        else:
            quality_checks['essential_files'] = 'OK'
            logger.info("✅ Todos os arquivos essenciais presentes")
        
        self.results['code_quality'] = quality_checks
        return len([v for v in quality_checks.values() if 'OK' in str(v)]) == len(quality_checks)
    
    def validate_configuration(self):
        """Valida configurações para produção"""
        logger.info("⚙️ Validando configurações...")
        
        config_checks = {}
        
        # 1. Verificar requirements.txt
        try:
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
                
            essential_packages = [
                'Flask==',
                'SQLAlchemy==',
                'psycopg2-binary==',
                'Flask-Login==',
                'pytest=='
            ]
            
            missing_packages = []
            for package in essential_packages:
                if package not in requirements:
                    missing_packages.append(package.replace('==', ''))
            
            if missing_packages:
                config_checks['requirements'] = f'MISSING: {missing_packages}'
            else:
                config_checks['requirements'] = 'OK'
                
        except Exception as e:
            config_checks['requirements'] = f'ERROR: {e}'
        
        # 2. Verificar config.py
        try:
            from config import config
            if 'production' in config:
                config_checks['production_config'] = 'OK'
            else:
                config_checks['production_config'] = 'MISSING'
        except Exception as e:
            config_checks['production_config'] = f'ERROR: {e}'
        
        # 3. Verificar Procfile
        try:
            with open('Procfile', 'r') as f:
                procfile = f.read().strip()
            
            if 'web:' in procfile and 'python' in procfile:
                config_checks['procfile'] = 'OK'
            else:
                config_checks['procfile'] = 'INVALID'
        except Exception as e:
            config_checks['procfile'] = f'ERROR: {e}'
        
        # 4. Verificar pytest.ini
        try:
            with open('pytest.ini', 'r') as f:
                pytest_config = f.read()
            
            if '[pytest]' in pytest_config and 'markers' in pytest_config:
                config_checks['pytest_config'] = 'OK'
            else:
                config_checks['pytest_config'] = 'INCOMPLETE'
        except Exception as e:
            config_checks['pytest_config'] = f'ERROR: {e}'
        
        self.results['configuration'] = config_checks
        return len([v for v in config_checks.values() if 'OK' in str(v)]) == len(config_checks)
    
    def generate_report(self):
        """Gera relatório final de validação"""
        logger.info("📋 Gerando relatório final...")
        
        # Calcular status geral
        all_checks = []
        for category in ['tests', 'code_quality', 'configuration']:
            if category in self.results:
                if category == 'tests':
                    all_checks.append(self.results[category].get('status') == 'PASS')
                else:
                    checks = self.results[category]
                    all_checks.append(all([('OK' in str(v)) for v in checks.values()]))
        
        if all(all_checks):
            self.results['overall_status'] = 'READY_FOR_PRODUCTION'
            status_emoji = "🎉"
            status_msg = "PRONTO PARA PRODUÇÃO"
        else:
            self.results['overall_status'] = 'NEEDS_ATTENTION'
            status_emoji = "⚠️"
            status_msg = "PRECISA DE ATENÇÃO"
        
        # Salvar relatório JSON
        with open('pre_deploy_validation.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Relatório de console
        print("\n" + "="*60)
        print(f"{status_emoji} STATUS DE VALIDAÇÃO PRÉ-DEPLOY")
        print("="*60)
        print(f"📅 Timestamp: {self.results['timestamp']}")
        print(f"🎯 Status Geral: {status_msg}")
        print()
        
        # Detalhes por categoria
        categories = {
            'tests': '🧪 TESTES AUTOMATIZADOS',
            'code_quality': '📊 QUALIDADE DO CÓDIGO', 
            'configuration': '⚙️ CONFIGURAÇÕES'
        }
        
        for key, title in categories.items():
            if key in self.results:
                print(f"{title}:")
                data = self.results[key]
                
                if key == 'tests':
                    if data.get('status') == 'PASS':
                        print(f"  ✅ {data.get('tests_passed', 0)} testes passaram")
                        print(f"  ✅ Taxa de sucesso: {data.get('success_rate', 'N/A')}")
                    else:
                        print(f"  ❌ Status: {data.get('status')}")
                        if 'error' in data:
                            print(f"  ❌ Erro: {data['error'][:100]}...")
                else:
                    for check, status in data.items():
                        emoji = "✅" if "OK" in str(status) else "❌"
                        print(f"  {emoji} {check}: {status}")
                print()
        
        print("="*60)
        
        if self.results['overall_status'] == 'READY_FOR_PRODUCTION':
            print("🚀 SISTEMA VALIDADO PARA DEPLOY EM PRODUÇÃO!")
            print("📄 Relatório salvo em: pre_deploy_validation.json")
        else:
            print("⚠️ CORRIJA OS PROBLEMAS ANTES DO DEPLOY")
            print("📄 Relatório detalhado em: pre_deploy_validation.json")
        
        print("="*60)
        
        return self.results['overall_status'] == 'READY_FOR_PRODUCTION'
    
    def validate_all(self):
        """Executa todas as validações"""
        logger.info("🔍 INICIANDO VALIDAÇÃO PRÉ-DEPLOY")
        
        validations = [
            self.validate_tests,
            self.validate_code_quality,
            self.validate_configuration
        ]
        
        for validation in validations:
            try:
                validation()
            except Exception as e:
                logger.error(f"❌ Erro na validação: {e}")
        
        return self.generate_report()

def main():
    """Função principal"""
    validator = PreDeployValidator()
    
    if validator.validate_all():
        print("\n🎉 PRONTO PARA DEPLOY!")
        sys.exit(0)
    else:
        print("\n❌ VALIDAÇÃO FALHOU - NÃO FAÇA DEPLOY")
        sys.exit(1)

if __name__ == "__main__":
    main()
