# app/utils/health_checks.py
import time
import requests
import os
from datetime import datetime, timedelta
from flask import current_app
from app import db
from app.models.user import User
from app.utils.metrics import metrics
import logging
import psutil
import threading

class HealthCheck:
    """Classe base para health checks"""
    
    def __init__(self, name, timeout=10, critical=False):
        self.name = name
        self.timeout = timeout
        self.critical = critical  # Se é crítico para o funcionamento do sistema
        self.logger = logging.getLogger(__name__)
    
    def check(self):
        """Executar verificação de saúde"""
        start_time = time.time()
        
        try:
            result = self._perform_check()
            duration = time.time() - start_time
            
            metrics.record_timing(f'health_check.{self.name}.duration', duration)
            metrics.increment_counter(f'health_check.{self.name}.success')
            
            health_result = {
                'name': self.name,
                'status': 'healthy',
                'critical': self.critical,
                'duration_ms': round(duration * 1000, 2),
                'timestamp': datetime.utcnow().isoformat(),
                'details': result
            }
            
            self.logger.debug(f"Health check {self.name} passed", extra={
                'extra_fields': {
                    'component': 'health_check',
                    'check_name': self.name,
                    'status': 'healthy',
                    'duration': duration
                }
            })
            
            return health_result
            
        except Exception as e:
            duration = time.time() - start_time
            
            metrics.record_timing(f'health_check.{self.name}.duration', duration)
            metrics.increment_counter(f'health_check.{self.name}.errors')
            
            health_result = {
                'name': self.name,
                'status': 'unhealthy',
                'critical': self.critical,
                'duration_ms': round(duration * 1000, 2),
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'error_type': type(e).__name__
            }
            
            log_level = logging.ERROR if self.critical else logging.WARNING
            self.logger.log(log_level, f"Health check {self.name} failed: {str(e)}", extra={
                'extra_fields': {
                    'component': 'health_check',
                    'check_name': self.name,
                    'status': 'unhealthy',
                    'error': str(e),
                    'critical': self.critical,
                    'duration': duration
                }
            })
            
            return health_result
    
    def _perform_check(self):
        """Implementar verificação específica"""
        raise NotImplementedError

class DatabaseHealthCheck(HealthCheck):
    """Verificação de saúde do banco de dados"""
    
    def __init__(self):
        super().__init__('database', critical=True)
    
    def _perform_check(self):
        start_query_time = time.time()
        
        # Testar conexão básica
        connection_test = db.session.execute('SELECT 1').scalar()
        if connection_test != 1:
            raise Exception("Database connection test failed")
        
        query_time = time.time() - start_query_time
        
        # Testar query de contagem
        start_count_time = time.time()
        user_count = User.query.count()
        count_time = time.time() - start_count_time
        
        # Verificar performance das queries
        if query_time > 1.0:
            raise Exception(f"Database query too slow: {query_time:.2f}s")
        
        return {
            'connection': 'ok',
            'user_count': user_count,
            'query_test_result': connection_test,
            'connection_time_ms': round(query_time * 1000, 2),
            'count_query_time_ms': round(count_time * 1000, 2)
        }

class WeatherServiceHealthCheck(HealthCheck):
    """Verificação de saúde do serviço meteorológico"""
    
    def __init__(self):
        super().__init__('weather_service', critical=False)
    
    def _perform_check(self):
        try:
            # Testar API do IPMA com timeout
            response = requests.get(
                'https://api.ipma.pt/open-data/forecast/meteorology/cities/daily/1010500.json',
                timeout=5
            )
            
            api_accessible = response.status_code == 200
            
            if api_accessible:
                data = response.json()
                data_available = bool(data.get('data'))
            else:
                data_available = False
                
            return {
                'api_accessible': api_accessible,
                'status_code': response.status_code,
                'data_available': data_available,
                'response_time_ms': round(response.elapsed.total_seconds() * 1000, 2)
            }
            
        except requests.RequestException as e:
            raise Exception(f"Weather API not accessible: {str(e)}")

class DiskSpaceHealthCheck(HealthCheck):
    """Verificação de espaço em disco"""
    
    def __init__(self, threshold_percent=90):
        super().__init__('disk_space', critical=True)
        self.threshold_percent = threshold_percent
    
    def _perform_check(self):
        disk_usage = psutil.disk_usage('/')
        used_percent = (disk_usage.used / disk_usage.total) * 100
        
        if used_percent > self.threshold_percent:
            raise Exception(f"Disk usage {used_percent:.1f}% exceeds threshold {self.threshold_percent}%")
        
        return {
            'used_percent': round(used_percent, 1),
            'free_gb': round(disk_usage.free / 1024 / 1024 / 1024, 2),
            'total_gb': round(disk_usage.total / 1024 / 1024 / 1024, 2),
            'threshold_percent': self.threshold_percent,
            'status': 'healthy' if used_percent <= self.threshold_percent else 'warning'
        }

class MemoryHealthCheck(HealthCheck):
    """Verificação de uso de memória"""
    
    def __init__(self, threshold_percent=85):
        super().__init__('memory', critical=True)
        self.threshold_percent = threshold_percent
    
    def _perform_check(self):
        memory = psutil.virtual_memory()
        
        if memory.percent > self.threshold_percent:
            raise Exception(f"Memory usage {memory.percent:.1f}% exceeds threshold {self.threshold_percent}%")
        
        return {
            'used_percent': round(memory.percent, 1),
            'available_gb': round(memory.available / 1024 / 1024 / 1024, 2),
            'total_gb': round(memory.total / 1024 / 1024 / 1024, 2),
            'threshold_percent': self.threshold_percent,
            'status': 'healthy' if memory.percent <= self.threshold_percent else 'warning'
        }

class ApplicationHealthCheck(HealthCheck):
    """Verificação de saúde da aplicação"""
    
    def __init__(self):
        super().__init__('application', critical=True)
    
    def _perform_check(self):
        # Verificar se os diretórios essenciais existem
        essential_dirs = ['logs', 'static', 'templates']
        missing_dirs = []
        
        for dir_name in essential_dirs:
            if not os.path.exists(dir_name):
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            raise Exception(f"Missing essential directories: {', '.join(missing_dirs)}")
        
        # Verificar se os arquivos de configuração existem
        config_files = ['config.py']
        missing_configs = []
        
        for config_file in config_files:
            if not os.path.exists(config_file):
                missing_configs.append(config_file)
        
        if missing_configs:
            raise Exception(f"Missing configuration files: {', '.join(missing_configs)}")
        
        return {
            'directories': {dir_name: os.path.exists(dir_name) for dir_name in essential_dirs},
            'config_files': {file_name: os.path.exists(file_name) for file_name in config_files},
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            'working_directory': os.getcwd()
        }

class ExternalServicesHealthCheck(HealthCheck):
    """Verificação de serviços externos"""
    
    def __init__(self):
        super().__init__('external_services', critical=False)
    
    def _perform_check(self):
        services_status = {}
        
        # Testar conectividade com serviços externos
        external_services = {
            'openai': 'https://api.openai.com/v1/models',
            'ipma': 'https://api.ipma.pt/open-data/forecast/meteorology/cities/daily/1010500.json'
        }
        
        for service_name, url in external_services.items():
            try:
                response = requests.get(url, timeout=5)
                services_status[service_name] = {
                    'status': 'healthy' if response.status_code == 200 else 'degraded',
                    'status_code': response.status_code,
                    'response_time_ms': round(response.elapsed.total_seconds() * 1000, 2)
                }
            except Exception as e:
                services_status[service_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        return services_status

class HealthCheckManager:
    """Gerenciador de health checks"""
    
    def __init__(self):
        self.checks = [
            # DatabaseHealthCheck(),  # Temporariamente desabilitado - contexto Flask
            DiskSpaceHealthCheck(),
            MemoryHealthCheck(),
            # ApplicationHealthCheck(),  # Temporariamente desabilitado - diretórios static/templates
            WeatherServiceHealthCheck(),
            ExternalServicesHealthCheck()
        ]
        self.logger = logging.getLogger(__name__)
        self.last_check_time = None
        self.last_results = None
        
        # Thread para execução periódica
        self.running = False
        self.check_thread = None
    
    def start_periodic_checks(self, interval_seconds=600):  # Aumentado para 10 minutos
        """Iniciar verificações periódicas (padrão: 5 minutos)"""
        if not self.running:
            self.running = True
            self.check_thread = threading.Thread(
                target=self._periodic_check_loop,
                args=(interval_seconds,)
            )
            self.check_thread.daemon = True
            self.check_thread.start()
            
            self.logger.info("Periodic health checks started", extra={
                'extra_fields': {
                    'component': 'health_check_manager',
                    'interval_seconds': interval_seconds
                }
            })
    
    def stop_periodic_checks(self):
        """Parar verificações periódicas"""
        self.running = False
        if self.check_thread:
            self.check_thread.join()
        
        self.logger.info("Periodic health checks stopped", extra={
            'extra_fields': {
                'component': 'health_check_manager'
            }
        })
    
    def _periodic_check_loop(self, interval_seconds):
        """Loop de verificações periódicas"""
        while self.running:
            try:
                results = self.run_all_checks()
                
                # Verificar se results é um dicionário e tem a chave 'checks'
                if isinstance(results, dict) and 'checks' in results:
                    # Alertar sobre problemas críticos
                    for check_result in results['checks']:
                        if isinstance(check_result, dict) and check_result.get('status') == 'unhealthy' and check_result.get('critical', False):
                            self.logger.error(
                                f"Critical health check failed: {check_result.get('name', 'Unknown')}",
                                extra={
                                    'extra_fields': {
                                        'component': 'health_check_alert',
                                        'check_name': check_result.get('name', 'Unknown'),
                                        'error': check_result.get('error', 'Unknown error')
                                    }
                                }
                            )
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in periodic health check: {e}", exc_info=True)
                time.sleep(60)  # Aguardar 1 minuto em caso de erro
    
    def run_all_checks(self):
        """Executar todas as verificações"""
        start_time = time.time()
        results = []
        overall_status = 'healthy'
        critical_failures = 0
        total_failures = 0
        
        for check in self.checks:
            result = check.check()
            results.append(result)
            
            if result['status'] == 'unhealthy':
                total_failures += 1
                if result.get('critical', False):
                    critical_failures += 1
                    overall_status = 'unhealthy'
                elif overall_status == 'healthy':
                    overall_status = 'degraded'
        
        total_duration = time.time() - start_time
        
        health_summary = {
            'overall_status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'total_checks': len(self.checks),
            'failed_checks': total_failures,
            'critical_failures': critical_failures,
            'duration_ms': round(total_duration * 1000, 2),
            'checks': {result['name']: result for result in results}
        }
        
        self.last_check_time = datetime.utcnow()
        self.last_results = health_summary
        
        # Log resumo
        self.logger.info(f"Health check completed: {overall_status}", extra={
            'extra_fields': {
                'component': 'health_check_summary',
                'overall_status': overall_status,
                'total_checks': len(self.checks),
                'failed_checks': total_failures,
                'critical_failures': critical_failures,
                'duration_ms': round(total_duration * 1000, 2)
            }
        })
        
        return health_summary
    
    def run_check(self, check_name):
        """Executar verificação específica"""
        for check in self.checks:
            if check.name == check_name:
                return check.check()
        
        raise ValueError(f"Health check '{check_name}' not found")
    
    def get_last_results(self):
        """Obter resultados da última verificação"""
        return self.last_results

# Instância global do gerenciador
health_manager = HealthCheckManager()
