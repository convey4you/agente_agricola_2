"""
Sistema Simplificado de Localizações
Adiciona localizações dos usuários diretamente na tabela weather_locations
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional
from app import db
from app.models.user import User
from app.models.weather import WeatherLocation
import math

logger = logging.getLogger(__name__)


class LocationManager:
    """
    Gerenciador simplificado de localizações meteorológicas
    Todos os pontos ficam na tabela weather_locations
    """
    
    # Raio em km para considerar localizações próximas como a mesma
    PROXIMITY_THRESHOLD_KM = 10
    
    @staticmethod
    def ensure_user_location(user: User) -> Optional[WeatherLocation]:
        """
        Garante que existe uma localização para o usuário
        Cria se necessário ou retorna existente próxima
        
        Args:
            user: Usuário com coordenadas
            
        Returns:
            WeatherLocation ou None se coordenadas inválidas
        """
        if not user.latitude or not user.longitude:
            return None
            
        try:
            # Buscar localização existente próxima
            existing = LocationManager._find_nearby_location(
                user.latitude, user.longitude
            )
            
            if existing:
                # Garantir que está ativa
                if not existing.is_active:
                    existing.is_active = True
                    db.session.commit()
                return existing
            
            # Criar nova localização
            location_name = (
                user.cidade if user.cidade 
                else user.propriedade_nome if user.propriedade_nome
                else f"Localização {user.id}"
            )
            
            new_location = WeatherLocation(
                name=location_name,
                latitude=user.latitude,
                longitude=user.longitude,
                country=user.estado or 'Portugal',
                is_active=True,
                is_default=False  # Localizações de usuários não são padrão
            )
            
            db.session.add(new_location)
            db.session.commit()
            
            logger.info(f"Nova localização criada para usuário {user.id}: {location_name}")
            return new_location
            
        except Exception as e:
            logger.error(f"Erro ao garantir localização para usuário {user.id}: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def _find_nearby_location(lat: float, lon: float) -> Optional[WeatherLocation]:
        """
        Busca localização existente próxima às coordenadas
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            WeatherLocation próxima ou None
        """
        # Buscar em área aproximada (mais eficiente que calcular distância para todas)
        margin = 0.1  # Aproximadamente 11km
        
        nearby_locations = WeatherLocation.query.filter(
            WeatherLocation.latitude.between(lat - margin, lat + margin),
            WeatherLocation.longitude.between(lon - margin, lon + margin)
        ).all()
        
        # Verificar distância exata
        for location in nearby_locations:
            distance = LocationManager._calculate_distance(
                lat, lon, location.latitude, location.longitude
            )
            if distance <= LocationManager.PROXIMITY_THRESHOLD_KM:
                return location
        
        return None
    
    @staticmethod
    def sync_all_users():
        """
        Sincroniza localizações para todos os usuários ativos
        Executa na inicialização e periodicamente
        """
        try:
            logger.info("Sincronizando localizações de todos os usuários...")
            
            # Buscar usuários ativos com coordenadas
            users_with_coords = User.query.filter(
                User.is_active == True,
                User.latitude.isnot(None),
                User.longitude.isnot(None),
                User.latitude != 0,
                User.longitude != 0
            ).all()
            
            created_count = 0
            updated_count = 0
            
            for user in users_with_coords:
                location = LocationManager.ensure_user_location(user)
                if location:
                    if location.id:  # Existente
                        updated_count += 1
                    else:  # Nova
                        created_count += 1
            
            # Desativar localizações sem usuários próximos
            inactive_count = LocationManager._cleanup_unused_locations()
            
            logger.info(f"Sincronização concluída: {created_count} criadas, "
                       f"{updated_count} atualizadas, {inactive_count} desativadas")
            
        except Exception as e:
            logger.error(f"Erro na sincronização de usuários: {e}")
    
    @staticmethod
    def _cleanup_unused_locations():
        """
        Desativa localizações de usuários que não têm mais usuários próximos
        
        Returns:
            Número de localizações desativadas
        """
        try:
            # Buscar localizações de usuários ativas
            user_locations = WeatherLocation.query.filter_by(
                is_default=False,
                is_active=True
            ).all()
            
            inactive_count = 0
            
            for location in user_locations:
                # Verificar se há usuários próximos
                nearby_users = User.query.filter(
                    User.is_active == True,
                    User.latitude.between(
                        location.latitude - 0.05,
                        location.latitude + 0.05
                    ),
                    User.longitude.between(
                        location.longitude - 0.05,
                        location.longitude + 0.05
                    )
                ).count()
                
                if nearby_users == 0:
                    location.is_active = False
                    inactive_count += 1
                    logger.info(f"Localização '{location.name}' desativada - sem usuários")
            
            if inactive_count > 0:
                db.session.commit()
            
            return inactive_count
            
        except Exception as e:
            logger.error(f"Erro na limpeza de localizações: {e}")
            db.session.rollback()
            return 0
    
    @staticmethod
    def get_user_weather_location(user_id: int) -> Optional[WeatherLocation]:
        """
        Retorna a localização meteorológica para um usuário específico
        
        Args:
            user_id: ID do usuário
            
        Returns:
            WeatherLocation ou None
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            return LocationManager.ensure_user_location(user)
            
        except Exception as e:
            logger.error(f"Erro ao obter localização do usuário {user_id}: {e}")
            return None
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula distância entre duas coordenadas usando fórmula de Haversine
        
        Args:
            lat1, lon1: Primeira coordenada
            lat2, lon2: Segunda coordenada
            
        Returns:
            Distância em quilômetros
        """
        # Raio da Terra em km
        R = 6371.0
        
        # Converter para radianos
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Diferenças
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Fórmula de Haversine
        a = (math.sin(dlat / 2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    @staticmethod
    def get_location_stats() -> dict:
        """
        Retorna estatísticas das localizações
        
        Returns:
            Dict com estatísticas
        """
        try:
            total_locations = WeatherLocation.query.filter_by(is_active=True).count()
            fixed_locations = WeatherLocation.query.filter_by(is_active=True, is_default=True).count()
            user_locations = WeatherLocation.query.filter_by(is_active=True, is_default=False).count()
            
            # Contar usuários com coordenadas
            users_with_coords = User.query.filter(
                User.is_active == True,
                User.latitude.isnot(None),
                User.longitude.isnot(None)
            ).count()
            
            return {
                'total_active_locations': total_locations,
                'fixed_locations': fixed_locations,
                'user_locations': user_locations,
                'users_with_coordinates': users_with_coords,
                'strategy': 'unified_table'
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
