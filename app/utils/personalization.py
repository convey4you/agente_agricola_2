"""
Sistema de Personalização Avançada para AgroTech Portugal
Implementa personalização baseada no perfil do usuário e contexto agrícola
"""

from flask import current_app, request, g
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import redis
from app.utils.database import get_db_connection

class PersonalizationEngine:
    """Engine principal de personalização"""
    
    def __init__(self):
        self.redis_client = None
        self.cache_ttl = 3600  # 1 hora
        self.init_redis()
    
    def init_redis(self):
        """Inicializar conexão Redis"""
        try:
            redis_url = current_app.config.get('REDIS_URL')
            # Verificar se temos uma URL válida (não placeholder)
            if redis_url and redis_url != '${{Redis.REDIS_URL}}':
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                current_app.logger.info(f"✅ Redis conectado para personalização: {redis_url[:20]}...")
            else:
                current_app.logger.info("⚠️ REDIS_URL não configurada para personalização")
                self.redis_client = None
        except Exception as e:
            current_app.logger.warning(f"❌ Redis não disponível para personalização: {e}")
            self.redis_client = None
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Obter preferências do usuário"""
        if not user_id:
            return self.get_default_preferences()
        
        # Tentar cache primeiro
        cache_key = f"user_prefs:{user_id}"
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
        
        # Buscar no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT preferences, ui_settings, accessibility_settings
            FROM user_preferences 
            WHERE user_id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if result:
            preferences = {
                'user_preferences': result[0] or {},
                'ui_settings': result[1] or {},
                'accessibility_settings': result[2] or {}
            }
        else:
            preferences = self.get_default_preferences()
            # Criar registro padrão
            self.save_user_preferences(user_id, preferences)
        
        cursor.close()
        conn.close()
        
        # Cachear resultado
        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key, 
                    self.cache_ttl, 
                    json.dumps(preferences)
                )
            except Exception:
                pass
        
        return preferences
    
    def get_default_preferences(self) -> Dict[str, Any]:
        """Preferências padrão"""
        return {
            'user_preferences': {
                'language': 'pt',
                'timezone': 'Europe/Lisbon',
                'currency': 'EUR',
                'units': 'metric',
                'dashboard_layout': 'default',
                'notification_frequency': 'daily',
                'data_retention_days': 365
            },
            'ui_settings': {
                'theme': 'light',
                'compact_mode': False,
                'animations_enabled': True,
                'sidebar_collapsed': False,
                'grid_density': 'comfortable',
                'font_size': 'medium',
                'high_contrast': False
            },
            'accessibility_settings': {
                'screen_reader_support': False,
                'keyboard_navigation': False,
                'reduced_motion': False,
                'high_contrast_mode': False,
                'large_text': False,
                'focus_indicators': True,
                'alt_text_enabled': True,
                'audio_cues': False
            }
        }
    
    def save_user_preferences(self, user_id: int, preferences: Dict[str, Any]):
        """Salvar preferências do usuário"""
        if not user_id:
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_preferences 
            (user_id, preferences, ui_settings, accessibility_settings, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                preferences = EXCLUDED.preferences,
                ui_settings = EXCLUDED.ui_settings,
                accessibility_settings = EXCLUDED.accessibility_settings,
                updated_at = EXCLUDED.updated_at
        """, (
            user_id,
            json.dumps(preferences.get('user_preferences', {})),
            json.dumps(preferences.get('ui_settings', {})),
            json.dumps(preferences.get('accessibility_settings', {})),
            datetime.utcnow()
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Invalidar cache
        if self.redis_client:
            try:
                self.redis_client.delete(f"user_prefs:{user_id}")
            except Exception:
                pass
    
    def get_contextual_recommendations(self, user_id: int) -> Dict[str, Any]:
        """Obter recomendações contextuais baseadas no perfil"""
        if not user_id:
            return {}
        
        cache_key = f"user_recommendations:{user_id}"
        
        # Tentar cache primeiro
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar dados do perfil do usuário
        cursor.execute("""
            SELECT u.*, up.farm_size, up.primary_crops, up.farming_experience,
                   up.technology_comfort_level, up.region
            FROM users u
            LEFT JOIN user_profiles up ON u.id = up.user_id
            WHERE u.id = %s
        """, (user_id,))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            cursor.close()
            conn.close()
            return {}
        
        # Gerar recomendações baseadas no perfil
        recommendations = self._generate_recommendations(user_data)
        
        cursor.close()
        conn.close()
        
        # Cachear por 4 horas
        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key, 
                    14400,  # 4 horas
                    json.dumps(recommendations)
                )
            except Exception:
                pass
        
        return recommendations
    
    def _generate_recommendations(self, user_data) -> Dict[str, Any]:
        """Gerar recomendações baseadas nos dados do usuário"""
        recommendations = {
            'dashboard_widgets': [],
            'suggested_features': [],
            'learning_resources': [],
            'automation_suggestions': [],
            'community_connections': []
        }
        
        if not user_data:
            return recommendations
        
        # Extrair dados relevantes
        farm_size = user_data[6] if len(user_data) > 6 else None
        primary_crops = user_data[7] if len(user_data) > 7 else []
        experience = user_data[8] if len(user_data) > 8 else 'beginner'
        tech_comfort = user_data[9] if len(user_data) > 9 else 'basic'
        region = user_data[10] if len(user_data) > 10 else None
        
        # Recomendações de widgets para dashboard
        if experience == 'beginner':
            recommendations['dashboard_widgets'].extend([
                'weather-simple',
                'basic-tasks',
                'learning-center',
                'help-center'
            ])
        elif experience == 'advanced':
            recommendations['dashboard_widgets'].extend([
                'detailed-analytics',
                'advanced-weather',
                'market-prices',
                'yield-prediction'
            ])
        else:  # intermediate
            recommendations['dashboard_widgets'].extend([
                'weather-detailed',
                'task-management',
                'crop-monitoring',
                'financial-overview'
            ])
        
        # Recomendações de recursos baseadas em culturas
        if primary_crops:
            for crop in primary_crops:
                recommendations['learning_resources'].append({
                    'type': 'crop_guide',
                    'title': f'Guia Completo de {crop}',
                    'priority': 'high'
                })
        
        # Sugestões de automação baseadas no conforto tecnológico
        if tech_comfort in ['advanced', 'expert']:
            recommendations['automation_suggestions'].extend([
                'automated_irrigation',
                'iot_sensors',
                'drone_monitoring',
                'ai_crop_analysis'
            ])
        elif tech_comfort == 'intermediate':
            recommendations['automation_suggestions'].extend([
                'weather_alerts',
                'task_reminders',
                'simple_sensors'
            ])
        
        # Conexões comunitárias baseadas na região
        if region:
            recommendations['community_connections'].append({
                'type': 'regional_group',
                'title': f'Agricultores de {region}',
                'description': 'Conecte-se com agricultores da sua região'
            })
        
        return recommendations
    
    def apply_ui_preferences(self, preferences: Dict[str, Any]) -> Dict[str, str]:
        """Aplicar preferências de UI como CSS customizado"""
        ui_settings = preferences.get('ui_settings', {})
        accessibility = preferences.get('accessibility_settings', {})
        
        css_vars = {}
        
        # Tema
        if ui_settings.get('theme') == 'dark':
            css_vars.update({
                '--bg-primary': '#1a1a1a',
                '--bg-secondary': '#2d2d2d',
                '--text-primary': '#ffffff',
                '--text-secondary': '#cccccc'
            })
        
        # Tamanho da fonte
        font_size = ui_settings.get('font_size', 'medium')
        font_multiplier = {
            'small': '0.875',
            'medium': '1',
            'large': '1.125',
            'extra-large': '1.25'
        }.get(font_size, '1')
        
        css_vars['--font-size-multiplier'] = font_multiplier
        
        # Alto contraste
        if accessibility.get('high_contrast_mode'):
            css_vars.update({
                '--primary-color': '#000000',
                '--secondary-color': '#ffffff',
                '--border-color': '#000000',
                '--focus-color': '#ffff00'
            })
        
        # Texto grande
        if accessibility.get('large_text'):
            css_vars['--font-size-multiplier'] = '1.5'
        
        # Redução de movimento
        if accessibility.get('reduced_motion'):
            css_vars['--animation-duration'] = '0s'
        
        return css_vars
    
    def get_personalized_content(self, user_id: int, content_type: str) -> List[Dict[str, Any]]:
        """Obter conteúdo personalizado para o usuário"""
        if not user_id:
            return []
        
        cache_key = f"user_content:{user_id}:{content_type}"
        
        # Tentar cache primeiro
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
        
        # Buscar preferências do usuário
        preferences = self.get_user_preferences(user_id)
        recommendations = self.get_contextual_recommendations(user_id)
        
        # Gerar conteúdo personalizado baseado no tipo
        content = self._generate_personalized_content(
            content_type, 
            preferences, 
            recommendations
        )
        
        # Cachear por 2 horas
        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key, 
                    7200,  # 2 horas
                    json.dumps(content)
                )
            except Exception:
                pass
        
        return content
    
    def _generate_personalized_content(self, content_type: str, preferences: Dict, recommendations: Dict) -> List[Dict[str, Any]]:
        """Gerar conteúdo personalizado específico"""
        content = []
        
        if content_type == 'dashboard_tips':
            # Dicas personalizadas para o dashboard
            experience = preferences.get('user_preferences', {}).get('farming_experience', 'beginner')
            
            if experience == 'beginner':
                content.extend([
                    {
                        'title': 'Comece pelo Básico',
                        'description': 'Configure primeiro o seu perfil de exploração agrícola',
                        'action_url': '/profile/farm-setup',
                        'priority': 'high'
                    },
                    {
                        'title': 'Monitorize o Clima',
                        'description': 'Verifique as previsões meteorológicas diariamente',
                        'action_url': '/weather',
                        'priority': 'medium'
                    }
                ])
            elif experience == 'advanced':
                content.extend([
                    {
                        'title': 'Análise Avançada',
                        'description': 'Explore os dados históricos da sua exploração',
                        'action_url': '/analytics/historical',
                        'priority': 'high'
                    },
                    {
                        'title': 'Integração IoT',
                        'description': 'Configure sensores para monitorização automática',
                        'action_url': '/iot/setup',
                        'priority': 'medium'
                    }
                ])
        
        elif content_type == 'learning_suggestions':
            # Sugestões de aprendizagem
            suggested_features = recommendations.get('suggested_features', [])
            
            for feature in suggested_features:
                content.append({
                    'title': f'Aprenda sobre {feature}',
                    'description': f'Descubra como usar {feature} na sua exploração',
                    'type': 'tutorial',
                    'duration': '15 min'
                })
        
        return content
    
    def track_user_interaction(self, user_id: int, interaction_type: str, data: Dict[str, Any]):
        """Rastrear interações do usuário para melhorar personalização"""
        if not user_id:
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_interactions 
                (user_id, interaction_type, interaction_data, created_at)
                VALUES (%s, %s, %s, %s)
            """, (
                user_id,
                interaction_type,
                json.dumps(data),
                datetime.utcnow()
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Invalidar caches relacionados
            if self.redis_client:
                try:
                    pattern = f"user_*:{user_id}*"
                    for key in self.redis_client.scan_iter(match=pattern):
                        self.redis_client.delete(key)
                except Exception:
                    pass
                    
        except Exception as e:
            current_app.logger.error(f"Erro ao rastrear interação: {e}")

# Instância global
personalization_engine = PersonalizationEngine()

def get_user_personalization(user_id: int) -> Dict[str, Any]:
    """Função helper para obter personalização completa do usuário"""
    if not user_id:
        return personalization_engine.get_default_preferences()
    
    preferences = personalization_engine.get_user_preferences(user_id)
    recommendations = personalization_engine.get_contextual_recommendations(user_id)
    
    return {
        'preferences': preferences,
        'recommendations': recommendations,
        'css_vars': personalization_engine.apply_ui_preferences(preferences)
    }

def update_user_preferences(user_id: int, preferences: Dict[str, Any]) -> bool:
    """Função helper para atualizar preferências do usuário"""
    try:
        personalization_engine.save_user_preferences(user_id, preferences)
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar preferências: {e}")
        return False
