"""
Modelo de cultura
"""
from datetime import datetime, timezone
from app import db


class CultureType(db.Model):
    """Tipos de cultura disponíveis"""
    __tablename__ = 'culture_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)  # 'fruit_tree', 'vegetable', 'grain', 'herb'
    growing_season = db.Column(db.String(50))  # 'spring', 'summer', 'autumn', 'winter', 'all_year'
    planting_depth_cm = db.Column(db.Float)
    spacing_cm = db.Column(db.Float)
    days_to_germination = db.Column(db.Integer)
    days_to_harvest = db.Column(db.Integer)
    water_requirements = db.Column(db.String(20))  # 'low', 'medium', 'high'
    sunlight_requirements = db.Column(db.String(20))  # 'full_sun', 'partial_shade', 'shade'
    soil_ph_min = db.Column(db.Float)
    soil_ph_max = db.Column(db.Float)
    
    # Relacionamentos
    cultures = db.relationship('Culture', backref='culture_type', lazy=True)


class Culture(db.Model):
    """Modelo para culturas da propriedade"""
    __tablename__ = 'cultures'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=True)
    culture_type_id = db.Column(db.Integer, db.ForeignKey('culture_types.id'), nullable=False)
    
    # Informações básicas
    nome = db.Column(db.String(100), nullable=False)
    variedade = db.Column(db.String(100))
    
    # Datas importantes
    data_plantio = db.Column(db.Date)
    data_colheita_prevista = db.Column(db.Date)
    
    # Área e localização
    area_plantada = db.Column(db.Float)  # em metros quadrados
    localizacao = db.Column(db.String(200))  # descrição da localização na quinta
    
    # Status e saúde
    is_active = db.Column(db.Boolean, default=True)
    health_status = db.Column(db.String(20), default='healthy')  # 'healthy', 'warning', 'critical'
    observacoes = db.Column(db.Text)
    
    # Métricas de produção
    expected_yield_kg = db.Column(db.Float)
    actual_yield_kg = db.Column(db.Float)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    activities = db.relationship('Activity', backref='culture', lazy=True)

    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "farm_id": self.farm_id,
            "culture_type_id": self.culture_type_id,
            "nome": self.nome,
            "variedade": self.variedade,
            "data_plantio": self.data_plantio.isoformat() if self.data_plantio else None,
            "data_colheita_prevista": self.data_colheita_prevista.isoformat() if self.data_colheita_prevista else None,
            "area_plantada": self.area_plantada,
            "localizacao": self.localizacao,
            "is_active": self.is_active,
            "health_status": self.health_status,
            "observacoes": self.observacoes,
            "expected_yield_kg": self.expected_yield_kg,
            "actual_yield_kg": self.actual_yield_kg,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Culture {self.nome} - {self.variedade}>'
