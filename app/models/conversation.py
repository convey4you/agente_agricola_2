"""
Modelos para conversas com o agente inteligente
"""
from datetime import datetime, timezone
from app import db


class Conversation(db.Model):
    """Conversas do usuário com o agente"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    messages = db.relationship('Message', backref='conversation', lazy=True, 
                              cascade='all, delete-orphan')
    user = db.relationship('User', backref='conversations')


class Message(db.Model):
    """Mensagens individuais dentro de uma conversa"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    
    # Conteúdo da mensagem
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' ou 'assistant'
    
    # Metadados
    tokens_used = db.Column(db.Integer)
    response_time_ms = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Converte mensagem para dicionário"""
        return {
            'id': self.id,
            'content': self.content,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
