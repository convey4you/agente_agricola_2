#!/usr/bin/env python3
"""
Script de Agendamento Automático de Alertas
Para ser executado via cron/agendador de tarefas do sistema operacional

Exemplo de configuração no cron (Linux/Mac):
# Executar a cada 30 minutos
*/30 * * * * cd /caminho/para/projeto && python scheduled_alert_generation.py

Exemplo no Windows Task Scheduler:
- Programa: python
- Argumentos: scheduled_alert_generation.py
- Diretório inicial: C:\caminho\para\projeto
- Trigger: Repetir a cada 30 minutos
"""
import sys
import os
from datetime import datetime
import logging

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Configurar logging para o agendador"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scheduled_alerts.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def run_scheduled_alerts():
    """Executar geração automática de alertas"""
    logger = setup_logging()
    
    try:
        logger.info("=== INICIANDO GERAÇÃO AUTOMÁTICA DE ALERTAS ===")
        
        # Importar dentro da função para evitar problemas de inicialização
        from app import create_app
        from app.services.auto_alert_service import AutoAlertService
        
        # Criar contexto da aplicação
        app = create_app()
        
        with app.app_context():
            # Executar serviço de alertas automáticos
            auto_alert_service = AutoAlertService()
            result = auto_alert_service.run_auto_generation()
            
            if result['success']:
                logger.info(f"✅ Geração automática concluída com sucesso!")
                logger.info(f"   Usuários processados: {result['users_processed']}")
                logger.info(f"   Alertas gerados: {result['alerts_generated']}")
                
                # Log adicional se houver alertas gerados
                if result['alerts_generated'] > 0:
                    logger.info(f"🔔 {result['alerts_generated']} novos alertas disponíveis para os usuários")
                else:
                    logger.info("ℹ Nenhum alerta novo gerado (condições não atendidas)")
                    
            else:
                logger.error(f"❌ Erro na geração automática: {result.get('error', 'Erro desconhecido')}")
                return False
                
        return True
        
    except ImportError as e:
        logger.error(f"❌ Erro de importação: {str(e)}")
        logger.error("Verifique se está executando do diretório correto e se as dependências estão instaladas")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado na geração automática: {str(e)}")
        logger.exception("Detalhes do erro:")
        return False

def check_system_health():
    """Verificar se o sistema está funcionando antes de gerar alertas"""
    try:
        from app import create_app
        from app.models.alerts import UserAlertPreference
        
        app = create_app()
        with app.app_context():
            # Verificar se consegue acessar o banco
            count = UserAlertPreference.query.filter_by(auto_generation_enabled=True).count()
            return True, f"{count} usuários com geração automática habilitada"
            
    except Exception as e:
        return False, f"Erro no health check: {str(e)}"

def main():
    """Função principal do agendador"""
    logger = setup_logging()
    
    logger.info(f"Iniciando verificação de saúde do sistema...")
    
    # Verificar saúde do sistema
    healthy, message = check_system_health()
    if not healthy:
        logger.error(f"❌ Sistema não está saudável: {message}")
        sys.exit(1)
    
    logger.info(f"✅ Sistema saudável: {message}")
    
    # Executar geração automática
    success = run_scheduled_alerts()
    
    if success:
        logger.info("=== GERAÇÃO AUTOMÁTICA FINALIZADA COM SUCESSO ===")
        sys.exit(0)
    else:
        logger.error("=== GERAÇÃO AUTOMÁTICA FINALIZADA COM ERRO ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
