"""
Agente Agrícola - Sistema de Gestão Agrícola Inteligente
Versão 1.0 - Railway Deploy com PostgreSQL
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Instâncias globais
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='development'):
    """Factory para criar instância da aplicação Flask"""
    
    app = Flask(__name__)
    
    # Configuração baseada no ambiente
    if config_name == 'production':
        from .config import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        from .config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from .config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    # User loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.cultura import cultura_bp
    from .routes.animal import animal_bp
    from .routes.tarefa import tarefa_bp
    from .routes.monitoramento import monitoramento_bp
    from .routes.clima import clima_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(cultura_bp)
    app.register_blueprint(animal_bp)
    app.register_blueprint(tarefa_bp)
    app.register_blueprint(monitoramento_bp)
    app.register_blueprint(clima_bp)
    
    # Rota principal
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    return app
