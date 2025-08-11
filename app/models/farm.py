"""
Modelo de fazenda/propriedade
"""
from datetime import datetime, timezone
from app import db


class Farm(db.Model):
    """Modelo para fazendas/propriedades"""
    __tablename__ = 'farms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    area_total = db.Column(db.Float)  # Área total em hectares
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Localização
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50), default='Brasil')
    postal_code = db.Column(db.String(20))
    
    # Metadados (atualizados conforme migração)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    cultures = db.relationship('Culture', backref='farm', lazy=True)
    activities = db.relationship('Activity', backref='farm', lazy=True)

    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "area_total": self.area_total,
            "user_id": self.user_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }

    def __repr__(self):
        return f'<Farm {self.name}>'
