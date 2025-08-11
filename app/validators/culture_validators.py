"""
Validators para culturas
"""
import re
from datetime import datetime, timezone, date
from typing import Tuple, Optional, Dict, Any
from app.models.farm import Farm
from flask_login import current_user


class CultureValidator:
    """Classe para validações de cultura"""
    
    # Tipos de cultura válidos
    VALID_CULTURE_TYPES = [
        'arvore_frutifera', 'hortalica', 'erva_aromatica', 
        'grao', 'cereal', 'leguminosa'
    ]
    
    # Status válidos
    VALID_STATUS = ['planejada', 'plantada', 'crescimento', 'colheita', 'finalizada']
    
    @staticmethod
    def validate_create_culture_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida dados para criação de cultura
        
        Args:
            data: Dicionário com dados da cultura
            
        Returns:
            Tuple (is_valid, error_message)
        """
        # Campos obrigatórios
        required_fields = ['farm_id', 'nome', 'tipo']
        for field in required_fields:
            if not data.get(field):
                return False, f'Campo {field} é obrigatório'
        
        # Validar nome
        nome = data.get('nome', '').strip()
        if len(nome) < 2:
            return False, 'Nome da cultura deve ter pelo menos 2 caracteres'
        
        if len(nome) > 100:
            return False, 'Nome da cultura não pode exceder 100 caracteres'
        
        # Validar tipo
        tipo = data.get('tipo')
        if tipo not in CultureValidator.VALID_CULTURE_TYPES:
            return False, f'Tipo de cultura inválido. Tipos válidos: {", ".join(CultureValidator.VALID_CULTURE_TYPES)}'
        
        # Validar farm_id
        farm_id = data.get('farm_id')
        try:
            farm_id = int(farm_id)
        except (ValueError, TypeError):
            return False, 'ID da fazenda deve ser um número válido'
        
        # Verificar se fazenda pertence ao usuário
        farm = Farm.query.filter_by(id=farm_id, user_id=current_user.id).first()
        if not farm:
            return False, 'Fazenda não encontrada ou não pertence ao usuário'
        
        # Validar área plantada (opcional)
        area_plantada = data.get('area_plantada')
        if area_plantada is not None:
            try:
                area = float(area_plantada)
                if area <= 0:
                    return False, 'Área plantada deve ser maior que zero'
                if area > 10000:  # 10000 hectares como limite máximo
                    return False, 'Área plantada muito grande (máximo: 10000 hectares)'
            except (ValueError, TypeError):
                return False, 'Área plantada deve ser um número válido'
        
        # Validar datas
        data_plantio = data.get('data_plantio')
        data_colheita_prevista = data.get('data_colheita_prevista')
        
        if data_plantio:
            if not CultureValidator._is_valid_date_string(data_plantio):
                return False, 'Data de plantio inválida (formato: YYYY-MM-DD)'
        
        if data_colheita_prevista:
            if not CultureValidator._is_valid_date_string(data_colheita_prevista):
                return False, 'Data de colheita inválida (formato: YYYY-MM-DD)'
            
            # Se ambas as datas estão presentes, colheita deve ser após plantio
            if data_plantio:
                try:
                    plantio = datetime.strptime(data_plantio, '%Y-%m-%d').date()
                    colheita = datetime.strptime(data_colheita_prevista, '%Y-%m-%d').date()
                    if colheita <= plantio:
                        return False, 'Data de colheita deve ser posterior à data de plantio'
                except ValueError:
                    return False, 'Formato de data inválido'
        
        return True, None
    
    @staticmethod
    def validate_update_culture_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida dados para atualização de cultura
        
        Args:
            data: Dicionário com dados da cultura
            
        Returns:
            Tuple (is_valid, error_message)
        """
        # Validar nome se fornecido
        if 'nome' in data:
            nome = data.get('nome', '').strip()
            if len(nome) < 2:
                return False, 'Nome da cultura deve ter pelo menos 2 caracteres'
            if len(nome) > 100:
                return False, 'Nome da cultura não pode exceder 100 caracteres'
        
        # Validar tipo se fornecido
        if 'tipo' in data:
            tipo = data.get('tipo')
            if tipo not in CultureValidator.VALID_CULTURE_TYPES:
                return False, f'Tipo de cultura inválido. Tipos válidos: {", ".join(CultureValidator.VALID_CULTURE_TYPES)}'
        
        # Validar status se fornecido
        if 'status' in data:
            status = data.get('status')
            if status and status not in CultureValidator.VALID_STATUS:
                return False, f'Status inválido. Status válidos: {", ".join(CultureValidator.VALID_STATUS)}'
        
        # Validar área plantada se fornecida
        if 'area_plantada' in data:
            area_plantada = data.get('area_plantada')
            if area_plantada is not None:
                try:
                    area = float(area_plantada)
                    if area <= 0:
                        return False, 'Área plantada deve ser maior que zero'
                    if area > 10000:
                        return False, 'Área plantada muito grande (máximo: 10000 hectares)'
                except (ValueError, TypeError):
                    return False, 'Área plantada deve ser um número válido'
        
        # Validar datas se fornecidas
        if 'data_plantio' in data and data['data_plantio']:
            if not CultureValidator._is_valid_date_string(data['data_plantio']):
                return False, 'Data de plantio inválida (formato: YYYY-MM-DD)'
        
        if 'data_colheita_prevista' in data and data['data_colheita_prevista']:
            if not CultureValidator._is_valid_date_string(data['data_colheita_prevista']):
                return False, 'Data de colheita inválida (formato: YYYY-MM-DD)'
        
        return True, None
    
    @staticmethod
    def validate_wizard_step_data(step: str, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida dados de uma etapa do wizard
        
        Args:
            step: Etapa do wizard
            data: Dados a validar
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if step == '1':
            # Etapa 1: Dados básicos da cultura
            nome = data.get('nome', '').strip()
            tipo = data.get('tipo')
            
            if not nome:
                return False, 'Nome da cultura é obrigatório'
            if len(nome) < 2:
                return False, 'Nome deve ter pelo menos 2 caracteres'
            
            if not tipo:
                return False, 'Tipo da cultura é obrigatório'
            if tipo not in CultureValidator.VALID_CULTURE_TYPES:
                return False, 'Tipo de cultura inválido'
                
        elif step == '2':
            # Etapa 2: Dados da área
            area_plantada = data.get('area_plantada')
            if area_plantada:
                try:
                    area = float(area_plantada)
                    if area <= 0:
                        return False, 'Área plantada deve ser maior que zero'
                except (ValueError, TypeError):
                    return False, 'Área plantada deve ser um número válido'
                    
        elif step == '3':
            # Etapa 3: Dados do calendário
            data_plantio = data.get('data_plantio')
            data_colheita = data.get('data_colheita_prevista')
            
            if data_plantio and not CultureValidator._is_valid_date_string(data_plantio):
                return False, 'Data de plantio inválida'
                
            if data_colheita and not CultureValidator._is_valid_date_string(data_colheita):
                return False, 'Data de colheita inválida'
                
            # Validar temperaturas
            temp_min = data.get('temp_min')
            temp_max = data.get('temp_max')
            
            if temp_min is not None:
                try:
                    temp_min = float(temp_min)
                    if temp_min < -50 or temp_min > 60:
                        return False, 'Temperatura mínima deve estar entre -50°C e 60°C'
                except (ValueError, TypeError):
                    return False, 'Temperatura mínima deve ser um número válido'
            
            if temp_max is not None:
                try:
                    temp_max = float(temp_max)
                    if temp_max < -50 or temp_max > 60:
                        return False, 'Temperatura máxima deve estar entre -50°C e 60°C'
                except (ValueError, TypeError):
                    return False, 'Temperatura máxima deve ser um número válido'
            
            if temp_min is not None and temp_max is not None and temp_min >= temp_max:
                return False, 'Temperatura mínima deve ser menor que a máxima'
                
        elif step == '4':
            # Etapa 4: Recursos
            quantidade_agua = data.get('quantidade_agua')
            if quantidade_agua is not None:
                try:
                    qtd = float(quantidade_agua)
                    if qtd < 0:
                        return False, 'Quantidade de água não pode ser negativa'
                except (ValueError, TypeError):
                    return False, 'Quantidade de água deve ser um número válido'
        
        return True, None
    
    @staticmethod
    def _is_valid_date_string(date_string: str) -> bool:
        """
        Verifica se a string representa uma data válida no formato YYYY-MM-DD
        
        Args:
            date_string: String da data
            
        Returns:
            True se válida, False caso contrário
        """
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def get_culture_types() -> list:
        """
        Retorna lista de tipos de cultura válidos
        
        Returns:
            Lista com tipos de cultura
        """
        return [
            {'value': 'arvore_frutifera', 'label': 'Árvore Frutífera'},
            {'value': 'hortalica', 'label': 'Hortaliça'},
            {'value': 'erva_aromatica', 'label': 'Erva Aromática'},
            {'value': 'grao', 'label': 'Grão'},
            {'value': 'cereal', 'label': 'Cereal'},
            {'value': 'leguminosa', 'label': 'Leguminosa'}
        ]
