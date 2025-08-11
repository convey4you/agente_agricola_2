"""
Services para culturas
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from flask import session, current_app
from flask_login import current_user

from app import db
from app.models.farm import Farm
from app.models.culture import Culture, CultureType
from app.validators.culture_validators import CultureValidator
from app.utils.cache_manager import cache, cached


logger = logging.getLogger(__name__)


class CultureService:
    """Service para operações de cultura"""
    
    @staticmethod
    @cached(
        timeout=lambda: current_app.config.get('CACHE_TIMEOUT_CULTURE', 86400),
        namespace='culture',
        key_func=lambda: f"user_cultures:user_{current_user.id if current_user.is_authenticated else 'anonymous'}"
    )
    def get_user_cultures() -> Dict[str, Any]:
        """
        Obtém todas as culturas do usuário
        
        Returns:
            Dict com resultado da operação
        """
        try:
            logger.info(f"Buscando culturas do usuário: {current_user.email}")
            logger.info(f"User ID: {current_user.id}")
            
            # Verificar se existe alguma farm para o usuário
            farms = Farm.query.filter(Farm.user_id == current_user.id).all()
            logger.info(f"Farms encontradas para o usuário: {len(farms)}")
            
            cultures = Culture.query.join(Farm).filter(
                Farm.user_id == current_user.id
            ).all()
            
            logger.info(f"Culturas encontradas: {len(cultures)}")
            
            return {
                'success': True,
                'cultures': [culture.to_dict() for culture in cultures]
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar culturas: {e}")
            logger.exception("Stack trace completo:")
            return {
                'success': False,
                'error': 'Erro ao buscar culturas',
                'status_code': 500
            }
    
    @staticmethod
    def create_culture(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria nova cultura
        
        Args:
            data: Dados da cultura
            
        Returns:
            Dict com resultado da operação
        """
        try:
            logger.info(f"Criando cultura: {data.get('nome')} para usuário: {current_user.email}")
            
            # Criar cultura
            culture = Culture(
                farm_id=data['farm_id'],
                nome=data['nome'],
                tipo=data['tipo'],
                variedade=data.get('variedade'),
                area_plantada=data.get('area_plantada'),
                localizacao=data.get('localizacao'),
                observacoes=data.get('observacoes')
            )
            
            # Processar datas
            if data.get('data_plantio'):
                culture.data_plantio = datetime.strptime(data['data_plantio'], '%Y-%m-%d').date()
            
            if data.get('data_colheita_prevista'):
                culture.data_colheita_prevista = datetime.strptime(data['data_colheita_prevista'], '%Y-%m-%d').date()
            
            db.session.add(culture)
            db.session.commit()
            
            logger.info(f"Cultura criada com sucesso: ID {culture.id}")
            
            return {
                'success': True,
                'message': 'Cultura criada com sucesso',
                'culture': culture.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar cultura: {e}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Erro ao criar cultura',
                'status_code': 500
            }
    
    @staticmethod
    @cached(
        timeout=lambda: current_app.config.get('CACHE_TIMEOUT_CULTURE', 86400),
        namespace='culture',
        key_func=lambda culture_id: f"culture_by_id:id_{culture_id}_user_{current_user.id if current_user.is_authenticated else 'anonymous'}"
    )
    def get_culture_by_id(culture_id: int) -> Dict[str, Any]:
        """
        Obtém cultura específica do usuário
        
        Args:
            culture_id: ID da cultura
            
        Returns:
            Dict com resultado da operação
        """
        try:
            logger.info(f"Buscando cultura ID {culture_id} para usuário: {current_user.email}")
            
            culture = Culture.query.join(Farm).filter(
                Culture.id == culture_id,
                Farm.user_id == current_user.id
            ).first()
            
            if not culture:
                return {
                    'success': False,
                    'error': 'Cultura não encontrada',
                    'status_code': 404
                }
            
            return {
                'success': True,
                'culture': culture.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar cultura: {e}")
            return {
                'success': False,
                'error': 'Erro ao buscar cultura',
                'status_code': 500
            }
    
    @staticmethod
    def update_culture(culture_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza cultura existente
        
        Args:
            culture_id: ID da cultura
            data: Dados para atualização
            
        Returns:
            Dict com resultado da operação
        """
        try:
            logger.info(f"Atualizando cultura ID {culture_id} para usuário: {current_user.email}")
            
            culture = Culture.query.join(Farm).filter(
                Culture.id == culture_id,
                Farm.user_id == current_user.id
            ).first()
            
            if not culture:
                return {
                    'success': False,
                    'error': 'Cultura não encontrada',
                    'status_code': 404
                }
            
            # Atualizar campos
            updatable_fields = [
                'nome', 'tipo', 'variedade', 'area_plantada', 
                'localizacao', 'status', 'observacoes'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(culture, field, data[field])
            
            # Processar datas
            if 'data_plantio' in data and data['data_plantio']:
                culture.data_plantio = datetime.strptime(data['data_plantio'], '%Y-%m-%d').date()
            
            if 'data_colheita_prevista' in data and data['data_colheita_prevista']:
                culture.data_colheita_prevista = datetime.strptime(data['data_colheita_prevista'], '%Y-%m-%d').date()
            
            db.session.commit()
            
            logger.info(f"Cultura atualizada com sucesso: ID {culture.id}")
            
            return {
                'success': True,
                'message': 'Cultura atualizada com sucesso',
                'culture': culture.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Erro ao atualizar cultura: {e}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Erro ao atualizar cultura',
                'status_code': 500
            }
    
    @staticmethod
    def delete_culture(culture_id: int) -> Dict[str, Any]:
        """
        Exclui cultura do usuário
        
        Args:
            culture_id: ID da cultura
            
        Returns:
            Dict com resultado da operação
        """
        try:
            logger.info(f"Excluindo cultura ID {culture_id} para usuário: {current_user.email}")
            
            culture = Culture.query.join(Farm).filter(
                Culture.id == culture_id,
                Farm.user_id == current_user.id
            ).first()
            
            if not culture:
                return {
                    'success': False,
                    'error': 'Cultura não encontrada',
                    'status_code': 404
                }
            
            culture_name = culture.nome
            db.session.delete(culture)
            db.session.commit()
            
            logger.info(f"Cultura excluída com sucesso: {culture_name}")
            
            return {
                'success': True,
                'message': 'Cultura excluída com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao excluir cultura: {e}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Erro ao excluir cultura',
                'status_code': 500
            }
    
    @staticmethod
    def get_culture_types() -> Dict[str, Any]:
        """
        Obtém tipos de cultura disponíveis
        
        Returns:
            Dict com tipos de cultura
        """
        return {
            'success': True,
            'types': CultureValidator.get_culture_types()
        }


class CultureWizardService:
    """Service para wizard de cultura"""
    
    @staticmethod
    def save_wizard_step(step: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Salva dados de uma etapa do wizard
        
        Args:
            step: Etapa do wizard
            data: Dados da etapa
            
        Returns:
            Dict com resultado da operação
        """
        try:
            logger.info(f"Salvando wizard step {step} para usuário: {current_user.email}")
            
            # Inicializar sessão do wizard se não existir
            if 'culture_wizard' not in session:
                session['culture_wizard'] = {}
            
            # Marcar sessão como permanente para persistir dados
            session.permanent = True
            
            if step == '1':
                # Etapa 1: Dados da cultura
                nome_cultura = data.get('nome')
                
                # Buscar informações completas da cultura
                cultura_completa = None
                if nome_cultura:
                    from app.services.base_conhecimento_culturas import buscar_cultura
                    cultura_completa = buscar_cultura(nome_cultura)
                
                session['culture_wizard'].update({
                    'nome': nome_cultura,
                    'tipo': data.get('tipo'),
                    'variedade': data.get('variedade'),
                    'step': 2
                })
                
                # Adicionar informações completas da cultura se encontrada
                if cultura_completa:
                    session['culture_wizard'].update({
                        'categoria': cultura_completa.get('categoria'),
                        'clima_ideal': cultura_completa.get('clima_ideal'),
                        'tempo_crescimento': cultura_completa.get('tempo_crescimento'),
                        'dificuldade': cultura_completa.get('dificuldade'),
                        'rega_frequencia': cultura_completa.get('rega_frequencia'),
                        'sol_horas_min': cultura_completa.get('sol_horas_min'),
                        'solo_ph': cultura_completa.get('solo_ph'),
                        'observacoes': cultura_completa.get('observacoes'),
                        'epoca_plantio': cultura_completa.get('epoca_plantio')
                    })
                
            elif step == '2':
                # Etapa 2: Dados da área
                session['culture_wizard'].update({
                    'area_plantada': data.get('area_plantada'),
                    'localizacao': data.get('localizacao'),
                    'exposicao_solar': data.get('exposicao_solar'),
                    'tipo_solo': data.get('tipo_solo'),
                    'drenagem': data.get('drenagem'),
                    'acesso_agua': data.get('acesso_agua'),
                    'coordenadas': data.get('coordenadas'),
                    'step': 3
                })
                
            elif step == '3':
                # Etapa 3: Dados do calendário
                session['culture_wizard'].update({
                    'data_plantio': data.get('data_plantio'),
                    'ciclo_dias': data.get('ciclo_dias'),
                    'data_colheita_prevista': data.get('data_colheita_prevista'),
                    'estacao_plantio': data.get('estacao_plantio'),
                    'temp_min': data.get('temp_min'),
                    'temp_max': data.get('temp_max'),
                    'step': 4
                })
                
            elif step == '4':
                # Etapa 4: Recursos
                session['culture_wizard'].update({
                    'freq_irrigacao': data.get('freq_irrigacao'),
                    'quantidade_agua': data.get('quantidade_agua'),
                    'horario_irrigacao': data.get('horario_irrigacao'),
                    'sistema_irrigacao': data.get('sistema_irrigacao'),
                    'tipo_fertilizante': data.get('tipo_fertilizante'),
                    'freq_fertilizacao': data.get('freq_fertilizacao'),
                    'quantidade_fertilizante': data.get('quantidade_fertilizante'),
                    'metodo_controle': data.get('metodo_controle'),
                    'freq_monitoramento': data.get('freq_monitoramento'),
                    'observacoes': data.get('observacoes'),
                    'step': 5
                })
                
            elif step == '5':
                # Etapa 5: Criar cultura final
                # Verificar se há dados de backup no request
                wizard_backup = data.get('wizard_backup')
                if wizard_backup and not session.get('culture_wizard'):
                    logger.info("DEBUG: Usando dados de backup do localStorage")
                    session['culture_wizard'] = wizard_backup
                    session.permanent = True
                    session.modified = True
                
                return CultureWizardService.create_culture_from_wizard()
            
            # Forçar commit da sessão para garantir persistência
            session.permanent = True
            session.modified = True
            
            logger.info(f"Wizard step {step} salvo com sucesso. Dados: {session.get('culture_wizard', {})}")
            
            return {
                'success': True,
                'message': 'Dados salvos com sucesso',
                'next_step': session['culture_wizard'].get('step', int(step) + 1),
                'data': session['culture_wizard']  # Retornar dados para debug
            }
            
        except Exception as e:
            logger.error(f"Erro ao salvar wizard step: {e}")
            return {
                'success': False,
                'error': 'Erro ao salvar dados',
                'status_code': 500
            }
    
    @staticmethod
    def create_culture_from_wizard() -> Dict[str, Any]:
        """
        Cria cultura com dados do wizard
        
        Returns:
            Dict com resultado da operação
        """
        try:
            wizard_data = session.get('culture_wizard', {})
            logger.info(f"Criando cultura do wizard para usuário: {current_user.email}")
            logger.info(f"DEBUG: Dados do wizard na sessão: {wizard_data}")
            logger.info(f"DEBUG: Sessão completa: {dict(session)}")
            logger.info(f"DEBUG: Session ID: {session.get('_id', 'Sem ID')}")
            
            # Verificar se há dados no wizard
            if not wizard_data:
                logger.error("DEBUG: Nenhum dado encontrado na sessão do wizard")
                logger.error(f"DEBUG: Tentando recuperar de localStorage/backup")
                
                if not wizard_data:
                    return {
                        'success': False,
                        'error': 'Nenhum dado do wizard encontrado na sessão. Verifique se completou todos os passos.',
                        'status_code': 400,
                        'debug_info': {
                            'session_keys': list(session.keys()),
                            'user_id': current_user.id,
                            'session_id': session.get('_id', 'unknown')
                        }
                    }
            
            # Obter fazenda do usuário
            farm = Farm.query.filter_by(user_id=current_user.id).first()
            logger.info(f"DEBUG: Fazenda encontrada: {farm.id if farm else 'Nenhuma'}")
            if not farm:
                return {
                    'success': False,
                    'error': 'Fazenda não encontrada',
                    'status_code': 404
                }
            
            # Buscar tipo de cultura
            culture_type = CultureType.query.first()
            if not culture_type:
                logger.error("DEBUG: Nenhum tipo de cultura encontrado")
                return {
                    'success': False,
                    'error': 'Tipo de cultura não encontrado',
                    'status_code': 404
                }
            
            # Criar cultura
            logger.info(f"DEBUG: Criando cultura com dados: nome={wizard_data.get('nome')}")
            
            culture = Culture(
                user_id=current_user.id,
                farm_id=farm.id,
                culture_type_id=culture_type.id,
                nome=wizard_data.get('nome', 'Cultura sem nome'),
                variedade=wizard_data.get('variedade'),
                area_plantada=wizard_data.get('area_plantada'),
                localizacao=wizard_data.get('localizacao'),
                observacoes=wizard_data.get('observacoes')
            )
            
            # Processar datas
            if wizard_data.get('data_plantio'):
                logger.info(f"DEBUG: Processando data_plantio: {wizard_data.get('data_plantio')}")
                culture.data_plantio = datetime.strptime(wizard_data['data_plantio'], '%Y-%m-%d').date()
            
            if wizard_data.get('data_colheita_prevista'):
                logger.info(f"DEBUG: Processando data_colheita_prevista: {wizard_data.get('data_colheita_prevista')}")
                culture.data_colheita_prevista = datetime.strptime(wizard_data['data_colheita_prevista'], '%Y-%m-%d').date()
            
            logger.info("DEBUG: Adicionando cultura ao banco de dados")
            db.session.add(culture)
            db.session.commit()
            logger.info("DEBUG: Cultura commitada com sucesso")
            
            # Limpar dados do wizard da sessão
            session.pop('culture_wizard', None)
            
            logger.info(f"Cultura criada do wizard com sucesso: ID {culture.id}")
            
            return {
                'success': True,
                'message': 'Cultura criada com sucesso!',
                'culture': culture.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar cultura do wizard: {e}")
            logger.exception("Stack trace completo:")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Erro ao criar cultura',
                'status_code': 500
            }
    
    @staticmethod
    def get_wizard_data() -> Dict[str, Any]:
        """
        Obtém dados salvos no wizard
        
        Returns:
            Dict com dados do wizard
        """
        wizard_data = session.get('culture_wizard', {})
        return {
            'success': True,
            'data': wizard_data
        }
