"""
Fixtures de dados para testes de autenticação
"""

# Emails válidos portugueses
VALID_EMAILS = [
    'joao.silva@gmail.com',
    'maria.santos@sapo.pt',
    'pedro.costa@gmail.pt',
    'ana.ferreira@hotmail.com',
    'carlos.oliveira@iol.pt',
    'rita.pereira@clix.pt',
    'miguel.rodrigues@netcabo.pt',
    'lucia.martins@portugalmail.pt',
]

# Emails inválidos
INVALID_EMAILS = [
    '',
    'email_sem_arroba',
    '@dominio.com',
    'email@',
    'email@dominio',
    'email..duplo@dominio.com',
    '.email@dominio.com',
    'email.@dominio.com',
    'email@dominio..com',
    'email@.dominio.com',
    'email@dominio.c',
    'email@dominio.commmm',
    'email@domínio.com',  # Caracteres especiais no domínio
    'email@dominio.com.',
]

# Senhas válidas
VALID_PASSWORDS = [
    'senha123',
    'MinhaSenh@123',
    'Password1',
    'agricultura2024',
    'AgriTech123',
    'fazenda456',
    'Quinta789',
    'oliveira123',
]

# Senhas inválidas
INVALID_PASSWORDS = [
    '',
    '123',  # Muito curta
    '12345',  # Muito curta
    'senha',  # Sem números
    '123456',  # Sem letras
    'a1',  # Muito curta
    '     ',  # Apenas espaços
]

# Dados de login válidos
VALID_LOGIN_DATA = [
    {
        'email': 'joao.silva@gmail.com',
        'password': 'senha123'
    },
    {
        'email': 'maria.santos@sapo.pt',
        'password': 'MinhaSenh@123'
    },
    {
        'email': 'pedro.costa@gmail.pt',
        'password': 'agricultura2024'
    }
]

# Dados de login inválidos
INVALID_LOGIN_DATA = [
    {},  # Vazio
    {'email': ''},  # Email vazio
    {'password': ''},  # Senha vazia
    {'email': 'email_invalido', 'password': 'senha123'},  # Email inválido
    {'email': 'joao@gmail.com', 'password': ''},  # Senha vazia
]

# Dados de registro válidos
VALID_REGISTER_DATA = [
    {
        'email': 'novo.usuario@gmail.com',
        'password': 'minhasenha123',
        'username': 'novousuario'
    },
    {
        'email': 'agricultor@sapo.pt',
        'password': 'AgriTech123',
        'username': 'agricultor_pt'
    },
    {
        'email': 'fazendeiro@gmail.pt',
        'password': 'fazenda456',
        'username': 'fazendeiro_norte'
    }
]

# Dados de registro inválidos
INVALID_REGISTER_DATA = [
    {},  # Vazio
    {'email': 'test@gmail.com'},  # Campos faltando
    {'password': 'senha123'},  # Campos faltando
    {'username': 'usuario'},  # Campos faltando
    {
        'email': 'email_invalido',
        'password': 'senha123',
        'username': 'usuario'
    },  # Email inválido
    {
        'email': 'test@gmail.com',
        'password': '123',  # Senha muito curta
        'username': 'usuario'
    },
    {
        'email': 'test@gmail.com',
        'password': 'senha123',
        'username': 'ab'  # Username muito curto
    },
]

# Dados de onboarding por etapa
VALID_ONBOARDING_STEP_1 = {
    'experience_level': 'beginner'
}

VALID_ONBOARDING_STEP_2 = {
    'propriedade_nome': 'Quinta do José'
}

VALID_ONBOARDING_STEP_3 = {
    'latitude': 38.7223,  # Coordenadas de Lisboa
    'longitude': -9.1393
}

INVALID_ONBOARDING_STEP_1 = [
    {},  # Vazio
    {'experience_level': 'invalid_level'},  # Nível inválido
    {'experience_level': ''},  # Vazio
]

INVALID_ONBOARDING_STEP_2 = [
    {},  # Vazio
    {'propriedade_nome': ''},  # Nome vazio
    {'propriedade_nome': '   '},  # Apenas espaços
]

INVALID_ONBOARDING_STEP_3 = [
    {},  # Vazio
    {'latitude': 38.7223},  # Falta longitude
    {'longitude': -9.1393},  # Falta latitude
    {'latitude': 'invalid', 'longitude': -9.1393},  # Latitude inválida
    {'latitude': 38.7223, 'longitude': 'invalid'},  # Longitude inválida
    {'latitude': 91, 'longitude': -9.1393},  # Latitude fora dos limites
    {'latitude': 38.7223, 'longitude': 181},  # Longitude fora dos limites
]

# Nomes de usuário com caracteres especiais portugueses
PORTUGUESE_USERNAMES = [
    'joão_silva',
    'maria_santos',
    'josé_antónio',
    'ana_conceição',
    'rui_brandão',
    'cristina_são_joão'
]

# Mensagens de erro esperadas
ERROR_MESSAGES = {
    'REQUIRED_FIELDS': 'Email e senha são obrigatórios',
    'INVALID_EMAIL': 'Email inválido',
    'ALL_FIELDS_REQUIRED': 'Todos os campos são obrigatórios',
    'PASSWORD_TOO_SHORT': 'Senha deve ter pelo menos 6 caracteres',
    'PASSWORD_NO_LETTER': 'Senha deve conter pelo menos uma letra',
    'PASSWORD_NO_NUMBER': 'Senha deve conter pelo menos um número',
    'USERNAME_TOO_SHORT': 'Nome de usuário deve ter pelo menos 3 caracteres',
    'EMAIL_IN_USE': 'Email já está em uso',
    'USERNAME_IN_USE': 'Nome de usuário já está em uso',
    'INVALID_EXPERIENCE': 'Nível de experiência inválido',
    'PROPERTY_NAME_REQUIRED': 'Nome da propriedade é obrigatório',
    'COORDINATES_REQUIRED': 'Coordenadas são obrigatórias',
    'INVALID_COORDINATES': 'Coordenadas inválidas',
    'COORDINATES_MUST_BE_NUMBERS': 'Coordenadas devem ser números válidos'
}
