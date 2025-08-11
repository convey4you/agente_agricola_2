"""
Sistema de Onboarding Avançado - AgroTech Portugal
Sistema completo de introdução e engajamento de novos usuários
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from flask import current_app, session, request, url_for
import logging

logger = logging.getLogger(__name__)

class OnboardingStepType(Enum):
    """Tipos de etapas do onboarding"""
    WELCOME = "welcome"
    PROFILE_SETUP = "profile_setup"
    TUTORIAL = "tutorial"
    FEATURE_INTRODUCTION = "feature_introduction"
    INTERACTIVE_DEMO = "interactive_demo"
    GOAL_SETTING = "goal_setting"
    COMPLETION = "completion"

class OnboardingStatus(Enum):
    """Status das etapas do onboarding"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

@dataclass
class OnboardingStep:
    """Etapa do onboarding"""
    id: str
    title: str
    description: str
    type: OnboardingStepType
    content: Dict[str, Any]
    order: int
    required: bool = True
    estimated_time: int = 5  # minutos
    prerequisites: List[str] = None
    completion_criteria: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.completion_criteria is None:
            self.completion_criteria = {}

@dataclass
class UserOnboardingProgress:
    """Progresso do usuário no onboarding"""
    user_id: int
    started_at: datetime
    current_step: str
    completed_steps: List[str]
    skipped_steps: List[str]
    progress_percentage: float
    estimated_completion_time: int
    personalization_data: Dict[str, Any]
    last_activity: datetime
    
    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = []
        if self.skipped_steps is None:
            self.skipped_steps = []
        if self.personalization_data is None:
            self.personalization_data = {}

class OnboardingEngine:
    """Motor do sistema de onboarding"""
    
    def __init__(self):
        self.steps = self._initialize_steps()
        self.user_progress = {}
    
    def _initialize_steps(self) -> Dict[str, OnboardingStep]:
        """Inicializar etapas do onboarding"""
        steps = {
            "welcome": OnboardingStep(
                id="welcome",
                title="Bem-vindo ao AgroTech Portugal",
                description="Descubra como nossa plataforma pode revolucionar sua atividade agrícola",
                type=OnboardingStepType.WELCOME,
                order=1,
                content={
                    "video_url": "/static/videos/welcome.mp4",
                    "highlights": [
                        "Gestão inteligente de culturas",
                        "Monitoramento climático em tempo real",
                        "Marketplace especializado",
                        "Assistente IA personalizado"
                    ],
                    "cta_text": "Vamos começar!"
                },
                estimated_time=3
            ),
            
            "profile_setup": OnboardingStep(
                id="profile_setup",
                title="Configure seu Perfil",
                description="Personalize sua experiência baseada no seu tipo de atividade agrícola",
                type=OnboardingStepType.PROFILE_SETUP,
                order=2,
                content={
                    "form_fields": [
                        {
                            "name": "farm_type",
                            "label": "Tipo de Exploração",
                            "type": "select",
                            "options": [
                                {"value": "cereais", "label": "Cereais"},
                                {"value": "horticultura", "label": "Horticultura"},
                                {"value": "fruticultura", "label": "Fruticultura"},
                                {"value": "vitivinicultura", "label": "Vitivinicultura"},
                                {"value": "pecuaria", "label": "Pecuária"},
                                {"value": "misto", "label": "Misto"}
                            ],
                            "required": True
                        },
                        {
                            "name": "farm_size",
                            "label": "Área da Exploração (hectares)",
                            "type": "select",
                            "options": [
                                {"value": "small", "label": "Até 5 hectares"},
                                {"value": "medium", "label": "5-50 hectares"},
                                {"value": "large", "label": "50-200 hectares"},
                                {"value": "enterprise", "label": "Mais de 200 hectares"}
                            ],
                            "required": True
                        },
                        {
                            "name": "experience_level",
                            "label": "Nível de Experiência",
                            "type": "select",
                            "options": [
                                {"value": "beginner", "label": "Iniciante"},
                                {"value": "intermediate", "label": "Intermédio"},
                                {"value": "advanced", "label": "Avançado"},
                                {"value": "expert", "label": "Especialista"}
                            ],
                            "required": True
                        },
                        {
                            "name": "location",
                            "label": "Localização",
                            "type": "text",
                            "placeholder": "Ex: Alentejo, Minho, Beira Interior...",
                            "required": True
                        },
                        {
                            "name": "goals",
                            "label": "Principais Objetivos",
                            "type": "checkbox",
                            "options": [
                                {"value": "increase_yield", "label": "Aumentar produtividade"},
                                {"value": "reduce_costs", "label": "Reduzir custos"},
                                {"value": "improve_quality", "label": "Melhorar qualidade"},
                                {"value": "sustainability", "label": "Sustentabilidade"},
                                {"value": "technology", "label": "Adotar tecnologia"},
                                {"value": "market_access", "label": "Acesso a mercados"}
                            ]
                        }
                    ]
                },
                completion_criteria={
                    "required_fields": ["farm_type", "farm_size", "experience_level", "location"]
                },
                estimated_time=5
            ),
            
            "dashboard_tour": OnboardingStep(
                id="dashboard_tour",
                title="Tour pelo Dashboard",
                description="Descubra as principais funcionalidades do seu painel de controlo",
                type=OnboardingStepType.TUTORIAL,
                order=3,
                content={
                    "tour_steps": [
                        {
                            "target": "#weather-widget",
                            "title": "Widget do Clima",
                            "content": "Monitorize as condições meteorológicas em tempo real para tomar decisões informadas."
                        },
                        {
                            "target": "#culture-overview",
                            "title": "Visão Geral das Culturas",
                            "content": "Acompanhe o estado das suas culturas e receba alertas importantes."
                        },
                        {
                            "target": "#quick-actions",
                            "title": "Ações Rápidas",
                            "content": "Aceda rapidamente às funcionalidades mais utilizadas."
                        },
                        {
                            "target": "#notifications",
                            "title": "Centro de Notificações",
                            "content": "Receba alertas personalizados sobre as suas culturas e atividades."
                        },
                        {
                            "target": "#ai-assistant",
                            "title": "Assistente IA",
                            "content": "Obtenha conselhos personalizados do nosso assistente inteligente."
                        }
                    ]
                },
                estimated_time=8
            ),
            
            "first_culture": OnboardingStep(
                id="first_culture",
                title="Adicione sua Primeira Cultura",
                description="Configure o monitoramento da sua primeira cultura",
                type=OnboardingStepType.INTERACTIVE_DEMO,
                order=4,
                content={
                    "demo_type": "culture_creation",
                    "guided_form": True,
                    "sample_data": {
                        "culture_suggestions": [
                            {"name": "Milho", "icon": "🌽", "season": "Primavera"},
                            {"name": "Trigo", "icon": "🌾", "season": "Outono"},
                            {"name": "Tomate", "icon": "🍅", "season": "Verão"},
                            {"name": "Oliveira", "icon": "🫒", "season": "Todo o ano"}
                        ]
                    },
                    "help_tips": [
                        "Escolha uma cultura adequada à sua região e época do ano",
                        "Defina a área cultivada para cálculos precisos",
                        "Configure alertas para etapas críticas do crescimento"
                    ]
                },
                completion_criteria={
                    "action": "culture_created"
                },
                estimated_time=10
            ),
            
            "weather_setup": OnboardingStep(
                id="weather_setup",
                title="Configure Alertas Meteorológicos",
                description="Personalize as notificações climáticas para suas culturas",
                type=OnboardingStepType.FEATURE_INTRODUCTION,
                order=5,
                content={
                    "feature_overview": {
                        "title": "Monitoramento Climático Inteligente",
                        "benefits": [
                            "Previsões meteorológicas precisas",
                            "Alertas de condições adversas",
                            "Recomendações baseadas no clima",
                            "Histórico climático detalhado"
                        ]
                    },
                    "configuration_options": [
                        {
                            "name": "frost_alerts",
                            "label": "Alertas de Geada",
                            "description": "Receba notificações quando há risco de geada",
                            "default": True
                        },
                        {
                            "name": "rain_alerts",
                            "label": "Alertas de Chuva",
                            "description": "Notificações sobre precipitação intensa",
                            "default": True
                        },
                        {
                            "name": "wind_alerts",
                            "label": "Alertas de Vento",
                            "description": "Avisos sobre ventos fortes",
                            "default": False
                        },
                        {
                            "name": "temperature_alerts",
                            "label": "Alertas de Temperatura",
                            "description": "Notificações sobre temperaturas extremas",
                            "default": True
                        }
                    ]
                },
                estimated_time=5
            ),
            
            "marketplace_intro": OnboardingStep(
                id="marketplace_intro",
                title="Explore o Marketplace",
                description="Descubra produtos e serviços especializados para agricultura",
                type=OnboardingStepType.FEATURE_INTRODUCTION,
                order=6,
                content={
                    "feature_overview": {
                        "title": "Marketplace Agrícola",
                        "description": "Conecte-se com fornecedores especializados e encontre os melhores produtos para sua atividade"
                    },
                    "categories_tour": [
                        {
                            "name": "Sementes e Plantas",
                            "icon": "🌱",
                            "description": "Variedades certificadas e adaptadas ao clima português"
                        },
                        {
                            "name": "Fertilizantes",
                            "icon": "🧪",
                            "description": "Nutrição especializada para cada tipo de cultura"
                        },
                        {
                            "name": "Equipamentos",
                            "icon": "🚜",
                            "description": "Maquinaria e ferramentas para agricultura moderna"
                        },
                        {
                            "name": "Serviços",
                            "icon": "🛠️",
                            "description": "Consultoria, análises e serviços especializados"
                        }
                    ],
                    "demo_search": {
                        "suggested_terms": ["fertilizante milho", "sementes tomate", "análise solo"]
                    }
                },
                estimated_time=7
            ),
            
            "ai_assistant_intro": OnboardingStep(
                id="ai_assistant_intro",
                title="Conheça seu Assistente IA",
                description="Aprenda a usar o assistente inteligente para otimizar sua produção",
                type=OnboardingStepType.INTERACTIVE_DEMO,
                order=7,
                content={
                    "demo_conversations": [
                        {
                            "question": "Quando devo plantar milho no Alentejo?",
                            "response": "No Alentejo, o milho deve ser plantado entre março e maio, quando as temperaturas mínimas estão consistentemente acima de 10°C..."
                        },
                        {
                            "question": "Como posso melhorar a qualidade do meu solo?",
                            "response": "Para melhorar a qualidade do solo, recomendo começar com uma análise completa. Com base nos resultados..."
                        }
                    ],
                    "conversation_starters": [
                        "Como cuidar de plantas de tomate?",
                        "Qual a melhor época para podar oliveiras?",
                        "Como prevenir pragas em hortaliças?",
                        "Que fertilizante usar para trigo?"
                    ]
                },
                completion_criteria={
                    "action": "ai_question_asked"
                },
                estimated_time=6
            ),
            
            "goal_setting": OnboardingStep(
                id="goal_setting",
                title="Defina seus Objetivos",
                description="Estabeleça metas para acompanhar o progresso da sua atividade",
                type=OnboardingStepType.GOAL_SETTING,
                order=8,
                content={
                    "goal_categories": [
                        {
                            "category": "Produtividade",
                            "goals": [
                                {"name": "Aumentar rendimento por hectare", "unit": "%", "target": 15},
                                {"name": "Reduzir perdas pós-colheita", "unit": "%", "target": 10},
                                {"name": "Melhorar qualidade dos produtos", "unit": "score", "target": 85}
                            ]
                        },
                        {
                            "category": "Sustentabilidade",
                            "goals": [
                                {"name": "Reduzir uso de pesticidas", "unit": "%", "target": 20},
                                {"name": "Melhorar eficiência da água", "unit": "%", "target": 25},
                                {"name": "Aumentar biodiversidade", "unit": "score", "target": 80}
                            ]
                        },
                        {
                            "category": "Financeiro",
                            "goals": [
                                {"name": "Reduzir custos de produção", "unit": "%", "target": 12},
                                {"name": "Aumentar margem de lucro", "unit": "%", "target": 18},
                                {"name": "Diversificar fontes de receita", "unit": "count", "target": 3}
                            ]
                        }
                    ]
                },
                estimated_time=8
            ),
            
            "completion": OnboardingStep(
                id="completion",
                title="Parabéns! Onboarding Concluído",
                description="Você está pronto para aproveitar ao máximo o AgroTech Portugal",
                type=OnboardingStepType.COMPLETION,
                order=9,
                content={
                    "celebration": {
                        "animation": "confetti",
                        "message": "Bem-vindo à família AgroTech Portugal!"
                    },
                    "next_steps": [
                        {
                            "title": "Explore o Dashboard",
                            "description": "Familiarize-se com todas as funcionalidades",
                            "action": "dashboard",
                            "icon": "📊"
                        },
                        {
                            "title": "Adicione mais Culturas",
                            "description": "Expanda o monitoramento para todas suas atividades",
                            "action": "cultures",
                            "icon": "🌱"
                        },
                        {
                            "title": "Configure Alertas",
                            "description": "Personalize as notificações conforme suas necessidades",
                            "action": "settings",
                            "icon": "🔔"
                        },
                        {
                            "title": "Contacte Suporte",
                            "description": "Nossa equipe está sempre disponível para ajudar",
                            "action": "support",
                            "icon": "💬"
                        }
                    ],
                    "achievement_badge": {
                        "title": "Pioneiro AgroTech",
                        "description": "Completou o onboarding com sucesso",
                        "icon": "🏆"
                    },
                    "bonus_content": {
                        "free_consultation": True,
                        "premium_trial": 30,  # dias
                        "welcome_discount": 15  # percentual
                    }
                },
                estimated_time=3
            )
        }
        
        return steps
    
    def start_onboarding(self, user_id: int) -> UserOnboardingProgress:
        """Iniciar onboarding para um usuário"""
        progress = UserOnboardingProgress(
            user_id=user_id,
            started_at=datetime.now(),
            current_step="welcome",
            completed_steps=[],
            skipped_steps=[],
            progress_percentage=0.0,
            estimated_completion_time=self._calculate_total_time(),
            personalization_data={},
            last_activity=datetime.now()
        )
        
        self.user_progress[user_id] = progress
        
        # Registrar evento de analytics
        from .analytics import analytics_tracker
        analytics_tracker.track_event(
            "onboarding_started",
            user_id=user_id,
            properties={
                "estimated_time": progress.estimated_completion_time,
                "first_step": "welcome"
            }
        )
        
        logger.info(f"Onboarding started for user {user_id}")
        return progress
    
    def get_user_progress(self, user_id: int) -> Optional[UserOnboardingProgress]:
        """Obter progresso do usuário"""
        return self.user_progress.get(user_id)
    
    def get_current_step(self, user_id: int) -> Optional[OnboardingStep]:
        """Obter etapa atual do usuário"""
        progress = self.get_user_progress(user_id)
        if not progress:
            return None
        
        return self.steps.get(progress.current_step)
    
    def complete_step(self, user_id: int, step_id: str, data: Dict[str, Any] = None) -> bool:
        """Marcar etapa como concluída"""
        progress = self.get_user_progress(user_id)
        if not progress or step_id not in self.steps:
            return False
        
        # Verificar se a etapa pode ser concluída
        step = self.steps[step_id]
        if not self._can_complete_step(progress, step, data):
            return False
        
        # Atualizar progresso
        if step_id not in progress.completed_steps:
            progress.completed_steps.append(step_id)
        
        # Salvar dados de personalização
        if data:
            progress.personalization_data.update(data)
        
        # Avançar para próxima etapa
        next_step = self._get_next_step(progress)
        if next_step:
            progress.current_step = next_step.id
        
        # Atualizar percentual de progresso
        progress.progress_percentage = self._calculate_progress_percentage(progress)
        progress.last_activity = datetime.now()
        
        # Registrar evento de analytics
        from .analytics import analytics_tracker
        analytics_tracker.track_event(
            "onboarding_step_completed",
            user_id=user_id,
            properties={
                "step_id": step_id,
                "step_title": step.title,
                "progress_percentage": progress.progress_percentage,
                "time_on_step": self._calculate_step_time(progress, step_id)
            }
        )
        
        # Verificar se onboarding foi concluído
        if self._is_onboarding_complete(progress):
            self._complete_onboarding(user_id, progress)
        
        logger.info(f"Step {step_id} completed for user {user_id}")
        return True
    
    def skip_step(self, user_id: int, step_id: str) -> bool:
        """Pular etapa"""
        progress = self.get_user_progress(user_id)
        if not progress or step_id not in self.steps:
            return False
        
        step = self.steps[step_id]
        if step.required:
            return False  # Não pode pular etapas obrigatórias
        
        # Atualizar progresso
        if step_id not in progress.skipped_steps:
            progress.skipped_steps.append(step_id)
        
        # Avançar para próxima etapa
        next_step = self._get_next_step(progress)
        if next_step:
            progress.current_step = next_step.id
        
        progress.progress_percentage = self._calculate_progress_percentage(progress)
        progress.last_activity = datetime.now()
        
        # Registrar evento
        from .analytics import analytics_tracker
        analytics_tracker.track_event(
            "onboarding_step_skipped",
            user_id=user_id,
            properties={
                "step_id": step_id,
                "step_title": step.title
            }
        )
        
        logger.info(f"Step {step_id} skipped for user {user_id}")
        return True
    
    def restart_onboarding(self, user_id: int) -> bool:
        """Reiniciar onboarding"""
        if user_id in self.user_progress:
            del self.user_progress[user_id]
        
        self.start_onboarding(user_id)
        
        # Registrar evento
        from .analytics import analytics_tracker
        analytics_tracker.track_event(
            "onboarding_restarted",
            user_id=user_id
        )
        
        return True
    
    def get_personalized_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Obter recomendações personalizadas baseadas no progresso"""
        progress = self.get_user_progress(user_id)
        if not progress:
            return []
        
        recommendations = []
        data = progress.personalization_data
        
        # Recomendações baseadas no tipo de exploração
        farm_type = data.get('farm_type')
        if farm_type:
            recommendations.extend(self._get_farm_type_recommendations(farm_type))
        
        # Recomendações baseadas no nível de experiência
        experience = data.get('experience_level')
        if experience:
            recommendations.extend(self._get_experience_recommendations(experience))
        
        # Recomendações baseadas nos objetivos
        goals = data.get('goals', [])
        if goals:
            recommendations.extend(self._get_goal_recommendations(goals))
        
        return recommendations[:5]  # Limitar a 5 recomendações
    
    def _calculate_total_time(self) -> int:
        """Calcular tempo total estimado do onboarding"""
        return sum(step.estimated_time for step in self.steps.values())
    
    def _can_complete_step(self, progress: UserOnboardingProgress, 
                          step: OnboardingStep, data: Dict[str, Any]) -> bool:
        """Verificar se uma etapa pode ser concluída"""
        # Verificar pré-requisitos
        for prereq in step.prerequisites:
            if prereq not in progress.completed_steps:
                return False
        
        # Verificar critérios de conclusão
        if step.completion_criteria:
            required_fields = step.completion_criteria.get('required_fields', [])
            if required_fields and data:
                for field in required_fields:
                    if field not in data or not data[field]:
                        return False
            
            required_action = step.completion_criteria.get('action')
            if required_action and not data.get('action_completed'):
                return False
        
        return True
    
    def _get_next_step(self, progress: UserOnboardingProgress) -> Optional[OnboardingStep]:
        """Obter próxima etapa"""
        current_step = self.steps.get(progress.current_step)
        if not current_step:
            return None
        
        # Encontrar próxima etapa em ordem
        next_order = current_step.order + 1
        for step in self.steps.values():
            if (step.order == next_order and 
                step.id not in progress.completed_steps and 
                step.id not in progress.skipped_steps):
                return step
        
        return None
    
    def _calculate_progress_percentage(self, progress: UserOnboardingProgress) -> float:
        """Calcular percentual de progresso"""
        total_steps = len(self.steps)
        completed_steps = len(progress.completed_steps) + len(progress.skipped_steps)
        return (completed_steps / total_steps) * 100
    
    def _calculate_step_time(self, progress: UserOnboardingProgress, step_id: str) -> int:
        """Calcular tempo gasto numa etapa (mock implementation)"""
        # Em uma implementação real, isso seria calculado baseado nos timestamps
        return 5  # minutos
    
    def _is_onboarding_complete(self, progress: UserOnboardingProgress) -> bool:
        """Verificar se onboarding está concluído"""
        required_steps = [step.id for step in self.steps.values() if step.required]
        completed_required = [step for step in required_steps if step in progress.completed_steps]
        return len(completed_required) == len(required_steps)
    
    def _complete_onboarding(self, user_id: int, progress: UserOnboardingProgress):
        """Finalizar onboarding"""
        progress.current_step = "completion"
        progress.progress_percentage = 100.0
        
        # Registrar conclusão
        from .analytics import analytics_tracker
        analytics_tracker.track_event(
            "onboarding_completed",
            user_id=user_id,
            properties={
                "total_time": (datetime.now() - progress.started_at).total_seconds() / 60,
                "steps_completed": len(progress.completed_steps),
                "steps_skipped": len(progress.skipped_steps),
                "completion_rate": progress.progress_percentage
            }
        )
        
        # Ativar benefícios de conclusão
        self._activate_completion_benefits(user_id)
        
        logger.info(f"Onboarding completed for user {user_id}")
    
    def _activate_completion_benefits(self, user_id: int):
        """Ativar benefícios de conclusão do onboarding"""
        # Implementar ativação de trial premium, desconto, etc.
        pass
    
    def _get_farm_type_recommendations(self, farm_type: str) -> List[Dict[str, Any]]:
        """Recomendações baseadas no tipo de exploração"""
        recommendations_map = {
            "cereais": [
                {"title": "Monitoramento de Pragas", "description": "Configure alertas para pragas comuns em cereais"},
                {"title": "Análise de Solo", "description": "Faça análises regulares para otimizar a nutrição"}
            ],
            "horticultura": [
                {"title": "Irrigação Inteligente", "description": "Otimize o uso da água com sensores de umidade"},
                {"title": "Controle de Estufa", "description": "Monitore temperatura e humidade em tempo real"}
            ],
            "fruticultura": [
                {"title": "Previsão de Colheita", "description": "Use IA para prever datas ideais de colheita"},
                {"title": "Controle de Qualidade", "description": "Monitore qualidade dos frutos durante crescimento"}
            ]
        }
        return recommendations_map.get(farm_type, [])
    
    def _get_experience_recommendations(self, experience: str) -> List[Dict[str, Any]]:
        """Recomendações baseadas no nível de experiência"""
        recommendations_map = {
            "beginner": [
                {"title": "Guias para Iniciantes", "description": "Acesse conteúdo educativo personalizado"},
                {"title": "Mentoria Virtual", "description": "Receba orientação do assistente IA"}
            ],
            "intermediate": [
                {"title": "Análises Avançadas", "description": "Use relatórios detalhados para otimização"},
                {"title": "Automação", "description": "Configure alertas e ações automáticas"}
            ],
            "advanced": [
                {"title": "API Integration", "description": "Conecte com seus sistemas existentes"},
                {"title": "Analytics Customizado", "description": "Crie dashboards personalizados"}
            ]
        }
        return recommendations_map.get(experience, [])
    
    def _get_goal_recommendations(self, goals: List[str]) -> List[Dict[str, Any]]:
        """Recomendações baseadas nos objetivos"""
        recommendations = []
        
        if "increase_yield" in goals:
            recommendations.append({
                "title": "Otimização de Produtividade",
                "description": "Use analytics para identificar oportunidades de melhoria"
            })
        
        if "sustainability" in goals:
            recommendations.append({
                "title": "Agricultura Sustentável", 
                "description": "Monitore métricas ambientais e reduza impacto"
            })
        
        if "technology" in goals:
            recommendations.append({
                "title": "Inovação Tecnológica",
                "description": "Explore funcionalidades avançadas da plataforma"
            })
        
        return recommendations

# Instância global
onboarding_engine = OnboardingEngine()
