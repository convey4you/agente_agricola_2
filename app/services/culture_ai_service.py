# app/services/culture_ai_service.py
"""
Serviço de IA para buscar informações de culturas desconhecidas
Expande automaticamente a base de conhecimento do sistema
"""
import logging
import json
from flask import current_app
from app.services.ai_service_v2 import AIServiceV2
from app.utils.api_integration import ai_api, APIIntegrationException

logger = logging.getLogger(__name__)


class CultureAIService:
    """Serviço para buscar informações de culturas usando IA"""
    
    @staticmethod
    def buscar_informacoes_cultura(nome_cultura):
        """
        Busca informações detalhadas sobre uma cultura usando IA
        
        Args:
            nome_cultura (str): Nome da cultura a pesquisar
            
        Returns:
            dict: Informações da cultura ou None se não encontrada
        """
        try:
            logger.info(f"Buscando informações via IA para cultura: {nome_cultura}")
            
            api_key = current_app.config.get('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OPENAI_API_KEY não configurada, não é possível buscar via IA")
                return None
            
            # Prompt otimizado para obter informações agrícolas estruturadas
            prompt = f"""
Você é um especialista em agricultura. Preciso de informações detalhadas sobre a cultura "{nome_cultura}".

Por favor, retorne APENAS um JSON válido com as seguintes informações (se aplicável):

{{
    "nome": "nome oficial da cultura",
    "nome_cientifico": "nome científico",
    "tipo": "hortalica|arvore_frutifera|erva_aromatica|cereal|leguminosa|tuberculo",
    "variedade": "variedade comum (se aplicável)",
    "ciclo_dias": "número de dias do plantio à colheita",
    "epoca_plantio": "melhor época para plantar",
    "espacamento": "espaçamento recomendado entre plantas",
    "profundidade_plantio": "profundidade de plantio das sementes",
    "temperatura_ideal": "faixa de temperatura ideal",
    "ph_solo": "pH ideal do solo",
    "irrigacao": "necessidades de irrigação",
    "luz_solar": "necessidades de luz solar",
    "fertilizacao": "recomendações de fertilização",
    "pragas_comuns": ["lista", "de", "pragas", "comuns"],
    "colheita_indicadores": "como saber quando colher",
    "dificuldade": "facil|medio|dificil",
    "regiao_adaptacao": "regiões onde se adapta bem"
}}

Cultura: {nome_cultura}

Importante: 
- Retorne APENAS o JSON, sem texto adicional
- Se não conhecer a cultura, retorne {{"erro": "cultura_desconhecida"}}
- Adapte as informações para o clima de Portugal quando possível
"""

            try:
                # Usar o serviço de IA existente
                response = ai_api.get_ai_recommendation(
                    prompt=prompt,
                    context={
                        "cultura": nome_cultura,
                        "formato": "JSON",
                        "idioma": "português"
                    },
                    api_key=api_key
                )
                
                if not response or not response.get('success'):
                    logger.error(f"Resposta inválida da API de IA: {response}")
                    return None
                
                # Extrair conteúdo da resposta OpenAI
                data = response.get('data', {})
                choices = data.get('choices', [])
                
                if not choices:
                    logger.error("Nenhuma escolha retornada pela API")
                    return None
                
                content = choices[0].get('message', {}).get('content', '').strip()
                
                # Tentar parsear o JSON
                try:
                    cultura_info = json.loads(content)
                    
                    if 'erro' in cultura_info:
                        logger.info(f"IA reportou que não conhece a cultura: {nome_cultura}")
                        return None
                    
                    # Validar se tem informações mínimas necessárias
                    if not cultura_info.get('nome') or not cultura_info.get('tipo'):
                        logger.warning("IA retornou dados incompletos")
                        return None
                    
                    logger.info(f"Encontrou informações via IA para: {cultura_info.get('nome')}")
                    return cultura_info
                    
                except json.JSONDecodeError as je:
                    logger.error(f"Erro ao parsear resposta JSON da IA: {je}")
                    logger.debug(f"Conteúdo recebido: {content}")
                    return None
                    
            except APIIntegrationException as e:
                logger.error(f"Erro na integração com API de IA: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar cultura via IA: {e}")
            return None
    
    @staticmethod
    def salvar_cultura_na_base(cultura_info):
        """
        Salva informações da cultura na base de conhecimento
        
        Args:
            cultura_info (dict): Informações da cultura obtidas via IA
            
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            from app.services.base_conhecimento_culturas import adicionar_cultura_dinamica
            
            # Converter formato da IA para formato da base de conhecimento
            cultura_formatada = {
                'nome': cultura_info.get('nome'),
                'nome_cientifico': cultura_info.get('nome_cientifico', ''),
                'tipo': cultura_info.get('tipo', 'hortalica'),
                'ciclo_dias': cultura_info.get('ciclo_dias'),
                'epoca_plantio': cultura_info.get('epoca_plantio'),
                'espacamento': cultura_info.get('espacamento'),
                'profundidade_plantio': cultura_info.get('profundidade_plantio'),
                'temperatura_ideal': cultura_info.get('temperatura_ideal'),
                'ph_solo': cultura_info.get('ph_solo'),
                'irrigacao': cultura_info.get('irrigacao'),
                'luz_solar': cultura_info.get('luz_solar'),
                'fertilizacao': cultura_info.get('fertilizacao'),
                'pragas_comuns': cultura_info.get('pragas_comuns', []),
                'colheita_indicadores': cultura_info.get('colheita_indicadores'),
                'dificuldade': cultura_info.get('dificuldade', 'medio'),
                'regiao_adaptacao': cultura_info.get('regiao_adaptacao'),
                'fonte': 'IA',
                'variedade': cultura_info.get('variedade')
            }
            
            # Tentar salvar na base de conhecimento
            resultado = adicionar_cultura_dinamica(cultura_formatada)
            
            if resultado:
                logger.info(f"Cultura {cultura_info.get('nome')} adicionada à base de conhecimento via IA")
                return True
            else:
                logger.warning(f"Não foi possível adicionar cultura {cultura_info.get('nome')} à base")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao salvar cultura na base: {e}")
            return False
    
    @staticmethod
    def buscar_e_salvar_cultura(nome_cultura):
        """
        Busca informações via IA e salva na base de conhecimento
        
        Args:
            nome_cultura (str): Nome da cultura
            
        Returns:
            dict: Informações da cultura encontrada ou None
        """
        try:
            # Buscar via IA
            cultura_info = CultureAIService.buscar_informacoes_cultura(nome_cultura)
            
            if not cultura_info:
                return None
            
            # Tentar salvar na base
            salvou = CultureAIService.salvar_cultura_na_base(cultura_info)
            
            if salvou:
                logger.info(f"Cultura {nome_cultura} expandida com sucesso via IA")
                
                # *** IMPORTANTE: Retornar dados da base, não dados brutos da IA ***
                from app.services.base_conhecimento_culturas import buscar_cultura
                cultura_formatada = buscar_cultura(nome_cultura)
                
                if cultura_formatada:
                    # Garantir que fonte seja marcada corretamente como IA (primeira descoberta)
                    cultura_formatada['fonte'] = 'IA'
                    return cultura_formatada
            
            # Se não conseguiu salvar, retornar dados originais da IA
            return cultura_info
            
        except Exception as e:
            logger.error(f"Erro no processo buscar_e_salvar_cultura: {e}")
            return None
