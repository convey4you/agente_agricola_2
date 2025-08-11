# app/utils/logging_config.py
import logging
import json
import sys
import os
from datetime import datetime
from flask import request, g, has_request_context
from functools import wraps
import traceback

# Flag para ambiente de desenvolvimento silencioso
SILENT_DEV_MODE = os.getenv('SILENT_DEV', 'false').lower() == 'true'

class SilentFormatter(logging.Formatter):
    """Formatter minimalista para desenvolvimento"""
    
    def format(self, record):
        if record.levelno >= logging.ERROR:
            return f"ERRO: {record.getMessage()}"
        return ""

class StructuredFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON (apenas para produção)"""
    
    def format(self, record):
        # Em modo desenvolvimento silencioso, não formatar logs detalhados
        if SILENT_DEV_MODE and record.levelno < logging.ERROR:
            return ""
            
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Adicionar contexto da requisição se disponível
        if has_request_context():
            try:
                if hasattr(g, 'user_id'):
                    log_entry['user_id'] = g.user_id
                
                if request:
                    log_entry['request'] = {
                        'method': request.method,
                        'url': request.url,
                        'path': request.path,
                        'remote_addr': request.remote_addr,
                        'user_agent': request.headers.get('User-Agent', ''),
                        'referrer': request.headers.get('Referer', ''),
                        'content_length': request.content_length
                    }
            except RuntimeError:
                # Contexto de request não disponível
                pass
        
        # Adicionar informações de exceção se presente
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Adicionar campos extras
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging(level='INFO', log_file='logs/agrotech.log', json_format=True):
    """Configurar sistema de logging estruturado ou silencioso baseado no ambiente"""
    
    # Verificar se está no modo de desenvolvimento silencioso
    if SILENT_DEV_MODE or os.getenv('FLASK_ENV') == 'development':
        # Configuração ultra-silenciosa para desenvolvimento
        logging.basicConfig(
            level=logging.CRITICAL,
            format='%(message)s',
            handlers=[logging.NullHandler()]
        )
        
        # Silenciar todos os loggers verbosos
        verbose_loggers = [
            'werkzeug', 'urllib3', 'requests', 'apscheduler',
            'app.utils.health_checks', 'app.utils.cache_optimization',
            'app.utils.performance_monitoring', 'app.services'
        ]
        
        for logger_name in verbose_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.CRITICAL)
            logger.disabled = True
        
        # Apenas erros críticos no console
        critical_handler = logging.StreamHandler()
        critical_handler.setLevel(logging.CRITICAL)
        critical_handler.setFormatter(SilentFormatter())
        
        root_logger = logging.getLogger()
        root_logger.handlers = [critical_handler]
        root_logger.setLevel(logging.CRITICAL)
        
        return
    
    # Configuração normal para produção
    # Criar diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    
    # Configurar formatter estruturado
    formatter = StructuredFormatter()
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Handler para arquivo geral
    file_handler = logging.FileHandler('logs/agrotech.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para erros
    error_handler = logging.FileHandler('logs/agrotech_errors.log')
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Handler para auditoria
    audit_handler = logging.FileHandler('logs/agrotech_audit.log')
    audit_handler.setFormatter(formatter)
    audit_handler.setLevel(logging.INFO)
    
    # Configurar logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Limpar handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Adicionar handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Configurar logger de auditoria
    audit_logger_obj = logging.getLogger('audit')
    audit_logger_obj.setLevel(logging.INFO)
    audit_logger_obj.addHandler(audit_handler)
    
    # Configurar loggers de bibliotecas
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Log de inicialização
    logging.info("Sistema de logging estruturado configurado", extra={
        'component': 'logging_system',
        'action': 'setup_complete',
        'level': level,
        'log_file': log_file
    })
    
    return root_logger

def log_performance(func):
    """Decorator para logging de performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        
        try:
            result = func(*args, **kwargs)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logging.getLogger(__name__).info(
                f"Function {func.__name__} executed successfully",
                extra={
                    'extra_fields': {
                        'component': 'performance',
                        'function': func.__name__,
                        'duration_seconds': duration,
                        'status': 'success',
                        'module': func.__module__
                    }
                }
            )
            
            return result
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logging.getLogger(__name__).error(
                f"Function {func.__name__} failed: {str(e)}",
                exc_info=True,
                extra={
                    'extra_fields': {
                        'component': 'performance',
                        'function': func.__name__,
                        'duration_seconds': duration,
                        'status': 'error',
                        'error_type': type(e).__name__,
                        'module': func.__module__
                    }
                }
            )
            
            raise
    
    return wrapper

class AuditLogger:
    """Logger para auditoria de ações do usuário"""
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
    
    def log_user_action(self, user_id, action, resource_type, resource_id=None, details=None):
        """Registrar ação do usuário"""
        self.logger.info(
            f"User action: {action} on {resource_type}",
            extra={
                'extra_fields': {
                    'audit_type': 'user_action',
                    'user_id': user_id,
                    'action': action,
                    'resource_type': resource_type,
                    'resource_id': resource_id,
                    'details': details or {},
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        )
    
    def log_system_event(self, event_type, description, severity='info', details=None):
        """Registrar evento do sistema"""
        log_method = getattr(self.logger, severity, self.logger.info)
        
        log_method(
            f"System event: {description}",
            extra={
                'extra_fields': {
                    'audit_type': 'system_event',
                    'event_type': event_type,
                    'severity': severity,
                    'details': details or {},
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        )
    
    def log_security_event(self, event_type, user_id=None, ip_address=None, details=None):
        """Registrar evento de segurança"""
        self.logger.warning(
            f"Security event: {event_type}",
            extra={
                'extra_fields': {
                    'audit_type': 'security_event',
                    'event_type': event_type,
                    'user_id': user_id,
                    'ip_address': ip_address,
                    'details': details or {},
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        )

# Instância global do audit logger
audit_logger = AuditLogger()
