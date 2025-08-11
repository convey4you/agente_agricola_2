"""
Configuração e Execução de Testes End-to-End
PROMPT 4 - Implementação de Testes Automatizados

Sistema de execução e relatórios de todos os testes
"""
import pytest
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Executor de testes com relatórios detalhados"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.results = {}
        
    def run_test_suite(self, test_type="all"):
        """Executa suite de testes específica ou completa"""
        self.start_time = time.time()
        
        print("🚀 INICIANDO SUITE DE TESTES AUTOMATIZADOS")
        print("=" * 60)
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tipo de teste: {test_type}")
        print("=" * 60)
        
        # Configurar argumentos do pytest
        pytest_args = [
            "-v",  # Verbose
            "--tb=short",  # Traceback curto
            "--strict-markers",  # Markers rigorosos
            "--strict-config",  # Configuração rigorosa
        ]
        
        # Adicionar cobertura se disponível
        try:
            import pytest_cov
            pytest_args.extend([
                "--cov=app",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-fail-under=70"
            ])
            print("📊 Cobertura de código habilitada")
        except ImportError:
            print("⚠️  pytest-cov não disponível, executando sem cobertura")
        
        # Selecionar testes baseado no tipo
        if test_type == "unit":
            pytest_args.extend([
                "tests/test_models.py",
                "tests/test_database.py"
            ])
        elif test_type == "integration":
            pytest_args.extend([
                "tests/test_alerts_api_integration.py"
            ])
        elif test_type == "security":
            pytest_args.extend([
                "tests/test_authentication_security.py"
            ])
        elif test_type == "performance":
            pytest_args.extend([
                "-m", "performance"
            ])
        elif test_type == "all":
            pytest_args.append("tests/")
        else:
            raise ValueError(f"Tipo de teste inválido: {test_type}")
        
        # Executar testes
        print(f"\n🧪 Executando testes: {' '.join(pytest_args)}")
        print("-" * 40)
        
        exit_code = pytest.main(pytest_args)
        
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        # Processar resultados
        self._process_results(exit_code, execution_time, test_type)
        
        return exit_code == 0
    
    def _process_results(self, exit_code, execution_time, test_type):
        """Processa e exibe resultados dos testes"""
        status = "✅ SUCESSO" if exit_code == 0 else "❌ FALHA"
        
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL DOS TESTES")
        print("=" * 60)
        print(f"Status: {status}")
        print(f"Código de saída: {exit_code}")
        print(f"Tempo de execução: {execution_time:.2f}s")
        print(f"Tipo de teste: {test_type}")
        
        # Salvar relatório JSON
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_type': test_type,
            'exit_code': exit_code,
            'success': exit_code == 0,
            'execution_time': execution_time,
            'status': 'PASSED' if exit_code == 0 else 'FAILED'
        }
        
        report_file = f"test_report_{test_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Relatório salvo em: {report_file}")
        
        # Verificar se há arquivo de cobertura
        coverage_file = Path("htmlcov/index.html")
        if coverage_file.exists():
            print(f"📊 Relatório de cobertura: {coverage_file.absolute()}")


def setup_test_environment():
    """Configura ambiente de teste"""
    print("🔧 Configurando ambiente de teste...")
    
    # Definir variáveis de ambiente para testes
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    # Verificar se diretório de testes existe
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("❌ Diretório 'tests' não encontrado!")
        return False
    
    # Verificar arquivos de teste necessários
    required_files = [
        "tests/conftest.py",
        "tests/test_models.py",
        "tests/test_database.py",
        "tests/test_alerts_api_integration.py",
        "tests/test_authentication_security.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Arquivos de teste faltando:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ Ambiente de teste configurado com sucesso")
    return True


def run_pre_test_validation():
    """Executa validações antes dos testes"""
    print("🔍 Executando validações pré-teste...")
    
    # Verificar imports críticos
    try:
        import flask
        import sqlalchemy
        import pytest
        print("✅ Dependências principais OK")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        return False
    
    # Verificar estrutura do projeto
    required_dirs = ["app", "app/models", "app/controllers"]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Diretório faltando: {dir_path}")
            return False
    
    print("✅ Estrutura do projeto OK")
    
    # Verificar arquivos críticos
    critical_files = [
        "app/__init__.py",
        "app/models/alerts.py",
        "app/models/user.py",
        "config.py"
    ]
    
    for file_path in critical_files:
        if not Path(file_path).exists():
            print(f"❌ Arquivo crítico faltando: {file_path}")
            return False
    
    print("✅ Arquivos críticos OK")
    return True


def main():
    """Função principal do executor de testes"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Executor de Testes Automatizados - PROMPT 4')
    parser.add_argument(
        '--type', 
        choices=['all', 'unit', 'integration', 'security', 'performance'],
        default='all',
        help='Tipo de teste a executar'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Pular validações pré-teste'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Saída verbosa'
    )
    
    args = parser.parse_args()
    
    # Banner inicial
    print("\n" + "🧪" * 20)
    print("  SISTEMA DE TESTES AUTOMATIZADOS")
    print("     PROMPT 4 - Sprint 2")
    print("🧪" * 20 + "\n")
    
    # Configurar ambiente
    if not setup_test_environment():
        print("❌ Falha na configuração do ambiente")
        sys.exit(1)
    
    # Validações pré-teste
    if not args.skip_validation:
        if not run_pre_test_validation():
            print("❌ Falha nas validações pré-teste")
            sys.exit(1)
    
    # Executar testes
    runner = TestRunner()
    success = runner.run_test_suite(args.type)
    
    # Exit code baseado no resultado
    exit_code = 0 if success else 1
    
    print(f"\n🏁 Execução finalizada com código: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
