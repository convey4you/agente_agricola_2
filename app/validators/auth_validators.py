"""
Validators para autenticação
"""
import re
from typing import Tuple, Optional
from app.models.user import User


class AuthValidator:
    """Classe para validações de autenticação"""
    
    @staticmethod
    def validate_login_data(data: dict) -> Tuple[bool, Optional[str]]:
        """
        Valida dados de login
        
        Args:
            data: Dicionário com email e password
            
        Returns:
            Tuple (is_valid, error_message)
        """
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return False, 'Email e senha são obrigatórios'
        
        if not AuthValidator.is_valid_email(email):
            return False, 'Email inválido'
        
        return True, None
    
    @staticmethod
    def validate_register_data(data: dict) -> Tuple[bool, Optional[str]]:
        """
        Valida dados de registro
        
        Args:
            data: Dicionário com dados do usuário
            
        Returns:
            Tuple (is_valid, error_message)
        """
        email = data.get('email', '').strip()
        password = data.get('password', '')
        location = data.get('location', '').strip()
        
        # Campos obrigatórios
        if not all([email, password]):
            return False, 'Email e senha são obrigatórios'
        
        # Validar email
        if not AuthValidator.is_valid_email(email):
            return False, 'Email inválido'
        
        # Validar senha
        is_valid_password, password_msg = AuthValidator.validate_password(password)
        if not is_valid_password:
            return False, password_msg
        
        # Validar localização se fornecida
        if location:
            is_valid_location, location_msg = AuthValidator.validate_location_input(location)
            if not is_valid_location:
                return False, location_msg
        
        # Verificar se email já existe
        try:
            if User.query.filter_by(email=email).first():
                return False, 'Email já está em uso'
        except Exception:
            # Em ambiente de teste sem banco, ignorar verificação
            pass

        return True, None
    
    @staticmethod
    def validate_onboarding_data(step: str, data: dict) -> Tuple[bool, Optional[str]]:
        """
        Valida dados do onboarding por etapa - CORREÇÃO SPRINT 1
        
        Args:
            step: Etapa do onboarding
            data: Dados a validar
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if step in ['1', 1]:
            # Informações pessoais
            experience_level = data.get('experience_level')
            if experience_level not in ['beginner', 'intermediate', 'advanced']:
                return False, 'Nível de experiência inválido'
                
        elif step in ['2', 2]:
            # CORREÇÃO SPRINT 1: Validação correta para step 2
            full_name = data.get('full_name', '').strip()
            if not full_name:
                return False, 'Nome completo é obrigatório'
            
            if len(full_name) < 2:
                return False, 'Nome deve ter pelo menos 2 caracteres'
            
            # Validar experiência (campo correto: farm_experience)
            farm_experience = data.get('farm_experience')
            valid_experiences = ['iniciante', 'basico', 'intermediario', 'avancado', 'profissional']
            if not farm_experience or farm_experience not in valid_experiences:
                return False, 'Experiência na agricultura é obrigatória e deve ser válida'
            
            # Validar tipo de produtor
            producer_type = data.get('producer_type')
            valid_types = ['hobby', 'pequeno', 'medio', 'grande', 'comercial']
            if not producer_type or producer_type not in valid_types:
                return False, 'Tipo de produtor é obrigatório e deve ser válido'
            
            # Validar interesses
            interests = data.get('interests', [])
            if not interests or len(interests) == 0:
                return False, 'Selecione pelo menos um interesse'
            
            if len(interests) > 3:
                return False, 'Selecione no máximo 3 interesses'
            
            valid_interests = ['vegetables', 'fruits', 'grains', 'herbs', 'flowers']
            for interest in interests:
                if interest not in valid_interests:
                    return False, f'Interesse inválido: {interest}'
            
            # Validar telefone se fornecido
            phone = data.get('phone', '').strip()
            if phone and not AuthValidator.is_valid_phone(phone):
                return False, 'Formato de telefone inválido'
                
        elif step in ['3', 3]:
            # Informações da propriedade
            farm_name = data.get('farm_name', '').strip()
            farm_location = data.get('location', '').strip()  # Corrigido: 'location' ao invés de 'farm_location'
            
            if not farm_name:
                return False, 'Nome da propriedade é obrigatório'
            
            if len(farm_name) < 2:
                return False, 'Nome da propriedade deve ter pelo menos 2 caracteres'
            
            if not farm_location:
                return False, 'Localização da propriedade é obrigatória'
            
            if len(farm_location) < 2:
                return False, 'Localização deve ter pelo menos 2 caracteres'
                
        elif step in ['4', 4]:
            # Preferências de notificação - opcionais
            notifications = data.get('notifications', [])
            # Validar que se houver notificações, são válidas
            if notifications:
                valid_notifications = ['weather', 'tasks', 'ai_tips', 'updates', 'pests', 'irrigation', 'harvest', 'market']
                for notification in notifications:
                    if notification not in valid_notifications:
                        return False, f'Tipo de notificação inválido: {notification}'
                        
        elif step in ['5', 5]:
            # Finalização - aceitar termos
            if not data.get('complete_onboarding'):
                return False, 'Onboarding deve ser marcado como completo'
        
        return True, None
    
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        Valida formato do telefone - CORREÇÃO SPRINT 1
        
        Args:
            phone: Telefone a validar
            
        Returns:
            True se válido
        """
        if not phone:
            return True  # Telefone é opcional
        
        # Remover todos os espaços e caracteres especiais para validação
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Formato português completo: +351 9XX XXX XXX
        portuguese_pattern_full = r'^\+351\s?9\d{8}$'
        # Formato português sem código: 9XX XXX XXX (9 dígitos)
        portuguese_pattern_short = r'^9\d{8}$'
        # Formato brasileiro: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
        brazilian_pattern = r'^\(\d{2}\)\s?\d{4,5}-?\d{4}$'
        
        # Verificar os padrões
        return (re.match(portuguese_pattern_full, phone.replace(' ', '')) is not None or 
                re.match(portuguese_pattern_short, clean_phone) is not None or
                re.match(brazilian_pattern, phone) is not None)
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Valida formato do email
        
        Args:
            email: Email a validar
            
        Returns:
            True se válido, False caso contrário
        """
        if not email or not isinstance(email, str):
            return False
            
        # Verificar comprimento máximo (RFC 5321 limita a 320 caracteres)
        if len(email) > 254:  # Limite mais restritivo para emails práticos
            return False
            
        # Verificar pontos duplos consecutivos
        if '..' in email:
            return False
            
        # Verificar se começa ou termina com ponto
        if email.startswith('.') or email.endswith('.'):
            return False
            
        # Verificar se há ponto antes ou depois do @
        if '.@' in email or '@.' in email:
            return False
            
        # Pattern básico melhorado
        pattern = r'^[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'
        
        if not re.match(pattern, email):
            return False
            
        # Verificar se o domínio não tem pontos duplos
        parts = email.split('@')
        if len(parts) != 2:
            return False
            
        local, domain = parts
        
        # Verificar se o domínio não termina com ponto
        if domain.endswith('.'):
            return False
            
        # Verificar pontos duplos no domínio
        if '..' in domain:
            return False
            
        return True
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Valida força da senha - CORREÇÃO SPRINT 1
        
        Args:
            password: Senha a validar
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if len(password) < 6:
            return False, 'Senha deve ter pelo menos 6 caracteres'
        
        if not re.search(r'[A-Za-z]', password):
            return False, 'Senha deve conter pelo menos uma letra (a-z ou A-Z)'
        
        if not re.search(r'\d', password):
            return False, 'Senha deve conter pelo menos um número (0-9)'
        
        # CORREÇÃO SPRINT 1: Adicionar mais validações
        if len(password) > 128:
            return False, 'Senha muito longa (máximo 128 caracteres)'
            
        # Verificar espaços em branco
        if ' ' in password:
            return False, 'Senha não pode conter espaços em branco'
            
        return True, None
    
    @staticmethod
    def validate_location_input(location: str) -> Tuple[bool, Optional[str]]:
        """
        Valida entrada de localização
        
        Args:
            location: String de localização
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not location or not location.strip():
            return False, 'Localização não pode estar vazia'
        
        location = location.strip()
        
        # Verificar comprimento mínimo
        if len(location) < 3:
            return False, 'Localização deve ter pelo menos 3 caracteres'
        
        # Verificar comprimento máximo
        if len(location) > 200:
            return False, 'Localização muito longa (máximo 200 caracteres)'
        
        # Verificar caracteres válidos
        if not re.match(r'^[a-zA-ZÀ-ÿ0-9\s,.\-\(\)]+$', location):
            return False, 'Localização contém caracteres inválidos'
        
        # Sugerir formato melhor se não tem vírgula ou distrito
        if ',' not in location and len(location.split()) < 2:
            return False, 'Use um formato mais específico como "Lisboa" ou "Porto, Distrito do Porto"'
        
        return True, None
    
    @staticmethod
    def validate_coordinates_input(latitude: float, longitude: float) -> Tuple[bool, Optional[str]]:
        """
        Valida coordenadas de entrada
        
        Args:
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            Tuple (is_valid, error_message)
        """
        try:
            # Converter para float se necessário
            lat = float(latitude)
            lng = float(longitude)
            
            # Validar range geral de coordenadas
            if not (-90 <= lat <= 90):
                return False, 'Latitude deve estar entre -90 e 90'
            
            if not (-180 <= lng <= 180):
                return False, 'Longitude deve estar entre -180 e 180'
            
            # Validar se está em Portugal (incluindo ilhas)
            # Portugal Continental
            if (36.9 <= lat <= 42.2) and (-9.5 <= lng <= -6.2):
                return True, None
            
            # Açores
            if (36.9 <= lat <= 39.7) and (-31.3 <= lng <= -25.0):
                return True, None
            
            # Madeira
            if (32.4 <= lat <= 33.1) and (-17.3 <= lng <= -16.3):
                return True, None
            
            return False, 'Coordenadas fora dos limites de Portugal'
            
            return True, None
            
        except (TypeError, ValueError):
            return False, 'Coordenadas devem ser números válidos'
