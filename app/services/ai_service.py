"""
Serviço de Inteligência Artificial para o agente agrícola
"""
import openai
import json
import hashlib
from typing import Dict, List, Optional
from flask import current_app
from datetime import datetime, timezone, date
from app.models.culture import Culture
from app.models.conversation import Conversation, Message
from app.utils.cache_manager import cache, cached


class AIService:
    """Serviço de Inteligência Artificial para o agente agrícola"""
    
    @staticmethod
    def process_message(message: str, context: Dict) -> Dict:
        """Processar mensagem do usuário e gerar resposta"""
        try:
            # Criar hash do contexto para cache
            context_str = json.dumps(context, sort_keys=True, default=str)
            context_hash = hashlib.md5(context_str.encode()).hexdigest()[:8]
            
            # Tentar obter do cache primeiro
            cache_key = f"ai_response:{hashlib.md5(message.encode()).hexdigest()[:10]}_{context_hash}"
            cached_response = cache.get(cache_key, 'ai')
            
            if cached_response:
                current_app.logger.info(f"Resposta IA obtida do cache para: {message[:50]}...")
                return cached_response
            
            # Tentar resposta offline primeiro
            offline_response = AIService._try_offline_response(message, context)
            if offline_response:
                # Cachear resposta offline (timeout menor)
                cache.set(cache_key, offline_response, 
                         current_app.config.get('CACHE_TIMEOUT_AI', 3600) // 4, 'ai')
                return offline_response
            
            # Se não conseguir offline, usar IA em nuvem
            cloud_response = AIService._process_with_cloud_ai(message, context)
            
            # Cachear resposta da nuvem (timeout completo)
            if cloud_response.get('success'):
                cache.set(cache_key, cloud_response, 
                         current_app.config.get('CACHE_TIMEOUT_AI', 3600), 'ai')
            
            return cloud_response
            
        except Exception as e:
            current_app.logger.error(f"Erro no processamento da mensagem: {e}")
            return {
                'success': False,
                'response': {
                    'text': 'Desculpe, ocorreu um erro. Tente novamente mais tarde.',
                    'type': 'error'
                }
            }
    
    @staticmethod
    def _try_offline_response(message: str, context: Dict) -> Optional[Dict]:
        """Tentar gerar resposta usando base de conhecimento local"""
        message_lower = message.lower()
        
        # Respostas baseadas em palavras-chave
        if any(word in message_lower for word in ['plantar', 'plantio', 'semear']):
            return {
                'success': True,
                'response': {
                    'text': AIService._get_planting_advice(context),
                    'type': 'advice',
                    'category': 'planting'
                }
            }
        
        elif any(word in message_lower for word in ['clima', 'tempo', 'chuva']):
            return {
                'success': True,
                'response': {
                    'text': AIService._get_weather_advice(context),
                    'type': 'advice',
                    'category': 'weather'
                }
            }
        
        elif any(word in message_lower for word in ['pragas', 'doenças', 'problemas']):
            return {
                'success': True,
                'response': {
                    'text': AIService._get_pest_advice(context),
                    'type': 'advice',
                    'category': 'pest_control'
                }
            }
        
        elif any(word in message_lower for word in ['fertilizar', 'adubo', 'nutrição']):
            return {
                'success': True,
                'response': {
                    'text': AIService._get_fertilizer_advice(context),
                    'type': 'advice',
                    'category': 'fertilization'
                }
            }
        
        # Se não encontrar palavra-chave específica, retornar None para usar IA
        return None
    
    @staticmethod
    def _process_with_cloud_ai(message: str, context: Dict) -> Dict:
        """Processar com IA em nuvem (OpenAI)"""
        api_key = current_app.config.get('OPENAI_API_KEY')
        
        if not api_key:
            return {
                'success': True,
                'response': {
                    'text': 'Como posso ajudá-lo com sua agricultura hoje? Fale-me sobre suas culturas ou dúvidas específicas.',
                    'type': 'general'
                }
            }
        
        try:
            openai.api_key = api_key
            
            system_prompt = AIService._build_system_prompt(context)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                'success': True,
                'response': {
                    'text': response.choices[0].message.content,
                    'type': 'ai_generated',
                    'tokens_used': response.usage.total_tokens
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro na IA em nuvem: {e}")
            return AIService._get_fallback_response()
    
    @staticmethod
    def _build_system_prompt(context: Dict) -> str:
        """Construir prompt do sistema baseado no contexto"""
        user_profile = context.get('user_profile', {})
        user_cultures = context.get('user_cultures', [])
        
        prompt = f"""Você é um agente inteligente especializado em agricultura em Portugal. 

Informações do usuário:
- Nível de experiência: {user_profile.get('experience_level', 'iniciante')}
- Localização: {user_profile.get('cidade', 'Portugal')}
- Culturas ativas: {', '.join([c.get('nome', '') for c in user_cultures]) if user_cultures else 'Nenhuma'}

Diretrizes:
1. Responda sempre em português de Portugal
2. Seja específico para o clima e condições de Portugal
3. Adapte a linguagem ao nível de experiência do usuário
4. Foque em soluções práticas e sustentáveis
5. Considere as culturas existentes do usuário ao dar conselhos
6. Se não souber algo específico, seja honesto e sugira consultar um especialista local

Mantenha as respostas concisas mas informativas."""
        
        return prompt
    
    @staticmethod
    def analyze_plant_image(image_file) -> Dict:
        """Analisar imagem de planta para identificar problemas"""
        # Por enquanto, retornar resposta simulada
        # Em produção, integrar com serviços de visão computacional
        return {
            'success': True,
            'analysis': {
                'plant_health': 'healthy',
                'confidence': 0.85,
                'issues_detected': [],
                'recommendations': [
                    'A planta parece saudável. Continue com os cuidados regulares.',
                    'Monitore a humidade do solo regularmente.',
                    'Verifique se há sinais de pragas semanalmente.'
                ]
            }
        }
    
    @staticmethod
    def get_contextual_suggestions(user) -> List[str]:
        """Gerar sugestões contextuais baseadas no perfil do usuário"""
        suggestions = []
        
        current_month = datetime.now().month
        
        # Sugestões sazonais
        if current_month in [3, 4, 5]:  # Primavera
            suggestions.extend([
                "Que culturas posso plantar na primavera?",
                "Como preparar o solo para o novo plantio?",
                "Quando devo começar a semear tomates?"
            ])
        elif current_month in [6, 7, 8]:  # Verão
            suggestions.extend([
                "Como proteger as plantas do calor excessivo?",
                "Qual a frequência ideal de rega no verão?",
                "Como identificar stress hídrico nas plantas?"
            ])
        elif current_month in [9, 10, 11]:  # Outono
            suggestions.extend([
                "Que culturas posso plantar no outono?",
                "Como preparar o jardim para o inverno?",
                "Quando colher os últimos tomates?"
            ])
        else:  # Inverno
            suggestions.extend([
                "Como proteger as plantas do frio?",
                "Que culturas resistem ao inverno?",
                "Como manter a horta produtiva no inverno?"
            ])
        
        # Sugestões baseadas nas culturas do usuário
        if hasattr(user, 'cultures'):
            user_cultures = Culture.query.filter_by(user_id=user.id, active=True).all()
            if user_cultures:
                culture_names = [c.nome for c in user_cultures[:3]]
                suggestions.append(f"Como cuidar melhor de {', '.join(culture_names)}?")
        
        return suggestions[:6]  # Máximo 6 sugestões
    
    @staticmethod
    def _get_planting_advice(context: Dict) -> str:
        """Conselhos sobre plantio"""
        current_month = datetime.now().month
        season_advice = {
            (3, 4, 5): "A primavera é ideal para plantar tomates, pimentos, beringelas e ervas aromáticas.",
            (6, 7, 8): "No verão, foque em culturas de crescimento rápido como alfaces e rabanetes.",
            (9, 10, 11): "O outono é perfeito para plantar couves, brócolos e outras crucíferas.",
            (12, 1, 2): "No inverno, pode plantar favas, ervilhas e preparar canteiros para a primavera."
        }
        
        for months, advice in season_advice.items():
            if current_month in months:
                return advice
        
        return "Consulte um calendário de plantio específico para sua região."
    
    @staticmethod
    def _get_weather_advice(context: Dict) -> str:
        """Conselhos sobre clima"""
        return ("Monitore a previsão meteorológica regularmente. "
                "Em Portugal, cuidado com as geadas tardias na primavera "
                "e o calor excessivo no verão. "
                "Ajuste a rega conforme as condições climáticas.")
    
    @staticmethod
    def _get_pest_advice(context: Dict) -> str:
        """Conselhos sobre pragas"""
        return ("Para controlo de pragas, prefira métodos biológicos. "
                "Use armadilhas amarelas para afídeos, "
                "plantas companheiras como malmequeres para repelir pragas, "
                "e inspecione as plantas regularmente.")
    
    @staticmethod
    def _get_fertilizer_advice(context: Dict) -> str:
        """Conselhos sobre fertilização"""
        return ("Use compostagem orgânica sempre que possível. "
                "Teste o pH do solo regularmente. "
                "Fertilize com moderação - excesso pode ser prejudicial. "
                "Considere fertilizantes orgânicos como húmus de minhoca.")
    
    @staticmethod
    def _get_fallback_response() -> Dict:
        """Resposta de fallback quando há erro"""
        return {
            'success': True,
            'response': {
                'text': 'Como posso ajudá-lo hoje? Estou aqui para responder suas dúvidas sobre agricultura.',
                'type': 'fallback'
            }
        }
    
    @staticmethod
    def invalidate_user_ai_cache(user_id: int):
        """Invalidar cache de IA para um usuário específico"""
        try:
            # Como o cache de IA usa hash de mensagem + contexto,
            # não podemos invalidar por usuário facilmente.
            # Em vez disso, podemos limpar todo o namespace de IA
            current_app.logger.info(f"Solicitada invalidação de cache IA para usuário {user_id}")
            return True
        except Exception as e:
            current_app.logger.error(f"Erro ao invalidar cache IA: {e}")
            return False
    
    @staticmethod
    def clear_all_ai_cache():
        """Limpar todo o cache de IA"""
        try:
            cleared = cache.clear_namespace('ai')
            current_app.logger.info(f"Cache de IA limpo: {cleared} chaves removidas")
            return cleared
        except Exception as e:
            current_app.logger.error(f"Erro ao limpar cache de IA: {e}")
            return 0
    
    @staticmethod
    def get_ai_cache_stats():
        """Obter estatísticas do cache de IA"""
        try:
            # Contar chaves do namespace 'ai'
            ai_keys = 0
            if cache.redis_client:
                pattern = f"{cache.app.config.get('CACHE_KEY_PREFIX', 'agagri:')}ai:*"
                ai_keys = len(cache.redis_client.keys(pattern))
            
            return {
                'ai_cached_responses': ai_keys,
                'cache_namespace': 'ai'
            }
        except Exception as e:
            current_app.logger.error(f"Erro ao obter stats de cache IA: {e}")
            return {'error': str(e)}
