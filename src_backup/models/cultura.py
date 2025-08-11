"""
Modelo Cultura - Culturas agrícolas
"""

from .. import db

class Cultura(db.Model):
    __tablename__ = 'culturas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # cereais, legumes, frutas, etc.
    variedade = db.Column(db.String(100))
    area_plantada = db.Column(db.Float)  # em hectares
    data_plantio = db.Column(db.Date)
    data_colheita_prevista = db.Column(db.Date)
    data_colheita_real = db.Column(db.Date)
    status = db.Column(db.String(20), default='planejado')  # planejado, plantado, crescendo, colhido
    producao_estimada = db.Column(db.Float)  # em toneladas
    producao_real = db.Column(db.Float)  # em toneladas
    observacoes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relacionamentos
    tarefas = db.relationship('Tarefa', backref='cultura', lazy=True, cascade='all, delete-orphan')
    monitoramentos = db.relationship('Monitoramento', backref='cultura', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'variedade': self.variedade,
            'area_plantada': self.area_plantada,
            'data_plantio': self.data_plantio.isoformat() if self.data_plantio else None,
            'data_colheita_prevista': self.data_colheita_prevista.isoformat() if self.data_colheita_prevista else None,
            'data_colheita_real': self.data_colheita_real.isoformat() if self.data_colheita_real else None,
            'status': self.status,
            'producao_estimada': self.producao_estimada,
            'producao_real': self.producao_real,
            'observacoes': self.observacoes,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calcular_rendimento(self):
        """Calcula o rendimento por hectare"""
        if self.area_plantada and self.producao_real:
            return self.producao_real / self.area_plantada
        return 0
    
    def __repr__(self):
        return f'<Cultura {self.nome} - {self.tipo}>'
