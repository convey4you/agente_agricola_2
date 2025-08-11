"""
Controlador para APIs de geocoding e localização
"""
import logging
from flask import Blueprint, request, jsonify
from app.services.geocoding_service import GeocodingService
from app.services.soil_detection_service import SoilDetectionService
from app.services.climate_detection_service import ClimateDetectionService
from app.utils.response_helpers import ResponseHandler, LoggingHelper
from app.utils.auth_decorators import public_route
from app.middleware.rate_limiter import api_endpoint_limit


logger = logging.getLogger(__name__)

geocoding_bp = Blueprint('geocoding', __name__)


# Rota de teste removida por segurança


@geocoding_bp.route('/search', methods=['GET'])
@public_route
def search_locations():
    """
    API para busca de localizações (autocomplete)
    
    Query Parameters:
        q: Termo de busca
        limit: Limite de resultados (padrão: 5)
    """
    try:
        from flask import jsonify
        
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 5))
        
        if len(query) < 3:
            return jsonify({
                'success': True,
                'suggestions': [],
                'message': 'Digite pelo menos 3 caracteres'
            })
        
        suggestions = GeocodingService.search_locations(query, limit)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'count': len(suggestions)
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Parâmetro limit deve ser um número'
        }), 400
    except Exception as e:
        LoggingHelper.log_error(e, 'geocoding.search_locations')
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar localizações'
        }), 500


@geocoding_bp.route('/geocode', methods=['POST'])
@public_route
def geocode_address():
    """
    API para geocoding de endereço completo
    
    Body:
        {
            "address": "endereço para geocoding"
        }
    """
    try:
        from flask import jsonify
        
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo address é obrigatório'
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({
                'success': False,
                'error': 'Endereço não pode estar vazio'
            }), 400
        
        result = GeocodingService.get_coordinates_from_address(address)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        LoggingHelper.log_error(e, 'geocoding.geocode_address')
        return jsonify({
            'success': False,
            'error': 'Erro ao processar geocoding'
        }), 500


@geocoding_bp.route('/validate', methods=['POST'])
@public_route
def validate_coordinates():
    """
    API para validação de coordenadas
    
    Body:
        {
            "latitude": float,
            "longitude": float
        }
    """
    try:
        from flask import jsonify
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        try:
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
        except (TypeError, ValueError):
            return jsonify({
                'success': False,
                'error': 'Coordenadas devem ser números válidos'
            }), 400
        
        is_valid, error_msg = GeocodingService.validate_coordinates(latitude, longitude)
        
        if is_valid:
            formatted_location = GeocodingService.format_location_for_display(latitude, longitude)
            return jsonify({
                'success': True,
                'valid': True,
                'latitude': latitude,
                'longitude': longitude,
                'formatted_location': formatted_location
            })
        else:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
    except Exception as e:
        LoggingHelper.log_error(e, 'geocoding.validate_coordinates')
        return jsonify({
            'success': False,
            'error': 'Erro ao validar coordenadas'
        }), 500


@geocoding_bp.route('/detect-soil', methods=['POST'])
@public_route
def detect_soil():
    """
    API para detecção automática de tipo de solo baseado na localização
    
    Body:
        {
            "location": "nome da localização",
            "latitude": float (opcional),
            "longitude": float (opcional),
            "climate": "tipo de clima" (opcional)
        }
    """
    try:
        from flask import jsonify
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        location = data.get('location', '').strip()
        if not location:
            return jsonify({
                'success': False,
                'error': 'Campo location é obrigatório'
            }), 400
        
        # Preparar coordenadas se fornecidas
        coordinates = None
        if data.get('latitude') and data.get('longitude'):
            try:
                coordinates = {
                    'latitude': str(float(data['latitude'])),
                    'longitude': str(float(data['longitude']))
                }
            except (TypeError, ValueError):
                logger.warning(f"Coordenadas inválidas fornecidas: {data.get('latitude')}, {data.get('longitude')}")
        
        # Clima opcional
        climate = data.get('climate', '').strip() or None
        
        # Detectar tipo de solo
        result = SoilDetectionService.detect_soil_from_location(
            location=location,
            coordinates=coordinates,
            climate=climate
        )
        
        if result.get('primary_soil'):
            # Enriquecer resposta com informações adicionais
            response_data = {
                'success': True,
                'soil_detection': result,
                'soil_info': {
                    'description': SoilDetectionService.get_soil_description(result['primary_soil']),
                    'available_types': SoilDetectionService.get_soil_types()
                },
                'input': {
                    'location': location,
                    'coordinates': coordinates,
                    'climate': climate
                }
            }
            
            logger.info(f"Solo detectado para {location}: {result['primary_soil']} (confiança: {result['confidence']})")
            return jsonify(response_data)
        else:
            return jsonify({
                'success': False,
                'error': 'Não foi possível detectar o tipo de solo para esta localização',
                'soil_info': {
                    'available_types': SoilDetectionService.get_soil_types()
                }
            }), 404
        
    except Exception as e:
        LoggingHelper.log_error(e, 'geocoding.detect_soil')
        return jsonify({
            'success': False,
            'error': 'Erro ao detectar tipo de solo'
        }), 500


@geocoding_bp.route('/detect-climate', methods=['POST'])
@public_route
def detect_climate():
    """
    API para detecção automática de clima baseado na localização
    
    Body:
        {
            "location": "nome da localização",
            "latitude": float (opcional),
            "longitude": float (opcional)
        }
    """
    try:
        from flask import jsonify
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        location = data.get('location', '').strip()
        if not location:
            return jsonify({
                'success': False,
                'error': 'Campo location é obrigatório'
            }), 400
        
        # Preparar coordenadas se fornecidas
        coordinates = None
        if data.get('latitude') and data.get('longitude'):
            try:
                coordinates = {
                    'latitude': str(float(data['latitude'])),
                    'longitude': str(float(data['longitude']))
                }
            except (TypeError, ValueError):
                logger.warning(f"Coordenadas inválidas fornecidas: {data.get('latitude')}, {data.get('longitude')}")
        
        # Detectar clima
        result = ClimateDetectionService.detect_climate_from_location(
            location=location,
            coordinates=coordinates
        )
        
        if result.get('climate'):
            response_data = {
                'success': True,
                'climate_detection': result,
                'input': {
                    'location': location,
                    'coordinates': coordinates
                }
            }
            
            logger.info(f"Clima detectado para {location}: {result['climate']} (confiança: {result['confidence']})")
            return jsonify(response_data)
        else:
            return jsonify({
                'success': False,
                'error': 'Não foi possível detectar o clima para esta localização'
            }), 404
        
    except Exception as e:
        LoggingHelper.log_error(e, 'geocoding.detect_climate')
        return jsonify({
            'success': False,
            'error': 'Erro ao detectar clima'
        }), 500
