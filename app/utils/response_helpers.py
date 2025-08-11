"""
Utilitários para tratamento de erros e respostas HTTP
"""
import logging
from typing import Dict, Any, Union, Tuple
from flask import jsonify, render_template, flash, request
from werkzeug.wrappers import Response


logger = logging.getLogger(__name__)


class ResponseHandler:
    """Classe para padronizar respostas HTTP"""
    
    @staticmethod
    def handle_error(error_msg: str, status_code: int = 400, template: str = None, **template_kwargs) -> Union[Response, str]:
        """
        Trata erros de forma consistente para JSON e HTML
        
        Args:
            error_msg: Mensagem de erro
            status_code: Código HTTP
            template: Template para renderizar (se não for JSON)
            **template_kwargs: Argumentos para o template
            
        Returns:
            Response apropriada (JSON ou HTML)
        """
        logger.warning(f"Erro tratado: {error_msg} (status: {status_code})")
        
        if request.is_json:
            return jsonify({'error': error_msg}), status_code
        
        flash(error_msg, 'error')
        if template:
            return render_template(template, **template_kwargs)
        
        return render_template('auth/login.html')
    
    @staticmethod
    def handle_success(data: Dict[str, Any], status_code: int = 200, template: str = None, redirect_url: str = None, **template_kwargs) -> Union[Response, str]:
        """
        Trata sucessos de forma consistente para JSON e HTML
        
        Args:
            data: Dados de sucesso
            status_code: Código HTTP
            template: Template para renderizar (se não for JSON)
            redirect_url: URL para redirecionamento (se não for JSON)
            **template_kwargs: Argumentos para o template
            
        Returns:
            Response apropriada (JSON ou HTML)
        """
        logger.info(f"Sucesso: {data.get('message', 'Operação realizada')}")
        
        if request.is_json:
            # Incluir success: true para compatibilidade com JavaScript
            response_data = {'success': True}
            response_data.update(data)
            return jsonify(response_data), status_code
        
        # Para requisições HTML
        if data.get('message'):
            flash(data['message'], 'success')
        
        if redirect_url:
            from flask import redirect
            return redirect(redirect_url)
        
        if template:
            return render_template(template, **template_kwargs)
        
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))
    
    @staticmethod
    def handle_validation_error(error_msg: str, template: str = 'auth/login.html', **template_kwargs) -> Union[Response, str]:
        """
        Trata erros de validação
        
        Args:
            error_msg: Mensagem de erro
            template: Template para renderizar
            **template_kwargs: Argumentos para o template
            
        Returns:
            Response apropriada
        """
        return ResponseHandler.handle_error(error_msg, 400, template, **template_kwargs)
    
    @staticmethod
    def handle_auth_error(error_msg: str = 'Credenciais inválidas', template: str = 'auth/login.html', **template_kwargs) -> Union[Response, str]:
        """
        Trata erros de autenticação
        
        Args:
            error_msg: Mensagem de erro
            template: Template para renderizar
            **template_kwargs: Argumentos para o template
            
        Returns:
            Response apropriada
        """
        return ResponseHandler.handle_error(error_msg, 401, template, **template_kwargs)
    
    @staticmethod
    def handle_server_error(error_msg: str = 'Erro interno do servidor', template: str = 'auth/login.html', **template_kwargs) -> Union[Response, str]:
        """
        Trata erros internos do servidor
        
        Args:
            error_msg: Mensagem de erro
            template: Template para renderizar
            **template_kwargs: Argumentos para o template
            
        Returns:
            Response apropriada
        """
        return ResponseHandler.handle_error(error_msg, 500, template, **template_kwargs)


class LoggingHelper:
    """Helper para logging consistente"""
    
    @staticmethod
    def log_request(endpoint: str, method: str, user_email: str = None):
        """
        Log de requisição
        
        Args:
            endpoint: Endpoint acessado
            method: Método HTTP
            user_email: Email do usuário (se autenticado)
        """
        user_info = f" - User: {user_email}" if user_email else ""
        logger.info(f"{method} {endpoint}{user_info}")
    
    @staticmethod
    def log_auth_attempt(email: str, success: bool):
        """
        Log de tentativa de autenticação
        
        Args:
            email: Email do usuário
            success: Se foi bem-sucedida
        """
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"AUTH_ATTEMPT: {email} - {status}")
    
    @staticmethod
    def log_user_action(user_email: str, action: str, details: str = None):
        """
        Log de ação do usuário
        
        Args:
            user_email: Email do usuário
            action: Ação realizada
            details: Detalhes adicionais
        """
        details_info = f" - {details}" if details else ""
        logger.info(f"USER_ACTION: {user_email} - {action}{details_info}")
    
    @staticmethod
    def log_error(error: Exception, context: str = None):
        """
        Log de erro com contexto
        
        Args:
            error: Exceção capturada
            context: Contexto onde ocorreu o erro
        """
        context_info = f" in {context}" if context else ""
        logger.error(f"ERROR{context_info}: {str(error)}", exc_info=True)
