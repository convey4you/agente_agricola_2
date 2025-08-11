from flask import session, request, redirect, url_for, flash
from functools import wraps
from app.controllers.portugal_controller import portugal as portugal_routes
from flask_login import current_user

def configure_portugal_routes(app):
    """Configura as rotas portuguesas e middleware de seleção de versão"""
    # Registra o blueprint português
    app.register_blueprint(portugal_routes)
    
    # Middleware para selecionar template apropriado
    @app.before_request
    def check_portugal_version():
        """
        Verifica se o usuário está usando a versão portuguesa e
        redireciona para as rotas apropriadas conforme necessário
        """
        # Só aplicar para usuários autenticados
        if not current_user.is_authenticated:
            return
            
        # Só verificar para rotas que têm versões portuguesas
        portugal_paths = [
            '/', 
            '/clima/previsao',
            '/alertas',
            '/gestao/culturas',
            '/gestao/culturas/nova',
        ]
        
        # Se caminho atual está na lista e tem versão portuguesa ativa
        is_portugal_path = any(request.path.startswith(p) for p in portugal_paths)
        using_portugal = session.get('portugal_version', False)
        
        if is_portugal_path:
            # Se está usando versão portuguesa mas não está na rota /portugal
            if using_portugal and not request.path.startswith('/portugal'):
                new_path = f"/portugal{request.path}"
                return redirect(new_path)
            
            # Se não está usando versão portuguesa mas está na rota /portugal
            elif not using_portugal and request.path.startswith('/portugal'):
                new_path = request.path.replace('/portugal', '', 1) or '/'
                return redirect(new_path)
    
    return app

def portugal_version_required(f):
    """
    Decorator para exigir que a versão portuguesa esteja ativa
    para acessar certas rotas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('portugal_version', False):
            flash('Este recurso requer a versão portuguesa', 'info')
            return redirect(url_for('portugal.toggle_version'))
        return f(*args, **kwargs)
    return decorated_function
