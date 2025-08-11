"""
Fixtures para testes do MarketplaceValidator
"""

# Categorias válidas de produtos agrícolas portugueses
VALID_CATEGORIES = [
    'frutas',
    'legumes',
    'cereais',
    'azeite',
    'vinho',
    'queijo',
    'mel',
    'ervas_aromaticas',
    'flores',
    'sementes',
    'plantas',
    'equipamentos',
    'fertilizantes',
    'defensivos',
    'ferramentas',
    'maquinaria'
]

# Categorias inválidas
INVALID_CATEGORIES = [
    '',
    'categoria_inexistente',
    'eletronicos',  # Não relacionado à agricultura
    'carros',       # Não relacionado à agricultura
    123,            # Não é string
    None,
    [],
    {}
]

# Dados válidos para criação de item
VALID_ITEM_CREATION_DATA = [
    {
        'title': 'Azeite Extra Virgem do Alentejo',
        'description': 'Azeite de primeira qualidade produzido em olivais tradicionais do Alentejo. Acidez inferior a 0,5%.',
        'category': 'azeite',
        'price': 15.50,
        'currency': 'EUR',
        'quantity_available': 100,
        'unit': 'litro',
        'location': {
            'district': 'Évora',
            'municipality': 'Évora',
            'latitude': 38.5667,
            'longitude': -7.9000
        },
        'contact': {
            'phone': '+351 266 123 456',
            'email': 'produtor@quinta.pt'
        },
        'images': [
            'https://example.com/azeite1.jpg',
            'https://example.com/azeite2.jpg'
        ],
        'certifications': ['biologico', 'dop_alentejo'],
        'harvest_date': '2023-11-15',
        'expiry_date': '2025-11-15'
    },
    {
        'title': 'Tomates Cherry Bio',
        'description': 'Tomates cherry cultivados em estufa sem pesticidas.',
        'category': 'legumes',
        'price': 3.50,
        'currency': 'EUR',
        'quantity_available': 50,
        'unit': 'kg',
        'location': {
            'district': 'Leiria',
            'municipality': 'Óbidos'
        },
        'contact': {
            'phone': '+351 262 987 654'
        },
        'organic': True
    },
    {
        'title': 'Mel de Lavanda',
        'description': 'Mel puro de lavanda colhido na Serra da Estrela.',
        'category': 'mel',
        'price': 8.00,
        'currency': 'EUR',
        'quantity_available': 25,
        'unit': 'frasco_500g',
        'location': {
            'district': 'Guarda',
            'municipality': 'Seia'
        },
        'contact': {
            'email': 'apicultor@serra.pt'
        }
    }
]

# Dados inválidos para criação de item
INVALID_ITEM_CREATION_DATA = [
    {},  # Vazio
    {
        'description': 'Descrição sem título',
        'category': 'frutas',
        'price': 10.0
    },  # Falta título
    {
        'title': 'Produto sem categoria',
        'description': 'Descrição',
        'price': 10.0
    },  # Falta categoria
    {
        'title': 'Produto sem preço',
        'description': 'Descrição',
        'category': 'frutas'
    },  # Falta preço
    {
        'title': '',  # Título vazio
        'description': 'Descrição',
        'category': 'frutas',
        'price': 10.0
    },
    {
        'title': 'A',  # Título muito curto
        'description': 'Descrição',
        'category': 'frutas',
        'price': 10.0
    },
    {
        'title': 'A' * 201,  # Título muito longo (assumindo limite de 200)
        'description': 'Descrição',
        'category': 'frutas',
        'price': 10.0
    },
    {
        'title': 'Produto com categoria inválida',
        'description': 'Descrição',
        'category': 'categoria_inexistente',
        'price': 10.0
    },
    {
        'title': 'Produto com preço negativo',
        'description': 'Descrição',
        'category': 'frutas',
        'price': -5.0
    },
    {
        'title': 'Produto com preço inválido',
        'description': 'Descrição',
        'category': 'frutas',
        'price': 'invalid'
    },
    {
        'title': 'Produto com quantidade negativa',
        'description': 'Descrição',
        'category': 'frutas',
        'price': 10.0,
        'quantity_available': -1
    }
]

# Termos de busca válidos
VALID_SEARCH_TERMS = [
    'azeite',
    'tomate',
    'mel',
    'oliveira',
    'vinho tinto',
    'queijo serra',
    'batata doce',
    'maçã reineta',
    'alface',
    'cenoura',
    # Termos com caracteres especiais portugueses
    'pêssego',
    'limão',
    'maçã',
    'pêra rocha',
    'açúcar',
    # Termos compostos
    'azeite extra virgem',
    'mel de eucalipto',
    'vinho do porto',
    'queijo da serra',
    'batata ramos'
]

# Termos de busca inválidos
INVALID_SEARCH_TERMS = [
    '',  # Vazio
    '   ',  # Apenas espaços
    'a',  # Muito curto (assumindo mínimo de 2 caracteres)
    'a' * 101,  # Muito longo (assumindo máximo de 100 caracteres)
    None,
    123,
    [],
    {},
    # Termos maliciosos
    '<script>alert("xss")</script>',
    'SELECT * FROM products',
    '\'; DROP TABLE products; --'
]

# Faixas de preço válidas
VALID_PRICE_RANGES = [
    {'min_price': 0, 'max_price': 10},
    {'min_price': 5, 'max_price': 50},
    {'min_price': 10, 'max_price': 100},
    {'min_price': 50, 'max_price': 500},
    {'min_price': 0},  # Apenas preço mínimo
    {'max_price': 100},  # Apenas preço máximo
    {},  # Sem filtro de preço
]

# Faixas de preço inválidas
INVALID_PRICE_RANGES = [
    {'min_price': -1},  # Preço mínimo negativo
    {'max_price': -10},  # Preço máximo negativo
    {'min_price': 100, 'max_price': 50},  # Min maior que max
    {'min_price': 'invalid'},  # Preço não numérico
    {'max_price': 'invalid'},  # Preço não numérico
    {'min_price': 10001},  # Preço muito alto (assumindo limite)
    {'max_price': 10001},  # Preço muito alto
]

# Condições de produto válidas
VALID_PRODUCT_CONDITIONS = [
    'novo',
    'usado_como_novo',
    'usado_bom_estado',
    'usado_estado_razoavel',
    'para_pecas'
]

# Condições de produto inválidas
INVALID_PRODUCT_CONDITIONS = [
    '',
    'condicao_inexistente',
    'perfeito',  # Não está na lista válida
    123,
    None,
    [],
    {}
]

# Localizações portuguesas válidas
VALID_PORTUGUESE_LOCATIONS = [
    {'district': 'Lisboa', 'municipality': 'Lisboa'},
    {'district': 'Porto', 'municipality': 'Porto'},
    {'district': 'Aveiro', 'municipality': 'Aveiro'},
    {'district': 'Braga', 'municipality': 'Braga'},
    {'district': 'Coimbra', 'municipality': 'Coimbra'},
    {'district': 'Évora', 'municipality': 'Évora'},
    {'district': 'Faro', 'municipality': 'Faro'},
    {'district': 'Leiria', 'municipality': 'Leiria'},
    {'district': 'Santarém', 'municipality': 'Santarém'},
    {'district': 'Setúbal', 'municipality': 'Setúbal'},
    # Regiões Autónomas
    {'district': 'Região Autónoma da Madeira', 'municipality': 'Funchal'},
    {'district': 'Região Autónoma dos Açores', 'municipality': 'Ponta Delgada'},
    # Apenas distrito
    {'district': 'Lisboa'},
    # Com coordenadas
    {
        'district': 'Lisboa',
        'municipality': 'Lisboa',
        'latitude': 38.7223,
        'longitude': -9.1393
    }
]

# Localizações inválidas
INVALID_PORTUGUESE_LOCATIONS = [
    {},  # Vazio
    {'municipality': 'Lisboa'},  # Falta distrito
    {'district': 'Distrito Inexistente'},
    {'district': 'Madrid'},  # Não é português
    {'district': 'Lisboa', 'municipality': 'Barcelona'},  # Município incompatível
    {
        'district': 'Lisboa',
        'latitude': 91,  # Latitude inválida
        'longitude': -9.1393
    },
    {
        'district': 'Lisboa',
        'latitude': 38.7223,
        'longitude': 181  # Longitude inválida
    }
]

# Unidades de medida válidas
VALID_UNITS = [
    'kg',
    'g',
    'litro',
    'ml',
    'unidade',
    'caixa',
    'saco',
    'frasco_250g',
    'frasco_500g',
    'frasco_1kg',
    'garrafa_750ml',
    'garrafa_1l',
    'pacote',
    'm2',
    'hectare',
    'peça'
]

# Certificações válidas
VALID_CERTIFICATIONS = [
    'biologico',
    'dop',  # Denominação de Origem Protegida
    'igp',  # Indicação Geográfica Protegida
    'dop_alentejo',
    'dop_douro',
    'igp_ribatejo',
    'modo_producao_biologico',
    'comercio_justo',
    'global_gap',
    'haccp',
    'iso_9001'
]

# Dados de paginação válidos
VALID_PAGINATION_DATA = [
    {'page': 1, 'per_page': 10},
    {'page': 1, 'per_page': 25},
    {'page': 2, 'per_page': 50},
    {'page': 10, 'per_page': 20},
    {'page': 1},  # per_page padrão
    {'per_page': 15},  # page padrão
    {}  # Valores padrão
]

# Dados de paginação inválidos
INVALID_PAGINATION_DATA = [
    {'page': 0},  # Page deve ser >= 1
    {'page': -1},  # Page negativo
    {'page': 'invalid'},  # Page não numérico
    {'per_page': 0},  # Per_page deve ser >= 1
    {'per_page': -5},  # Per_page negativo
    {'per_page': 'invalid'},  # Per_page não numérico
    {'per_page': 101},  # Per_page muito grande (assumindo limite de 100)
]

# Dados de filtros combinados válidos
VALID_COMBINED_FILTERS = [
    {
        'category': 'frutas',
        'search_term': 'maçã',
        'price_range': {'min_price': 1, 'max_price': 5},
        'location': {'district': 'Lisboa'},
        'condition': 'novo',
        'organic_only': True,
        'with_certification': True
    },
    {
        'category': 'azeite',
        'price_range': {'min_price': 10},
        'location': {'district': 'Évora', 'municipality': 'Évora'}
    },
    {
        'search_term': 'mel',
        'location': {'district': 'Guarda'}
    },
    {}  # Sem filtros
]

# Dados de estatísticas válidos
VALID_STATS_REQUESTS = [
    {'period': 'day'},
    {'period': 'week'},
    {'period': 'month'},
    {'period': 'year'},
    {'category': 'frutas'},
    {'district': 'Lisboa'},
    {
        'period': 'month',
        'category': 'azeite',
        'district': 'Évora'
    }
]

# Dados de estatísticas inválidos
INVALID_STATS_REQUESTS = [
    {'period': 'invalid_period'},
    {'category': 'categoria_inexistente'},
    {'district': 'distrito_inexistente'},
    {'period': 123},  # Não é string
    {'category': None},
    {'district': ''}
]

# Produtos em destaque válidos
VALID_FEATURED_ITEMS = [
    {
        'item_id': 1,
        'priority': 1,
        'start_date': '2024-01-01',
        'end_date': '2024-01-31'
    },
    {
        'item_id': 2,
        'priority': 2,
        'start_date': '2024-02-01',
        'end_date': '2024-02-28'
    },
    {
        'item_id': 3,
        'priority': 3  # Sem datas (permanente)
    }
]

# Contatos válidos
VALID_CONTACT_INFO = [
    {
        'phone': '+351 123 456 789',
        'email': 'vendedor@quinta.pt',
        'whatsapp': '+351 912 345 678'
    },
    {
        'phone': '123456789',  # Formato nacional
        'email': 'produtor@farm.pt'
    },
    {
        'email': 'contato@agricola.com'  # Apenas email
    },
    {
        'phone': '+351 262 123 456'  # Apenas telefone
    }
]

# Contatos inválidos
INVALID_CONTACT_INFO = [
    {},  # Vazio (deve ter pelo menos um meio de contato)
    {
        'phone': '123',  # Telefone muito curto
        'email': 'invalido'
    },
    {
        'phone': '+351 123 456 789',
        'email': 'email_sem_arroba'
    },
    {
        'phone': 'not_a_phone',
        'email': 'valid@email.com'
    }
]

# Preços realistas por categoria (EUR)
REALISTIC_PRICES = {
    'frutas': {'min': 0.50, 'max': 15.00},
    'legumes': {'min': 0.30, 'max': 8.00},
    'cereais': {'min': 0.80, 'max': 5.00},
    'azeite': {'min': 8.00, 'max': 50.00},
    'vinho': {'min': 3.00, 'max': 200.00},
    'queijo': {'min': 5.00, 'max': 80.00},
    'mel': {'min': 6.00, 'max': 25.00},
    'ervas_aromaticas': {'min': 1.00, 'max': 10.00},
    'flores': {'min': 2.00, 'max': 30.00},
    'sementes': {'min': 1.50, 'max': 20.00},
    'plantas': {'min': 3.00, 'max': 100.00},
    'equipamentos': {'min': 10.00, 'max': 5000.00},
    'fertilizantes': {'min': 5.00, 'max': 100.00},
    'defensivos': {'min': 8.00, 'max': 200.00},
    'ferramentas': {'min': 5.00, 'max': 500.00},
    'maquinaria': {'min': 100.00, 'max': 50000.00}
}

# Mensagens de erro esperadas
MARKETPLACE_ERROR_MESSAGES = {
    'TITLE_REQUIRED': 'Título é obrigatório',
    'TITLE_TOO_SHORT': 'Título deve ter pelo menos 3 caracteres',
    'TITLE_TOO_LONG': 'Título não pode exceder 200 caracteres',
    'DESCRIPTION_REQUIRED': 'Descrição é obrigatória',
    'CATEGORY_REQUIRED': 'Categoria é obrigatória',
    'INVALID_CATEGORY': 'Categoria inválida',
    'PRICE_REQUIRED': 'Preço é obrigatório',
    'INVALID_PRICE': 'Preço deve ser um número positivo',
    'PRICE_TOO_HIGH': 'Preço muito alto',
    'INVALID_QUANTITY': 'Quantidade deve ser um número positivo',
    'INVALID_SEARCH_TERM': 'Termo de busca inválido',
    'SEARCH_TERM_TOO_SHORT': 'Termo de busca muito curto',
    'SEARCH_TERM_TOO_LONG': 'Termo de busca muito longo',
    'INVALID_PRICE_RANGE': 'Faixa de preços inválida',
    'MIN_GREATER_THAN_MAX': 'Preço mínimo não pode ser maior que o máximo',
    'INVALID_PAGE': 'Página deve ser um número maior que zero',
    'INVALID_PER_PAGE': 'Itens por página deve ser um número entre 1 e 100',
    'INVALID_CONDITION': 'Condição do produto inválida',
    'INVALID_LOCATION': 'Localização inválida',
    'DISTRICT_REQUIRED': 'Distrito é obrigatório',
    'INVALID_DISTRICT': 'Distrito inválido',
    'CONTACT_REQUIRED': 'Pelo menos um meio de contato é obrigatório',
    'INVALID_PHONE': 'Número de telefone inválido',
    'INVALID_EMAIL': 'Email inválido'
}
