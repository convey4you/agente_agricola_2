"""
Agent Service - Lógica de negócio para o agente inteligente
"""
from flask import current_app
from flask_login import current_user
from app import db
from app.services.ai_service import AIService
from app.models.conversation import Conversation, Message
from app.models.culture import Culture
from datetime import datetime, timezone


class AgentService:
    """Serviço para gerenciar operações do agente inteligente"""
    
    @staticmethod
    def get_agent_index_data():
        """Obter dados para a página inicial do agente"""
        try:
            # Buscar conversas recentes
            recent_conversations = Conversation.query.filter_by(
                user_id=current_user.id,
                active=True
            ).order_by(Conversation.updated_at.desc()).limit(10).all()
            
            # Sugestões contextuais
            suggestions = AIService.get_contextual_suggestions(current_user)
            
            return {
                'success': True,
                'data': {
                    'conversations': recent_conversations,
                    'suggestions': suggestions
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter dados do agente: {e}")
            return {
                'success': False,
                'error': 'Erro ao carregar dados do agente'
            }
    
    @staticmethod
    def process_chat_message(message_text, conversation_id=None):
        """Processar mensagem do chat com o agente"""
        try:
            # Buscar ou criar conversa
            if conversation_id:
                conversation = Conversation.query.filter_by(
                    id=conversation_id,
                    user_id=current_user.id
                ).first()
                
                if not conversation:
                    return {
                        'success': False,
                        'error': 'Conversa não encontrada'
                    }
            else:
                # Criar nova conversa
                conversation = Conversation(
                    user_id=current_user.id,
                    title=message_text[:50] + ('...' if len(message_text) > 50 else ''),
                    active=True
                )
                db.session.add(conversation)
                db.session.flush()  # Para obter o ID
            
            # Salvar mensagem do usuário
            user_message = Message(
                conversation_id=conversation.id,
                content=message_text,
                role='user'
            )
            db.session.add(user_message)
            
            # Construir contexto para o agente
            context = AgentService._build_conversation_context(conversation, current_user)
            
            # Processar com IA
            start_time = datetime.now()
            ai_response = AIService.process_message(message_text, context)
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            if ai_response['success']:
                # Salvar resposta do agente
                agent_message = Message(
                    conversation_id=conversation.id,
                    content=ai_response['response']['text'],
                    role='assistant',
                    tokens_used=ai_response['response'].get('tokens_used'),
                    response_time_ms=response_time
                )
                db.session.add(agent_message)
                
                # Atualizar timestamp da conversa
                conversation.updated_at = datetime.now(timezone.utc)
                
                db.session.commit()
                
                return {
                    'success': True,
                    'data': {
                        'response': ai_response['response'],
                        'conversation_id': conversation.id,
                        'message_id': agent_message.id
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Erro ao processar mensagem com IA'
                }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao processar chat: {e}")
            return {
                'success': False,
                'error': 'Erro interno ao processar mensagem'
            }
    
    @staticmethod
    def analyze_plant_image(image_file):
        """Analisar imagem de planta enviada"""
        try:
            # Processar imagem com IA
            analysis = AIService.analyze_plant_image(image_file)
            
            return {
                'success': True,
                'data': {
                    'analysis': analysis
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao analisar imagem: {e}")
            return {
                'success': False,
                'error': 'Erro ao analisar imagem'
            }
    
    @staticmethod
    def get_user_conversations():
        """Obter todas as conversas do usuário"""
        try:
            conversations = Conversation.query.filter_by(
                user_id=current_user.id,
                active=True
            ).order_by(Conversation.updated_at.desc()).all()
            
            conversations_data = []
            for conv in conversations:
                conversations_data.append({
                    'id': conv.id,
                    'title': conv.title,
                    'created_at': conv.created_at.isoformat(),
                    'updated_at': conv.updated_at.isoformat(),
                    'message_count': len(conv.messages)
                })
            
            return {
                'success': True,
                'data': {
                    'conversations': conversations_data
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao listar conversas: {e}")
            return {
                'success': False,
                'error': 'Erro ao obter conversas'
            }
    
    @staticmethod
    def get_conversation_details(conversation_id):
        """Obter detalhes de uma conversa específica"""
        try:
            conversation = Conversation.query.filter_by(
                id=conversation_id,
                user_id=current_user.id
            ).first()
            
            if not conversation:
                return {
                    'success': False,
                    'error': 'Conversa não encontrada'
                }
            
            messages = Message.query.filter_by(
                conversation_id=conversation_id
            ).order_by(Message.created_at).all()
            
            return {
                'success': True,
                'data': {
                    'conversation': {
                        'id': conversation.id,
                        'title': conversation.title,
                        'created_at': conversation.created_at.isoformat(),
                        'updated_at': conversation.updated_at.isoformat()
                    },
                    'messages': [msg.to_dict() for msg in messages]
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter conversa: {e}")
            return {
                'success': False,
                'error': 'Erro ao obter conversa'
            }
    
    @staticmethod
    def delete_conversation(conversation_id):
        """Deletar (desativar) uma conversa"""
        try:
            conversation = Conversation.query.filter_by(
                id=conversation_id,
                user_id=current_user.id
            ).first()
            
            if not conversation:
                return {
                    'success': False,
                    'error': 'Conversa não encontrada'
                }
            
            conversation.active = False
            db.session.commit()
            
            return {
                'success': True,
                'data': {
                    'message': 'Conversa deletada com sucesso'
                }
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao deletar conversa: {e}")
            return {
                'success': False,
                'error': 'Erro ao deletar conversa'
            }
    
    @staticmethod
    def get_culture_suggestions(preferences=None, farm_conditions=None):
        """Obter sugestões de culturas baseadas em localização e época"""
        try:
            ai_service = AIService()
            suggestions = ai_service.get_culture_suggestions(
                user_location={
                    'latitude': current_user.latitude,
                    'longitude': current_user.longitude,  
                    'city': current_user.cidade,
                    'state': current_user.estado
                },
                preferences=preferences or {},
                farm_conditions=farm_conditions or {}
            )
            
            return {
                'success': True,
                'data': {
                    'suggestions': suggestions
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao gerar sugestões de cultura: {e}")
            return {
                'success': False,
                'error': 'Erro ao gerar sugestões'
            }
    
    @staticmethod
    def analyze_specific_culture(culture_id):
        """Análise de cultura específica"""
        try:
            from app.models.farm import Farm
            
            culture = Culture.query.join(Farm).filter(
                Culture.id == culture_id,
                Farm.user_id == current_user.id
            ).first()
            
            if not culture:
                return {
                    'success': False,
                    'error': 'Cultura não encontrada'
                }
            
            ai_service = AIService()
            analysis = ai_service.analyze_culture(culture.to_dict())
            
            return {
                'success': True,
                'data': {
                    'analysis': analysis,
                    'culture': culture.to_dict()
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao analisar cultura: {e}")
            return {
                'success': False,
                'error': 'Erro na análise da cultura'
            }
    
    @staticmethod
    def get_activity_recommendations():
        """Obter recomendações de atividades baseadas nas culturas do usuário"""
        try:
            ai_service = AIService()
            recommendations = ai_service.get_activity_recommendations(current_user.id)
            
            return {
                'success': True,
                'data': {
                    'recommendations': recommendations
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao gerar recomendações: {e}")
            return {
                'success': False,
                'error': 'Erro ao gerar recomendações'
            }
    
    @staticmethod
    def _build_conversation_context(conversation, user):
        """Construir contexto para o agente IA"""
        try:
            # Buscar culturas ativas do usuário
            user_cultures = Culture.query.filter_by(
                user_id=user.id,
                active=True
            ).all()
            
            context = {
                'user_profile': {
                    'id': user.id,
                    'experience_level': user.experience_level or 'beginner',
                    'cidade': user.cidade,
                    'estado': user.estado,
                    'latitude': user.latitude,
                    'longitude': user.longitude
                },
                'user_cultures': [{
                    'id': c.id,
                    'nome': c.nome,
                    'variedade': c.variedade,
                    'area_plantada': c.area_plantada,
                    'data_plantio': c.data_plantio.isoformat() if c.data_plantio else None,
                    'health_status': c.health_status
                } for c in user_cultures],
                'conversation_history': [{
                    'role': msg.role,
                    'content': msg.content[:200]  # Limitar contexto
                } for msg in conversation.messages[-5:]]  # Últimas 5 mensagens
            }
            
            return context
            
        except Exception as e:
            current_app.logger.error(f"Erro ao construir contexto: {e}")
            return {
                'user_profile': {
                    'id': user.id,
                    'experience_level': 'beginner'
                },
                'user_cultures': [],
                'conversation_history': []
            }
