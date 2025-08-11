"""
Fixtures de dados para testes de culturas
"""
from datetime import datetime, timezone, date, timedelta

# Tipos de cultura válidos em Portugal
VALID_CULTURE_TYPES = [
    'arvore_frutifera',
    'hortalica',
    'erva_aromatica',
    'grao',
    'cereal',
    'leguminosa'
]

# Culturas típicas portuguesas por região
PORTUGUESE_CULTURES = {
    'alentejo': {
        'oliveira': {
            'name': 'Oliveira Galega',
            'culture_type': 'arvore_frutifera',
            'variety': 'Galega Vulgar',
            'area_hectares': 2.5,
            'planting_season': 'outono',
            'harvest_season': 'inverno'
        },
        'sobreiro': {
            'name': 'Sobreiro Alentejano',
            'culture_type': 'arvore_frutifera',
            'variety': 'Quercus suber',
            'area_hectares': 10.0,
            'planting_season': 'inverno',
            'harvest_season': 'verao'
        },
        'trigo': {
            'name': 'Trigo Duro',
            'culture_type': 'cereal',
            'variety': 'Claudio',
            'area_hectares': 5.0,
            'planting_season': 'outono',
            'harvest_season': 'verao'
        }
    },
    'douro': {
        'vinha': {
            'name': 'Vinha do Porto',
            'culture_type': 'arvore_frutifera',
            'variety': 'Touriga Nacional',
            'area_hectares': 1.2,
            'planting_season': 'inverno',
            'harvest_season': 'outono'
        },
        'amendoeira': {
            'name': 'Amendoeira Tradicional',
            'culture_type': 'arvore_frutifera',
            'variety': 'Ferragnes',
            'area_hectares': 0.8,
            'planting_season': 'inverno',
            'harvest_season': 'verao'
        }
    },
    'ribatejo': {
        'tomate': {
            'name': 'Tomate de Indústria',
            'culture_type': 'hortalica',
            'variety': 'Heinz 9553',
            'area_hectares': 0.5,
            'planting_season': 'primavera',
            'harvest_season': 'verao'
        },
        'milho': {
            'name': 'Milho Grão',
            'culture_type': 'cereal',
            'variety': 'DKC6724',
            'area_hectares': 3.0,
            'planting_season': 'primavera',
            'harvest_season': 'outono'
        }
    },
    'oeste': {
        'couve': {
            'name': 'Couve Portuguesa',
            'culture_type': 'hortalica',
            'variety': 'Tronchuda',
            'area_hectares': 0.2,
            'planting_season': 'outono',
            'harvest_season': 'inverno'
        },
        'batata': {
            'name': 'Batata Ramos',
            'culture_type': 'hortalica',
            'variety': 'Ramos',
            'area_hectares': 1.0,
            'planting_season': 'primavera',
            'harvest_season': 'verao'
        }
    },
    'algarve': {
        'laranjeira': {
            'name': 'Laranja do Algarve',
            'culture_type': 'arvore_frutifera',
            'variety': 'Valencia Late',
            'area_hectares': 1.5,
            'planting_season': 'primavera',
            'harvest_season': 'inverno'
        },
        'figueira': {
            'name': 'Figo Lampo',
            'culture_type': 'arvore_frutifera',
            'variety': 'Lampo Preto',
            'area_hectares': 0.3,
            'planting_season': 'inverno',
            'harvest_season': 'verao'
        }
    }
}

# Coordenadas das principais regiões agrícolas portuguesas
PORTUGUESE_COORDINATES = {
    'lisboa': {'lat': 38.7223, 'lng': -9.1393},
    'porto': {'lat': 41.1579, 'lng': -8.6291},
    'coimbra': {'lat': 40.2033, 'lng': -8.4103},
    'evora': {'lat': 38.5667, 'lng': -7.9000},
    'faro': {'lat': 37.0194, 'lng': -7.9322},
    'braga': {'lat': 41.5518, 'lng': -8.4229},
    'aveiro': {'lat': 40.6443, 'lng': -8.6455},
    'viseu': {'lat': 40.6566, 'lng': -7.9139},
    'santarem': {'lat': 39.2362, 'lng': -8.6859},
    'leiria': {'lat': 39.7437, 'lng': -8.8071},
    'castelo_branco': {'lat': 39.8195, 'lng': -7.4969},
    'guarda': {'lat': 40.5364, 'lng': -7.2683},
    'braganca': {'lat': 41.8066, 'lng': -6.7574},
    'vila_real': {'lat': 41.3005, 'lng': -7.7442},
    'viana_do_castelo': {'lat': 41.6947, 'lng': -8.8314},
    'portalegre': {'lat': 39.2967, 'lng': -7.4281},
    'beja': {'lat': 38.0148, 'lng': -7.8632},
    'setubal': {'lat': 38.5244, 'lng': -8.8882},
    # Ilhas
    'funchal': {'lat': 32.6669, 'lng': -16.9241},  # Madeira
    'angra_heroismo': {'lat': 38.6553, 'lng': -27.2176},  # Açores
}

# Dados válidos para criação de cultura
VALID_CULTURE_CREATE_DATA = [
    {
        'farm_id': 1,
        'nome': 'Oliveira Galega',
        'tipo': 'arvore_frutifera',
        'area_plantada': 2.5,
        'data_plantio': '2024-03-15',
        'data_colheita_prevista': '2024-11-30',
        'variedade': 'Galega Vulgar',
        'observacoes': 'Plantação tradicional no Alentejo'
    },
    {
        'farm_id': 2,
        'nome': 'Tomate Indústria',
        'tipo': 'hortalica',
        'area_plantada': 0.8,
        'data_plantio': '2024-04-01',
        'data_colheita_prevista': '2024-08-15',
        'variedade': 'Heinz 9553'
    },
    {
        'farm_id': 1,
        'nome': 'Trigo Mole',
        'tipo': 'cereal',
        'area_plantada': 5.2,
        'data_plantio': '2023-11-20',
        'data_colheita_prevista': '2024-07-10',
        'variedade': 'Antequera'
    }
]

# Dados inválidos para criação de cultura
INVALID_CULTURE_CREATE_DATA = [
    {},  # Vazio
    {'nome': 'Teste'},  # Falta farm_id e tipo
    {'farm_id': 1, 'nome': 'Teste'},  # Falta tipo
    {'farm_id': 1, 'tipo': 'arvore_frutifera'},  # Falta nome
    {
        'farm_id': 'invalid',  # farm_id inválido
        'nome': 'Teste',
        'tipo': 'arvore_frutifera'
    },
    {
        'farm_id': 1,
        'nome': 'A',  # Nome muito curto
        'tipo': 'arvore_frutifera'
    },
    {
        'farm_id': 1,
        'nome': 'A' * 101,  # Nome muito longo
        'tipo': 'arvore_frutifera'
    },
    {
        'farm_id': 1,
        'nome': 'Teste',
        'tipo': 'tipo_invalido'  # Tipo inválido
    },
    {
        'farm_id': 1,
        'nome': 'Teste',
        'tipo': 'arvore_frutifera',
        'area_plantada': -1  # Área negativa
    },
    {
        'farm_id': 1,
        'nome': 'Teste',
        'tipo': 'arvore_frutifera',
        'area_plantada': 10001  # Área muito grande
    },
    {
        'farm_id': 1,
        'nome': 'Teste',
        'tipo': 'arvore_frutifera',
        'data_plantio': 'data_invalida'
    },
    {
        'farm_id': 1,
        'nome': 'Teste',
        'tipo': 'arvore_frutifera',
        'data_plantio': '2024-03-15',
        'data_colheita_prevista': '2024-03-10'  # Colheita antes do plantio
    }
]

# Dados válidos para atualização de cultura
VALID_CULTURE_UPDATE_DATA = [
    {
        'nome': 'Oliveira Galega Atualizada',
        'area_plantada': 3.0,
        'observacoes': 'Plantação expandida'
    },
    {
        'status': 'crescimento',
        'data_colheita_prevista': '2024-12-15'
    }
]

# Dados de wizard por etapa
VALID_WIZARD_STEP_DATA = {
    1: {
        'culture_type': 'arvore_frutifera',
        'name': 'Oliveira do Norte'
    },
    2: {
        'variety': 'Galega Vulgar',
        'area_hectares': 2.5
    },
    3: {
        'planting_date': '2024-03-15',
        'irrigation_type': 'gota_a_gota'
    },
    4: {
        'latitude': 38.5667,
        'longitude': -7.9000,
        'address': 'Évora, Alentejo'
    },
    5: {
        'objectives': ['producao_comercial', 'sustentabilidade'],
        'expected_yield': 1500  # kg/hectare
    }
}

INVALID_WIZARD_STEP_DATA = {
    1: [
        {},  # Vazio
        {'culture_type': 'tipo_invalido'},  # Tipo inválido
        {'name': ''},  # Nome vazio
    ],
    2: [
        {'area_hectares': -1},  # Área negativa
        {'area_hectares': 'invalid'},  # Área inválida
    ],
    3: [
        {'planting_date': 'invalid_date'},  # Data inválida
        {'irrigation_type': 'tipo_inexistente'},  # Tipo de irrigação inválido
    ],
    4: [
        {'latitude': 91},  # Latitude inválida
        {'longitude': 181},  # Longitude inválida
    ],
    5: [
        {'expected_yield': -1},  # Rendimento negativo
        {'objectives': []},  # Objetivos vazios
    ]
}

# Datas específicas para agricultura portuguesa
PORTUGUESE_PLANTING_DATES = {
    'oliveira': {
        'inicio': '2024-10-01',  # Outubro
        'fim': '2024-12-31'      # Dezembro
    },
    'vinha': {
        'inicio': '2024-01-01',  # Janeiro
        'fim': '2024-03-31'      # Março
    },
    'tomate': {
        'inicio': '2024-03-01',  # Março
        'fim': '2024-05-31'      # Maio
    },
    'trigo': {
        'inicio': '2023-10-01',  # Outubro
        'fim': '2023-12-31'      # Dezembro
    }
}

# Variedades específicas por cultura
PORTUGUESE_VARIETIES = {
    'oliveira': [
        'Galega Vulgar', 'Cobrançosa', 'Picual', 
        'Verdeal Transmontana', 'Cordovil de Serpa'
    ],
    'vinha': [
        'Touriga Nacional', 'Touriga Franca', 'Tinta Roriz',
        'Castelão', 'Aragonez', 'Alvarinho', 'Vinhão'
    ],
    'tomate': [
        'Heinz 9553', 'Perfectpeel', 'Red Cherry',
        'San Marzano', 'Coração de Boi'
    ],
    'trigo': [
        'Antequera', 'Almansor', 'Claudio',
        'Nabão', 'Paiva', 'Roxo'
    ]
}

# Status válidos de cultura
VALID_CULTURE_STATUS = [
    'planejada',
    'plantada', 
    'crescimento',
    'colheita',
    'finalizada'
]

# Tipos de irrigação válidos
VALID_IRRIGATION_TYPES = [
    'gota_a_gota',
    'aspersao',
    'inundacao',
    'micro_aspersao',
    'sem_irrigacao'
]

# Mensagens de erro esperadas
CULTURE_ERROR_MESSAGES = {
    'FIELD_REQUIRED': 'Campo {} é obrigatório',
    'NAME_TOO_SHORT': 'Nome da cultura deve ter pelo menos 2 caracteres',
    'NAME_TOO_LONG': 'Nome da cultura não pode exceder 100 caracteres',
    'INVALID_TYPE': 'Tipo de cultura inválido',
    'INVALID_FARM_ID': 'ID da fazenda deve ser um número válido',
    'FARM_NOT_FOUND': 'Fazenda não encontrada ou não pertence ao usuário',
    'INVALID_AREA': 'Área plantada deve ser maior que zero',
    'AREA_TOO_LARGE': 'Área plantada muito grande (máximo: 10000 hectares)',
    'INVALID_DATE': 'Data inválida (formato: YYYY-MM-DD)',
    'HARVEST_BEFORE_PLANTING': 'Data de colheita deve ser posterior à data de plantio',
    'INVALID_STATUS': 'Status de cultura inválido',
    'INVALID_WIZARD_STEP': 'Etapa do wizard inválida'
}
