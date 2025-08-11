"""
Modelo de usuário
"""
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from app import db


class User(UserMixin, db.Model):
    """Modelo para usuários do sistema"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Informações pessoais
    nome_completo = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    
    # Nível de experiência
    experience_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    
    # Interesses do usuário (separados por vírgula)
    interesses = db.Column(db.String(200), nullable=True)
    
    # Informações da propriedade
    propriedade_nome = db.Column(db.String(120))
    # location = db.Column(db.String(200))  # TEMPORARIAMENTE COMENTADO - será adicionado via migration
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)
    ativo = db.Column(db.Boolean, default=True)
    
    # Onboarding
    onboarding_completed = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    farm = db.relationship('Farm', backref='owner', uselist=False, lazy=True)
    activities = db.relationship('Activity', backref='user', lazy=True)
    marketplace_items = db.relationship('MarketplaceItem', backref='seller', lazy=True)
    cultures = db.relationship('Culture', backref='user', lazy=True)

    def set_password(self, password):
        """Define a senha do usuário com hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            "id": self.id,
            "email": self.email,
            "nome_completo": self.nome_completo,
            "telefone": self.telefone,
            "experience_level": self.experience_level,
            "interesses": self.interesses,
            "propriedade_nome": self.propriedade_nome,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "cidade": self.cidade,
            "estado": self.estado,
            "data_criacao": (
                self.data_criacao.isoformat() if self.data_criacao else None
            ),
            "ultimo_acesso": (
                self.ultimo_acesso.isoformat() if self.ultimo_acesso else None
            ),
            "ativo": self.ativo,
            "onboarding_completed": self.onboarding_completed,
        }

    def __repr__(self):
        return f'<User {self.email}>'
