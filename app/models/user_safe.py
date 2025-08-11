"""
Modelo de usuário com migração segura para Railway
"""
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from sqlalchemy import inspect


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
    
    # Informações da propriedade
    propriedade_nome = db.Column(db.String(120))
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

    def __init__(self, **kwargs):
        """Inicializar usuário com verificação de colunas"""
        super().__init__()
        
        # Verificar se a coluna interesses existe
        try:
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            self._has_interesses_column = 'interesses' in columns
        except:
            self._has_interesses_column = False
        
        # Aplicar kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def interesses(self):
        """Getter para interesses com verificação de coluna"""
        if hasattr(self, '_interesses'):
            return self._interesses
        
        if self._has_interesses_column:
            try:
                # Tentar buscar do banco
                result = db.session.execute(
                    db.text("SELECT interesses FROM users WHERE id = :user_id"),
                    {"user_id": self.id}
                ).fetchone()
                return result[0] if result else None
            except:
                return None
        return None

    @interesses.setter
    def interesses(self, value):
        """Setter para interesses com verificação de coluna"""
        self._interesses = value
        
        if self._has_interesses_column and self.id:
            try:
                db.session.execute(
                    db.text("UPDATE users SET interesses = :value WHERE id = :user_id"),
                    {"value": value, "user_id": self.id}
                )
                db.session.commit()
            except:
                pass

    def set_password(self, password):
        """Define a senha do usuário"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Converte o usuário para dicionário"""
        data = {
            'id': self.id,
            'email': self.email,
            'nome_completo': self.nome_completo,
            'telefone': self.telefone,
            'experience_level': self.experience_level,
            'propriedade_nome': self.propriedade_nome,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'cidade': self.cidade,
            'estado': self.estado,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None,
            'ativo': self.ativo,
            'onboarding_completed': self.onboarding_completed
        }
        
        # Adicionar interesses se disponível
        try:
            data['interesses'] = self.interesses
        except:
            data['interesses'] = None
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data
    
    def get_interests_list(self):
        """Retorna os interesses como lista"""
        if self.interesses:
            return [interest.strip() for interest in self.interesses.split(',')]
        return []
    
    def set_interests_list(self, interests):
        """Define os interesses a partir de uma lista"""
        if interests and isinstance(interests, list):
            self.interesses = ','.join(interests)
        else:
            self.interesses = None

    def __repr__(self):
        return f'<User {self.email}>'
