"""
Modelo Monitoramento - Dados de monitoramento
"""

from .. import db

class Monitoramento(db.Model):
    __tablename__ = 'monitoramentos'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # clima, solo, pragas, crescimento, etc.
    metrica = db.Column(db.String(100), nullable=False)  # temperatura, umidade, ph, altura, etc.
    valor = db.Column(db.Float, nullable=False)
    unidade = db.Column(db.String(20))  # °C, %, cm, kg, etc.
    data_coleta = db.Column(db.DateTime, nullable=False)
    localizacao = db.Column(db.String(200))  # coordenadas ou descrição
    equipamento = db.Column(db.String(100))  # sensor, equipamento usado
    observacoes = db.Column(db.Text)
    alerta = db.Column(db.Boolean, default=False)  # se requer atenção
    valor_minimo = db.Column(db.Float)  # para alertas automáticos
    valor_maximo = db.Column(db.Float)  # para alertas automáticos
    
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
            'tipo': self.tipo,
            'metrica': self.metrica,
            'valor': self.valor,
            'unidade': self.unidade,
            'data_coleta': self.data_coleta.isoformat() if self.data_coleta else None,
            'localizacao': self.localizacao,
            'equipamento': self.equipamento,
            'observacoes': self.observacoes,
            'alerta': self.alerta,
            'valor_minimo': self.valor_minimo,
            'valor_maximo': self.valor_maximo,
            'user_id': self.user_id,
            'cultura_id': self.cultura_id,
            'animal_id': self.animal_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def verificar_alerta(self):
        """Verifica se o valor está fora dos limites"""
        if self.valor_minimo and self.valor < self.valor_minimo:
            return True
        if self.valor_maximo and self.valor > self.valor_maximo:
            return True
        return False
    
    def status_valor(self):
        """Retorna o status do valor (normal, baixo, alto)"""
        if self.valor_minimo and self.valor < self.valor_minimo:
            return 'baixo'
        elif self.valor_maximo and self.valor > self.valor_maximo:
            return 'alto'
        return 'normal'
    
    def __repr__(self):
        return f'<Monitoramento {self.tipo} - {self.metrica}: {self.valor}{self.unidade}>'