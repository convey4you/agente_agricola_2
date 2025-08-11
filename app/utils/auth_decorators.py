"""
Decorador para rotas públicas que não requerem autenticação
"""
from functools import wraps
from flask import request, g


def public_route(f):
    """
    Decorador para marcar rotas como públicas (não requerem autenticação)
    
    Uso:
    @app.route('/api/public-endpoint')
    @public_route
    def public_endpoint():
        return {'message': 'Esta rota é pública'}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Marcar a rota como pública no contexto da requisição
        g.is_public_route = True
        return f(*args, **kwargs)
    
    return decorated_function


def is_public_route():
    """
    Verificar se a rota atual é marcada como pública
    
    Returns:
        bool: True se a rota é pública, False caso contrário
    """
    return getattr(g, 'is_public_route', False)


def get_public_routes():
    """
    Lista de endpoints que devem ser tratados como públicos
    
    Returns:
        list: Lista de endpoints públicos
    """
    return [
        'geocoding.search_locations',
        'geocoding.geocode_address', 
        'geocoding.validate_coordinates',
        'geocoding.detect_soil',
        'geocoding.detect_climate',
        'geocoding.test_public',
        'auth.login',
        'auth.register',
        'health.health_check',
        'health.status',
        'migration_web.migrate_interesses_web',
        'migration_web.check_migration'
    ]


def is_public_endpoint(endpoint):
    """
    Verificar se um endpoint específico é público
    
    Args:
        endpoint: Nome do endpoint
        
    Returns:
        bool: True se o endpoint é público
    """
    if not endpoint:
        return False
    
    public_routes = get_public_routes()
    return endpoint in public_routes


def is_public_path(path):
    """
    Verificar se um caminho específico é público
    
    Args:
        path: Caminho da URL
        
    Returns:
        bool: True se o caminho é público
    """
    if not path:
        return False
    
    public_paths = [
        '/api/geocoding',
        '/auth/login',
        '/auth/register',
        '/health',
        '/static',
        '/favicon.ico'
    ]
    
    return any(path.startswith(public_path) for public_path in public_paths)
