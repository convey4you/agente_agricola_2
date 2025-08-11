"""
Factory function para aplicação Flask - AgTech Portugal
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS

# Inicializar extensões
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Inicializar rate limiter
rate_limiter = None
try:
    from app.middleware.rate_limiter import RateLimitManager
    rate_limiter = RateLimitManager()
except ImportError as e:
    print(f"⚠️ RateLimitManager não disponível: {e}")


def create_app(config_name=None):
    """Factory function para criar aplicação Flask"""
    
    # Determinar configuração
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Carregar configurações - suporte para modo limpo
    if config_name == 'development_clean':
        from config_dev_clean import config
        app.config.from_object(config[config_name])
        print("🧹 Usando configuração de desenvolvimento limpa")
    else:
        from config import config
        app.config.from_object(config[config_name])
    
    # Verificar se deve desabilitar sistemas pesados
    disable_heavy_systems = (
        app.config.get('DISABLE_PERFORMANCE_MONITORING') or
        os.environ.get('DISABLE_PERFORMANCE_MONITORING') == 'true' or
        config_name == 'development_clean'
    )
    
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app, supports_credentials=True)
    
    # Inicializar rate limiter
    if rate_limiter is not None:
        try:
            rate_limiter.init_app(app)
            print("✅ Rate limiting configurado com sucesso")
        except Exception as e:
            print(f"⚠️ Aviso: Rate limiting não configurado: {e}")
    else:
        print("⚠️ Rate limiting não disponível - funcionando sem proteção")
    
    # Inicializar middleware de segurança
    try:
        from app.middleware.security import security_middleware, csrf_protection, security_audit
        security_middleware.init_app(app)
        csrf_protection.init_app(app)
        security_audit.init_app(app)
        print("✅ Middleware de segurança configurado com sucesso")
    except Exception as e:
        print(f"⚠️ Aviso: Middleware de segurança não configurado: {e}")
    
    # Inicializar middleware de sessão - CORREÇÃO SPRINT 1
    from app.middleware.session_middleware import session_middleware
    session_middleware.init_app(app)
    
    # Configurar Flask-Login ROBUSTO - CORREÇÃO SPRINT 1
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para aceder a esta página.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'  # Proteção forte de sessão
    login_manager.refresh_view = 'auth.login'
    login_manager.needs_refresh_message = 'Sessão expirada. Por favor, faça login novamente.'
    
    @login_manager.unauthorized_handler
    def unauthorized():
        """Handler customizado para usuários não autorizados"""
        from flask import request, jsonify, redirect, url_for
        from app.utils.auth_decorators import is_public_endpoint, is_public_path
        
        # Verificar se é uma rota pública
        if (is_public_endpoint(request.endpoint) or 
            is_public_path(request.path)):
            # Para rotas públicas, permitir acesso
            return None
        
        # Para APIs, retornar JSON
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({
                'success': False,
                'error': 'Autenticação requerida',
                'redirect': url_for('auth.login')
            }), 401
        
        # Para páginas web, redirecionar para login
        return redirect(url_for('auth.login'))
    
    @login_manager.user_loader
    def load_user(user_id):
        """User loader robusto com tratamento de erros - CORREÇÃO SPRINT 1"""
        try:
            from app.models.user import User
            from app.utils.auth_debug_logger import AuthDebugLogger
            
            if not user_id or user_id == 'None':
                AuthDebugLogger.log_user_loading(user_id, False, "Invalid user_id")
                return None
                
            user = User.query.get(int(user_id))
            if user and user.is_active:
                AuthDebugLogger.log_user_loading(user_id, True)
                return user
            else:
                AuthDebugLogger.log_user_loading(user_id, False, "User not found or inactive")
                return None
                
        except (ValueError, TypeError) as e:
            AuthDebugLogger.log_user_loading(user_id, False, f"Type error: {str(e)}")
            return None
        except Exception as e:
            AuthDebugLogger.log_user_loading(user_id, False, f"Unexpected error: {str(e)}")
            return None
    
    # Registrar modelos para que as migrações funcionem (marketplace removido)
    from app.models import user, farm, culture, activity, conversation, alerts
    
    # Registrar blueprints (controllers)
    register_blueprints(app)
    
    # Registrar handlers de erro
    register_error_handlers(app)
    
    # Inicialização simplificada do banco de dados
    with app.app_context():
        try:
            # Importar modelos essenciais (marketplace removido)
            from app.models import user, farm, activity, culture
            # Criar tabelas se não existirem (delegado para Flask-Migrate)
            db.create_all()
        except Exception as e:
            print(f"⚠️ Aviso na inicialização do banco: {e}")

    # Configurar contexto e logging
    setup_template_context(app)
    setup_logging(app)
    
    # Registrar rotas adicionais para compatibilidade
    register_compatibility_routes(app)
    
    return app


def register_compatibility_routes(app):
    """Registrar rotas de compatibilidade"""
    
    # Rota de informações da API (marketplace removido)
    @app.route('/api')
    def api_info():
        return {
            "message": "Agente Agrícola API",
            "version": "2.0.0",
            "status": "running",
            "endpoints": {
                "auth": "/auth",
                "dashboard": "/",
                "cultures": "/api/cultures",
                "agent": "/api/agent",
                "alerts": "/api/alerts"
            }
        }
    
    # Rotas para servir arquivos HTML estáticos (compatibilidade)
    @app.route('/login.html')
    def login_html():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    @app.route('/register.html')
    def register_html():
        from flask import redirect, url_for
        return redirect(url_for('auth.register'))
    
    @app.route('/index.html')
    def index_html():
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))
    
    # Rotas adicionais para URLs com prefixo /auth
    @app.route('/auth/login.html')
    def auth_login_html():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    @app.route('/auth/register.html')
    def auth_register_html():
        from flask import redirect, url_for
        return redirect(url_for('auth.register'))


def register_blueprints(app):
    """Registrar todos os blueprints"""
    
    # Rota para favicon
    @app.route('/favicon.ico')
    def favicon():
        from flask import send_from_directory
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
    # Rota para Service Worker com cache busting
    @app.route('/sw.js')
    def service_worker():
        from flask import send_from_directory, Response, make_response
        try:
            response = make_response(send_from_directory(os.path.join(app.root_path, 'static'), 'sw.js', mimetype='application/javascript'))
            # FORÇAR não-cache do Service Worker
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        except FileNotFoundError:
            # Fallback: Service Worker vazio se arquivo não existir
            response = Response('console.log("Service Worker não encontrado");', mimetype='application/javascript')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            return response
    
    # Controladores principais (marketplace removido)
    from app.controllers.auth_controller import auth_bp
    from app.controllers.dashboard_controller import dashboard_bp
    from app.controllers.culture_controller import culture_bp
    from app.controllers.agent_controller import agent_bp
    from app.controllers.alerts_controller import alerts_bp  # SPRINT 2 - Sistema de Alertas (UI)
    from app.routes.alerts_api import alerts_api_bp  # SPRINT 2 - API de Alertas Corrigida
    from app.controllers.cache_controller import cache_bp
    from app.routes.admin import admin_bp  # Sistema de detecção de bots
    from app.controllers.diagnostics_controller import diagnostics_bp  # CORREÇÃO SPRINT 1
    from app.controllers.health_controller import health_bp  # CORREÇÃO SPRINT 1 - Health Check
    from app.controllers.reports_controller import reports_bp  # REPORTS SYSTEM
    from app.controllers.geocoding_controller import geocoding_bp  # GEOCODING SERVICE
    from app.controllers.fixes_controller import fixes_bp  # CORREÇÕES CRÍTICAS
    
    # Registrar com prefixos apropriados (marketplace removido)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(culture_bp, url_prefix='/cultures')
    app.register_blueprint(agent_bp, url_prefix='/agent')
    app.register_blueprint(alerts_bp, url_prefix='/alerts')  # SPRINT 2 - Sistema de Alertas
    app.register_blueprint(cache_bp, url_prefix='/cache')
    app.register_blueprint(diagnostics_bp, url_prefix='/diagnostics')  # CORREÇÃO SPRINT 1
    app.register_blueprint(health_bp, url_prefix='/')  # CORREÇÃO SPRINT 1 - Health Check
    app.register_blueprint(reports_bp, url_prefix='/reports')  # REPORTS SYSTEM
    app.register_blueprint(geocoding_bp, url_prefix='/api/geocoding')  # GEOCODING SERVICE
    app.register_blueprint(fixes_bp, url_prefix='/admin/fixes')  # CORREÇÕES CRÍTICAS
    app.register_blueprint(admin_bp, url_prefix='/admin/bots')  # DETECÇÃO DE BOTS
    
    # API endpoints (para compatibilidade) - marketplace removido
    app.register_blueprint(auth_bp, url_prefix='/api/auth', name='api_auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard', name='api_dashboard')
    app.register_blueprint(culture_bp, url_prefix='/api/cultures', name='api_cultures')
    app.register_blueprint(agent_bp, url_prefix='/api/agent', name='api_agent')
    app.register_blueprint(alerts_api_bp, url_prefix='/api/alerts')  # SPRINT 2 - API Corrigida
    app.register_blueprint(cache_bp, url_prefix='/api/cache', name='api_cache')


def setup_template_context(app):
    """Configurar contexto global para templates"""
    
    @app.context_processor
    def inject_global_vars():
        from app.middleware.security import CSRFProtection
        import time
        import os
        
        # Cache busting baseado em timestamp de modificação ou deploy
        cache_version = str(int(time.time()))
        
        # Em produção, usar timestamp de inicialização da app para cache mais estável
        if not app.debug:
            if not hasattr(app, '_cache_version'):
                app._cache_version = str(int(time.time()))
            cache_version = app._cache_version
        
        return {
            'app_name': 'AgTech Portugal',
            'app_version': '2.0.0',
            'cache_version': cache_version,
            'csrf_token': CSRFProtection.generate_csrf_token
        }


def setup_logging(app):
    """Configurar sistema de logging"""
    import logging
    from logging.handlers import RotatingFileHandler
    
    if not app.debug and not app.testing:
        # Criar diretório de logs se não existir
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configurar handler de arquivo
        file_handler = RotatingFileHandler(
            'logs/agtech.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('AgTech Portugal startup')


def register_error_handlers(app):
    """Registrar handlers para erros"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template, request, jsonify
        
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Endpoint não encontrado'}), 404
        
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template, request, jsonify
        
        db.session.rollback()
        
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Erro interno do servidor'}), 500
        
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template, request, jsonify
        
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Acesso negado'}), 403
        
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        from flask import render_template, request, jsonify
        
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Não autorizado'}), 401
        
        return render_template('errors/401.html'), 401


# Para compatibilidade com versões anteriores
def init_app():
    """Função de compatibilidade"""
    return create_app()
