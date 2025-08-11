"""
Modelo Animal - Animais da fazenda
"""

from .. import db

class Animal(db.Model):
    __tablename__ = 'animais'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)  # bovino, suino, aves, etc.
    raca = db.Column(db.String(50))
    sexo = db.Column(db.String(10))  # macho, femea
    idade = db.Column(db.Integer)  # em meses
    peso = db.Column(db.Float)  # em kg
    data_nascimento = db.Column(db.Date)
    data_aquisicao = db.Column(db.Date)
    valor_aquisicao = db.Column(db.Float)
    status = db.Column(db.String(20), default='ativo')  # ativo, vendido, morto
    identificacao = db.Column(db.String(50))  # chip, brinco, etc.
    observacoes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relacionamentos
    tarefas = db.relationship('Tarefa', backref='animal', lazy=True, cascade='all, delete-orphan')
    monitoramentos = db.relationship('Monitoramento', backref='animal', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'especie': self.especie,
            'raca': self.raca,
            'sexo': self.sexo,
            'idade': self.idade,
            'peso': self.peso,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'data_aquisicao': self.data_aquisicao.isoformat() if self.data_aquisicao else None,
            'valor_aquisicao': self.valor_aquisicao,
            'status': self.status,
            'identificacao': self.identificacao,
            'observacoes': self.observacoes,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calcular_idade_atual(self):
        """Calcula a idade atual em meses"""
        from datetime import date
        if self.data_nascimento:
            hoje = date.today()
            anos = hoje.year - self.data_nascimento.year
            meses = hoje.month - self.data_nascimento.month
            return anos * 12 + meses
        return self.idade or 0
    
    def __repr__(self):
        return f'<Animal {self.nome} - {self.especie}>'
