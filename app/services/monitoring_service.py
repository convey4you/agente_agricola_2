"""
Monitoring Service - Lógica de negócio para monitoramento do sistema
"""
from flask import current_app
from app import db
from app.models.user import User
from app.models.culture import Culture
from app.models.activity import Activity
from datetime import datetime, timezone, timedelta
import psutil
import platform
import sys
from sqlalchemy import text


class MonitoringService:
    """Serviço para gerenciar operações de monitoramento do sistema"""
    
    @staticmethod
    def get_system_status():
        """Obter status completo do sistema"""
        try:
            # Informações do sistema operacional
            system_info = MonitoringService._get_system_info()
            
            # Informações de hardware
            hardware_info = MonitoringService._get_hardware_info()
            
            # Estatísticas da aplicação
            app_stats = MonitoringService._get_application_stats()
            
            # Verificações de saúde
            health_checks = MonitoringService._perform_health_checks()
            
            # Determinar status geral
            overall_status = MonitoringService._determine_overall_status(
                hardware_info, health_checks
            )
            
            return {
                'success': True,
                'data': {
                    'system': system_info,
                    'hardware': hardware_info,
                    'application': app_stats,
                    'health': health_checks,
                    'status': overall_status,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter status do sistema: {e}")
            return {
                'success': False,
                'error': 'Erro ao obter status do sistema'
            }
    
    @staticmethod
    def get_health_check():
        """Health check básico para monitoramento externo"""
        try:
            # Testar conexão com banco de dados
            db_status = MonitoringService._check_database_connection()
            
            # Verificar recursos básicos do sistema
            system_checks = MonitoringService._check_basic_resources()
            
            # Determinar status geral
            is_healthy = db_status['connected'] and system_checks['adequate']
            
            return {
                'success': True,
                'data': {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'database': 'connected' if db_status['connected'] else 'disconnected',
                    'version': '2.0.0',
                    'checks': {
                        'database': db_status,
                        'system': system_checks
                    }
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro no health check: {e}")
            return {
                'success': False,
                'error': 'Health check falhou',
                'status': 'unhealthy',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    def get_performance_metrics():
        """Obter métricas detalhadas de performance"""
        try:
            # CPU e memória ao longo do tempo
            cpu_history = MonitoringService._get_cpu_history()
            memory_history = MonitoringService._get_memory_history()
            
            # Métricas de banco de dados
            db_metrics = MonitoringService._get_database_metrics()
            
            # Métricas de aplicação
            app_metrics = MonitoringService._get_application_metrics()
            
            return {
                'success': True,
                'data': {
                    'cpu': cpu_history,
                    'memory': memory_history,
                    'database': db_metrics,
                    'application': app_metrics,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter métricas de performance: {e}")
            return {
                'success': False,
                'error': 'Erro ao obter métricas de performance'
            }
    
    @staticmethod
    def get_user_activity_stats():
        """Obter estatísticas de atividade dos usuários"""
        try:
            now = datetime.now(timezone.utc)
            
            # Estatísticas por período
            stats = {
                'last_hour': MonitoringService._get_activity_in_period(now - timedelta(hours=1), now),
                'last_24h': MonitoringService._get_activity_in_period(now - timedelta(days=1), now),
                'last_week': MonitoringService._get_activity_in_period(now - timedelta(days=7), now),
                'last_month': MonitoringService._get_activity_in_period(now - timedelta(days=30), now)
            }
            
            # Top usuários mais ativos
            top_users = MonitoringService._get_top_active_users()
            
            # Atividades por tipo
            activity_types = MonitoringService._get_activity_by_type()
            
            return {
                'success': True,
                'data': {
                    'periods': stats,
                    'top_users': top_users,
                    'activity_types': activity_types,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter estatísticas de usuário: {e}")
            return {
                'success': False,
                'error': 'Erro ao obter estatísticas de usuário'
            }
    
    @staticmethod
    def get_error_logs(limit=50, severity=None):
        """Obter logs de erro recentes"""
        try:
            # Esta seria uma implementação mais complexa com sistema de logs
            # Por ora, simulamos com dados básicos
            logs = MonitoringService._get_application_logs(limit, severity)
            
            return {
                'success': True,
                'data': {
                    'logs': logs,
                    'total': len(logs),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter logs: {e}")
            return {
                'success': False,
                'error': 'Erro ao obter logs'
            }
    
    @staticmethod
    def get_dashboard_data():
        """Obter dados consolidados para dashboard de monitoramento"""
        try:
            # Combinar várias métricas para o dashboard
            system_status = MonitoringService.get_system_status()
            if not system_status['success']:
                return system_status
            
            user_stats = MonitoringService.get_user_activity_stats()
            performance = MonitoringService.get_performance_metrics()
            
            return {
                'success': True,
                'data': {
                    'overview': system_status['data'],
                    'user_activity': user_stats['data'] if user_stats['success'] else {},
                    'performance': performance['data'] if performance['success'] else {},
                    'alerts': MonitoringService._get_system_alerts(),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter dados do dashboard: {e}")
            return {
                'success': False,
                'error': 'Erro ao carregar dashboard de monitoramento'
            }
    
    # Métodos privados auxiliares
    
    @staticmethod
    def _get_system_info():
        """Obter informações do sistema operacional"""
        try:
            return {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.architecture()[0],
                'hostname': platform.node(),
                'python_version': sys.version.split()[0],
                'uptime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception:
            return {'error': 'Não foi possível obter informações do sistema'}
    
    @staticmethod
    def _get_hardware_info():
        """Obter informações de hardware"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memória
            memory = psutil.virtual_memory()
            
            # Disco
            disk = psutil.disk_usage('/')
            
            # Rede (se disponível)
            network = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                'memory': {
                    'total_mb': memory.total // (1024*1024),
                    'used_mb': memory.used // (1024*1024),
                    'available_mb': memory.available // (1024*1024),
                    'usage_percent': memory.percent
                },
                'disk': {
                    'total_gb': disk.total // (1024*1024*1024),
                    'used_gb': disk.used // (1024*1024*1024),
                    'free_gb': disk.free // (1024*1024*1024),
                    'usage_percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_received': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_received': network.packets_recv
                }
            }
        except Exception as e:
            return {'error': f'Não foi possível obter informações de hardware: {str(e)}'}
    
    @staticmethod
    def _get_application_stats():
        """Obter estatísticas da aplicação"""
        try:
            # Contadores básicos
            total_users = User.query.count()
            total_cultures = Culture.query.count()
            total_activities = Activity.query.count()
            
            # Atividades recentes
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            recent_activities = Activity.query.filter(
                Activity.created_at >= yesterday
            ).count()
            
            # Usuários ativos (últimos 7 dias)
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            active_users = User.query.filter(
                User.last_seen >= week_ago
            ).count() if hasattr(User, 'last_seen') else 0
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'total_cultures': total_cultures,
                'total_activities': total_activities,
                'recent_activities_24h': recent_activities,
                'growth_rate': MonitoringService._calculate_growth_rate()
            }
        except Exception as e:
            return {'error': f'Não foi possível obter estatísticas da aplicação: {str(e)}'}
    
    @staticmethod
    def _perform_health_checks():
        """Realizar verificações de saúde do sistema"""
        checks = {}
        
        # Verificar banco de dados
        checks['database'] = MonitoringService._check_database_connection()
        
        # Verificar recursos do sistema
        checks['resources'] = MonitoringService._check_basic_resources()
        
        # Verificar dependências críticas
        checks['dependencies'] = MonitoringService._check_dependencies()
        
        return checks
    
    @staticmethod
    def _check_database_connection():
        """Verificar conexão com banco de dados"""
        try:
            db.session.execute(text('SELECT 1'))
            return {
                'connected': True,
                'response_time_ms': 0,  # Poderia medir tempo real
                'status': 'healthy'
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'status': 'unhealthy'
            }
    
    @staticmethod
    def _check_basic_resources():
        """Verificar recursos básicos do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'adequate': cpu_percent < 90 and memory.percent < 90 and disk.percent < 90,
                'cpu_ok': cpu_percent < 90,
                'memory_ok': memory.percent < 90,
                'disk_ok': disk.percent < 90,
                'status': 'healthy' if cpu_percent < 90 and memory.percent < 90 else 'warning'
            }
        except Exception:
            return {
                'adequate': False,
                'status': 'error'
            }
    
    @staticmethod
    def _check_dependencies():
        """Verificar dependências críticas"""
        dependencies = {
            'psutil': True,
            'sqlalchemy': True,
            'flask': True
        }
        
        try:
            import psutil, sqlalchemy, flask
            return {
                'all_available': True,
                'details': dependencies,
                'status': 'healthy'
            }
        except ImportError as e:
            return {
                'all_available': False,
                'error': str(e),
                'status': 'unhealthy'
            }
    
    @staticmethod
    def _determine_overall_status(hardware_info, health_checks):
        """Determinar status geral do sistema"""
        try:
            # Verificar se há problemas críticos
            if not health_checks.get('database', {}).get('connected', False):
                return 'critical'
            
            # Verificar recursos
            if hardware_info.get('cpu', {}).get('usage_percent', 0) > 90:
                return 'critical'
            
            if hardware_info.get('memory', {}).get('usage_percent', 0) > 90:
                return 'critical'
            
            # Verificar warnings
            if (hardware_info.get('cpu', {}).get('usage_percent', 0) > 80 or
                hardware_info.get('memory', {}).get('usage_percent', 0) > 80):
                return 'warning'
            
            return 'healthy'
        except Exception:
            return 'unknown'
    
    @staticmethod
    def _get_cpu_history():
        """Obter histórico de CPU (simulado)"""
        # Em uma implementação real, isto viria de um sistema de métricas
        return {
            'current': psutil.cpu_percent(interval=0.1),
            'average_1h': 25.5,
            'average_24h': 22.3,
            'peak_24h': 67.8
        }
    
    @staticmethod
    def _get_memory_history():
        """Obter histórico de memória (simulado)"""
        memory = psutil.virtual_memory()
        return {
            'current': memory.percent,
            'average_1h': 45.2,
            'average_24h': 42.8,
            'peak_24h': 78.5
        }
    
    @staticmethod
    def _get_database_metrics():
        """Obter métricas do banco de dados"""
        try:
            # Métricas básicas (expandir conforme necessário)
            return {
                'total_tables': 10,  # Simulado
                'connection_pool_size': 5,  # Simulado
                'active_connections': 2,  # Simulado
                'query_performance': 'good'  # Simulado
            }
        except Exception:
            return {'error': 'Métricas de banco indisponíveis'}
    
    @staticmethod
    def _get_application_metrics():
        """Obter métricas da aplicação"""
        return {
            'response_time_avg': 145,  # ms simulado
            'requests_per_minute': 24,  # Simulado
            'error_rate': 0.02,  # 2% simulado
            'uptime_hours': 72  # Simulado
        }
    
    @staticmethod
    def _get_activity_in_period(start_date, end_date):
        """Obter atividades em um período"""
        try:
            count = Activity.query.filter(
                Activity.created_at >= start_date,
                Activity.created_at <= end_date
            ).count()
            return count
        except Exception:
            return 0
    
    @staticmethod
    def _get_top_active_users(limit=10):
        """Obter usuários mais ativos"""
        try:
            # Simulado - em implementação real seria mais complexo
            return [
                {'user_id': 1, 'email': 'user1@example.com', 'activity_count': 45},
                {'user_id': 2, 'email': 'user2@example.com', 'activity_count': 32}
            ]
        except Exception:
            return []
    
    @staticmethod
    def _get_activity_by_type():
        """Obter atividades por tipo"""
        try:
            # Simulado
            return {
                'plantio': 25,
                'colheita': 18,
                'irrigacao': 32,
                'monitoramento': 15
            }
        except Exception:
            return {}
    
    @staticmethod
    def _get_application_logs(limit=50, severity=None):
        """Obter logs da aplicação"""
        # Simulado - em implementação real integraria com sistema de logs
        return [
            {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'level': 'INFO',
                'message': 'Sistema funcionando normalmente',
                'module': 'monitoring'
            }
        ]
    
    @staticmethod
    def _get_system_alerts():
        """Obter alertas do sistema"""
        alerts = []
        
        try:
            # Verificar CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > 80:
                alerts.append({
                    'type': 'warning',
                    'message': f'CPU usage alto: {cpu_percent:.1f}%',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            # Verificar memória
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                alerts.append({
                    'type': 'warning',
                    'message': f'Memory usage alto: {memory.percent:.1f}%',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            return alerts
        except Exception:
            return []
    
    @staticmethod
    def _calculate_growth_rate():
        """Calcular taxa de crescimento"""
        try:
            # Implementação simplificada
            return {
                'users_growth_week': 5.2,  # % simulado
                'activities_growth_week': 12.8  # % simulado
            }
        except Exception:
            return {'error': 'Não foi possível calcular taxa de crescimento'}
