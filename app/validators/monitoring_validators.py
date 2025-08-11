"""
Monitoring Validators - Validações para o sistema de monitoramento
"""
from datetime import datetime, timezone, timedelta


class MonitoringValidator:
    """Classe para validações relacionadas ao monitoramento do sistema"""
    
    @staticmethod
    def validate_limit_parameter(limit=None):
        """Validar parâmetro de limite"""
        if limit is None:
            return True, None
        
        if not isinstance(limit, int):
            return False, "Limite deve ser um número inteiro"
        
        if limit < 1:
            return False, "Limite deve ser maior que zero"
        
        if limit > 1000:
            return False, "Limite muito alto (máximo: 1000)"
        
        return True, None
    
    @staticmethod
    def validate_severity_level(severity=None):
        """Validar nível de severidade"""
        if severity is None:
            return True, None
        
        if not isinstance(severity, str):
            return False, "Severidade deve ser uma string"
        
        valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
        if severity.lower() not in valid_levels:
            return False, f"Severidade inválida. Use: {', '.join(valid_levels)}"
        
        return True, None
    
    @staticmethod
    def validate_time_period(period=None):
        """Validar período de tempo"""
        if period is None:
            return True, None
        
        if not isinstance(period, str):
            return False, "Período deve ser uma string"
        
        valid_periods = ['1h', '24h', '7d', '30d', '1m', '3m', '6m', '1y']
        if period not in valid_periods:
            return False, f"Período inválido. Use: {', '.join(valid_periods)}"
        
        return True, None
    
    @staticmethod
    def validate_date_range(start_date=None, end_date=None):
        """Validar intervalo de datas"""
        if start_date is None and end_date is None:
            return True, None
        
        # Validar formato das datas
        try:
            if start_date:
                if isinstance(start_date, str):
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                else:
                    start_dt = start_date
            
            if end_date:
                if isinstance(end_date, str):
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                else:
                    end_dt = end_date
        except ValueError:
            return False, "Formato de data inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        
        # Validar lógica das datas
        if start_date and end_date:
            if start_dt >= end_dt:
                return False, "Data de início deve ser anterior à data de fim"
            
            # Verificar se o intervalo não é muito longo
            if (end_dt - start_dt).days > 365:
                return False, "Intervalo de datas muito longo (máximo: 1 ano)"
        
        # Verificar se as datas não são no futuro
        now = datetime.now(timezone.utc)
        if start_date and start_dt > now:
            return False, "Data de início não pode ser no futuro"
        
        if end_date and end_dt > now:
            return False, "Data de fim não pode ser no futuro"
        
        return True, None
    
    @staticmethod
    def validate_metric_type(metric_type=None):
        """Validar tipo de métrica"""
        if metric_type is None:
            return True, None
        
        if not isinstance(metric_type, str):
            return False, "Tipo de métrica deve ser uma string"
        
        valid_metrics = [
            'cpu', 'memory', 'disk', 'network', 'database', 
            'application', 'users', 'activities', 'errors'
        ]
        
        if metric_type.lower() not in valid_metrics:
            return False, f"Tipo de métrica inválido. Use: {', '.join(valid_metrics)}"
        
        return True, None
    
    @staticmethod
    def validate_aggregation_method(method=None):
        """Validar método de agregação"""
        if method is None:
            return True, None
        
        if not isinstance(method, str):
            return False, "Método de agregação deve ser uma string"
        
        valid_methods = ['avg', 'sum', 'min', 'max', 'count', 'last']
        if method.lower() not in valid_methods:
            return False, f"Método de agregação inválido. Use: {', '.join(valid_methods)}"
        
        return True, None
    
    @staticmethod
    def validate_threshold_values(cpu_threshold=None, memory_threshold=None, disk_threshold=None):
        """Validar valores de threshold"""
        thresholds = {
            'cpu_threshold': cpu_threshold,
            'memory_threshold': memory_threshold,
            'disk_threshold': disk_threshold
        }
        
        for name, value in thresholds.items():
            if value is not None:
                try:
                    threshold = float(value)
                    if threshold < 0 or threshold > 100:
                        return False, f"{name} deve estar entre 0 e 100"
                except (ValueError, TypeError):
                    return False, f"{name} deve ser um número válido"
        
        return True, None
    
    @staticmethod
    def validate_status_filter(status=None):
        """Validar filtro de status"""
        if status is None:
            return True, None
        
        if not isinstance(status, str):
            return False, "Status deve ser uma string"
        
        valid_statuses = ['healthy', 'warning', 'critical', 'unknown', 'unhealthy']
        if status.lower() not in valid_statuses:
            return False, f"Status inválido. Use: {', '.join(valid_statuses)}"
        
        return True, None
    
    @staticmethod
    def validate_refresh_interval(interval=None):
        """Validar intervalo de refresh"""
        if interval is None:
            return True, None
        
        if not isinstance(interval, int):
            return False, "Intervalo deve ser um número inteiro"
        
        if interval < 5:
            return False, "Intervalo mínimo é 5 segundos"
        
        if interval > 3600:
            return False, "Intervalo máximo é 3600 segundos (1 hora)"
        
        return True, None
    
    @staticmethod
    def validate_component_name(component=None):
        """Validar nome do componente"""
        if component is None:
            return True, None
        
        if not isinstance(component, str):
            return False, "Nome do componente deve ser uma string"
        
        valid_components = [
            'system', 'database', 'application', 'network', 'storage',
            'authentication', 'monitoring', 'logging', 'cache'
        ]
        
        if component.lower() not in valid_components:
            return False, f"Componente inválido. Use: {', '.join(valid_components)}"
        
        return True, None
    
    @staticmethod
    def validate_alert_parameters(alert_type=None, priority=None):
        """Validar parâmetros de alerta"""
        if alert_type is not None:
            if not isinstance(alert_type, str):
                return False, "Tipo de alerta deve ser uma string"
            
            valid_alert_types = ['info', 'warning', 'error', 'critical']
            if alert_type.lower() not in valid_alert_types:
                return False, f"Tipo de alerta inválido. Use: {', '.join(valid_alert_types)}"
        
        if priority is not None:
            if not isinstance(priority, str):
                return False, "Prioridade deve ser uma string"
            
            valid_priorities = ['low', 'medium', 'high', 'urgent']
            if priority.lower() not in valid_priorities:
                return False, f"Prioridade inválida. Use: {', '.join(valid_priorities)}"
        
        return True, None
    
    @staticmethod
    def validate_monitoring_config(config):
        """Validar configuração de monitoramento"""
        if not config:
            return False, "Configuração não fornecida"
        
        if not isinstance(config, dict):
            return False, "Configuração deve ser um objeto JSON"
        
        # Validar campos obrigatórios
        required_fields = ['enabled', 'refresh_interval']
        for field in required_fields:
            if field not in config:
                return False, f"Campo obrigatório '{field}' não encontrado"
        
        # Validar enabled
        if not isinstance(config['enabled'], bool):
            return False, "Campo 'enabled' deve ser booleano"
        
        # Validar refresh_interval
        is_valid, error_msg = MonitoringValidator.validate_refresh_interval(
            config['refresh_interval']
        )
        if not is_valid:
            return False, f"refresh_interval: {error_msg}"
        
        # Validar thresholds se fornecidos
        if 'thresholds' in config:
            thresholds = config['thresholds']
            if not isinstance(thresholds, dict):
                return False, "Thresholds devem ser um objeto"
            
            is_valid, error_msg = MonitoringValidator.validate_threshold_values(
                thresholds.get('cpu'),
                thresholds.get('memory'),
                thresholds.get('disk')
            )
            if not is_valid:
                return False, f"Thresholds: {error_msg}"
        
        return True, None
    
    @staticmethod
    def validate_export_format(format_type=None):
        """Validar formato de exportação"""
        if format_type is None:
            return True, None
        
        if not isinstance(format_type, str):
            return False, "Formato deve ser uma string"
        
        valid_formats = ['json', 'csv', 'xml', 'prometheus']
        if format_type.lower() not in valid_formats:
            return False, f"Formato inválido. Use: {', '.join(valid_formats)}"
        
        return True, None
