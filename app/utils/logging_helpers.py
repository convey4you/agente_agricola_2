"""
Logging Helpers - Utilitários para logging estruturado
"""
from flask import current_app
from datetime import datetime, timezone
import traceback


class LoggingHelper:
    """Classe para logging estruturado da aplicação"""
    
    @staticmethod
    def log_request(endpoint, method, user_email=None):
        """Log de requisição HTTP"""
        try:
            current_app.logger.info(
                f"REQUEST - {method} {endpoint} - User: {user_email or 'Anonymous'}"
            )
        except Exception:
            pass  # Não quebrar a aplicação por erro de log
    
    @staticmethod
    def log_user_action(user_email, action, details=None):
        """Log de ação do usuário"""
        try:
            log_msg = f"USER_ACTION - {user_email} - {action}"
            if details:
                log_msg += f" - Details: {details}"
            current_app.logger.info(log_msg)
        except Exception:
            pass
    
    @staticmethod
    def log_error(error, context=None, user_email=None):
        """Log de erro com contexto"""
        try:
            log_msg = f"ERROR - {context or 'Unknown'}"
            if user_email:
                log_msg += f" - User: {user_email}"
            log_msg += f" - {str(error)}"
            
            current_app.logger.error(log_msg)
            current_app.logger.error(f"TRACEBACK: {traceback.format_exc()}")
        except Exception:
            pass
    
    @staticmethod
    def log_warning(message, context=None, user_email=None):
        """Log de warning"""
        try:
            log_msg = f"WARNING - {context or 'Unknown'}"
            if user_email:
                log_msg += f" - User: {user_email}"
            log_msg += f" - {message}"
            
            current_app.logger.warning(log_msg)
        except Exception:
            pass
    
    @staticmethod
    def log_debug(message, context=None):
        """Log de debug"""
        try:
            log_msg = f"DEBUG - {context or 'Unknown'} - {message}"
            current_app.logger.debug(log_msg)
        except Exception:
            pass
    
    @staticmethod
    def log_performance(operation, duration_ms, user_email=None):
        """Log de performance"""
        try:
            log_msg = f"PERFORMANCE - {operation} - {duration_ms}ms"
            if user_email:
                log_msg += f" - User: {user_email}"
            current_app.logger.info(log_msg)
        except Exception:
            pass
    
    @staticmethod
    def log_database_operation(operation, table, user_email=None):
        """Log de operação de banco de dados"""
        try:
            log_msg = f"DB_OPERATION - {operation} on {table}"
            if user_email:
                log_msg += f" - User: {user_email}"
            current_app.logger.info(log_msg)
        except Exception:
            pass
