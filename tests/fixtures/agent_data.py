"""
Fixtures para testes do AgentValidator
"""
import base64
from io import BytesIO

# Mensagens de chat válidas
VALID_CHAT_MESSAGES = [
    "Olá, como posso cuidar das minhas oliveiras?",
    "As folhas da minha vinha estão amareladas. O que pode ser?",
    "Qual a melhor época para plantar tomates em Portugal?",
    "Como identificar pragas no meu pomar?",
    "Preciso de ajuda com irrigação por gotejamento",
    "Quando devo colher as azeitonas?",
    "Como fazer compostagem caseira?",
    "Quais os sintomas de oídio nas videiras?",
    "Temperatura ideal para germinação de sementes",
    "Como calcular a quantidade de adubo necessária?",
    # Mensagens com caracteres especiais portugueses
    "Como cuidar de maçãs em região montanhosa?",
    "Doenças comuns em pêssegos no verão",
    "Técnicas de poda para árvores de fruto",
    "Controlo biológico de pragas: soluções naturais",
    # Mensagens longas (casos extremos válidos)
    "Tenho uma propriedade no Alentejo com 5 hectares de oliveiras da variedade Galega. Notei que algumas árvores apresentam folhas amareladas e queda prematura. O solo é argiloso e o sistema de irrigação é por gotejamento. As árvores têm entre 10 a 15 anos. Que medidas devo tomar para resolver este problema?",
]

# Mensagens de chat inválidas
INVALID_CHAT_MESSAGES = [
    "",  # Vazia
    "   ",  # Apenas espaços
    "\n\n\n",  # Apenas quebras de linha
    "\t\t",  # Apenas tabs
    "a" * 5001,  # Muito longa (assumindo limite de 5000 caracteres)
    None,  # Nulo
    123,  # Não é string
    [],  # Lista
    {},  # Dicionário
    # Mensagens potencialmente maliciosas
    "<script>alert('xss')</script>",
    "'; DROP TABLE messages; --",
    "javascript:alert('hack')",
    "../../../etc/passwd",
]

# IDs de conversação válidos
VALID_CONVERSATION_IDS = [
    1, 2, 3, 10, 100, 999, 123456789,
    "1", "2", "123",  # Strings numéricas válidas
]

# IDs de conversação inválidos
INVALID_CONVERSATION_IDS = [
    0,  # Deve ser maior que zero
    -1, -10, -999,  # Negativos
    "abc", "invalid", "test123",  # Strings não numéricas
    "", "  ",  # Strings vazias
    None,  # Nulo
    [],  # Lista
    {},  # Dicionário
    1.5, 2.7,  # Float
]

# Dados válidos para sugestões de cultura
VALID_CULTURE_SUGGESTIONS_DATA = [
    {
        'location': {
            'latitude': 38.7223,
            'longitude': -9.1393,
            'district': 'Lisboa'
        },
        'soil_type': 'argiloso',
        'area_hectares': 2.5,
        'experience_level': 'beginner',
        'objectives': ['producao_comercial']
    },
    {
        'location': {
            'latitude': 41.1579,
            'longitude': -8.6291,
            'district': 'Porto'
        },
        'soil_type': 'arenoso',
        'area_hectares': 1.0,
        'experience_level': 'intermediate',
        'objectives': ['sustentabilidade', 'autoconsumo']
    },
    {
        'location': {
            'latitude': 38.5667,
            'longitude': -7.9000,
            'district': 'Évora'
        },
        'soil_type': 'calcario',
        'area_hectares': 10.0,
        'experience_level': 'advanced',
        'objectives': ['producao_comercial', 'exportacao']
    },
    # Dados mínimos obrigatórios
    {
        'location': {
            'latitude': 37.0194,
            'longitude': -7.9322
        },
        'area_hectares': 0.5
    }
]

# Dados inválidos para sugestões de cultura
INVALID_CULTURE_SUGGESTIONS_DATA = [
    {},  # Vazio
    {
        'location': {
            'latitude': 38.7223
            # Falta longitude
        },
        'area_hectares': 2.5
    },
    {
        'location': {
            'longitude': -9.1393
            # Falta latitude
        },
        'area_hectares': 2.5
    },
    {
        'location': {
            'latitude': 91,  # Inválida
            'longitude': -9.1393
        },
        'area_hectares': 2.5
    },
    {
        'location': {
            'latitude': 38.7223,
            'longitude': -9.1393
        }
        # Falta area_hectares
    },
    {
        'location': {
            'latitude': 38.7223,
            'longitude': -9.1393
        },
        'area_hectares': -1  # Negativa
    },
    {
        'location': {
            'latitude': 38.7223,
            'longitude': -9.1393
        },
        'area_hectares': 'invalid'  # Não numérica
    }
]

# Tipos de solo válidos para Portugal
VALID_SOIL_TYPES = [
    'argiloso',
    'arenoso',
    'calcario',
    'granítico',
    'xistoso',
    'basáltico',
    'aluvial',
    'terra_rossa',
    'podzol',
    'vertissolo'
]

# Níveis de experiência válidos
VALID_EXPERIENCE_LEVELS = [
    'beginner',
    'intermediate',
    'advanced',
    'expert'
]

# Objetivos válidos para agricultura
VALID_OBJECTIVES = [
    'autoconsumo',
    'producao_comercial',
    'sustentabilidade',
    'exportacao',
    'diversificacao',
    'turismo_rural',
    'agricultura_biologica',
    'permacultura'
]

# Formatos de imagem válidos
VALID_IMAGE_FORMATS = ['JPEG', 'PNG', 'JPG', 'WEBP']

# Extensões de arquivo válidas
VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

# Tamanhos de imagem válidos (em bytes)
VALID_IMAGE_SIZES = {
    'min': 1024,      # 1KB
    'max': 10485760   # 10MB
}

def create_base64_image(format='JPEG', size=(100, 100)):
    """
    Cria uma imagem simulada em base64 para testes
    """
    # Dados base64 de uma imagem pequena válida (1x1 pixel JPEG)
    fake_jpeg = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/8A"
    
    return f"data:image/{format.lower()};base64,{fake_jpeg}"

# Arquivos de imagem válidos (simulados)
VALID_IMAGE_FILES = [
    {
        'filename': 'planta_doente.jpg',
        'content_type': 'image/jpeg',
        'size': 2048576,  # 2MB
        'data': create_base64_image('JPEG', (800, 600))
    },
    {
        'filename': 'folhas_amarelas.png',
        'content_type': 'image/png',
        'size': 1536000,  # 1.5MB
        'data': create_base64_image('PNG', (640, 480))
    },
    {
        'filename': 'sintomas_praga.webp',
        'content_type': 'image/webp',
        'size': 512000,  # 512KB
        'data': create_base64_image('WEBP', (400, 300))
    },
    # Imagem pequena (limite mínimo)
    {
        'filename': 'thumb.jpg',
        'content_type': 'image/jpeg',
        'size': 1024,  # 1KB
        'data': create_base64_image('JPEG', (50, 50))
    }
]

# Arquivos de imagem inválidos
INVALID_IMAGE_FILES = [
    # Sem filename
    {
        'content_type': 'image/jpeg',
        'size': 2048576,
        'data': create_base64_image('JPEG')
    },
    # Filename vazio
    {
        'filename': '',
        'content_type': 'image/jpeg',
        'size': 2048576,
        'data': create_base64_image('JPEG')
    },
    # Extensão inválida
    {
        'filename': 'image.gif',
        'content_type': 'image/gif',
        'size': 2048576,
        'data': 'invalid_data'
    },
    # Arquivo muito grande
    {
        'filename': 'huge_image.jpg',
        'content_type': 'image/jpeg',
        'size': 20971520,  # 20MB
        'data': create_base64_image('JPEG')
    },
    # Arquivo muito pequeno
    {
        'filename': 'tiny_image.jpg',
        'content_type': 'image/jpeg',
        'size': 512,  # 512B
        'data': 'data:image/jpeg;base64,invalid'
    },
    # Content-type inválido
    {
        'filename': 'document.pdf',
        'content_type': 'application/pdf',
        'size': 2048576,
        'data': 'invalid_data'
    },
    # Dados corrompidos
    {
        'filename': 'corrupted.jpg',
        'content_type': 'image/jpeg',
        'size': 2048576,
        'data': 'data:image/jpeg;base64,corrupted_data'
    },
    # Sem dados
    {
        'filename': 'empty.jpg',
        'content_type': 'image/jpeg',
        'size': 0,
        'data': ''
    }
]

# Contextos de análise de imagem válidos
VALID_IMAGE_ANALYSIS_CONTEXTS = [
    'identificacao_doenca',
    'identificacao_praga',
    'diagnostico_nutricional',
    'identificacao_especie',
    'analise_crescimento',
    'qualidade_fruto',
    'estado_solo',
    'condicoes_irrigacao'
]

# Dados válidos para análise de imagem
VALID_IMAGE_ANALYSIS_DATA = [
    {
        'image': VALID_IMAGE_FILES[0],
        'context': 'identificacao_doenca',
        'culture_type': 'oliveira',
        'additional_info': 'Folhas com manchas escuras'
    },
    {
        'image': VALID_IMAGE_FILES[1],
        'context': 'identificacao_praga',
        'culture_type': 'vinha',
        'location': 'Douro'
    },
    {
        'image': VALID_IMAGE_FILES[2],
        'context': 'diagnostico_nutricional',
        'culture_type': 'tomate'
    },
    # Dados mínimos
    {
        'image': VALID_IMAGE_FILES[0],
        'context': 'identificacao_especie'
    }
]

# Histórico de conversas válido
VALID_CONVERSATION_HISTORY = [
    {
        'conversation_id': 1,
        'messages': [
            {
                'role': 'user',
                'content': 'Como cuidar de oliveiras?',
                'timestamp': '2024-01-15T10:30:00Z'
            },
            {
                'role': 'assistant',
                'content': 'Para cuidar de oliveiras, é importante...',
                'timestamp': '2024-01-15T10:30:15Z'
            }
        ],
        'created_at': '2024-01-15T10:30:00Z',
        'last_message_at': '2024-01-15T10:30:15Z'
    },
    {
        'conversation_id': 2,
        'messages': [
            {
                'role': 'user',
                'content': 'Análise desta imagem de planta doente',
                'timestamp': '2024-01-16T14:20:00Z',
                'image_data': VALID_IMAGE_FILES[0]['data']
            }
        ],
        'created_at': '2024-01-16T14:20:00Z',
        'last_message_at': '2024-01-16T14:20:00Z'
    }
]

# Parâmetros de busca válidos
VALID_SEARCH_PARAMS = [
    {
        'query': 'oliveira doença',
        'limit': 10,
        'offset': 0
    },
    {
        'query': 'irrigação vinha',
        'limit': 25
    },
    {
        'query': 'pragas tomate'
    },
    # Query com caracteres especiais portugueses
    {
        'query': 'pêssego podridão',
        'limit': 15
    }
]

# Mensagens de erro esperadas
AGENT_ERROR_MESSAGES = {
    'EMPTY_MESSAGE': 'Mensagem não pode estar vazia',
    'MESSAGE_TOO_LONG': 'Mensagem muito longa (máximo 5000 caracteres)',
    'INVALID_CONVERSATION_ID': 'ID de conversa inválido',
    'INVALID_IMAGE_FILE': 'Arquivo de imagem inválido',
    'IMAGE_TOO_LARGE': 'Imagem muito grande (máximo 10MB)',
    'IMAGE_TOO_SMALL': 'Imagem muito pequena (mínimo 1KB)',
    'UNSUPPORTED_FORMAT': 'Formato de imagem não suportado',
    'INVALID_LOCATION': 'Localização inválida',
    'INVALID_AREA': 'Área deve ser maior que zero',
    'INVALID_SOIL_TYPE': 'Tipo de solo inválido',
    'INVALID_EXPERIENCE_LEVEL': 'Nível de experiência inválido',
    'INVALID_OBJECTIVE': 'Objetivo inválido',
    'CORRUPTED_IMAGE': 'Imagem corrompida ou inválida'
}

# Prompts de sistema para diferentes contextos
SYSTEM_PROMPTS = {
    'general': 'Você é um assistente especializado em agricultura portuguesa.',
    'disease_identification': 'Analise a imagem e identifique possíveis doenças.',
    'pest_identification': 'Examine a imagem para identificar pragas.',
    'nutrition_analysis': 'Avalie o estado nutricional da planta na imagem.',
    'species_identification': 'Identifique a espécie da planta na imagem.'
}

# Respostas simuladas da IA
MOCK_AI_RESPONSES = {
    'oliveira_cuidados': 'Para cuidar de oliveiras, é importante manter rega regular, podar anualmente e proteger contra pragas como a mosca-da-azeitona.',
    'vinha_doenca': 'Com base na descrição, pode ser míldio. Recomendo tratamento com fungicida cúprico e melhoria da ventilação.',
    'tomate_plantio': 'A melhor época para plantar tomates em Portugal é entre março e maio, dependendo da região.',
    'imagem_analise': 'Analisando a imagem, identifiquei sintomas compatíveis com deficiência de ferro (clorose férrica).'
}
