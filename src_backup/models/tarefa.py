"""
Modelo Tarefa - Tarefas de manejo
"""

from .. import db

class Tarefa(db.Model):
    __tablename__ = 'tarefas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(50), nullable=False)  # plantio, irrigacao, colheita, vacinacao, etc.
    prioridade = db.Column(db.String(20), default='media')  # baixa, media, alta, urgente
    status = db.Column(db.String(20), default='pendente')  # pendente, em_andamento, concluida, cancelada
    data_inicio = db.Column(db.DateTime)
    data_fim = db.Column(db.DateTime)
    data_prevista = db.Column(db.DateTime)
    tempo_estimado = db.Column(db.Integer)  # em horas
    tempo_real = db.Column(db.Integer)  # em horas
    custo_estimado = db.Column(db.Float)
    custo_real = db.Column(db.Float)
    observacoes = db.Column(db.Text)
    
    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cultura_id = db.Column(db.Integer, db.ForeignKey('culturas.id'), nullable=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animais.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'prioridade': self.prioridade,
            'status': self.status,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'data_prevista': self.data_prevista.isoformat() if self.data_prevista else None,
            'tempo_estimado': self.tempo_estimado,
            'tempo_real': self.tempo_real,
            'custo_estimado': self.custo_estimado,
            'custo_real': self.custo_real,
            'observacoes': self.observacoes,
            'user_id': self.user_id,
            'cultura_id': self.cultura_id,
            'animal_id': self.animal_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calcular_eficiencia(self):
        """Calcula a eficiência da tarefa (tempo real vs estimado)"""
        if self.tempo_estimado and self.tempo_real:
            return (self.tempo_estimado / self.tempo_real) * 100
        return 0
    
    def is_atrasada(self):
        """Verifica se a tarefa está atrasada"""
        from datetime import datetime
        if self.data_prevista and self.status != 'concluida':
            return datetime.now() > self.data_prevista
        return False
    
    def __repr__(self):
        return f'<Tarefa {self.titulo} - {self.status}>'
