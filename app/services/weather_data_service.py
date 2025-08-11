"""
Serviço Principal de Dados Climáticos
Substitui WeatherService e WeatherServiceV2
Foca apenas na consulta do banco de dados local
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from app.models.weather import WeatherData, WeatherLocation, WeatherStats

logger = logging.getLogger(__name__)


class WeatherDataService:
    """
    Serviço principal para dados climáticos
    Consulta apenas dados locais do banco
    Não faz chamadas para APIs externas
    """
    
    @staticmethod
    def get_current_weather(location_name: str = None, lat: float = None, lon: float = None) -> Dict[str, any]:
        """
        Obtém dados climáticos atuais do banco de dados
        
        Args:
            location_name: Nome da localização (ex: "Lisboa")
            lat: Latitude (alternativa ao nome)
            lon: Longitude (alternativa ao nome)
            
        Returns:
            Dict com dados climáticos ou dados padrão se não encontrado
        """
        try:
            # Estratégia de busca em cascata
            weather_data = None
            
            if location_name:
                # 1. Buscar por nome da localização primeiro
                logger.info(f"Buscando dados para localização: {location_name}")
                location = WeatherLocation.query.filter(
                    WeatherLocation.name.ilike(f'%{location_name}%'),
                    WeatherLocation.is_active == True
                ).first()
                
                if location:
                    # Buscar dados climáticos para essa localização
                    weather_data = WeatherData.query.filter(
                        WeatherData.latitude.between(location.latitude - 0.01, location.latitude + 0.01),
                        WeatherData.longitude.between(location.longitude - 0.01, location.longitude + 0.01),
                        WeatherData.is_current == True
                    ).order_by(WeatherData.collected_at.desc()).first()
                    logger.info(f"Dados encontrados via localização: {weather_data is not None}")
                
                # 2. Se não encontrou por nome, tentar por cidade na tabela weather_data
                if not weather_data:
                    logger.info(f"Tentando busca direta por cidade: {location_name}")
                    weather_data = WeatherData.query.filter(
                        WeatherData.location_name.ilike(f'%{location_name}%'),
                        WeatherData.is_current == True
                    ).order_by(WeatherData.collected_at.desc()).first()
                    logger.info(f"Dados encontrados via busca direta: {weather_data is not None}")
            
            elif lat is not None and lon is not None:
                # 1. Buscar por coordenadas exatas primeiro
                logger.info(f"Buscando por coordenadas exatas: {lat}, {lon}")
                weather_data = WeatherData.query.filter(
                    WeatherData.latitude.between(lat - 0.01, lat + 0.01),
                    WeatherData.longitude.between(lon - 0.01, lon + 0.01),
                    WeatherData.is_current == True
                ).order_by(WeatherData.collected_at.desc()).first()
                logger.info(f"Dados encontrados: {weather_data is not None}")
            
            else:
                # Usar localização padrão (último registro atual)
                logger.info("Usando localização padrão (último registro)")
                weather_data = WeatherData.query.filter_by(is_current=True).order_by(WeatherData.collected_at.desc()).first()
            
            if weather_data:
                logger.info(f"Dados climáticos encontrados: {weather_data.location_name}, {weather_data.temperature}°C")
                formatted_data = WeatherDataService._format_weather_response(weather_data)
                return {
                    'success': True,
                    'data': formatted_data
                }
            else:
                logger.warning(f"Nenhum dado climático encontrado para {location_name or 'coordenadas fornecidas'}")
                default_data = WeatherDataService._get_default_weather()
                return {
                    'success': False,
                    'data': default_data,
                    'message': 'Dados não encontrados'
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter dados climáticos: {e}")
            default_data = WeatherDataService._get_default_weather()
            return {
                'success': False,
                'data': default_data,
                'error': str(e)
            }
    
    @staticmethod
    def get_weather_forecast(location_name: str = None, days: int = 5) -> List[Dict[str, any]]:
        """
        Obtém previsão do tempo do banco de dados
        
        Args:
            location_name: Nome da localização
            days: Número de dias para previsão (padrão: 5)
            
        Returns:
            Lista com previsão dos próximos dias
        """
        try:
            # Encontrar localização
            location = None
            if location_name:
                location = WeatherLocation.query.filter(
                    WeatherLocation.name.ilike(f'%{location_name}%'),
                    WeatherLocation.is_active == True
                ).first()
            
            if not location:
                # Usar primeira localização ativa
                location = WeatherLocation.query.filter_by(is_active=True).first()
            
            if not location:
                return []
            
            # Buscar dados de previsão mais recentes
            weather_data = WeatherData.get_current_for_location(
                location.latitude, 
                location.longitude
            )
            
            if weather_data and weather_data.forecast_data:
                forecast_list = weather_data.forecast_data
                
                # Limitar ao número de dias solicitado
                if isinstance(forecast_list, list):
                    return forecast_list[:days]
            
            return []
            
        except Exception as e:
            logger.error(f"Erro ao obter previsão: {e}")
            return []
    
    @staticmethod
    def get_weather_history(location_name: str = None, days: int = 7) -> List[Dict[str, any]]:
        """
        Obtém histórico climático dos últimos dias
        
        Args:
            location_name: Nome da localização
            days: Número de dias para histórico (padrão: 7)
            
        Returns:
            Lista com dados históricos
        """
        try:
            # Encontrar localização
            location = None
            if location_name:
                location = WeatherLocation.query.filter(
                    WeatherLocation.name.ilike(f'%{location_name}%'),
                    WeatherLocation.is_active == True
                ).first()
            
            if not location:
                location = WeatherLocation.query.filter_by(is_active=True).first()
            
            if not location:
                return []
            
            # Calcular período
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Buscar dados históricos
            history_data = WeatherData.get_history_for_location(
                location.latitude,
                location.longitude,
                start_date,
                end_date
            )
            
            # Formatar resposta
            formatted_history = []
            for record in history_data:
                formatted_history.append(WeatherDataService._format_weather_response(record))
            
            return formatted_history
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {e}")
            return []
    
    @staticmethod
    def get_weather_statistics(location_name: str = None, period: str = 'daily', days: int = 30) -> Dict[str, any]:
        """
        Obtém estatísticas climáticas
        
        Args:
            location_name: Nome da localização
            period: Tipo de período ('daily', 'weekly', 'monthly')
            days: Número de dias para análise
            
        Returns:
            Dict com estatísticas
        """
        try:
            # Encontrar localização
            location = None
            if location_name:
                location = WeatherLocation.query.filter(
                    WeatherLocation.name.ilike(f'%{location_name}%'),
                    WeatherLocation.is_active == True
                ).first()
            
            if not location:
                location = WeatherLocation.query.filter_by(is_active=True).first()
            
            if not location:
                return {}
            
            # Calcular período
            end_date = datetime.now(timezone.utc).date()
            start_date = end_date - timedelta(days=days)
            
            # Buscar estatísticas
            stats = WeatherStats.query.filter(
                WeatherStats.location_id == location.id,
                WeatherStats.period_type == period,
                WeatherStats.period_date >= start_date,
                WeatherStats.period_date <= end_date
            ).order_by(WeatherStats.period_date.desc()).all()
            
            if not stats:
                return {}
            
            # Calcular médias do período
            total_stats = len(stats)
            avg_temp = sum(s.temp_avg for s in stats) / total_stats
            avg_humidity = sum(s.humidity_avg for s in stats) / total_stats
            avg_wind = sum(s.wind_avg for s in stats) / total_stats
            
            return {
                'location': location.name,
                'period': period,
                'days_analyzed': days,
                'records_found': total_stats,
                'temperature': {
                    'average': round(avg_temp, 1),
                    'min': min(s.temp_min for s in stats),
                    'max': max(s.temp_max for s in stats)
                },
                'humidity': {
                    'average': round(avg_humidity, 1),
                    'min': min(s.humidity_min for s in stats),
                    'max': max(s.humidity_max for s in stats)
                },
                'wind': {
                    'average': round(avg_wind, 1),
                    'max': max(s.wind_max for s in stats)
                },
                'weather_patterns': {
                    'total_rainy_hours': sum(s.rainy_hours or 0 for s in stats),
                    'total_sunny_hours': sum(s.sunny_hours or 0 for s in stats),
                    'total_readings': sum(s.total_readings or 0 for s in stats)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    @staticmethod
    def get_available_locations() -> List[Dict[str, any]]:
        """
        Lista todas as localizações disponíveis
        
        Returns:
            Lista com localizações ativas
        """
        try:
            locations = WeatherLocation.get_active_locations()
            
            result = []
            for location in locations:
                # Verificar se há dados atuais
                current_data = WeatherData.get_current_for_location(
                    location.latitude,
                    location.longitude
                )
                
                result.append({
                    'id': location.id,
                    'name': location.name,
                    'country': location.country,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'has_current_data': current_data is not None,
                    'last_update': current_data.collected_at.isoformat() if current_data else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao listar localizações: {e}")
            return []
    
    @staticmethod
    def get_data_freshness() -> Dict[str, any]:
        """
        Verifica atualização dos dados
        
        Returns:
            Dict com informações sobre atualização dos dados
        """
        try:
            # Buscar dados mais recentes
            latest_data = WeatherData.query.filter_by(
                is_current=True
            ).order_by(WeatherData.collected_at.desc()).first()
            
            if not latest_data:
                return {
                    'status': 'no_data',
                    'message': 'Nenhum dado disponível',
                    'needs_collection': True
                }
            
            # Verificar idade dos dados
            now = datetime.now(timezone.utc)
            age_hours = (now - latest_data.collected_at).total_seconds() / 3600
            
            if age_hours <= 1:
                status = 'fresh'
                message = 'Dados muito atuais'
            elif age_hours <= 2:
                status = 'current'
                message = 'Dados atuais'
            elif age_hours <= 6:
                status = 'acceptable'
                message = 'Dados aceitáveis'
            else:
                status = 'stale'
                message = 'Dados desatualizados'
            
            return {
                'status': status,
                'message': message,
                'last_collection': latest_data.collected_at.isoformat(),
                'age_hours': round(age_hours, 1),
                'data_quality': latest_data.data_quality,
                'needs_collection': age_hours > 2,
                'total_locations': WeatherData.query.filter_by(is_current=True).count()
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar atualização: {e}")
            return {
                'status': 'error',
                'message': f'Erro: {str(e)}',
                'needs_collection': True
            }
    
    @staticmethod
    def _format_weather_response(weather_data: WeatherData) -> Dict[str, any]:
        """
        Formata dados para resposta padronizada
        
        Args:
            weather_data: Objeto WeatherData
            
        Returns:
            Dict formatado para resposta
        """
        # Processar dados de forecast se disponíveis
        forecast = []
        if weather_data.forecast_data:
            try:
                import json
                if isinstance(weather_data.forecast_data, str):
                    forecast_data = json.loads(weather_data.forecast_data)
                else:
                    forecast_data = weather_data.forecast_data
                
                if isinstance(forecast_data, list):
                    # Limitar a 5 dias e formatar
                    for day_data in forecast_data[:5]:
                        if isinstance(day_data, dict):
                            forecast.append({
                                'date': day_data.get('date'),
                                'condition': day_data.get('condition', 'N/A'),
                                'temp_max': day_data.get('temp_max'),
                                'temp_min': day_data.get('temp_min'),
                                'humidity': day_data.get('humidity'),
                                'icon': WeatherDataService._get_condition_icon(day_data.get('condition', ''))
                            })
            except Exception as e:
                logger.warning(f"Erro ao processar forecast: {e}")
                forecast = []
        
        return {
            'temperature': weather_data.temperature,
            'feels_like': weather_data.feels_like,
            'condition': weather_data.condition,
            'description': weather_data.description or weather_data.condition,
            'humidity': weather_data.humidity,
            'pressure': weather_data.pressure,
            'wind_speed': weather_data.wind_speed,
            'wind_direction': weather_data.wind_direction,
            'visibility': weather_data.visibility,
            'uv_index': 0,  # Campo não disponível no modelo atual
            'location_name': weather_data.location_name,
            'latitude': weather_data.latitude,
            'longitude': weather_data.longitude,
            'collected_at': weather_data.collected_at.isoformat(),
            'is_current': weather_data.is_current,
            'data_quality': weather_data.data_quality,
            'source': 'database_cache',
            'forecast': forecast,  # Incluir dados de previsão
            # Campos para compatibilidade com template
            'location': {
                'name': weather_data.location_name,
                'latitude': weather_data.latitude,
                'longitude': weather_data.longitude
            },
            'timestamp': weather_data.collected_at.isoformat()
        }
    
    @staticmethod
    def _get_condition_icon(condition: str) -> str:
        """
        Retorna ícone Font Awesome baseado na condição climática
        
        Args:
            condition: Condição climática
            
        Returns:
            Classe do ícone Font Awesome
        """
        condition_lower = condition.lower()
        
        if 'sol' in condition_lower or 'limpo' in condition_lower or 'clear' in condition_lower:
            return 'fas fa-sun'
        elif 'chuva' in condition_lower or 'rain' in condition_lower or 'chover' in condition_lower:
            return 'fas fa-cloud-rain'
        elif 'neve' in condition_lower or 'snow' in condition_lower:
            return 'fas fa-snowflake'
        elif 'nublado' in condition_lower or 'cloud' in condition_lower or 'nuvem' in condition_lower:
            return 'fas fa-cloud'
        elif 'tempestade' in condition_lower or 'storm' in condition_lower or 'thunder' in condition_lower:
            return 'fas fa-bolt'
        elif 'névoa' in condition_lower or 'fog' in condition_lower or 'mist' in condition_lower:
            return 'fas fa-smog'
        elif 'vento' in condition_lower or 'wind' in condition_lower:
            return 'fas fa-wind'
        else:
            return 'fas fa-cloud-sun'  # Ícone padrão
    
    @staticmethod
    def _get_default_weather() -> Dict[str, any]:
        """
        Retorna dados climáticos padrão quando não há dados disponíveis
        
        Returns:
            Dict com dados padrão
        """
        return {
            'temperature': 20,
            'condition': 'Dados indisponíveis',
            'description': 'Aguardando coleta de dados',
            'humidity': 50,
            'pressure': 1013,
            'wind_speed': 0,
            'wind_direction': 0,
            'visibility': 10,
            'uv_index': 0,
            'location': {
                'name': 'Portugal',
                'latitude': 39.3999,
                'longitude': -8.2245
            },
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'is_current': False,
            'data_quality': 'unavailable',
            'source': 'default_fallback'
        }
