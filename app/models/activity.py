"""
Modelo de atividade/tarefa
"""
from datetime import datetime, timezone
from app import db


class Activity(db.Model):
    """Modelo para atividades/tarefas agrícolas"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=True)
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id'), nullable=True)
    
    # Informações da atividade
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(50), nullable=False)  # 'plantio', 'irrigacao', 'fertilizacao', 'colheita', etc.
    
    # Datas e status
    data_prevista = db.Column(db.DateTime, nullable=False)
    data_concluida = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='pendente')  # 'pendente', 'em_andamento', 'concluida', 'cancelada'
    prioridade = db.Column(db.String(20), default='media')  # 'baixa', 'media', 'alta', 'urgente'
    
    # Recursos necessários
    recursos_necessarios = db.Column(db.JSON)  # Ex: {'ferramentas': ['enxada'], 'materiais': ['sementes']}
    custo_estimado = db.Column(db.Float)
    tempo_estimado_horas = db.Column(db.Float)
    
    # Resultado
    resultado = db.Column(db.Text)  # Observações sobre o resultado da atividade
    custo_real = db.Column(db.Float)
    tempo_real_horas = db.Column(db.Float)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "farm_id": self.farm_id,
            "culture_id": self.culture_id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "tipo": self.tipo,
            "data_prevista": self.data_prevista.isoformat() if self.data_prevista else None,
            "data_concluida": self.data_concluida.isoformat() if self.data_concluida else None,
            "status": self.status,
            "prioridade": self.prioridade,
            "recursos_necessarios": self.recursos_necessarios,
            "custo_estimado": self.custo_estimado,
            "tempo_estimado_horas": self.tempo_estimado_horas,
            "resultado": self.resultado,
            "custo_real": self.custo_real,
            "tempo_real_horas": self.tempo_real_horas,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Activity {self.titulo}>'
