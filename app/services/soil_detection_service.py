"""
Serviço para detecção automática de tipo de solo baseado na localização e IA
"""
import re
import logging
from typing import Optional, Dict, List
from flask import current_app


logger = logging.getLogger(__name__)


class SoilDetectionService:
    """Serviço para detectar tipo de solo baseado na localização geográfica e dados geológicos"""
    
    # Mapeamento de regiões portuguesas e tipos de solo predominantes
    PORTUGAL_SOIL_MAP = {
        'minho': {
            'keywords': ['viana do castelo', 'braga', 'guimarães', 'barcelos', 'minho'],
            'soils': [
                {'type': 'humifero', 'probability': 0.4, 'description': 'Solos húmicos devido ao clima oceânico'},
                {'type': 'argiloso', 'probability': 0.3, 'description': 'Argilas devido à erosão das montanhas'},
                {'type': 'misto', 'probability': 0.3, 'description': 'Solos mistos em áreas de transição'}
            ]
        },
        'douro': {
            'keywords': ['porto', 'vila nova de gaia', 'matosinhos', 'espinho', 'douro'],
            'soils': [
                {'type': 'misto', 'probability': 0.4, 'description': 'Solos mistos típicos da região do Douro'},
                {'type': 'argiloso', 'probability': 0.3, 'description': 'Argilas nas encostas do rio Douro'},
                {'type': 'siltoso', 'probability': 0.3, 'description': 'Siltes nas planícies aluviais'}
            ]
        },
        'tras_os_montes': {
            'keywords': ['bragança', 'vila real', 'chaves', 'mirandela', 'trás-os-montes'],
            'soils': [
                {'type': 'argiloso', 'probability': 0.4, 'description': 'Argilas de alteração de rochas graníticas'},
                {'type': 'misto', 'probability': 0.4, 'description': 'Solos mistos em terrenos montanhosos'},
                {'type': 'calcario', 'probability': 0.2, 'description': 'Calcários em algumas áreas específicas'}
            ]
        },
        'beira_litoral': {
            'keywords': ['aveiro', 'coimbra', 'leiria', 'figueira da foz', 'ílhavo'],
            'soils': [
                {'type': 'arenoso', 'probability': 0.4, 'description': 'Areias da faixa costeira atlântica'},
                {'type': 'humifero', 'probability': 0.3, 'description': 'Solos orgânicos em áreas húmidas'},
                {'type': 'misto', 'probability': 0.3, 'description': 'Solos mistos no interior'}
            ]
        },
        'beira_interior': {
            'keywords': ['viseu', 'guarda', 'castelo branco', 'covilhã', 'seia'],
            'soils': [
                {'type': 'argiloso', 'probability': 0.4, 'description': 'Argilas de decomposição granítica'},
                {'type': 'misto', 'probability': 0.4, 'description': 'Solos mistos de montanha'},
                {'type': 'calcario', 'probability': 0.2, 'description': 'Calcários em formações específicas'}
            ]
        },
        'lisboa_vale_tejo': {
            'keywords': ['lisboa', 'sintra', 'cascais', 'oeiras', 'almada', 'setúbal', 'santarém'],
            'soils': [
                {'type': 'calcario', 'probability': 0.4, 'description': 'Calcários típicos da região de Lisboa'},
                {'type': 'argiloso', 'probability': 0.3, 'description': 'Argilas nas áreas mais interiores'},
                {'type': 'arenoso', 'probability': 0.3, 'description': 'Areias na costa e estuários'}
            ]
        },
        'alentejo_litoral': {
            'keywords': ['sines', 'santiago do cacém', 'grândola', 'alcácer do sal'],
            'soils': [
                {'type': 'arenoso', 'probability': 0.5, 'description': 'Areias costeiras atlânticas'},
                {'type': 'misto', 'probability': 0.3, 'description': 'Solos mistos em transição'},
                {'type': 'argiloso', 'probability': 0.2, 'description': 'Argilas em áreas interiores'}
            ]
        },
        'alentejo_central': {
            'keywords': ['évora', 'estremoz', 'borba', 'vila viçosa', 'arraiolos'],
            'soils': [
                {'type': 'calcario', 'probability': 0.4, 'description': 'Mármores e calcários típicos do Alentejo'},
                {'type': 'argiloso', 'probability': 0.4, 'description': 'Argilas mediterrânicas'},
                {'type': 'misto', 'probability': 0.2, 'description': 'Solos mistos em planícies'}
            ]
        },
        'alentejo_alto': {
            'keywords': ['portalegre', 'elvas', 'campo maior', 'alter do chão'],
            'soils': [
                {'type': 'argiloso', 'probability': 0.4, 'description': 'Argilas vermelhas mediterrânicas'},
                {'type': 'misto', 'probability': 0.4, 'description': 'Solos mistos de planície'},
                {'type': 'calcario', 'probability': 0.2, 'description': 'Calcários em formações específicas'}
            ]
        },
        'baixo_alentejo': {
            'keywords': ['beja', 'serpa', 'moura', 'cuba', 'vidigueira'],
            'soils': [
                {'type': 'argiloso', 'probability': 0.5, 'description': 'Argilas pesadas mediterrânicas'},
                {'type': 'misto', 'probability': 0.3, 'description': 'Solos mistos em planícies alentejanas'},
                {'type': 'calcario', 'probability': 0.2, 'description': 'Calcários em algumas áreas'}
            ]
        },
        'algarve': {
            'keywords': ['faro', 'lagos', 'portimão', 'tavira', 'olhão', 'albufeira', 'sagres'],
            'soils': [
                {'type': 'calcario', 'probability': 0.4, 'description': 'Calcários típicos do Algarve'},
                {'type': 'arenoso', 'probability': 0.4, 'description': 'Areias da costa algarvia'},
                {'type': 'argiloso', 'probability': 0.2, 'description': 'Argilas no interior'}
            ]
        },
        'madeira': {
            'keywords': ['funchal', 'machico', 'santa cruz', 'ribeira brava', 'madeira'],
            'soils': [
                {'type': 'vulcanico', 'probability': 0.6, 'description': 'Solos vulcânicos ricos em minerais'},
                {'type': 'humifero', 'probability': 0.3, 'description': 'Solos orgânicos em áreas de floresta'},
                {'type': 'misto', 'probability': 0.1, 'description': 'Solos mistos em áreas costeiras'}
            ]
        },
        'azores': {
            'keywords': ['angra do heroísmo', 'ponta delgada', 'horta', 'açores', 'azores'],
            'soils': [
                {'type': 'vulcanico', 'probability': 0.7, 'description': 'Solos vulcânicos extremamente férteis'},
                {'type': 'humifero', 'probability': 0.2, 'description': 'Solos orgânicos devido ao clima oceânico'},
                {'type': 'misto', 'probability': 0.1, 'description': 'Solos mistos em algumas ilhas'}
            ]
        }
    }
    
    # Mapeamento adicional por altitude (para maior precisão)
    ALTITUDE_SOIL_INFLUENCE = {
        'montanha': {  # > 800m
            'modifiers': {
                'argiloso': 0.3,  # Maior decomposição rochosa
                'misto': 0.4,     # Mais comum em montanha
                'humifero': 0.2,  # Menor devido ao frio
                'arenoso': 0.1    # Raro em montanha
            }
        },
        'colina': {  # 200-800m
            'modifiers': {
                'misto': 0.4,     # Mais comum
                'argiloso': 0.3,
                'humifero': 0.2,
                'arenoso': 0.1
            }
        },
        'planicie': {  # < 200m
            'modifiers': {
                'argiloso': 0.3,
                'arenoso': 0.3,   # Mais comum em planícies
                'misto': 0.2,
                'humifero': 0.2
            }
        }
    }
    
    @staticmethod
    def detect_soil_from_location(location: str, coordinates: Optional[Dict] = None, climate: Optional[str] = None) -> Dict:
        """
        Detecta o tipo de solo mais provável baseado na localização, coordenadas e clima
        
        Args:
            location (str): Nome da localização (cidade, distrito)
            coordinates (Dict, optional): Coordenadas geográficas
            climate (str, optional): Clima regional detectado
            
        Returns:
            Dict: Informações sobre o solo detectado com probabilidades
        """
        try:
            result = {
                'primary_soil': '',
                'confidence': 'low',
                'method': 'geographic',
                'description': '',
                'alternatives': [],
                'reasoning': []
            }
            
            if not location:
                return result
            
            # Normalizar localização para busca
            location_clean = location.lower().strip()
            location_clean = re.sub(r'[^\w\s-]', ' ', location_clean)
            
            logger.info(f"Detectando tipo de solo para localização: {location}")
            
            # Buscar por região geológica
            region_match = SoilDetectionService._find_geological_region(location_clean)
            if region_match:
                region_data = SoilDetectionService.PORTUGAL_SOIL_MAP[region_match]
                soils = region_data['soils'].copy()
                
                # Aplicar modificadores baseados em coordenadas
                if coordinates:
                    soils = SoilDetectionService._apply_coordinate_modifiers(soils, coordinates)
                
                # Aplicar modificadores baseados no clima
                if climate:
                    soils = SoilDetectionService._apply_climate_modifiers(soils, climate)
                
                # Ordenar por probabilidade
                soils.sort(key=lambda x: x['probability'], reverse=True)
                
                # Definir resultado principal
                primary = soils[0]
                result.update({
                    'primary_soil': primary['type'],
                    'confidence': SoilDetectionService._calculate_confidence(primary['probability']),
                    'method': 'regional_geological',
                    'description': primary['description'],
                    'alternatives': [
                        {
                            'type': soil['type'],
                            'probability': round(soil['probability'] * 100, 1),
                            'description': soil['description']
                        }
                        for soil in soils[:3]  # Top 3
                    ],
                    'reasoning': [
                        f"Região geológica identificada: {region_match.replace('_', ' ').title()}",
                        f"Solo primário: {primary['type']} ({round(primary['probability'] * 100, 1)}%)",
                        f"Baseado em características geológicas regionais"
                    ]
                })
                
                if coordinates:
                    result['reasoning'].append("Ajustado por coordenadas geográficas")
                if climate:
                    result['reasoning'].append(f"Ajustado por clima ({climate})")
                
                logger.info(f"Solo detectado: {primary['type']} (confiança: {result['confidence']})")
                return result
            
            # Fallback: análise genérica por coordenadas
            if coordinates and coordinates.get('latitude') and coordinates.get('longitude'):
                coord_result = SoilDetectionService._detect_by_coordinates_only(
                    float(coordinates['latitude']), 
                    float(coordinates['longitude'])
                )
                if coord_result:
                    result.update(coord_result)
                    logger.info(f"Solo detectado por coordenadas: {coord_result['primary_soil']}")
                    return result
            
            # Fallback final: padrão para Portugal
            if 'portugal' in location_clean or 'pt' in location_clean:
                result.update({
                    'primary_soil': 'misto',
                    'confidence': 'medium',
                    'method': 'country_default',
                    'description': 'Solos mistos típicos de Portugal (diversidade geológica)',
                    'alternatives': [
                        {'type': 'misto', 'probability': 40.0, 'description': 'Solos mistos mais comuns'},
                        {'type': 'argiloso', 'probability': 30.0, 'description': 'Argilas em muitas regiões'},
                        {'type': 'calcario', 'probability': 20.0, 'description': 'Calcários em várias áreas'}
                    ],
                    'reasoning': ['Padrão para Portugal baseado na diversidade geológica nacional']
                })
                logger.info("Usando solo padrão para Portugal")
                return result
            
            logger.warning(f"Não foi possível detectar solo para: {location}")
            return result
            
        except Exception as e:
            logger.error(f"Erro na detecção de solo: {str(e)}")
            return {
                'primary_soil': '',
                'confidence': 'low',
                'method': 'error',
                'description': 'Erro na detecção automática',
                'alternatives': [],
                'reasoning': [f'Erro: {str(e)}']
            }
    
    @staticmethod
    def _find_geological_region(location_clean: str) -> Optional[str]:
        """Encontra a região geológica baseada na localização"""
        for region, data in SoilDetectionService.PORTUGAL_SOIL_MAP.items():
            for keyword in data['keywords']:
                if keyword in location_clean:
                    return region
        return None
    
    @staticmethod
    def _apply_coordinate_modifiers(soils: List[Dict], coordinates: Dict) -> List[Dict]:
        """Aplica modificadores baseados nas coordenadas (altitude, proximidade do mar)"""
        try:
            lat = float(coordinates.get('latitude', 0))
            lon = float(coordinates.get('longitude', 0))
            
            # Estimar altitude baseada em coordenadas (aproximação simples)
            altitude_category = 'planicie'
            if lat > 41.5:  # Norte montanhoso
                altitude_category = 'montanha'
            elif lat > 40.0:  # Centro com colinas
                altitude_category = 'colina'
            
            # Verificar proximidade do mar (longitude mais a oeste = mais próximo do mar)
            coastal_proximity = lon < -8.0  # Aproximadamente costa oeste
            
            # Aplicar modificadores
            modifiers = SoilDetectionService.ALTITUDE_SOIL_INFLUENCE.get(altitude_category, {}).get('modifiers', {})
            
            for soil in soils:
                soil_type = soil['type']
                if soil_type in modifiers:
                    # Ajustar probabilidade baseada na altitude
                    altitude_factor = modifiers[soil_type]
                    soil['probability'] *= (0.7 + altitude_factor)
                    
                    # Se próximo da costa, aumentar chance de solos arenosos
                    if coastal_proximity and soil_type == 'arenoso':
                        soil['probability'] *= 1.3
                    elif coastal_proximity and soil_type == 'calcario':
                        soil['probability'] *= 1.1
            
            # Normalizar probabilidades para somarem ~1.0
            total_prob = sum(soil['probability'] for soil in soils)
            if total_prob > 0:
                for soil in soils:
                    soil['probability'] /= total_prob
            
            return soils
            
        except Exception as e:
            logger.error(f"Erro ao aplicar modificadores de coordenadas: {str(e)}")
            return soils
    
    @staticmethod
    def _apply_climate_modifiers(soils: List[Dict], climate: str) -> List[Dict]:
        """Aplica modificadores baseados no clima"""
        climate_modifiers = {
            'temperado': {
                'humifero': 1.2,  # Clima húmido favorece solos orgânicos
                'argiloso': 1.1,  
                'arenoso': 0.9
            },
            'subtropical': {
                'calcario': 1.2,  # Clima seco favorece calcários
                'argiloso': 1.1,
                'humifero': 0.8   # Menos orgânicos em clima seco
            },
            'semiarido': {
                'calcario': 1.3,
                'arenoso': 1.2,
                'humifero': 0.6
            }
        }
        
        modifiers = climate_modifiers.get(climate, {})
        for soil in soils:
            soil_type = soil['type']
            if soil_type in modifiers:
                soil['probability'] *= modifiers[soil_type]
        
        return soils
    
    @staticmethod
    def _detect_by_coordinates_only(latitude: float, longitude: float) -> Optional[Dict]:
        """Detecção básica apenas por coordenadas quando não há match regional"""
        try:
            # Portugal Continental
            if 36.5 <= latitude <= 42.5 and -9.5 <= longitude <= -6.0:
                if latitude < 38.0:  # Sul (Algarve/Alentejo)
                    return {
                        'primary_soil': 'calcario',
                        'confidence': 'medium',
                        'method': 'coordinates_only',
                        'description': 'Calcários típicos do Sul de Portugal',
                        'alternatives': [
                            {'type': 'calcario', 'probability': 40.0, 'description': 'Calcários predominantes'},
                            {'type': 'argiloso', 'probability': 35.0, 'description': 'Argilas mediterrânicas'},
                            {'type': 'arenoso', 'probability': 25.0, 'description': 'Areias costeiras'}
                        ],
                        'reasoning': ['Detecção por coordenadas: Sul de Portugal']
                    }
                elif latitude > 41.0:  # Norte
                    return {
                        'primary_soil': 'argiloso',
                        'confidence': 'medium',
                        'method': 'coordinates_only',
                        'description': 'Argilas de decomposição granítica do Norte',
                        'alternatives': [
                            {'type': 'argiloso', 'probability': 40.0, 'description': 'Argilas graníticas'},
                            {'type': 'misto', 'probability': 35.0, 'description': 'Solos mistos montanhosos'},
                            {'type': 'humifero', 'probability': 25.0, 'description': 'Solos orgânicos'}
                        ],
                        'reasoning': ['Detecção por coordenadas: Norte de Portugal']
                    }
                else:  # Centro
                    return {
                        'primary_soil': 'misto',
                        'confidence': 'medium',
                        'method': 'coordinates_only',
                        'description': 'Solos mistos típicos do Centro de Portugal',
                        'alternatives': [
                            {'type': 'misto', 'probability': 40.0, 'description': 'Solos mistos predominantes'},
                            {'type': 'argiloso', 'probability': 30.0, 'description': 'Argilas regionais'},
                            {'type': 'calcario', 'probability': 30.0, 'description': 'Calcários locais'}
                        ],
                        'reasoning': ['Detecção por coordenadas: Centro de Portugal']
                    }
            
            # Madeira
            elif 32.6 <= latitude <= 33.1 and -17.3 <= longitude <= -16.2:
                return {
                    'primary_soil': 'vulcanico',
                    'confidence': 'high',
                    'method': 'coordinates_only',
                    'description': 'Solos vulcânicos ricos da Madeira',
                    'alternatives': [
                        {'type': 'vulcanico', 'probability': 70.0, 'description': 'Solos vulcânicos férteis'},
                        {'type': 'humifero', 'probability': 20.0, 'description': 'Solos orgânicos'},
                        {'type': 'misto', 'probability': 10.0, 'description': 'Solos mistos costeiros'}
                    ],
                    'reasoning': ['Detecção por coordenadas: Madeira (origem vulcânica)']
                }
            
            # Açores
            elif 36.9 <= latitude <= 39.7 and -31.3 <= longitude <= -25.0:
                return {
                    'primary_soil': 'vulcanico',
                    'confidence': 'high',
                    'method': 'coordinates_only',
                    'description': 'Solos vulcânicos extremamente férteis dos Açores',
                    'alternatives': [
                        {'type': 'vulcanico', 'probability': 80.0, 'description': 'Solos vulcânicos muito férteis'},
                        {'type': 'humifero', 'probability': 15.0, 'description': 'Solos orgânicos oceânicos'},
                        {'type': 'misto', 'probability': 5.0, 'description': 'Solos mistos'}
                    ],
                    'reasoning': ['Detecção por coordenadas: Açores (origem vulcânica)']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na detecção por coordenadas: {str(e)}")
            return None
    
    @staticmethod
    def _calculate_confidence(probability: float) -> str:
        """Calcula nível de confiança baseado na probabilidade"""
        if probability >= 0.6:
            return 'high'
        elif probability >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def get_soil_types():
        """Retorna lista de tipos de solo disponíveis"""
        return [
            {'value': 'argiloso', 'label': 'Argiloso'},
            {'value': 'arenoso', 'label': 'Arenoso'},
            {'value': 'siltoso', 'label': 'Siltoso'},
            {'value': 'humifero', 'label': 'Humífero'},
            {'value': 'calcario', 'label': 'Calcário'},
            {'value': 'misto', 'label': 'Misto'},
            {'value': 'vulcanico', 'label': 'Vulcânico (Ilhas)'}
        ]
    
    @staticmethod
    def get_soil_description(soil_type: str) -> str:
        """Retorna descrição detalhada de um tipo de solo"""
        descriptions = {
            'argiloso': 'Solo com alta concentração de argila, retém bem a água mas pode ter drenagem limitada. Bom para culturas que precisam de umidade constante.',
            'arenoso': 'Solo com partículas grandes, boa drenagem mas baixa retenção de água e nutrientes. Adequado para culturas que preferem solo bem drenado.',
            'siltoso': 'Solo com partículas médias, boa retenção de água e nutrientes. Equilibrado para muitas culturas.',
            'humifero': 'Solo rico em matéria orgânica, muito fértil e com boa estrutura. Excelente para a maioria das culturas.',
            'calcario': 'Solo com alto teor de calcário, pH alcalino. Adequado para culturas que toleram solo alcalino.',
            'misto': 'Combinação equilibrada de diferentes tipos de solo. Versátil para diversas culturas.',
            'vulcanico': 'Solo de origem vulcânica, extremamente fértil e rico em minerais. Ideal para agricultura intensiva.'
        }
        return descriptions.get(soil_type, 'Tipo de solo não reconhecido.')
