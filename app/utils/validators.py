"""
Validadores utilitários
"""
import re
from datetime import datetime, timezone


def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validar força da senha"""
    if len(password) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Senha deve conter pelo menos uma letra"
    
    if not re.search(r'[0-9]', password):
        return False, "Senha deve conter pelo menos um número"
    
    return True, "Senha válida"


def validate_date_format(date_string, format='%Y-%m-%d'):
    """Validar formato de data"""
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False


def validate_coordinates(latitude, longitude):
    """Validar coordenadas geográficas"""
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True, "Coordenadas válidas"
        else:
            return False, "Coordenadas fora do intervalo válido"
    except (ValueError, TypeError):
        return False, "Coordenadas devem ser números"


def validate_phone(phone):
    """Validar formato de telefone brasileiro"""
    # Remove todos os caracteres não numéricos
    clean_phone = re.sub(r'\D', '', phone)
    
    # Verifica se tem 10 ou 11 dígitos (com ou sem 9 no celular)
    if len(clean_phone) in [10, 11]:
        return True, "Telefone válido"
    else:
        return False, "Telefone deve ter 10 ou 11 dígitos"


def validate_cpf(cpf):
    """Validar CPF brasileiro"""
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False, "CPF deve ter 11 dígitos"
    
    # Verifica se não são todos os dígitos iguais
    if cpf == cpf[0] * 11:
        return False, "CPF inválido"
    
    # Calcula os dígitos verificadores
    def calculate_digit(cpf_partial):
        sum_value = sum(int(cpf_partial[i]) * (len(cpf_partial) + 1 - i) for i in range(len(cpf_partial)))
        remainder = sum_value % 11
        return 0 if remainder < 2 else 11 - remainder
    
    # Valida primeiro dígito
    if int(cpf[9]) != calculate_digit(cpf[:9]):
        return False, "CPF inválido"
    
    # Valida segundo dígito
    if int(cpf[10]) != calculate_digit(cpf[:10]):
        return False, "CPF inválido"
    
    return True, "CPF válido"


def validate_positive_number(value, field_name="valor"):
    """Validar se é um número positivo"""
    try:
        num = float(value)
        if num > 0:
            return True, f"{field_name} válido"
        else:
            return False, f"{field_name} deve ser maior que zero"
    except (ValueError, TypeError):
        return False, f"{field_name} deve ser um número"


def validate_string_length(text, min_length=1, max_length=255, field_name="campo"):
    """Validar comprimento de string"""
    if not text:
        return False, f"{field_name} é obrigatório"
    
    text_length = len(text.strip())
    
    if text_length < min_length:
        return False, f"{field_name} deve ter pelo menos {min_length} caracteres"
    
    if text_length > max_length:
        return False, f"{field_name} deve ter no máximo {max_length} caracteres"
    
    return True, f"{field_name} válido"
