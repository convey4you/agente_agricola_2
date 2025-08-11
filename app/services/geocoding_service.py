"""
Serviço de Geocoding para conversão de endereços em coordenadas
"""
import requests
import logging
from typing import Dict, Optional, Tuple, List
from urllib.parse import quote


logger = logging.getLogger(__name__)


class GeocodingService:
    """Serviço para geocoding usando APIs gratuitas"""
    
    @staticmethod
    def get_coordinates_from_address(address: str) -> Dict:
        """
        Obter coordenadas a partir de um endereço usando Nominatim (OpenStreetMap)
        
        Args:
            address: Endereço para geocoding
            
        Returns:
            Dict com success, latitude, longitude, formatted_address e dados extras
        """
        try:
            # Limpar e formatar endereço
            clean_address = address.strip()
            if not clean_address:
                return {
                    'success': False,
                    'error': 'Endereço não pode estar vazio',
                    'latitude': None,
                    'longitude': None,
                    'formatted_address': None
                }
            
            # URL da API Nominatim (OpenStreetMap)
            base_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': clean_address,
                'format': 'json',
                'addressdetails': 1,
                'limit': 1,
                'countrycodes': 'pt',  # Focar em Portugal
                'accept-language': 'pt-PT'
            }
            
            headers = {
                'User-Agent': 'AgenteAgricola/1.0 (contato@example.com)'
            }
            
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return {
                    'success': False,
                    'error': 'Localização não encontrada. Tente ser mais específico (ex: "Lisboa" ou "Porto, Distrito do Porto")',
                    'latitude': None,
                    'longitude': None,
                    'formatted_address': None
                }
            
            result = data[0]
            latitude = float(result['lat'])
            longitude = float(result['lon'])
            
            # Extrair informações de endereço
            address_parts = result.get('address', {})
            formatted_parts = []
            
            # Priorizar cidade, distrito, país
            if address_parts.get('city'):
                formatted_parts.append(address_parts['city'])
            elif address_parts.get('town'):
                formatted_parts.append(address_parts['town'])
            elif address_parts.get('village'):
                formatted_parts.append(address_parts['village'])
            
            if address_parts.get('state_district'):
                formatted_parts.append(address_parts['state_district'])
            elif address_parts.get('state'):
                formatted_parts.append(address_parts['state'])
            
            if address_parts.get('country'):
                formatted_parts.append(address_parts['country'])
            
            formatted_address = ', '.join(formatted_parts) if formatted_parts else result.get('display_name')
            
            return {
                'success': True,
                'latitude': latitude,
                'longitude': longitude,
                'formatted_address': formatted_address,
                'raw_address': result.get('display_name'),
                'address_components': address_parts,
                'importance': result.get('importance', 0),
                'place_id': result.get('place_id')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição de geocoding: {e}")
            return {
                'success': False,
                'error': 'Erro de conexão com serviço de localização. Tente novamente.',
                'latitude': None,
                'longitude': None,
                'formatted_address': None
            }
        except Exception as e:
            logger.error(f"Erro inesperado no geocoding: {e}")
            return {
                'success': False,
                'error': 'Erro interno ao processar localização',
                'latitude': None,
                'longitude': None,
                'formatted_address': None
            }
    
    @staticmethod
    def search_locations(query: str, limit: int = 5) -> List[Dict]:
        """
        Buscar localizações para autocomplete
        
        Args:
            query: Termo de busca
            limit: Limite de resultados
            
        Returns:
            Lista de localizações sugeridas
        """
        try:
            if len(query.strip()) < 3:
                return []
            
            base_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': query.strip(),
                'format': 'json',
                'addressdetails': 1,
                'limit': limit,
                'countrycodes': 'pt',
                'accept-language': 'pt-PT'
            }
            
            headers = {
                'User-Agent': 'AgenteAgricola/1.0 (contato@example.com)'
            }
            
            response = requests.get(base_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            suggestions = []
            for item in data:
                address_parts = item.get('address', {})
                formatted_parts = []
                
                if address_parts.get('city'):
                    formatted_parts.append(address_parts['city'])
                elif address_parts.get('town'):
                    formatted_parts.append(address_parts['town'])
                elif address_parts.get('village'):
                    formatted_parts.append(address_parts['village'])
                
                if address_parts.get('state_district'):
                    formatted_parts.append(address_parts['state_district'])
                elif address_parts.get('state'):
                    formatted_parts.append(address_parts['state'])
                
                formatted_name = ', '.join(formatted_parts) if formatted_parts else item.get('display_name')
                
                suggestions.append({
                    'display_name': formatted_name,
                    'full_address': item.get('display_name'),
                    'latitude': float(item['lat']),
                    'longitude': float(item['lon']),
                    'importance': item.get('importance', 0)
                })
            
            # Ordenar por importância
            suggestions.sort(key=lambda x: x['importance'], reverse=True)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Erro na busca de localizações: {e}")
            return []
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, Optional[str]]:
        """
        Validar se as coordenadas estão dentro do território português (incluindo ilhas)
        
        Args:
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            Tuple (is_valid, error_message)
        """
        try:
            # Limites de Portugal Continental e Ilhas
            # Portugal Continental: Latitude: 36.9 (sul) a 42.2 (norte)
            #                      Longitude: -9.5 (oeste) a -6.2 (leste)
            # Açores: Latitude: 36.9 a 39.7, Longitude: -31.3 a -25.0
            # Madeira: Latitude: 32.4 a 33.1, Longitude: -17.3 a -16.3
            
            # Verificar Portugal Continental
            if (36.9 <= latitude <= 42.2) and (-9.5 <= longitude <= -6.2):
                return True, None
            
            # Verificar Açores
            if (36.9 <= latitude <= 39.7) and (-31.3 <= longitude <= -25.0):
                return True, None
            
            # Verificar Madeira
            if (32.4 <= latitude <= 33.1) and (-17.3 <= longitude <= -16.3):
                return True, None
            
            return False, 'Coordenadas fora dos limites de Portugal'
            
        except (TypeError, ValueError):
            return False, 'Coordenadas inválidas'
    
    @staticmethod
    def format_location_for_display(latitude: float, longitude: float, address: str = None) -> str:
        """
        Formatar localização para exibição
        
        Args:
            latitude: Latitude
            longitude: Longitude
            address: Endereço formatado (opcional)
            
        Returns:
            String formatada para exibição
        """
        coords = f"{latitude:.6f}, {longitude:.6f}"
        if address:
            return f"{address} ({coords})"
        return coords
