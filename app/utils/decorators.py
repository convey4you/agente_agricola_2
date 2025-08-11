"""
Decoradores utilitários
"""
from functools import wraps
from flask import jsonify, request, redirect, url_for
from flask_login import current_user


def api_login_required(f):
    """Decorador para exigir login em rotas de API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Autenticação necessária'}), 401
        return f(*args, **kwargs)
    return decorated_function


def validate_json(required_fields=None):
    """Decorador para validar dados JSON"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type deve ser application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Dados JSON não fornecidos'}), 400
            
            if required_fields:
                missing_fields = [field for field in required_fields if not data.get(field)]
                if missing_fields:
                    return jsonify({
                        'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorador para exigir permissão de admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Autenticação necessária'}), 401
            return redirect(url_for('auth.login'))
        
        # Assumindo que usuários com ID 1 são admin (você pode implementar um campo is_admin)
        if current_user.id != 1:
            if request.is_json:
                return jsonify({'error': 'Permissão de administrador necessária'}), 403
            return jsonify({'error': 'Acesso negado'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def handle_db_errors(f):
    """Decorador para tratar erros de banco de dados"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            from app import db
            db.session.rollback()
            
            error_message = str(e)
            if 'UNIQUE constraint failed' in error_message:
                return jsonify({'error': 'Dados duplicados. Verifique os valores únicos.'}), 409
            elif 'FOREIGN KEY constraint failed' in error_message:
                return jsonify({'error': 'Referência inválida. Verifique as relações.'}), 400
            else:
                return jsonify({'error': 'Erro interno do servidor'}), 500
    return decorated_function
