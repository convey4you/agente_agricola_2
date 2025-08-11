"""
Serviço de Coleta de Dados Climáticos
Sistema automatizado para buscar e armazenar dados meteorológicos
"""
import requests
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from flask import current_app
from app import db
from app.models.weather import WeatherData, WeatherLocation, WeatherStats
from app.services.location_manager import LocationManager

logger = logging.getLogger(__name__)


class WeatherCollectorService:
    """
    Serviço responsável por coletar dados da API externa e armazenar no DB
    Executa automaticamente a cada hora via task scheduler
    """
    
    @staticmethod
    def collect_all_locations() -> Dict[str, any]:
        """
        Coleta dados de todas as localizações ativas
        Função principal chamada pelo scheduler
        
        Returns:
            Dict com resultado da coleta
        """
        results = {
            'success': True,
            'locations_processed': 0,
            'locations_failed': 0,
            'errors': [],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Sincronizar localizações dos usuários antes da coleta
            try:
                LocationManager.sync_all_users()
            except Exception as e:
                logger.warning(f"Erro na sincronização de localizações: {e}")
            
            # Obter todas as localizações ativas da tabela
            locations = WeatherLocation.query.filter_by(is_active=True).all()
            
            if not locations:
                logger.warning("Nenhuma localização ativa encontrada")
                return results
            
            for location in locations:
                try:
                    success = WeatherCollectorService.collect_location_data(location)
                    if success:
                        results['locations_processed'] += 1
                        logger.info(f"Dados coletados com sucesso para {location.name}")
                    else:
                        results['locations_failed'] += 1
                        results['errors'].append(f"Falha na coleta para {location.name}")
                        
                except Exception as e:
                    results['locations_failed'] += 1
                    error_msg = f"Erro ao processar {location.name}: {str(e)}"
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
            
            # Atualizar estatísticas se houve coletas bem-sucedidas
            if results['locations_processed'] > 0:
                WeatherCollectorService.update_statistics()
                
        except Exception as e:
            results['success'] = False
            results['errors'].append(f"Erro geral na coleta: {str(e)}")
            logger.error(f"Erro na coleta automática: {e}")
        
        return results
    
    @staticmethod
    def collect_location_data(location: WeatherLocation) -> bool:
        """
        Coleta dados para uma localização específica
        
        Args:
            location: Objeto WeatherLocation
            
        Returns:
            bool: True se coleta foi bem-sucedida
        """
        try:
            api_key = current_app.config.get('WEATHER_API_KEY')
            if not api_key:
                logger.error("WEATHER_API_KEY não configurada")
                return False
            
            # Buscar dados atuais da API
            current_data = WeatherCollectorService._fetch_current_weather(
                location.latitude, 
                location.longitude, 
                api_key
            )
            
            if not current_data:
                logger.error(f"Falha ao obter dados atuais para {location.name}")
                return False
            
            # Buscar previsão (opcional)
            forecast_data = WeatherCollectorService._fetch_forecast_weather(
                location.latitude,
                location.longitude,
                api_key
            )
            
            # Marcar registros anteriores como não-atuais
            WeatherCollectorService._mark_previous_as_old(location)
            
            # Criar novo registro
            weather_record = WeatherData.create_from_api_data(
                current_data,
                {
                    'name': location.name,
                    'latitude': location.latitude,
                    'longitude': location.longitude
                },
                forecast_data
            )
            
            db.session.add(weather_record)
            db.session.commit()
            
            logger.info(f"Dados salvos para {location.name}: {weather_record.temperature}°C")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados para {location.name}: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def _fetch_current_weather(lat: float, lon: float, api_key: str) -> Optional[Dict]:
        """
        Busca dados atuais da API OpenWeatherMap
        
        Args:
            lat: Latitude
            lon: Longitude  
            api_key: Chave da API
            
        Returns:
            Dict com dados da API ou None se falhou
        """
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric',
                'lang': 'pt'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Validar estrutura básica
            if not data.get('main') or not data.get('weather'):
                logger.error("Dados da API incompletos")
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição da API: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao processar dados da API: {e}")
            return None
    
    @staticmethod
    def _fetch_forecast_weather(lat: float, lon: float, api_key: str) -> Optional[List[Dict]]:
        """
        Busca previsão de 5 dias da API
        
        Args:
            lat: Latitude
            lon: Longitude
            api_key: Chave da API
            
        Returns:
            List com dados de previsão ou None
        """
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric',
                'lang': 'pt'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('list'):
                return None
            
            # Processar previsão para próximos 5 dias (pegar 1 registro por dia ao meio-dia)
            forecast_list = []
            processed_dates = set()
            
            for item in data['list']:
                # Obter data do item
                dt = datetime.fromtimestamp(item['dt'], tz=timezone.utc)
                date_str = dt.strftime('%Y-%m-%d')
                
                # Pegar apenas 1 registro por dia (preferencialmente meio-dia)
                if date_str not in processed_dates and len(forecast_list) < 5:
                    forecast_list.append({
                        'date': dt.isoformat(),
                        'condition': item['weather'][0]['description'],
                        'temp_max': item['main']['temp_max'],
                        'temp_min': item['main']['temp_min'],
                        'humidity': item['main']['humidity'],
                        'pressure': item['main']['pressure'],
                        'wind_speed': item.get('wind', {}).get('speed', 0)
                    })
                    processed_dates.add(date_str)
            
            return forecast_list
            
        except Exception as e:
            logger.error(f"Erro ao buscar previsão: {e}")
            return None
    
    @staticmethod
    def _mark_previous_as_old(location: WeatherLocation):
        """
        Marca registros anteriores como não-atuais
        
        Args:
            location: Localização para atualizar
        """
        try:
            WeatherData.query.filter_by(
                latitude=location.latitude,
                longitude=location.longitude,
                is_current=True
            ).update({'is_current': False})
            
        except Exception as e:
            logger.error(f"Erro ao marcar registros antigos: {e}")
    
    @staticmethod
    def update_statistics():
        """
        Atualiza estatísticas pré-calculadas
        Executa após coleta bem-sucedida
        """
        try:
            today = datetime.now(timezone.utc).date()
            
            # Atualizar estatísticas diárias para cada localização
            locations = WeatherLocation.get_active_locations()
            
            for location in locations:
                # Obter dados do dia
                start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
                end_of_day = start_of_day + timedelta(days=1)
                
                daily_data = WeatherData.query.filter(
                    WeatherData.latitude == location.latitude,
                    WeatherData.longitude == location.longitude,
                    WeatherData.collected_at >= start_of_day,
                    WeatherData.collected_at < end_of_day
                ).all()
                
                if daily_data:
                    WeatherCollectorService._calculate_daily_stats(location, today, daily_data)
                    
        except Exception as e:
            logger.error(f"Erro ao atualizar estatísticas: {e}")
    
    @staticmethod
    def _calculate_daily_stats(location: WeatherLocation, date, data_records: List[WeatherData]):
        """
        Calcula estatísticas diárias
        
        Args:
            location: Localização
            date: Data das estatísticas
            data_records: Lista de registros do dia
        """
        try:
            if not data_records:
                return
            
            # Calcular estatísticas
            temperatures = [r.temperature for r in data_records]
            humidities = [r.humidity for r in data_records]
            wind_speeds = [r.wind_speed for r in data_records]
            
            # Verificar se já existe registro
            existing_stats = WeatherStats.query.filter_by(
                location_id=location.id,
                period_type='daily',
                period_date=date
            ).first()
            
            if existing_stats:
                # Atualizar existente
                stats = existing_stats
            else:
                # Criar novo
                stats = WeatherStats(
                    location_id=location.id,
                    period_type='daily',
                    period_date=date
                )
            
            # Atualizar valores
            stats.temp_avg = sum(temperatures) / len(temperatures)
            stats.temp_min = min(temperatures)
            stats.temp_max = max(temperatures)
            
            stats.humidity_avg = sum(humidities) / len(humidities)
            stats.humidity_min = min(humidities)
            stats.humidity_max = max(humidities)
            
            stats.wind_avg = sum(wind_speeds) / len(wind_speeds)
            stats.wind_max = max(wind_speeds)
            
            stats.total_readings = len(data_records)
            
            # Contar condições
            conditions = [r.condition.lower() for r in data_records]
            stats.rainy_hours = sum(1 for c in conditions if 'chuva' in c or 'rain' in c)
            stats.sunny_hours = sum(1 for c in conditions if 'sol' in c or 'clear' in c or 'sun' in c)
            
            if not existing_stats:
                db.session.add(stats)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas diárias: {e}")
            db.session.rollback()
    
    @staticmethod
    def force_collection_now() -> Dict[str, any]:
        """
        Força coleta imediata (para testes ou refresh manual)
        
        Returns:
            Dict com resultado da coleta
        """
        logger.info("Iniciando coleta forçada de dados meteorológicos")
        return WeatherCollectorService.collect_all_locations()
    
    @staticmethod
    def get_collection_status() -> Dict[str, any]:
        """
        Retorna status da última coleta
        
        Returns:
            Dict com informações de status
        """
        try:
            # Obter registro mais recente
            latest_record = WeatherData.query.filter_by(
                is_current=True
            ).order_by(WeatherData.collected_at.desc()).first()
            
            if not latest_record:
                return {
                    'status': 'no_data',
                    'message': 'Nenhum dado coletado ainda',
                    'last_collection': None
                }
            
            # Verificar se dados estão atualizados (menos de 2 horas)
            now = datetime.now(timezone.utc)
            
            # Garantir que collected_at seja timezone aware
            if latest_record.collected_at.tzinfo is None:
                collected_at = latest_record.collected_at.replace(tzinfo=timezone.utc)
            else:
                collected_at = latest_record.collected_at
            
            time_diff = now - collected_at
            
            if time_diff.total_seconds() > 7200:  # 2 horas
                status = 'outdated'
                message = f'Dados desatualizados (última coleta: {time_diff})'
            else:
                status = 'current'
                message = 'Dados atualizados'
            
            return {
                'status': status,
                'message': message,
                'last_collection': latest_record.collected_at.isoformat(),
                'locations_with_data': WeatherData.query.filter_by(is_current=True).count(),
                'data_quality': latest_record.data_quality
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar status: {e}")
            return {
                'status': 'error',
                'message': f'Erro ao verificar status: {str(e)}',
                'last_collection': None
            }
