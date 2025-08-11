"""
Modelos para dados climáticos - ATUALIZADO conforme banco otimizado
"""
from app import db
from datetime import datetime, timedelta


class WeatherLocation(db.Model):
    """Modelo para localização de dados climáticos"""
    __tablename__ = 'weather_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    country = db.Column(db.String(5), nullable=False)
    timezone = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento apenas com WeatherStats (que tem FK)
    weather_stats = db.relationship('WeatherStats', backref='location', lazy=True)

    @staticmethod
    def get_active_locations():
        """Obtém todas as localizações ativas"""
        return WeatherLocation.query.filter_by(is_active=True).all()


class WeatherData(db.Model):
    """Modelo para dados climáticos coletados"""
    __tablename__ = 'weather_data'
    
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Timestamps
    collected_at = db.Column(db.DateTime, nullable=False)
    api_timestamp = db.Column(db.DateTime)
    
    # Dados climáticos principais
    temperature = db.Column(db.Float, nullable=False)
    feels_like = db.Column(db.Float)
    humidity = db.Column(db.Integer, nullable=False)
    pressure = db.Column(db.Integer, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    wind_direction = db.Column(db.Integer)
    visibility = db.Column(db.Integer)
    
    # Condições climáticas
    condition = db.Column(db.String(100), nullable=False)
    condition_code = db.Column(db.String(10))
    description = db.Column(db.String(200))
    
    # Dados adicionais em JSON
    forecast_data = db.Column(db.Text)  # JSON
    alerts_data = db.Column(db.Text)    # JSON
    
    # Controle e qualidade
    is_current = db.Column(db.Boolean, nullable=False, default=False)
    api_source = db.Column(db.String(50), nullable=False)
    api_response_time = db.Column(db.Float)
    data_quality = db.Column(db.String(20), nullable=False)
    error_message = db.Column(db.Text)
    
    # Timestamps de controle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_latest_current():
        """Obtém o registro mais recente marcado como current"""
        return WeatherData.query.filter_by(is_current=True).order_by(WeatherData.collected_at.desc()).first()
    
    @staticmethod
    def get_current_for_location(latitude, longitude, tolerance=0.01):
        """Obtém dados atuais para uma localização específica"""
        return WeatherData.query.filter(
            WeatherData.latitude.between(latitude - tolerance, latitude + tolerance),
            WeatherData.longitude.between(longitude - tolerance, longitude + tolerance),
            WeatherData.is_current == True
        ).order_by(WeatherData.collected_at.desc()).first()
    
    @staticmethod
    def get_history_for_location(latitude, longitude, days=7, tolerance=0.01):
        """Obtém histórico para uma localização"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return WeatherData.query.filter(
            WeatherData.latitude.between(latitude - tolerance, latitude + tolerance),
            WeatherData.longitude.between(longitude - tolerance, longitude + tolerance),
            WeatherData.collected_at >= start_date
        ).order_by(WeatherData.collected_at.desc()).all()


class WeatherStats(db.Model):
    """Modelo para estatísticas climáticas agregadas"""
    __tablename__ = 'weather_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('weather_locations.id'), nullable=False)
    
    # Período das estatísticas
    period_type = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly
    period_date = db.Column(db.Date, nullable=False)
    
    # Estatísticas de temperatura
    temp_avg = db.Column(db.Float)
    temp_min = db.Column(db.Float)
    temp_max = db.Column(db.Float)
    
    # Estatísticas de umidade
    humidity_avg = db.Column(db.Float)
    humidity_min = db.Column(db.Integer)
    humidity_max = db.Column(db.Integer)
    
    # Estatísticas de vento
    wind_avg = db.Column(db.Float)
    wind_max = db.Column(db.Float)
    
    # Dados adicionais
    total_readings = db.Column(db.Integer)
    rainy_hours = db.Column(db.Integer)
    sunny_hours = db.Column(db.Integer)
    total_rain = db.Column(db.Float)
    total_snow = db.Column(db.Float)
    data_points = db.Column(db.Integer)  # Número de medições no período
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
