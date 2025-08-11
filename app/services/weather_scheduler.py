"""
Sistema de Agendamento para Coleta Automática de Dados Climáticos
Executa coleta a cada hora usando APScheduler
"""
import logging
from datetime import datetime, timezone
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.services.weather_collector import WeatherCollectorService

logger = logging.getLogger(__name__)

# Instância global do scheduler
weather_scheduler = None


class WeatherScheduler:
    """
    Gerenciador de agendamento para coleta automática
    Executa coleta de hora em hora
    """
    
    def __init__(self, app: Flask = None):
        self.scheduler = None
        self.app = app
        self.is_running = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """
        Inicializa o scheduler com a aplicação Flask
        
        Args:
            app: Instância Flask
        """
        self.app = app
        
        # Configurar scheduler
        self.scheduler = BackgroundScheduler(
            timezone='UTC',
            daemon=True,
            coalesce=True,
            max_instances=1
        )
        
        # Adicionar job de coleta automática
        self.setup_collection_jobs()
        
        # Registrar cleanup no encerramento da app
        app.teardown_appcontext(self._cleanup_handler)
    
    def setup_collection_jobs(self):
        """
        Configura jobs de coleta automática
        """
        if not self.scheduler:
            return
        
        try:
            # Job principal: coleta a cada hora
            self.scheduler.add_job(
                func=self._scheduled_collection,
                trigger=CronTrigger(minute=0),  # A cada hora no minuto 0
                id='weather_collection_hourly',
                name='Coleta Automática de Dados Climáticos',
                max_instances=1,
                coalesce=True,
                replace_existing=True
            )
            
            # Job de limpeza: remove dados antigos (diário às 2:00)
            self.scheduler.add_job(
                func=self._scheduled_cleanup,
                trigger=CronTrigger(hour=2, minute=0),  # Diariamente às 2:00
                id='weather_cleanup_daily',
                name='Limpeza de Dados Antigos',
                max_instances=1,
                coalesce=True,
                replace_existing=True
            )
            
            # Job de estatísticas: atualiza estatísticas (diário às 1:00)
            self.scheduler.add_job(
                func=self._scheduled_statistics,
                trigger=CronTrigger(hour=1, minute=0),  # Diariamente às 1:00
                id='weather_statistics_daily',
                name='Atualização de Estatísticas',
                max_instances=1,
                coalesce=True,
                replace_existing=True
            )
            
            logger.info("Jobs de coleta automática configurados")
            
        except Exception as e:
            logger.error(f"Erro ao configurar jobs: {e}")
    
    def start(self):
        """
        Inicia o scheduler
        """
        if self.scheduler and not self.is_running:
            try:
                self.scheduler.start()
                self.is_running = True
                logger.info("Sistema de coleta automática iniciado")
                
                # Log dos jobs configurados
                jobs = self.scheduler.get_jobs()
                for job in jobs:
                    logger.info(f"Job agendado: {job.name} - {job.next_run_time}")
                    
            except Exception as e:
                logger.error(f"Erro ao iniciar scheduler: {e}")
    
    def stop(self):
        """
        Para o scheduler
        """
        if self.scheduler and self.is_running:
            try:
                self.scheduler.shutdown(wait=False)
                self.is_running = False
                logger.info("Sistema de coleta automática parado")
            except Exception as e:
                logger.error(f"Erro ao parar scheduler: {e}")
    
    def force_collection_now(self) -> dict:
        """
        Força execução imediata da coleta
        
        Returns:
            Dict com resultado da coleta
        """
        logger.info("Executando coleta forçada")
        
        with self.app.app_context():
            return self._scheduled_collection()
    
    def get_status(self) -> dict:
        """
        Retorna status do scheduler
        
        Returns:
            Dict com informações de status
        """
        if not self.scheduler:
            return {
                'scheduler_status': 'not_initialized',
                'is_running': False,
                'jobs': []
            }
        
        jobs_info = []
        try:
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                jobs_info.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
        except Exception as e:
            logger.error(f"Erro ao obter jobs: {e}")
        
        return {
            'scheduler_status': 'running' if self.is_running else 'stopped',
            'is_running': self.is_running,
            'jobs': jobs_info,
            'current_time': datetime.now(timezone.utc).isoformat()
        }
    
    def _scheduled_collection(self) -> dict:
        """
        Executa coleta agendada com contexto da aplicação
        
        Returns:
            Dict com resultado da coleta
        """
        try:
            logger.info("Iniciando coleta automática agendada")
            
            # Executar coleta
            result = WeatherCollectorService.collect_all_locations()
            
            # Log do resultado
            if result['success']:
                logger.info(f"Coleta concluída: {result['locations_processed']} localizações processadas")
            else:
                logger.error(f"Coleta falhou: {result['errors']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na coleta agendada: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _scheduled_cleanup(self):
        """
        Executa limpeza automática de dados antigos
        """
        try:
            logger.info("Iniciando limpeza automática de dados antigos")
            
            from app.models.weather import WeatherData
            from app import db
            from datetime import timedelta
            
            # Remover dados não-atuais com mais de 30 dias
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            
            deleted_count = WeatherData.query.filter(
                WeatherData.is_current == False,
                WeatherData.collected_at < cutoff_date
            ).delete()
            
            db.session.commit()
            
            logger.info(f"Limpeza concluída: {deleted_count} registros removidos")
            
        except Exception as e:
            logger.error(f"Erro na limpeza automática: {e}")
    
    def _scheduled_statistics(self):
        """
        Executa atualização automática de estatísticas
        """
        try:
            logger.info("Iniciando atualização automática de estatísticas")
            
            WeatherCollectorService.update_statistics()
            
            logger.info("Atualização de estatísticas concluída")
            
        except Exception as e:
            logger.error(f"Erro na atualização de estatísticas: {e}")
    
    def _cleanup_handler(self, exception=None):
        """
        Handler de cleanup para encerramento da aplicação
        """
        if self.is_running:
            self.stop()


def init_weather_scheduler(app: Flask):
    """
    Inicializa o sistema de agendamento global
    
    Args:
        app: Instância Flask
    """
    global weather_scheduler
    
    try:
        weather_scheduler = WeatherScheduler(app)
        
        # Iniciar automaticamente se não estiver em modo de teste
        if not app.config.get('TESTING', False):
            weather_scheduler.start()
            
        logger.info("Sistema de agendamento de coleta climática inicializado")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar sistema de agendamento: {e}")


def get_weather_scheduler():
    """
    Retorna instância global do scheduler
    
    Returns:
        WeatherScheduler instance
    """
    global weather_scheduler
    return weather_scheduler


def force_collection():
    """
    Força coleta imediata via scheduler global
    
    Returns:
        Dict com resultado da coleta
    """
    global weather_scheduler
    
    if weather_scheduler:
        return weather_scheduler.force_collection_now()
    else:
        logger.error("Scheduler não inicializado")
        return {
            'success': False,
            'error': 'Scheduler não inicializado'
        }


def get_scheduler_status():
    """
    Retorna status do scheduler global
    
    Returns:
        Dict com status
    """
    global weather_scheduler
    
    if weather_scheduler:
        return weather_scheduler.get_status()
    else:
        return {
            'scheduler_status': 'not_initialized',
            'is_running': False,
            'jobs': []
        }
