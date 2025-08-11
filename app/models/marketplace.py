"""
Modelo de marketplace
"""
from datetime import datetime, timezone
from app import db


class MarketplaceItem(db.Model):
    """Modelo para itens do marketplace"""
    __tablename__ = 'marketplace_items'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informações do produto
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # 'produtos', 'sementes', 'ferramentas', 'servicos'
    subcategory = db.Column(db.String(50))
    
    # Preço e quantidade
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='BRL')
    quantity_available = db.Column(db.Integer, default=1)
    unit = db.Column(db.String(20))  # 'kg', 'unidade', 'litro', etc.
    
    # Status e condições
    status = db.Column(db.String(20), default='active')  # 'active', 'sold', 'inactive'
    condition = db.Column(db.String(20), default='new')  # 'new', 'used', 'refurbished'
    
    # Localização
    location_city = db.Column(db.String(100))
    location_state = db.Column(db.String(50))
    shipping_available = db.Column(db.Boolean, default=False)
    pickup_available = db.Column(db.Boolean, default=True)
    
    # Imagens e mídia
    images = db.Column(db.JSON)  # Lista de URLs das imagens
    
    # Metadados
    views_count = db.Column(db.Integer, default=0)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "seller": self.seller.email if self.seller else None,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "subcategory": self.subcategory,
            "price": self.price,
            "currency": self.currency,
            "quantity_available": self.quantity_available,
            "unit": self.unit,
            "status": self.status,
            "condition": self.condition,
            "location_city": self.location_city,
            "location_state": self.location_state,
            "shipping_available": self.shipping_available,
            "pickup_available": self.pickup_available,
            "images": self.images,
            "views_count": self.views_count,
            "featured": self.featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

    def __repr__(self):
        return f'<MarketplaceItem {self.title}>'
