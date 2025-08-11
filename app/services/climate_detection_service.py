"""
Serviço para detecção automática de clima regional baseado na localização
"""
import re
from typing import Optional, Dict
from flask import current_app


class ClimateDetectionService:
    """Serviço para detectar clima regional baseado na localização geográfica"""
    
    # Mapeamento de regiões portuguesas e climas predominantes
    PORTUGAL_CLIMATE_MAP = {
        'norte': {
            'keywords': ['braga', 'porto', 'viana', 'bragança', 'vila real', 'aveiro', 'guarda'],
            'climate': 'temperado',
            'description': 'Temperado oceânico com influência atlântica'
        },
        'centro': {
            'keywords': ['coimbra', 'leiria', 'viseu', 'castelo branco', 'santarém'],
            'climate': 'temperado',
            'description': 'Temperado mediterrânico'
        },
        'lisboa': {
            'keywords': ['lisboa', 'setúbal', 'sintra', 'cascais', 'oeiras'],
            'climate': 'subtropical',
            'description': 'Subtropical mediterrânico'
        },
        'alentejo': {
            'keywords': ['évora', 'beja', 'portalegre', 'elvas', 'sines'],
            'climate': 'subtropical',
            'description': 'Subtropical seco com verões quentes'
        },
        'algarve': {
            'keywords': ['faro', 'lagos', 'portimão', 'tavira', 'olhão', 'albufeira'],
            'climate': 'subtropical',
            'description': 'Subtropical mediterrânico seco'
        },
        'madeira': {
            'keywords': ['funchal', 'madeira', 'porto santo'],
            'climate': 'subtropical',
            'description': 'Subtropical oceânico'
        },
        'açores': {
            'keywords': ['angra', 'ponta delgada', 'horta', 'açores'],
            'climate': 'temperado',
            'description': 'Temperado oceânico'
        }
    }
    
    @staticmethod
    def detect_climate_from_location(location: str, coordinates: Optional[Dict] = None) -> Dict[str, str]:
        """
        Detecta o clima regional baseado na localização
        
        Args:
            location (str): Nome da localização (cidade, distrito)
            coordinates (Dict, optional): Coordenadas geográficas
            
        Returns:
            Dict: Informações sobre o clima detectado
        """
        try:
            result = {
                'climate': '',
                'confidence': 'low',
                'method': 'geographic',
                'description': ''
            }
            
            if not location:
                return result
            
            # Normalizar localização para busca
            location_clean = location.lower().strip()
            location_clean = re.sub(r'[^\w\s]', ' ', location_clean)
            
            current_app.logger.info(f"Detectando clima para localização: {location}")
            
            # Buscar por palavras-chave geográficas
            for region, data in ClimateDetectionService.PORTUGAL_CLIMATE_MAP.items():
                for keyword in data['keywords']:
                    if keyword in location_clean:
                        result.update({
                            'climate': data['climate'],
                            'confidence': 'high',
                            'method': 'geographic_keyword',
                            'description': f"Detectado por localização: {data['description']}",
                            'region': region.title()
                        })
                        current_app.logger.info(f"Clima detectado: {data['climate']} (região: {region})")
                        return result
            
            # Se temos coordenadas, usar análise geográfica mais precisa
            if coordinates and coordinates.get('latitude') and coordinates.get('longitude'):
                lat = float(coordinates['latitude'])
                lon = float(coordinates['longitude'])
                
                climate_by_coords = ClimateDetectionService._detect_by_coordinates(lat, lon)
                if climate_by_coords:
                    result.update(climate_by_coords)
                    result['method'] = 'coordinates'
                    current_app.logger.info(f"Clima detectado por coordenadas: {climate_by_coords['climate']}")
                    return result
            
            # Fallback: análise genérica por país/região
            if 'portugal' in location_clean or 'pt' in location_clean:
                result.update({
                    'climate': 'temperado',
                    'confidence': 'medium',
                    'method': 'country_default',
                    'description': 'Clima temperado mediterrânico (padrão para Portugal)'
                })
                current_app.logger.info("Usando clima padrão para Portugal")
                return result
            
            current_app.logger.warning(f"Não foi possível detectar clima para: {location}")
            return result
            
        except Exception as e:
            current_app.logger.error(f"Erro na detecção de clima: {str(e)}")
            return {
                'climate': '',
                'confidence': 'low',
                'method': 'error',
                'description': 'Erro na detecção automática'
            }
    
    @staticmethod
    def _detect_by_coordinates(latitude: float, longitude: float) -> Optional[Dict]:
        """
        Detecta clima baseado em coordenadas geográficas
        Focado em Portugal Continental e Ilhas
        """
        try:
            # Portugal Continental: aproximadamente 36.5°N to 42.5°N, -9.5°W to -6°W
            if 36.5 <= latitude <= 42.5 and -9.5 <= longitude <= -6.0:
                
                # Algarve (Sul): latitude < 37.5
                if latitude < 37.5:
                    return {
                        'climate': 'subtropical',
                        'confidence': 'high',
                        'description': 'Subtropical mediterrânico (Algarve)',
                        'region': 'Algarve'
                    }
                
                # Norte: latitude > 41.0
                elif latitude > 41.0:
                    return {
                        'climate': 'temperado',
                        'confidence': 'high',
                        'description': 'Temperado oceânico (Norte)',
                        'region': 'Norte'
                    }
                
                # Centro: entre 39.0 e 41.0
                elif 39.0 <= latitude <= 41.0:
                    return {
                        'climate': 'temperado',
                        'confidence': 'high',
                        'description': 'Temperado mediterrânico (Centro)',
                        'region': 'Centro'
                    }
                
                # Lisboa e Vale do Tejo: entre 37.5 e 39.0
                else:
                    return {
                        'climate': 'subtropical',
                        'confidence': 'high',
                        'description': 'Subtropical mediterrânico (Lisboa/Vale do Tejo)',
                        'region': 'Lisboa'
                    }
            
            # Madeira: aproximadamente 32.6°N to 33.1°N, -17.3°W to -16.2°W
            elif 32.6 <= latitude <= 33.1 and -17.3 <= longitude <= -16.2:
                return {
                    'climate': 'subtropical',
                    'confidence': 'high',
                    'description': 'Subtropical oceânico (Madeira)',
                    'region': 'Madeira'
                }
            
            # Açores: aproximadamente 36.9°N to 39.7°N, -31.3°W to -25.0°W
            elif 36.9 <= latitude <= 39.7 and -31.3 <= longitude <= -25.0:
                return {
                    'climate': 'temperado',
                    'confidence': 'high',
                    'description': 'Temperado oceânico (Açores)',
                    'region': 'Açores'
                }
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Erro na análise por coordenadas: {str(e)}")
            return None
    
    @staticmethod
    def get_climate_options():
        """Retorna as opções de clima disponíveis no sistema"""
        return [
            {'value': 'tropical', 'label': 'Tropical'},
            {'value': 'subtropical', 'label': 'Subtropical'},
            {'value': 'temperado', 'label': 'Temperado'},
            {'value': 'semiarido', 'label': 'Semiárido'},
            {'value': 'equatorial', 'label': 'Equatorial'}
        ]
    
    @staticmethod
    def validate_climate_option(climate: str) -> bool:
        """Valida se a opção de clima é válida"""
        valid_options = [opt['value'] for opt in ClimateDetectionService.get_climate_options()]
        return climate in valid_options
