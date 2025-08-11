"""
Modelo User - Usuários do sistema
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relacionamentos
    culturas = db.relationship('Cultura', backref='proprietario', lazy=True, cascade='all, delete-orphan')
    animais = db.relationship('Animal', backref='proprietario', lazy=True, cascade='all, delete-orphan')
    tarefas = db.relationship('Tarefa', backref='responsavel', lazy=True, cascade='all, delete-orphan')
    monitoramentos = db.relationship('Monitoramento', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Define a senha do usuário com hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'email': self.email,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'
