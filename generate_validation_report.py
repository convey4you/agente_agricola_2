#!/usr/bin/env python3
"""
Gerador de Relatório Final de Validação
Consolida todos os resultados e gera relatório executivo
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List

class ValidationReportGenerator:
    """Gerador de relatórios de validação"""
    
    def __init__(self, validation_data: Dict[str, Any]):
        self.data = validation_data
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def generate_executive_summary(self) -> str:
        """Gera resumo executivo"""
        summary = self.data.get('summary', {})
        
        status = summary.get('overall_status', 'UNKNOWN')
        score = summary.get('overall_score', 0)
        emoji = summary.get('status_emoji', '❓')
        
        if status == 'APPROVED':
            decision = "SPRINT 1 APROVADO"
            next_steps = "Autorizado início do Sprint 2"
        elif status == 'CONDITIONAL':
            decision = "SPRINT 1 APROVADO CONDICIONALMENTE"
            next_steps = "Implementar melhorias recomendadas"
        else:
            decision = "SPRINT 1 NÃO APROVADO"
            next_steps = "Implementar correções obrigatórias"
        
        return f"""
# RELATÓRIO EXECUTIVO - VALIDAÇÃO DE CORREÇÕES CRÍTICAS

**Projeto:** AgroTech Portugal  
**Data:** {self.timestamp}  
**Validação:** Correções do Sistema de Registro  

## {emoji} DECISÃO FINAL: {decision}

**Score de Conformidade:** {score}%  
**Próximos Passos:** {next_steps}

### Resumo dos Testes
- **Total de Testes:** {summary.get('total_tests', 0)}
- **Testes Aprovados:** {summary.get('passed_tests', 0)} ✅
- **Testes Parciais:** {summary.get('partial_tests', 0)} ⚠️
- **Testes Falharam:** {summary.get('failed_tests', 0)} ❌
"""
    
    def generate_detailed_results(self) -> str:
        """Gera resultados detalhados"""
        tests = self.data.get('tests', {})
        
        details = "\n## 📋 RESULTADOS DETALHADOS\n"
        
        for test_name, test_data in tests.items():
            status = test_data.get('status', 'unknown')
            duration = test_data.get('duration_ms', 0)
            name = test_data.get('name', test_name)
            
            status_emoji = {
                'pass': '✅',
                'partial': '⚠️',
                'fail': '❌',
                'error': '💥'
            }.get(status, '❓')
            
            details += f"\n### {status_emoji} {name}\n"
            details += f"**Status:** {status.upper()}  \n"
            details += f"**Duração:** {duration}ms  \n"
            
            # Adicionar detalhes específicos
            test_details = test_data.get('details', {})
            if test_details:
                details += "**Detalhes:**\n"
                for key, value in test_details.items():
                    if isinstance(value, dict):
                        details += f"- {key}: {json.dumps(value, indent=2)}\n"
                    else:
                        details += f"- {key}: {value}\n"
            
            details += "\n"
        
        return details
    
    def generate_recommendations(self) -> str:
        """Gera seção de recomendações"""
        recommendations = self.data.get('recommendations', [])
        
        if not recommendations:
            return "\n## ✅ NENHUMA RECOMENDAÇÃO ADICIONAL\n\nTodos os testes passaram com sucesso.\n"
        
        rec_text = "\n## 💡 RECOMENDAÇÕES\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            rec_text += f"{i}. **{rec}**\n"
        
        return rec_text
    
    def generate_technical_details(self) -> str:
        """Gera detalhes técnicos"""
        base_url = self.data.get('base_url', 'N/A')
        timestamp = self.data.get('timestamp', 'N/A')
        
        return f"""
## 🔧 DETALHES TÉCNICOS

**URL Testada:** {base_url}  
**Timestamp da Validação:** {timestamp}  
**Ferramenta:** Validador Automático de Correções  
**Versão:** 1.0.0  

### Critérios de Aprovação
- **Score Mínimo:** 70% para aprovação condicional
- **Score Ideal:** 90% para aprovação completa
- **Testes Críticos:** Conectividade, Health Checks, Registro, Banco de Dados

### Metodologia
1. Teste de conectividade básica
2. Validação de endpoints de health check
3. Teste do fluxo de registro
4. Verificação da inicialização do banco
5. Benchmarks de performance
"""
    
    def generate_full_report(self) -> str:
        """Gera relatório completo"""
        report = self.generate_executive_summary()
        report += self.generate_detailed_results()
        report += self.generate_recommendations()
        report += self.generate_technical_details()
        
        return report
    
    def save_markdown_report(self, filename: str = None) -> str:
        """Salva relatório em formato Markdown"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_report_{timestamp}.md"
        
        report_content = self.generate_full_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return filename
    
    def generate_csv_summary(self) -> str:
        """Gera resumo em formato CSV para análise"""
        tests = self.data.get('tests', {})
        summary = self.data.get('summary', {})
        
        csv_content = "Test,Status,Duration_ms,Score\n"
        
        for test_name, test_data in tests.items():
            status = test_data.get('status', 'unknown')
            duration = test_data.get('duration_ms', 0)
            
            # Calcular score individual baseado no status
            score = {
                'pass': 100,
                'partial': 50,
                'fail': 0,
                'error': 0
            }.get(status, 0)
            
            csv_content += f"{test_name},{status},{duration},{score}\n"
        
        # Adicionar linha de resumo
        overall_score = summary.get('overall_score', 0)
        csv_content += f"OVERALL,{summary.get('overall_status', 'UNKNOWN')},0,{overall_score}\n"
        
        return csv_content
    
    def save_csv_report(self, filename: str = None) -> str:
        """Salva relatório em formato CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_summary_{timestamp}.csv"
        
        csv_content = self.generate_csv_summary()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        return filename

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python generate_validation_report.py <arquivo_json> [--csv]")
        print("Opções:")
        print("  --csv    Gerar também relatório CSV")
        sys.exit(1)
    
    json_file = sys.argv[1]
    generate_csv = '--csv' in sys.argv
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            validation_data = json.load(f)
        
        generator = ValidationReportGenerator(validation_data)
        
        # Gerar relatório em Markdown
        report_file = generator.save_markdown_report()
        print(f"📄 Relatório Markdown gerado: {report_file}")
        
        # Gerar relatório CSV se solicitado
        if generate_csv:
            csv_file = generator.save_csv_report()
            print(f"📊 Relatório CSV gerado: {csv_file}")
        
        # Imprimir resumo executivo
        print("\n" + "="*80)
        print(generator.generate_executive_summary())
        print("="*80)
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Arquivo JSON inválido: {json_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
