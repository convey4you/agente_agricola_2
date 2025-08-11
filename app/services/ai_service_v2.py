# app/services/ai_service_v2.py
"""
Serviço de IA robusto para a aplicação - Sprint 4 Prompt 2
Implementação com integração robusta de APIs
"""
from flask import current_app
from datetime import datetime
from app.utils.api_integration import ai_api, APIIntegrationException
import logging
import json

logger = logging.getLogger(__name__)


class AIServiceV2:
    """Serviço para integração robusta com APIs de IA"""
    
    @staticmethod
    def get_agricultural_recommendation(culture_data, weather_data, user_context=None):
        """Obter recomendação agrícola usando IA com integração robusta"""
        try:
            logger.info(f"Obtendo recomendação de IA para cultura: {culture_data.get('type', 'N/A')}")
            
            api_key = current_app.config.get('OPENAI_API_KEY')
            
            if not api_key:
                logger.warning("OPENAI_API_KEY não configurada, usando recomendação padrão")
                return AIServiceV2._get_default_recommendation(culture_data, weather_data)
            
            # Preparar contexto para IA
            context = {
                'culture': {
                    'type': culture_data.get('type', 'cultura'),
                    'planting_date': culture_data.get('planting_date', ''),
                    'area': culture_data.get('area', 0),
                    'growth_stage': culture_data.get('growth_stage', 'unknown'),
                    'location': culture_data.get('location', 'Portugal')
                },
                'weather': {
                    'current_temp': weather_data.get('temperature', 20),
                    'condition': weather_data.get('condition', 'normal'),
                    'humidity': weather_data.get('humidity', 60),
                    'wind_speed': weather_data.get('wind_speed', 3)
                },
                'user_context': user_context or {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Prompt otimizado para agricultura portuguesa
            prompt = f"""
            Como especialista em agricultura portuguesa, analise as seguintes informações e forneça recomendações específicas:

            CULTURA:
            - Tipo: {context['culture']['type']}
            - Data de plantio: {context['culture']['planting_date']}
            - Área: {context['culture']['area']} hectares
            - Estágio de crescimento: {context['culture']['growth_stage']}
            - Localização: {context['culture']['location']}

            CONDIÇÕES METEOROLÓGICAS ATUAIS:
            - Temperatura: {context['weather']['current_temp']}°C
            - Condição: {context['weather']['condition']}
            - Humidade: {context['weather']['humidity']}%
            - Vento: {context['weather']['wind_speed']} m/s

            Forneça recomendações práticas e específicas para:
            1. Irrigação e gestão da água
            2. Cuidados fitossanitários
            3. Nutrição e fertilização
            4. Proteção contra condições adversas
            5. Atividades recomendadas para os próximos dias

            Seja específico, prático e considere as condições climáticas de Portugal.
            """
            
            # Usar integração robusta
            result = ai_api.get_ai_recommendation(prompt, context, api_key)
            
            if result['success']:
                response_data = result['data']
                ai_response = response_data['choices'][0]['message']['content']
                
                logger.info(f"Recomendação IA obtida (duração: {result['duration']:.2f}s)")
                
                return {
                    'success': True,
                    'recommendation': ai_response,
                    'context': context,
                    'api_performance': {
                        'duration': result['duration'],
                        'cached': result.get('cached', False),
                        'tokens_used': response_data['usage']['total_tokens']
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"Erro na integração IA: {result['error']}")
                return AIServiceV2._get_default_recommendation(culture_data, weather_data)
                
        except APIIntegrationException as e:
            logger.error(f"Erro de integração IA: {e}")
            return AIServiceV2._get_default_recommendation(culture_data, weather_data)
        except Exception as e:
            logger.error(f"Erro inesperado na IA: {e}")
            return AIServiceV2._get_default_recommendation(culture_data, weather_data)
    
    @staticmethod
    def get_pest_disease_analysis(symptoms, culture_type, images=None):
        """Análise de pragas e doenças usando IA"""
        try:
            logger.info(f"Analisando sintomas para {culture_type}")
            
            api_key = current_app.config.get('OPENAI_API_KEY')
            
            if not api_key:
                logger.warning("OPENAI_API_KEY não configurada, usando análise padrão")
                return AIServiceV2._get_default_pest_analysis(symptoms, culture_type)
            
            # Preparar contexto
            context = {
                'culture_type': culture_type,
                'symptoms': symptoms,
                'timestamp': datetime.now().isoformat(),
                'location': 'Portugal'
            }
            
            # Prompt especializado para diagnóstico
            prompt = f"""
            Como fitopatologista especializado em culturas portuguesas, analise os seguintes sintomas:

            CULTURA: {culture_type}
            SINTOMAS OBSERVADOS: {symptoms}
            LOCALIZAÇÃO: Portugal

            Forneça uma análise detalhada incluindo:

            1. POSSÍVEIS CAUSAS:
            - Pragas mais prováveis
            - Doenças fungicas/bacterianas/virais
            - Deficiências nutricionais
            - Stress abiótico

            2. DIAGNÓSTICO DIFERENCIAL:
            - Sintomas distintivos
            - Sinais específicos a procurar
            - Testes recomendados

            3. TRATAMENTO RECOMENDADO:
            - Medidas imediatas
            - Produtos fitofarmacêuticos adequados
            - Métodos biológicos
            - Prevenção futura

            4. PROGNÓSTICO:
            - Gravidade da situação
            - Potencial de propagação
            - Impacto na produção

            Seja específico para as condições climáticas e pragas comuns em Portugal.
            """
            
            # Usar integração robusta
            result = ai_api.get_ai_recommendation(prompt, context, api_key)
            
            if result['success']:
                response_data = result['data']
                ai_response = response_data['choices'][0]['message']['content']
                
                logger.info(f"Análise de pragas/doenças obtida (duração: {result['duration']:.2f}s)")
                
                return {
                    'success': True,
                    'analysis': ai_response,
                    'context': context,
                    'api_performance': {
                        'duration': result['duration'],
                        'cached': result.get('cached', False),
                        'tokens_used': response_data['usage']['total_tokens']
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"Erro na análise IA: {result['error']}")
                return AIServiceV2._get_default_pest_analysis(symptoms, culture_type)
                
        except APIIntegrationException as e:
            logger.error(f"Erro de integração IA: {e}")
            return AIServiceV2._get_default_pest_analysis(symptoms, culture_type)
        except Exception as e:
            logger.error(f"Erro inesperado na análise: {e}")
            return AIServiceV2._get_default_pest_analysis(symptoms, culture_type)
    
    @staticmethod
    def get_crop_planning_advice(location, season, desired_crops):
        """Obter conselhos de planeamento de culturas"""
        try:
            logger.info(f"Obtendo conselhos de planeamento para {location}")
            
            api_key = current_app.config.get('OPENAI_API_KEY')
            
            if not api_key:
                logger.warning("OPENAI_API_KEY não configurada, usando conselhos padrão")
                return AIServiceV2._get_default_planning_advice(location, season, desired_crops)
            
            # Preparar contexto
            context = {
                'location': location,
                'season': season,
                'desired_crops': desired_crops,
                'timestamp': datetime.now().isoformat()
            }
            
            # Prompt para planeamento
            prompt = f"""
            Como consultor agrícola especializado em Portugal, forneça um plano de culturas para:

            LOCALIZAÇÃO: {location}
            ÉPOCA: {season}
            CULTURAS DESEJADAS: {', '.join(desired_crops)}

            Forneça recomendações para:

            1. CALENDÁRIO DE PLANTIO:
            - Datas ideais de sementeira/plantio
            - Sucessão de culturas
            - Rotação recomendada

            2. PREPARAÇÃO DO SOLO:
            - Análises necessárias
            - Correções e fertilização
            - Mobilização adequada

            3. GESTÃO DE RECURSOS:
            - Necessidades de irrigação
            - Mão-de-obra necessária
            - Equipamentos requeridos

            4. ASPECTOS ECONÓMICOS:
            - Custos estimados
            - Potencial de mercado
            - Rentabilidade esperada

            5. RISCOS E MITIGAÇÃO:
            - Pragas e doenças comuns
            - Condições meteorológicas adversas
            - Estratégias de gestão de risco

            Considere as condições climáticas específicas de Portugal e tendências de mercado atuais.
            """
            
            # Usar integração robusta
            result = ai_api.get_ai_recommendation(prompt, context, api_key)
            
            if result['success']:
                response_data = result['data']
                ai_response = response_data['choices'][0]['message']['content']
                
                logger.info(f"Conselhos de planeamento obtidos (duração: {result['duration']:.2f}s)")
                
                return {
                    'success': True,
                    'advice': ai_response,
                    'context': context,
                    'api_performance': {
                        'duration': result['duration'],
                        'cached': result.get('cached', False),
                        'tokens_used': response_data['usage']['total_tokens']
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"Erro nos conselhos IA: {result['error']}")
                return AIServiceV2._get_default_planning_advice(location, season, desired_crops)
                
        except APIIntegrationException as e:
            logger.error(f"Erro de integração IA: {e}")
            return AIServiceV2._get_default_planning_advice(location, season, desired_crops)
        except Exception as e:
            logger.error(f"Erro inesperado no planeamento: {e}")
            return AIServiceV2._get_default_planning_advice(location, season, desired_crops)
    
    @staticmethod
    def _get_default_recommendation(culture_data, weather_data):
        """Recomendação padrão quando IA não está disponível"""
        culture_type = culture_data.get('type', 'cultura')
        temp = weather_data.get('temperature', 20)
        
        recommendations = []
        
        # Recomendações baseadas na temperatura
        if temp > 30:
            recommendations.append("• Aumente a frequência de irrigação devido às altas temperaturas")
            recommendations.append("• Monitore sinais de stress térmico nas plantas")
            recommendations.append("• Considere aplicar sombreamento temporário")
        elif temp < 10:
            recommendations.append("• Proteja as plantas do frio excessivo")
            recommendations.append("• Reduza a irrigação devido às baixas temperaturas")
            recommendations.append("• Monitore possíveis danos por geada")
        else:
            recommendations.append("• Mantenha irrigação regular conforme necessidades da cultura")
            recommendations.append("• Monitore o desenvolvimento vegetativo")
        
        # Recomendações baseadas na cultura
        culture_advice = {
            'tomate': [
                "• Verifique a presença de pragas como mosca-branca e ácaros",
                "• Faça desbrota regular para melhor desenvolvimento",
                "• Monitore sinais de míldio e alternaria"
            ],
            'milho': [
                "• Observe sinais de larva-alfinete no solo",
                "• Verifique necessidades de adubação azotada",
                "• Monitore crescimento e desenvolvimento da planta"
            ],
            'oliveira': [
                "• Observe sinais de mosca-da-azeitona",
                "• Verifique necessidades de poda",
                "• Monitore stress hídrico"
            ]
        }
        
        recommendations.extend(culture_advice.get(culture_type.lower(), [
            "• Monitore pragas e doenças específicas da cultura",
            "• Mantenha programa de nutrição adequado",
            "• Observe desenvolvimento e crescimento"
        ]))
        
        return {
            'success': True,
            'recommendation': '\n'.join(recommendations),
            'context': {'culture': culture_data, 'weather': weather_data},
            'api_performance': {'duration': 0, 'cached': False, 'tokens_used': 0},
            'timestamp': datetime.now().isoformat(),
            'fallback': True
        }
    
    @staticmethod
    def _get_default_pest_analysis(symptoms, culture_type):
        """Análise padrão de pragas/doenças"""
        common_issues = {
            'tomate': {
                'folhas amarelas': 'Possível deficiência de azoto ou ataque de mosca-branca',
                'manchas escuras': 'Possível míldio ou alternaria',
                'frutos rachados': 'Irrigação irregular ou excesso de água'
            },
            'milho': {
                'folhas amarelas': 'Possível deficiência nutricional ou ataque de ácaros',
                'perfurações': 'Possível ataque de larva-alfinete',
                'crescimento lento': 'Possível compactação do solo ou falta de nutrientes'
            }
        }
        
        analysis = common_issues.get(culture_type.lower(), {}).get(
            symptoms.lower(), 
            'Consulte um técnico especializado para diagnóstico preciso'
        )
        
        return {
            'success': True,
            'analysis': f"Análise preliminar: {analysis}\n\nRecomenda-se observação detalhada e eventual consulta técnica especializada.",
            'context': {'culture_type': culture_type, 'symptoms': symptoms},
            'api_performance': {'duration': 0, 'cached': False, 'tokens_used': 0},
            'timestamp': datetime.now().isoformat(),
            'fallback': True
        }
    
    @staticmethod
    def _get_default_planning_advice(location, season, desired_crops):
        """Conselhos padrão de planeamento"""
        seasonal_advice = {
            'primavera': [
                "• Época ideal para sementeiras de culturas de verão",
                "• Prepare o solo com mobilização e fertilização",
                "• Instale sistemas de irrigação se necessário"
            ],
            'verão': [
                "• Mantenha irrigação adequada",
                "• Monitore pragas e doenças",
                "• Prepare terreno para culturas de outono"
            ],
            'outono': [
                "• Época para plantio de culturas de inverno",
                "• Faça colheitas de culturas de verão",
                "• Prepare proteções contra frio"
            ],
            'inverno': [
                "• Proteja culturas do frio",
                "• Planeie culturas para próxima primavera",
                "• Faça manutenção de equipamentos"
            ]
        }
        
        advice = seasonal_advice.get(season.lower(), [
            "• Consulte calendário agrícola local",
            "• Adapte às condições climáticas específicas",
            "• Considere rotação de culturas"
        ])
        
        crops_advice = [f"• {crop}: Consulte épocas específicas de plantio para sua região" for crop in desired_crops]
        
        return {
            'success': True,
            'advice': '\n'.join(advice + crops_advice),
            'context': {'location': location, 'season': season, 'desired_crops': desired_crops},
            'api_performance': {'duration': 0, 'cached': False, 'tokens_used': 0},
            'timestamp': datetime.now().isoformat(),
            'fallback': True
        }


# Mantém compatibilidade com código existente
AIService = AIServiceV2
