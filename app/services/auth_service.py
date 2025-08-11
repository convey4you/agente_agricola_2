"""
Services para autenticação
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from flask import current_app
from flask_login import login_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models.user import User
from app.models.alerts import UserAlertPreference, AlertType, AlertPriority
from app.validators.auth_validators import AuthValidator


logger = logging.getLogger(__name__)


class AuthService:
    """Service para operações de autenticação"""
    
    @staticmethod
    def _create_default_alert_preferences(user: User) -> None:
        """
        Cria preferências de alerta padrão para um novo usuário
        
        Args:
            user: Usuário para criar as preferências
        """
        try:
            logger.info(f"Criando preferências de alerta padrão para usuário: {user.email}")
            
            # Definir configurações padrão baseadas no nível de experiência
            is_beginner = getattr(user, 'experience_level', 'beginner') == 'beginner'
            
            # Configurações padrão por tipo de alerta
            default_preferences = {
                AlertType.WEATHER: {
                    'enabled': True,
                    'web': True,
                    'email': True,
                    'sms': False,
                    'min_priority': AlertPriority.MEDIUM
                },
                AlertType.PEST: {
                    'enabled': True,
                    'web': True,
                    'email': is_beginner,  # Iniciantes recebem mais emails
                    'sms': False,
                    'min_priority': AlertPriority.HIGH if not is_beginner else AlertPriority.MEDIUM
                },
                AlertType.DISEASE: {
                    'enabled': True,
                    'web': True,
                    'email': is_beginner,
                    'sms': False,
                    'min_priority': AlertPriority.HIGH if not is_beginner else AlertPriority.MEDIUM
                },
                AlertType.IRRIGATION: {
                    'enabled': True,
                    'web': True,
                    'email': is_beginner,
                    'sms': False,
                    'min_priority': AlertPriority.MEDIUM
                },
                AlertType.FERTILIZATION: {
                    'enabled': True,
                    'web': True,
                    'email': is_beginner,
                    'sms': False,
                    'min_priority': AlertPriority.MEDIUM
                },
                AlertType.HARVEST: {
                    'enabled': True,
                    'web': True,
                    'email': True,  # Todos recebem alertas de colheita
                    'sms': False,
                    'min_priority': AlertPriority.HIGH
                },
                AlertType.PRUNING: {
                    'enabled': True,
                    'web': True,
                    'email': is_beginner,
                    'sms': False,
                    'min_priority': AlertPriority.MEDIUM
                },
                AlertType.MARKET: {
                    'enabled': True,
                    'web': True,
                    'email': False,  # Oportunidades de mercado só na web por padrão
                    'sms': False,
                    'min_priority': AlertPriority.MEDIUM
                },
                AlertType.GENERAL: {
                    'enabled': True,
                    'web': True,
                    'email': False,
                    'sms': False,
                    'min_priority': AlertPriority.HIGH
                }
            }
            
            # Criar preferências para cada tipo de alerta
            created_count = 0
            for alert_type, settings in default_preferences.items():
                # Verificar se já existe preferência para este tipo
                existing = UserAlertPreference.query.filter_by(
                    user_id=user.id,
                    alert_type=alert_type
                ).first()
                
                if not existing:
                    preference = UserAlertPreference()
                    preference.user_id = user.id
                    preference.alert_type = alert_type
                    preference.is_enabled = settings['enabled']
                    preference.web_enabled = settings['web']
                    preference.email_enabled = settings['email']
                    preference.sms_enabled = settings['sms']
                    preference.min_priority = settings['min_priority']
                    preference.quiet_hours_start = datetime.strptime('22:00', '%H:%M').time()
                    preference.quiet_hours_end = datetime.strptime('08:00', '%H:%M').time()
                    
                    db.session.add(preference)
                    created_count += 1
            
            if created_count > 0:
                db.session.commit()
                logger.info(f"Criadas {created_count} preferências de alerta para {user.email}")
            else:
                logger.info(f"Preferências de alerta já existem para {user.email}")
                
        except Exception as e:
            logger.error(f"Erro ao criar preferências de alerta para {user.email}: {e}")
            db.session.rollback()
            raise
    
    @staticmethod
    def authenticate_user(email: str, password: str, remember: bool = False) -> Dict[str, Any]:
        """
        Autentica usuário
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            remember: Se deve lembrar o login
            
        Returns:
            Dict com resultado da autenticação
        """
        try:
            logger.info(f"Tentativa de login para: {email}")
            
            user = User.query.filter_by(email=email).first()
            
            if not user:
                logger.warning(f"Usuário não encontrado: {email}")
                return {
                    'success': False,
                    'error': 'Credenciais inválidas',
                    'status_code': 401
                }
            
            if not check_password_hash(user.password_hash, password):
                logger.warning(f"Senha incorreta para: {email}")
                return {
                    'success': False,
                    'error': 'Credenciais inválidas',
                    'status_code': 401
                }
            
            # Atualizar último acesso
            user.ultimo_acesso = datetime.now(timezone.utc)
            db.session.commit()
            
            # Fazer login
            login_user(user, remember=remember)
            
            logger.info(f"Login realizado com sucesso: {email}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'needs_onboarding': not user.onboarding_completed
            }
            
        except Exception as e:
            logger.error(f"Erro durante autenticação: {e}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Erro interno durante autenticação',
                'status_code': 500
            }
    
    @staticmethod
    def create_user(email: str, password: str, nome_completo: str = '', telefone: str = '',
                   location: str = '', latitude: float = None, longitude: float = None) -> Dict[str, Any]:
        """
        Cria novo usuário - CORREÇÃO SPRINT 1 + Geocoding + Telefone
        
        Args:
            email: Email do usuário
            password: Senha
            nome_completo: Nome completo (opcional)
            telefone: Telefone completo com código do país (opcional)
            location: Localização fornecida pelo usuário (opcional)
            latitude: Latitude geocodificada (opcional)
            longitude: Longitude geocodificada (opcional)
            
        Returns:
            Dict com resultado da criação
        """
        try:
            logger.info(f"Criando novo usuário: {email}")
            
            # CORREÇÃO SPRINT 1: Verificação mais específica de email existente
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                logger.warning(f"Tentativa de criação com email já existente: {email}")
                return {
                    'success': False,
                    'error': f'Já existe uma conta com o email {email}. Tente fazer login ou use um email diferente.',
                    'error_code': 'EMAIL_EXISTS',
                    'status_code': 409
                }
            
            # Preparar dados do usuário
            user_data = {
                'email': email,
                'nome_completo': nome_completo,
                'password_hash': generate_password_hash(password)
            }
            
            # Adicionar telefone se fornecido
            if telefone:
                # CORREÇÃO: Garantir que o telefone não tenha duplicação do código do país
                # Se o telefone já começa com +, usar como está
                # Se não, verificar se não há duplicação
                if telefone.startswith('+'):
                    # Verificar se há duplicação de código do país
                    # Ex: +351351912345678 -> +351912345678
                    telefone_limpo = telefone
                    for code in ['+351', '+34', '+33', '+55', '+1', '+49', '+39', '+44']:
                        if telefone.startswith(code + code.replace('+', '')):
                            # Remover duplicação: +351351... -> +351...
                            telefone_limpo = code + telefone[len(code + code.replace('+', '')):]
                            break
                    user_data['telefone'] = telefone_limpo
                else:
                    user_data['telefone'] = telefone
            
            # Adicionar informações de localização se disponíveis
            # CORREÇÃO: Salvar location no campo cidade que existe no modelo
            if location:
                user_data['cidade'] = location
            if latitude is not None and longitude is not None:
                user_data['latitude'] = latitude
                user_data['longitude'] = longitude
            
            # Criar usuário
            user = User(**user_data)
            
            db.session.add(user)
            db.session.flush()  # CORREÇÃO SPRINT 1: Flush para detectar erros de DB
            db.session.commit()
            
            # Login automático
            login_user(user)
            
            logger.info(f"Usuário criado com sucesso: {email} (ID: {user.id})")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'user_id': user.id,
                'message': f'Conta criada com sucesso para {email}! Bem-vindo ao AgroTech Portugal.',
                'has_location': bool(location),
                'has_coordinates': bool(latitude is not None and longitude is not None),
                'has_phone': bool(telefone)
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário {email}: {e}")
            db.session.rollback()
            
            # CORREÇÃO SPRINT 1: Mensagens de erro mais específicas
            error_msg = 'Erro interno do servidor. Tente novamente em alguns minutos.'
            if 'UNIQUE constraint failed' in str(e):
                error_msg = f'Email {email} já está em uso. Tente fazer login ou usar outro email.'
            elif 'database is locked' in str(e):
                error_msg = 'Sistema temporariamente indisponível. Tente novamente em alguns segundos.'
            
            return {
                'success': False,
                'error': error_msg,
                'error_code': 'DB_ERROR',
                'status_code': 500,
                'technical_error': str(e)
            }
    
    @staticmethod
    def save_onboarding_step(user: User, step: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Salva dados de uma etapa do onboarding
        
        Args:
            user: Usuário atual
            step: Etapa do onboarding
            data: Dados a salvar
            
        Returns:
            Dict com resultado da operação
        """
        try:
            logger.info(f"Salvando onboarding step {step} para usuário: {user.email}")
            logger.debug(f"Dados recebidos: {data}")
            
            if step in ['1', 1]:
                # Informações básicas do usuário
                user.experience_level = data.get('experience_level', 'beginner')
                
            elif step in ['2', 2]:
                # CORREÇÃO SPRINT 1: Dados pessoais do passo 2 com campos corretos
                if 'full_name' in data:
                    user.nome_completo = data.get('full_name', '').strip()
                    logger.info(f"Nome completo salvo: {user.nome_completo}")
                    
                if 'phone' in data:
                    phone_value = data.get('phone', '').strip()
                    country_code = data.get('country_code', '+351').strip()
                    
                    # Se o phone já inclui código do país, usar como está
                    # Se não, combinar código do país + número
                    if phone_value.startswith('+'):
                        user.telefone = phone_value
                    elif phone_value:
                        user.telefone = f"{country_code}{phone_value}"
                    else:
                        user.telefone = ''
                    
                    logger.info(f"Telefone salvo: {user.telefone}")
                    
                # CORREÇÃO: Aceitar tanto farm_experience quanto experience_level
                experience_value = None
                if 'farm_experience' in data:
                    experience_value = data.get('farm_experience', '').lower()
                elif 'experience_level' in data:
                    experience_value = data.get('experience_level', '').lower()
                
                if experience_value:
                    # Padronizar valores em português para inglês
                    experience_mapping = {
                        'iniciante': 'beginner',
                        'basico': 'beginner', 
                        'beginner': 'beginner',
                        'intermediario': 'intermediate',
                        'intermedio': 'intermediate',
                        'intermediate': 'intermediate',
                        'avancado': 'advanced',
                        'experiente': 'advanced',
                        'advanced': 'advanced'
                    }
                    
                    standardized_experience = experience_mapping.get(experience_value, 'beginner')
                    user.experience_level = standardized_experience
                    logger.info(f"Experiência salva e padronizada: {experience_value} -> {standardized_experience}")
                    
                # CORREÇÃO: producer_type 
                if 'producer_type' in data:
                    # Adicionar campo se não existir no modelo
                    if hasattr(user, 'producer_type'):
                        user.producer_type = data.get('producer_type', '')
                    logger.info(f"Tipo de produtor salvo: {data.get('producer_type', '')}")
                
                # Salvar interesses se fornecidos
                interests = data.get('interests', [])
                if interests:
                    # Converter lista de interesses em string separada por vírgulas
                    interests_str = ','.join(interests)
                    if hasattr(user, 'interesses'):
                        user.interesses = interests_str
                    logger.info(f"Interesses salvos: {interests}")
                
            elif step in ['3', 3]:
                # Informações da propriedade com geolocalização
                farm_name = data.get('farm_name', '').strip()
                location = data.get('location', '').strip()
                latitude = data.get('latitude')
                longitude = data.get('longitude')
                formatted_address = data.get('formatted_address', '').strip()
                farm_area = data.get('farm_area')
                soil_type = data.get('soil_type', '').strip()
                climate = data.get('climate', '').strip()
                water_sources = data.get('water_sources', [])
                
                # Validação básica
                if not farm_name or not location:
                    logger.warning(f"Dados obrigatórios ausentes no step 3: farm_name={farm_name}, location={location}")
                    return {
                        'success': False,
                        'error': 'Nome da propriedade e localização são obrigatórios'
                    }
                
                # Salvar no perfil do usuário
                user.propriedade_nome = farm_name
                user.cidade = location
                
                # Salvar coordenadas se disponíveis
                if latitude and longitude:
                    try:
                        user.latitude = float(latitude)
                        user.longitude = float(longitude)
                        logger.info(f"Coordenadas salvas: {latitude}, {longitude}")
                    except (ValueError, TypeError):
                        logger.warning(f"Coordenadas inválidas: lat={latitude}, lng={longitude}")
                
                # Criar ou atualizar Farm
                from app.models.farm import Farm
                existing_farm = Farm.query.filter_by(user_id=user.id).first()
                
                # Preparar área (converter para float ou usar padrão)
                try:
                    area_value = float(farm_area) if farm_area else 1.0
                except (ValueError, TypeError):
                    area_value = 1.0
                
                if not existing_farm:
                    new_farm = Farm(
                        name=farm_name,
                        address=formatted_address or location,
                        city=location.split(',')[0].strip() if ',' in location else location,
                        state=location.split(',')[1].strip() if ',' in location else '',
                        user_id=user.id,
                        area_total=area_value,
                        latitude=float(latitude) if latitude else None,
                        longitude=float(longitude) if longitude else None,
                        description=f"Solo: {soil_type}, Clima: {climate}, Água: {', '.join(water_sources)}" if any([soil_type, climate, water_sources]) else None
                    )
                    db.session.add(new_farm)
                    logger.info(f"Farm criada: {farm_name} em {location} para usuário {user.email}")
                else:
                    # Atualizar farm existente
                    existing_farm.name = farm_name
                    existing_farm.address = formatted_address or location
                    existing_farm.city = location.split(',')[0].strip() if ',' in location else location
                    existing_farm.state = location.split(',')[1].strip() if ',' in location else ''
                    existing_farm.area_total = area_value
                    if latitude and longitude:
                        try:
                            existing_farm.latitude = float(latitude)
                            existing_farm.longitude = float(longitude)
                        except (ValueError, TypeError):
                            pass
                    existing_farm.description = f"Solo: {soil_type}, Clima: {climate}, Água: {', '.join(water_sources)}" if any([soil_type, climate, water_sources]) else existing_farm.description
                    logger.info(f"Farm atualizada: {farm_name} em {location} para usuário {user.email}")
                
                logger.info(f"Step 3 processado com sucesso: propriedade='{farm_name}', localização='{location}'")
                
            elif step in ['4', 4]:
                # Informações da propriedade
                user.propriedade_nome = data.get('propriedade_nome', '')
                
            elif step in ['5', 5] or data.get('complete_onboarding'):
                # Finalizar onboarding
                user.onboarding_completed = True
                
                # Criar preferências de alerta padrão se ainda não existem
                try:
                    AuthService._create_default_alert_preferences(user)
                    logger.info(f"Preferências de alerta configuradas para usuário: {user.email}")
                except Exception as e:
                    logger.warning(f"Erro ao configurar preferências de alerta para {user.email}: {e}")
                
                logger.info(f"Onboarding finalizado para usuário: {user.email}")
            
            db.session.commit()
            logger.info(f"Onboarding step {step} salvo com sucesso para {user.email}")
            
            return {
                'success': True,
                'message': f'Dados do passo {step} salvos com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao salvar onboarding: {e}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Erro ao salvar dados',
                'status_code': 500
            }
    
    @staticmethod
    def get_user_auth_status(user) -> Dict[str, Any]:
        """
        Retorna status de autenticação do usuário
        
        Args:
            user: Usuário atual (current_user)
            
        Returns:
            Dict com status de autenticação
        """
        if user.is_authenticated:
            return {
                'authenticated': True,
                'user': user.to_dict()
            }
        else:
            return {
                'authenticated': False
            }
