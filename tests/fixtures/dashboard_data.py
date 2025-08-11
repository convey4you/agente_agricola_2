"""
Fixtures de dados para testes de dashboard
"""

# Dados de localização válidos
VALID_LOCATION_DATA = [
    {'latitude': 38.7223, 'longitude': -9.1393, 'city': 'Lisboa'},
    {'latitude': 41.1579, 'longitude': -8.6291, 'city': 'Porto'},
    {'latitude': 40.2033, 'longitude': -8.4103, 'city': 'Coimbra'},
    {'latitude': 38.5667, 'longitude': -7.9000, 'city': 'Évora'},
    {'latitude': 37.0194, 'longitude': -7.9322, 'city': 'Faro'},
    {'latitude': 0, 'longitude': 0},  # Origem
    {'latitude': -23.5505, 'longitude': -46.6333},  # São Paulo (teste internacional)
]

# Dados de localização inválidos
INVALID_LOCATION_DATA = [
    {'latitude': 91, 'longitude': 0},  # Latitude inválida
    {'latitude': -91, 'longitude': 0},  # Latitude inválida
    {'latitude': 0, 'longitude': 181},  # Longitude inválida
    {'latitude': 0, 'longitude': -181},  # Longitude inválida
    {'latitude': 'inválido', 'longitude': 0},  # Tipo inválido
    {'latitude': 0, 'longitude': 'inválido'},  # Tipo inválido
    {'city': 'A'},  # Cidade muito curta
    {'latitude': None, 'longitude': None, 'city': ''},  # Dados vazios
]

# Dados de localização portugueses específicos
PORTUGUESE_LOCATION_DATA = [
    {'latitude': 38.7223, 'longitude': -9.1393, 'city': 'Lisboa'},
    {'latitude': 41.1579, 'longitude': -8.6291, 'city': 'Porto'},
    {'latitude': 40.2033, 'longitude': -8.4103, 'city': 'Coimbra'},
    {'latitude': 38.5667, 'longitude': -7.9000, 'city': 'Évora'},
    {'latitude': 37.0194, 'longitude': -7.9322, 'city': 'Faro'},
    {'latitude': 41.5454, 'longitude': -8.4265, 'city': 'Braga'},
    {'latitude': 39.2969, 'longitude': -7.4300, 'city': 'Castelo Branco'},
    {'latitude': 40.6564, 'longitude': -7.9147, 'city': 'Guarda'},
    {'latitude': 39.7436, 'longitude': -8.8071, 'city': 'Leiria'},
    {'latitude': 39.0015, 'longitude': -7.8617, 'city': 'Portalegre'},
    {'latitude': 32.6669, 'longitude': -16.9241, 'city': 'Funchal'},  # Madeira
    {'latitude': 37.7412, 'longitude': -25.6756, 'city': 'Ponta Delgada'},  # Açores
]

# Dados de exibição de tempo válidos
VALID_WEATHER_DISPLAY_DATA = [
    {
        'temperature': 25.5,
        'humidity': 65,
        'rainfall': 0.0,
        'wind_speed': 12.5,
        'weather_condition': 'sunny',
        'unit_system': 'metric'
    },
    {
        'temperature': 18.2,
        'humidity': 80,
        'rainfall': 2.5,
        'wind_speed': 8.0,
        'weather_condition': 'rainy',
        'unit_system': 'metric'
    },
    {
        'temperature': 30.0,
        'humidity': 45,
        'rainfall': 0.0,
        'wind_speed': 15.0,
        'weather_condition': 'clear',
        'unit_system': 'metric'
    }
]

# Dados de exibição de tempo inválidos
INVALID_WEATHER_DISPLAY_DATA = [
    {'temperature': 'muito quente'},  # Tipo inválido
    {'humidity': 150},  # Valor inválido (>100%)
    {'rainfall': -5.0},  # Valor negativo inválido
    {'wind_speed': -10},  # Velocidade negativa
    {'weather_condition': 'inexistente'},  # Condição inválida
    {'unit_system': 'unknown'},  # Sistema de unidades inválido
    {},  # Dados vazios
]

# Métricas de monitoramento válidas
VALID_MONITORING_METRICS = [
    {
        'metric_type': 'temperature',
        'value': 22.5,
        'unit': 'celsius',
        'timestamp': '2024-01-15T10:30:00Z',
        'location': 'greenhouse_1'
    },
    {
        'metric_type': 'soil_moisture',
        'value': 75.0,
        'unit': 'percentage',
        'timestamp': '2024-01-15T10:30:00Z',
        'location': 'field_a'
    },
    {
        'metric_type': 'ph_level',
        'value': 6.8,
        'unit': 'ph',
        'timestamp': '2024-01-15T10:30:00Z',
        'location': 'field_b'
    }
]

# Métricas de monitoramento inválidas
INVALID_MONITORING_METRICS = [
    {'metric_type': '', 'value': 22.5},  # Tipo vazio
    {'metric_type': 'temperature', 'value': 'muito'},  # Valor inválido
    {'metric_type': 'temperature', 'value': -300},  # Valor impossível
    {'metric_type': 'soil_moisture', 'value': 150},  # Percentual inválido
    {'metric_type': 'ph_level', 'value': 20},  # pH impossível
    {},  # Dados vazios
]

# Configurações de gráfico válidas
VALID_CHART_CONFIGURATIONS = [
    {
        'chart_type': 'line',
        'data_source': 'temperature',
        'time_range': '24h',
        'aggregation': 'hourly',
        'show_legend': True
    },
    {
        'chart_type': 'bar',
        'data_source': 'rainfall',
        'time_range': '7d',
        'aggregation': 'daily',
        'show_legend': False
    },
    {
        'chart_type': 'pie',
        'data_source': 'crop_distribution',
        'time_range': 'current',
        'aggregation': 'total',
        'show_legend': True
    }
]

# Configurações de gráfico inválidas
INVALID_CHART_CONFIGURATIONS = [
    {'chart_type': 'inexistente'},  # Tipo inválido
    {'chart_type': 'line', 'data_source': ''},  # Fonte vazia
    {'chart_type': 'line', 'time_range': 'invalid'},  # Intervalo inválido
    {'aggregation': 'unknown'},  # Agregação inválida
    {},  # Configuração vazia
]

# Critérios de filtro válidos
VALID_FILTER_CRITERIA = [
    {'field': 'crop_type', 'operator': 'equals', 'value': 'tomate'},
    {'field': 'temperature', 'operator': 'greater_than', 'value': 20.0},
    {'field': 'humidity', 'operator': 'between', 'value': [40, 80]},
    {'field': 'location', 'operator': 'in', 'value': ['field_a', 'field_b']},
    {'field': 'date', 'operator': 'last_days', 'value': 7},
]

# Critérios de filtro inválidos
INVALID_FILTER_CRITERIA = [
    {'field': '', 'operator': 'equals', 'value': 'tomate'},  # Campo vazio
    {'field': 'crop_type', 'operator': 'invalid', 'value': 'tomate'},  # Operador inválido
    {'field': 'temperature', 'operator': 'greater_than'},  # Valor ausente
    {'field': 'humidity', 'operator': 'between', 'value': [80, 40]},  # Intervalo inválido
    {},  # Vazio
]

# Permissões do dashboard válidas
VALID_DASHBOARD_PERMISSIONS = [
    {'user_id': 1, 'permission_level': 'read'},
    {'user_id': 2, 'permission_level': 'write'},
    {'user_id': 3, 'permission_level': 'admin'},
    {'role': 'farm_manager', 'permission_level': 'write'},
    {'role': 'viewer', 'permission_level': 'read'},
]

# Permissões do dashboard inválidas
INVALID_DASHBOARD_PERMISSIONS = [
    {'user_id': 'invalid', 'permission_level': 'read'},  # ID inválido
    {'user_id': 1, 'permission_level': 'invalid'},  # Nível inválido
    {'permission_level': 'read'},  # Falta identificador
    {},  # Vazio
]

# Configurações de widget válidas
VALID_WIDGET_CONFIGURATIONS = [
    {
        'widget_type': 'metric_card',
        'title': 'Temperatura Atual',
        'data_source': 'temperature_sensor',
        'refresh_interval': 60,
        'position': {'x': 0, 'y': 0, 'width': 4, 'height': 2}
    },
    {
        'widget_type': 'chart',
        'title': 'Histórico de Chuva',
        'data_source': 'rainfall_data',
        'refresh_interval': 300,
        'position': {'x': 4, 'y': 0, 'width': 8, 'height': 4}
    },
    {
        'widget_type': 'map',
        'title': 'Localização das Culturas',
        'data_source': 'farm_locations',
        'refresh_interval': 3600,
        'position': {'x': 0, 'y': 2, 'width': 12, 'height': 6}
    }
]

# Configurações de widget inválidas
INVALID_WIDGET_CONFIGURATIONS = [
    {'widget_type': 'inexistente'},  # Tipo inválido
    {'widget_type': 'metric_card', 'title': ''},  # Título vazio
    {'widget_type': 'chart', 'refresh_interval': -60},  # Intervalo negativo
    {'widget_type': 'map', 'position': {'x': -1, 'y': 0}},  # Posição inválida
    {},  # Vazio
]

# Estações meteorológicas portuguesas
PORTUGUESE_WEATHER_STATIONS = [
    {'latitude': 38.7167, 'longitude': -9.1333, 'city': 'Lisboa', 'station_code': 'LPPT'},
    {'latitude': 41.2481, 'longitude': -8.6814, 'city': 'Porto', 'station_code': 'LPPR'},
    {'latitude': 37.0144, 'longitude': -7.9658, 'city': 'Faro', 'station_code': 'LPFR'},
    {'latitude': 40.1553, 'longitude': -8.4636, 'city': 'Coimbra', 'station_code': 'LPCO'},
    {'latitude': 38.5244, 'longitude': -7.8969, 'city': 'Évora', 'station_code': 'LPEV'},
    {'latitude': 32.6978, 'longitude': -16.7725, 'city': 'Funchal', 'station_code': 'LPMA'},
    {'latitude': 37.7411, 'longitude': -25.6981, 'city': 'Ponta Delgada', 'station_code': 'LPPD'},
]

# Configurações de exportação válidas
VALID_EXPORT_CONFIGURATIONS = [
    {
        'format': 'csv',
        'data_range': {'start': '2024-01-01', 'end': '2024-01-31'},
        'fields': ['temperature', 'humidity', 'rainfall'],
        'filename': 'weather_data_january'
    },
    {
        'format': 'pdf',
        'report_type': 'monthly_summary',
        'include_charts': True,
        'filename': 'monthly_report'
    },
    {
        'format': 'excel',
        'worksheets': ['temperature', 'humidity', 'crops'],
        'include_formulas': True,
        'filename': 'farm_analysis'
    }
]

# Configurações de exportação inválidas
INVALID_EXPORT_CONFIGURATIONS = [
    {'format': 'invalid_format'},  # Formato inválido
    {'format': 'csv', 'fields': []},  # Campos vazios
    {'format': 'pdf', 'filename': ''},  # Nome vazio
    {'format': 'excel', 'worksheets': 'invalid'},  # Tipo inválido
    {},  # Vazio
]

# Parâmetros de paginação válidos
VALID_PAGINATION_DATA = [
    {'page': 1, 'per_page': 10},
    {'page': 1, 'per_page': 25},
    {'page': 2, 'per_page': 50},
    {'page': 10, 'per_page': 100},
    {'page': 1},  # per_page opcional
    {'per_page': 20},  # page opcional
    {}  # Ambos opcionais
]

# Parâmetros de paginação inválidos
INVALID_PAGINATION_DATA = [
    {'page': 0},  # Page deve ser >= 1
    {'page': -1},  # Page negativo
    {'page': 'invalid'},  # Page não numérico
    {'per_page': 0},  # Per_page deve ser >= 1
    {'per_page': -10},  # Per_page negativo
    {'per_page': 'invalid'},  # Per_page não numérico
    {'per_page': 101},  # Per_page muito grande (assumindo limite de 100)
    {'page': 1.5},  # Page deve ser inteiro
    {'per_page': 25.5},  # Per_page deve ser inteiro
]

# Intervalos de data válidos
VALID_DATE_RANGES = [
    {
        'start_date': '2024-01-01',
        'end_date': '2024-12-31'
    },
    {
        'start_date': '2024-06-01',
        'end_date': '2024-06-30'
    },
    {
        'start_date': '2023-01-01',
        'end_date': '2024-01-01'
    },
    # Apenas start_date
    {'start_date': '2024-01-01'},
    # Apenas end_date
    {'end_date': '2024-12-31'},
    # Nenhuma data (permitido)
    {}
]

# Intervalos de data inválidos
INVALID_DATE_RANGES = [
    {
        'start_date': 'invalid_date',
        'end_date': '2024-12-31'
    },
    {
        'start_date': '2024-01-01',
        'end_date': 'invalid_date'
    },
    {
        'start_date': '2024-12-31',
        'end_date': '2024-01-01'  # End antes do start
    },
    {
        'start_date': '2024-13-01',  # Mês inválido
        'end_date': '2024-12-31'
    },
    {
        'start_date': '2024-01-32',  # Dia inválido
        'end_date': '2024-12-31'
    },
    {
        'start_date': '24-01-01',  # Formato incorreto
        'end_date': '2024-12-31'
    }
]

# Coordenadas de localização válidas (Portugal)
VALID_LOCATION_DATA = [
    # Portugal Continental
    {'latitude': 38.7223, 'longitude': -9.1393},  # Lisboa
    {'latitude': 41.1579, 'longitude': -8.6291},  # Porto
    {'latitude': 40.2033, 'longitude': -8.4103},  # Coimbra
    {'latitude': 38.5667, 'longitude': -7.9000},  # Évora
    {'latitude': 37.0194, 'longitude': -7.9322},  # Faro
    
    # Regiões específicas
    {'latitude': 39.2362, 'longitude': -8.6859},  # Santarém (Ribatejo)
    {'latitude': 40.6443, 'longitude': -8.6455},  # Aveiro (Beira Litoral)
    {'latitude': 41.5518, 'longitude': -8.4229},  # Braga (Minho)
    {'latitude': 41.8066, 'longitude': -6.7574},  # Bragança (Trás-os-Montes)
    {'latitude': 38.0148, 'longitude': -7.8632},  # Beja (Baixo Alentejo)
    
    # Ilhas
    {'latitude': 32.6669, 'longitude': -16.9241}, # Funchal, Madeira
    {'latitude': 38.6553, 'longitude': -27.2176}, # Angra do Heroísmo, Açores
    {'latitude': 37.7412, 'longitude': -25.6756}, # Ponta Delgada, Açores
    
    # Com campos opcionais
    {
        'latitude': 38.7223, 
        'longitude': -9.1393,
        'address': 'Lisboa, Portugal',
        'district': 'Lisboa'
    }
]

# Coordenadas de localização inválidas
INVALID_LOCATION_DATA = [
    {},  # Vazio
    {'latitude': 38.7223},  # Falta longitude
    {'longitude': -9.1393},  # Falta latitude
    {'latitude': 'invalid', 'longitude': -9.1393},  # Latitude inválida
    {'latitude': 38.7223, 'longitude': 'invalid'},  # Longitude inválida
    {'latitude': 91, 'longitude': -9.1393},  # Latitude fora dos limites
    {'latitude': -91, 'longitude': -9.1393},  # Latitude fora dos limites
    {'latitude': 38.7223, 'longitude': 181},  # Longitude fora dos limites
    {'latitude': 38.7223, 'longitude': -181},  # Longitude fora dos limites
    
    # Coordenadas fora de Portugal (para validação específica)
    {'latitude': 40.4168, 'longitude': -3.7038},  # Madrid, Espanha
    {'latitude': 48.8566, 'longitude': 2.3522},   # Paris, França
    {'latitude': 51.5074, 'longitude': -0.1278},  # Londres, Reino Unido
]

# Dados de requisição meteorológica válidos
VALID_WEATHER_REQUEST_DATA = [
    {
        'latitude': 38.7223,
        'longitude': -9.1393,
        'days': 7
    },
    {
        'latitude': 41.1579,
        'longitude': -8.6291,
        'days': 1
    },
    {
        'latitude': 32.6669,
        'longitude': -16.9241,
        'days': 14
    },
    # Sem days (opcional)
    {
        'latitude': 38.7223,
        'longitude': -9.1393
    }
]

# Dados de requisição meteorológica inválidos
INVALID_WEATHER_REQUEST_DATA = [
    {},  # Vazio
    {'latitude': 38.7223},  # Falta longitude
    {'longitude': -9.1393},  # Falta latitude
    {
        'latitude': 91,  # Latitude inválida
        'longitude': -9.1393,
        'days': 7
    },
    {
        'latitude': 38.7223,
        'longitude': -9.1393,
        'days': 0  # Days deve ser >= 1
    },
    {
        'latitude': 38.7223,
        'longitude': -9.1393,
        'days': 15  # Days deve ser <= 14 (assumindo limite)
    },
    {
        'latitude': 38.7223,
        'longitude': -9.1393,
        'days': 'invalid'  # Days deve ser numérico
    }
]

# Tipos de alerta válidos para agricultura portuguesa
VALID_ALERT_TYPES = [
    'geada',
    'seca',
    'chuva_excessiva',
    'vento_forte',
    'granizo',
    'temperatura_alta',
    'temperatura_baixa',
    'umidade_alta',
    'umidade_baixa',
    'pragas',
    'doencas',
    'irrigacao',
    'colheita',
    'plantio',
    'fertilizacao',
    'poda',
    'tratamento_fitossanitario'
]

# Tipos de alerta inválidos
INVALID_ALERT_TYPES = [
    '',
    'tipo_inexistente',
    'tornado',  # Não relevante para Portugal
    'furacao',  # Não relevante para Portugal
    'tsunami',  # Não relevante para agricultura
    123,  # Não é string
    None,
    [],
    {}
]

# Tipos de gráfico válidos
VALID_CHART_TYPES = [
    'linha',
    'barra',
    'pizza',
    'area',
    'scatter',
    'radar',
    'gauge',
    'donut',
    'timeline',
    'heatmap'
]

# Tipos de gráfico inválidos
INVALID_CHART_TYPES = [
    '',
    'tipo_inexistente',
    '3d',  # Não suportado
    'bubble',  # Não suportado
    123,  # Não é string
    None,
    [],
    {}
]

# Distritos portugueses (para validação geográfica)
PORTUGUESE_DISTRICTS = [
    'Aveiro', 'Beja', 'Braga', 'Bragança', 'Castelo Branco',
    'Coimbra', 'Évora', 'Faro', 'Guarda', 'Leiria',
    'Lisboa', 'Portalegre', 'Porto', 'Santarém', 'Setúbal',
    'Viana do Castelo', 'Vila Real', 'Viseu',
    # Regiões Autónomas
    'Região Autónoma dos Açores',
    'Região Autónoma da Madeira'
]

# Coordenadas dos limites geográficos de Portugal
PORTUGAL_BOUNDARIES = {
    'continental': {
        'north': 42.154,    # Minho
        'south': 36.838,    # Algarve
        'west': -9.526,     # Cabo da Roca
        'east': -6.189      # Fronteira com Espanha
    },
    'madeira': {
        'north': 33.174,
        'south': 32.394,
        'west': -17.293,
        'east': -16.250
    },
    'azores': {
        'north': 39.756,
        'south': 36.908,
        'west': -31.331,
        'east': -24.758
    }
}

# Períodos sazonais para agricultura portuguesa
SEASONAL_PERIODS = {
    'primavera': {
        'start_date': '2024-03-20',
        'end_date': '2024-06-20'
    },
    'verao': {
        'start_date': '2024-06-21',
        'end_date': '2024-09-22'
    },
    'outono': {
        'start_date': '2024-09-23',
        'end_date': '2024-12-20'
    },
    'inverno': {
        'start_date': '2024-12-21',
        'end_date': '2024-03-19'
    }
}

# Dados de filtros de dashboard válidos
VALID_FILTER_DATA = [
    {
        'date_range': {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        },
        'location': {
            'latitude': 38.7223,
            'longitude': -9.1393
        },
        'alert_types': ['geada', 'seca'],
        'chart_type': 'linha'
    },
    {
        'date_range': {
            'start_date': '2024-06-01'
        },
        'alert_types': ['irrigacao']
    },
    {
        'location': {
            'latitude': 41.1579,
            'longitude': -8.6291
        },
        'chart_type': 'barra'
    },
    {}  # Filtros vazios (válido)
]

# Mensagens de erro esperadas
DASHBOARD_ERROR_MESSAGES = {
    'INVALID_PAGE': 'Página deve ser um número maior que zero',
    'INVALID_PER_PAGE': 'Itens por página deve ser um número entre 1 e 100',
    'INVALID_DATE_FORMAT': 'Formato de data inválido (esperado: YYYY-MM-DD)',
    'END_BEFORE_START': 'Data final deve ser posterior à data inicial',
    'COORDINATES_REQUIRED': 'Latitude e longitude são obrigatórias',
    'INVALID_LATITUDE': 'Latitude deve estar entre -90 e 90',
    'INVALID_LONGITUDE': 'Longitude deve estar entre -180 e 180',
    'COORDINATES_OUTSIDE_PORTUGAL': 'Coordenadas fora do território português',
    'INVALID_DAYS': 'Número de dias deve estar entre 1 e 14',
    'INVALID_ALERT_TYPE': 'Tipo de alerta inválido',
    'INVALID_CHART_TYPE': 'Tipo de gráfico inválido'
}
