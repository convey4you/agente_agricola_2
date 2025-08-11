"""
Sistema de Validação de Entrada para AgroTech Portugal
Implementa validação robusta e sanitização de dados
"""

from marshmallow import Schema, fields, validate, ValidationError, pre_load
import re
import html
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Validador de segurança para sanitização de entrada"""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitiza string para prevenir XSS"""
        if not isinstance(value, str):
            return value
        
        # Escape HTML
        value = html.escape(value)
        
        # Remove caracteres perigosos
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        for char in dangerous_chars:
            value = value.replace(char, '')
        
        # Limitar tamanho
        if len(value) > 1000:
            value = value[:1000]
        
        return value.strip()
    
    @staticmethod
    def validate_sql_injection(value: str) -> bool:
        """Verifica se há tentativas de SQL injection"""
        if not isinstance(value, str):
            return True
        
        # Padrões suspeitos de SQL injection (case insensitive)
        sql_patterns = [
            r"(\\'|\\\"|(;)|(\\;)|(\\|)|(\\|\\|))",  # Aspas e ponto-vírgula
            r"((union)|(select)|(insert)|(delete)|(update)|(drop)|(create)|(alter))\s",  # Comandos SQL com espaço
            r"(\s(or|and)\s+(1|true|false)\s*(=|!=|<>)\s*(1|true|false))",  # Condições sempre verdadeiras
            r"(exec|execute|sp_|xp_)\s",  # Stored procedures com espaço
            r"(\-\-|\#|\/\*)",  # Comentários SQL
        ]
        
        value_lower = value.lower()
        for pattern in sql_patterns:
            if re.search(pattern, value_lower):
                logger.warning(f"Possible SQL injection attempt detected: {value[:50]}")
                return False
        
        return True

# Esquemas de Validação Específicos

class LoginSchema(Schema):
    """Schema de validação para login"""
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={'invalid': 'Email inválido', 'required': 'Email é obrigatório'}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128),
        error_messages={
            'required': 'Senha é obrigatória',
            'validator_failed': 'Senha deve ter entre 6 e 128 caracteres'
        }
    )
    remember_me = fields.Bool(load_default=False)
    
    @pre_load
    def sanitize_input(self, data, **kwargs):
        """Sanitiza entrada antes da validação"""
        # Converter ImmutableMultiDict para dict mutável
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        elif hasattr(data, 'copy'):
            data = dict(data)
        else:
            data = dict(data) if data else {}
            
        if 'email' in data:
            data['email'] = SecurityValidator.sanitize_string(data['email'])
        return data

class RegistrationSchema(Schema):
    """Schema de validação para registro"""
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, max=100),
            validate.Regexp(r'^[a-zA-ZÀ-ÿ\s]+$', error='Nome deve conter apenas letras')
        ],
        error_messages={'required': 'Nome é obrigatório'}
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={'invalid': 'Email inválido', 'required': 'Email é obrigatório'}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128),
        error_messages={
            'required': 'Senha é obrigatória',
            'validator_failed': 'Senha deve ter entre 6 e 128 caracteres'
        }
    )
    confirm_password = fields.Str(
        required=True,
        error_messages={'required': 'Confirmação de senha é obrigatória'}
    )
    
    @pre_load
    def sanitize_input(self, data, **kwargs):
        """Sanitiza entrada antes da validação"""
        # Converter ImmutableMultiDict para dict mutável
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        elif hasattr(data, 'copy'):
            data = dict(data)
        else:
            data = dict(data) if data else {}
            
        for field in ['name', 'email']:
            if field in data:
                data[field] = SecurityValidator.sanitize_string(data[field])
        return data
    
    def validate_password_match(self, data, **kwargs):
        """Valida se senhas coincidem"""
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError({'confirm_password': 'Senhas não coincidem'})

class SearchSchema(Schema):
    """Schema de validação para busca"""
    query = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'Termo de busca é obrigatório'}
    )
    category = fields.Str(
        validate=validate.OneOf(['all', 'cultures', 'users', 'agents']),
        load_default='all'
    )
    page = fields.Int(
        validate=validate.Range(min=1, max=1000),
        load_default=1
    )
    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        load_default=20
    )
    
    @pre_load
    def sanitize_input(self, data, **kwargs):
        """Sanitiza entrada antes da validação"""
        # Converter ImmutableMultiDict para dict mutável
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        elif hasattr(data, 'copy'):
            data = dict(data)
        else:
            data = dict(data) if data else {}
            
        if 'query' in data:
            query = SecurityValidator.sanitize_string(data['query'])
            if not SecurityValidator.validate_sql_injection(query):
                raise ValidationError('Busca contém caracteres inválidos', 'query')
            data['query'] = query
        return data

class CultureSchema(Schema):
    """Schema de validação para culturas"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'Nome da cultura é obrigatório'}
    )
    type = fields.Str(
        required=True,
        validate=validate.OneOf(['cereal', 'vegetable', 'fruit', 'legume', 'herb']),
        error_messages={'required': 'Tipo de cultura é obrigatório'}
    )
    area = fields.Float(
        required=True,
        validate=validate.Range(min=0.1, max=10000),
        error_messages={'required': 'Área é obrigatória'}
    )
    location = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={'required': 'Localização é obrigatória'}
    )
    description = fields.Str(
        validate=validate.Length(max=1000),
        load_default=''
    )
    
    @pre_load
    def sanitize_input(self, data, **kwargs):
        """Sanitiza entrada antes da validação"""
        # Converter ImmutableMultiDict para dict mutável
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        elif hasattr(data, 'copy'):
            data = dict(data)
        else:
            data = dict(data) if data else {}
            
        text_fields = ['name', 'location', 'description']
        for field in text_fields:
            if field in data:
                data[field] = SecurityValidator.sanitize_string(data[field])
        return data

class ValidationManager:
    """Gerenciador central de validação"""
    
    schemas = {
        'login': LoginSchema(),
        'registration': RegistrationSchema(),
        'search': SearchSchema(),
        'culture': CultureSchema()
    }
    
    @classmethod
    def validate(cls, schema_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados usando schema específico"""
        if schema_name not in cls.schemas:
            raise ValueError(f"Schema '{schema_name}' não encontrado")
        
        schema = cls.schemas[schema_name]
        
        try:
            result = schema.load(data)
            logger.debug(f"Validation successful for schema: {schema_name}")
            return result
        except ValidationError as e:
            logger.warning(f"Validation failed for schema {schema_name}: {e.messages}")
            raise
    
    @classmethod
    def validate_partial(cls, schema_name: str, data: Dict[str, Any], partial: bool = True) -> Dict[str, Any]:
        """Valida dados parcialmente (para updates)"""
        if schema_name not in cls.schemas:
            raise ValueError(f"Schema '{schema_name}' não encontrado")
        
        schema = cls.schemas[schema_name]
        
        try:
            result = schema.load(data, partial=partial)
            logger.debug(f"Partial validation successful for schema: {schema_name}")
            return result
        except ValidationError as e:
            logger.warning(f"Partial validation failed for schema {schema_name}: {e.messages}")
            raise
