"""
Utilitários para tratamento de resposta e logging
"""
import logging
from flask import jsonify, render_template, request
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ResponseHandler:
    """
    Classe para padronizar respostas da aplicação
    """
    
    @staticmethod
    def is_json_request():
        """
        Verifica se a requisição espera resposta JSON
        """
        return (
            request.is_json or
            'application/json' in request.headers.get('Accept', '') or
            'json' in request.headers.get('Content-Type', '') or
            request.args.get('format') == 'json'
        )
    
    @staticmethod
    def success_response(data: Any = None, message: Optional[str] = None):
        """
        Retorna resposta de sucesso padronizada
        """
        response = {
            'success': True,
            'data': data
        }
        
        if message:
            response['message'] = message
            
        return jsonify(response)
    
    @staticmethod
    def error_response(error: str, code: int = 400, data: Any = None):
        """
        Retorna resposta de erro padronizada
        """
        response = {
            'success': False,
            'error': error
        }
        
        if data:
            response['data'] = data
            
        return jsonify(response), code
    
    @staticmethod
    def handle_response(data: Dict[str, Any], template: Optional[str] = None, **template_vars):
        """
        Trata resposta baseado no tipo de requisição
        """
        if ResponseHandler.is_json_request():
            return jsonify(data)
        elif template:
            return render_template(template, data=data, **template_vars)
        else:
            return jsonify(data)
    
    @staticmethod
    def handle_success(data: Any = None, status_code: int = 200, redirect_url: Optional[str] = None):
        """
        Método para tratamento de sucesso com suporte a redirecionamento
        """
        from flask import redirect
        
        # Se há URL de redirecionamento e não é uma requisição JSON, redirecionar
        if redirect_url and not ResponseHandler.is_json_request():
            return redirect(redirect_url)
        
        # Caso contrário, retornar JSON
        response = {
            'success': True,
            'data': data
        }
        
        if redirect_url:
            response['redirect_url'] = redirect_url
            
        return jsonify(response), status_code
    
    @staticmethod
    def handle_server_error(message: str = "Erro interno do servidor"):
        """
        Método para compatibilidade - retorna erro 500
        """
        return ResponseHandler.error_response(message, 500)


class LoggingHelper:
    """
    Classe auxiliar para logging padronizado
    """
    
    @staticmethod
    def log_request(endpoint: str, method: str, user: Optional[str] = None):
        """
        Log de requisição recebida
        """
        message = f"Request {method} {endpoint}"
        if user:
            message += f" by {user}"
        logger.info(message)
    
    @staticmethod
    def log_user_action(user: str, action: str, details: Optional[str] = None):
        """
        Log de ação do usuário
        """
        message = f"User {user} performed {action}"
        if details:
            message += f": {details}"
        logger.info(message)
    
    @staticmethod
    def log_error(error: Exception, context: Optional[str] = None):
        """
        Log de erro padronizado
        """
        message = f"Error: {str(error)}"
        if context:
            message = f"Error in {context}: {str(error)}"
        logger.error(message, exc_info=True)
    
    @staticmethod
    def log_warning(message: str, context: Optional[str] = None):
        """
        Log de aviso
        """
        if context:
            message = f"Warning in {context}: {message}"
        logger.warning(message)
    
    @staticmethod
    def log_info(message: str, context: Optional[str] = None):
        """
        Log de informação
        """
        if context:
            message = f"Info in {context}: {message}"
        logger.info(message)
