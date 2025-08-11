"""
Rotas para Sistema de Onboarding - AgroTech Portugal
API endpoints para gestão do processo de onboarding
"""

from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from flask_login import login_required, current_user
from app.utils.onboarding import onboarding_engine, OnboardingStepType
from app.utils.analytics import analytics_tracker
import logging

logger = logging.getLogger(__name__)

onboarding_bp = Blueprint('onboarding', __name__, url_prefix='/api/onboarding')

@onboarding_bp.route('/start', methods=['POST'])
@login_required
def start_onboarding():
    """Iniciar processo de onboarding"""
    try:
        progress = onboarding_engine.start_onboarding(current_user.id)
        
        return jsonify({
            "success": True,
            "message": "Onboarding iniciado com sucesso",
            "data": {
                "user_id": progress.user_id,
                "current_step": progress.current_step,
                "progress_percentage": progress.progress_percentage,
                "estimated_time": progress.estimated_completion_time
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting onboarding: {e}")
        return jsonify({
            "success": False,
            "message": "Erro ao iniciar onboarding"
        }), 500

@onboarding_bp.route('/progress', methods=['GET'])
@login_required
def get_progress():
    """Obter progresso atual do onboarding"""
    try:
        progress = onboarding_engine.get_user_progress(current_user.id)
        
        if not progress:
            return jsonify({
                "success": False,
                "message": "Onboarding não iniciado"
            }), 404
        
        current_step = onboarding_engine.get_current_step(current_user.id)
        
        return jsonify({
            "success": True,
            "data": {
                "user_id": progress.user_id,
                "started_at": progress.started_at.isoformat(),
                "current_step": {
                    "id": current_step.id if current_step else None,
                    "title": current_step.title if current_step else None,
                    "description": current_step.description if current_step else None,
                    "type": current_step.type.value if current_step else None,
                    "content": current_step.content if current_step else None,
                    "estimated_time": current_step.estimated_time if current_step else None
                },
                "completed_steps": progress.completed_steps,
                "skipped_steps": progress.skipped_steps,
                "progress_percentage": progress.progress_percentage,
                "estimated_completion_time": progress.estimated_completion_time,
                "personalization_data": progress.personalization_data
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting onboarding progress: {e}")
        return jsonify({
            "success": False,
            "message": "Erro ao obter progresso"
        }), 500

@onboarding_bp.route('/step/<step_id>/complete', methods=['POST'])
@login_required
def complete_step(step_id):
    """Marcar etapa como concluída"""
    try:
        data = request.get_json() or {}
        
        success = onboarding_engine.complete_step(current_user.id, step_id, data)
        
        if not success:
            return jsonify({
                "success": False,
                "message": "Não foi possível completar a etapa"
            }), 400
        
        # Obter progresso atualizado
        progress = onboarding_engine.get_user_progress(current_user.id)
        next_step = onboarding_engine.get_current_step(current_user.id)
        
        return jsonify({
            "success": True,
            "message": "Etapa concluída com sucesso",
            "data": {
                "progress_percentage": progress.progress_percentage,
                "next_step": {
                    "id": next_step.id if next_step else None,
                    "title": next_step.title if next_step else None,
                    "type": next_step.type.value if next_step else None
                } if next_step else None,
                "is_complete": progress.progress_percentage >= 100
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error completing onboarding step: {e}")
        return jsonify({
            "success": False,
            "message": "Erro ao completar etapa"
        }), 500

@onboarding_bp.route('/step/<step_id>/skip', methods=['POST'])
@login_required
def skip_step(step_id):
    """Pular etapa não obrigatória"""
    try:
        success = onboarding_engine.skip_step(current_user.id, step_id)
        
        if not success:
            return jsonify({
                "success": False,
                "message": "Não é possível pular esta etapa"
            }), 400
        
        # Obter progresso atualizado
        progress = onboarding_engine.get_user_progress(current_user.id)
        next_step = onboarding_engine.get_current_step(current_user.id)
        
        return jsonify({
            "success": True,
            "message": "Etapa pulada com sucesso",
            "data": {
                "progress_percentage": progress.progress_percentage,
                "next_step": {
                    "id": next_step.id if next_step else None,
                    "title": next_step.title if next_step else None
                } if next_step else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error skipping onboarding step: {e}")
        return jsonify({
            "success": False,
            "message": "Erro ao pular etapa"
        }), 500

@onboarding_bp.route('/restart', methods=['POST'])
@login_required
def restart_onboarding():
    """Reiniciar processo de onboarding"""
    try:
        success = onboarding_engine.restart_onboarding(current_user.id)
        
        if not success:
            return jsonify({
                "success": False,
                "message": "Erro ao reiniciar onboarding"
            }), 500
        
        progress = onboarding_engine.get_user_progress(current_user.id)
        
        return jsonify({
            "success": True,
            "message": "Onboarding reiniciado com sucesso",
            "data": {
                "current_step": progress.current_step,
                "progress_percentage": progress.progress_percentage
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error restarting onboarding: {e}")
        return jsonify({
            "success": False,
            "message": "Erro ao reiniciar onboarding"
        }), 500

@onboarding_bp.route('/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    """Obter recomendações personalizadas"""
    try:
        recommendations = onboarding_engine.get_personalized_recommendations(current_user.id)
        
        return jsonify({
            "success": True,
            "data": {
                "recommendations": recommendations,
                "count": len(recommendations)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({
            "success": False,
            "message": "Erro ao obter recomendações"
        }), 500

@onboarding_bp.route('/steps', methods=['GET'])
@login_required
def get_all_steps():
    """Obter todas as etapas do onboarding"""
    try:
        steps = []
        for step in onboarding_engine.steps.values():
            steps.append({
                "id": step.id,
                "title": step.title,
                "description": step.description,
                "type": step.type.value,
                "order": step.order,
                "required": step.required,
                "estimated_time": step.estimated_time
            })
        
        # Ordenar por ordem
        steps.sort(key=lambda x: x['order'])
        
        return jsonify({
            "success": True,
            "data": {
                "steps": steps,
                "total_steps": len(steps),
                "total_time": sum(step['estimated_time'] for step in steps)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting onboarding steps: {e}")
        return jsonify({
            "success": False,
            "message": "Erro ao obter etapas"
        }), 500

# Templates para onboarding
@onboarding_bp.route('/welcome')
@login_required
def welcome_page():
    """Página de boas-vindas do onboarding"""
    progress = onboarding_engine.get_user_progress(current_user.id)
    if not progress:
        # Iniciar onboarding automaticamente
        progress = onboarding_engine.start_onboarding(current_user.id)
    
    current_step = onboarding_engine.get_current_step(current_user.id)
    
    return render_template('onboarding/welcome.html', 
                         progress=progress, 
                         current_step=current_step)

@onboarding_bp.route('/step/<step_id>')
@login_required
def step_page(step_id):
    """Página de uma etapa específica do onboarding"""
    progress = onboarding_engine.get_user_progress(current_user.id)
    if not progress:
        return redirect(url_for('onboarding.welcome_page'))
    
    step = onboarding_engine.steps.get(step_id)
    if not step:
        return redirect(url_for('onboarding.welcome_page'))
    
    return render_template(f'onboarding/steps/{step.type.value}.html',
                         step=step,
                         progress=progress)

# Webhook para eventos de onboarding
@onboarding_bp.route('/webhook/step-interaction', methods=['POST'])
@login_required
def track_step_interaction():
    """Registrar interação com etapa do onboarding"""
    try:
        data = request.get_json()
        
        # Validar dados
        required_fields = ['step_id', 'interaction_type']
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "message": "Dados incompletos"
            }), 400
        
        # Registrar evento de analytics
        analytics_tracker.track_event(
            "onboarding_interaction",
            user_id=current_user.id,
            properties={
                "step_id": data['step_id'],
                "interaction_type": data['interaction_type'],
                "interaction_data": data.get('interaction_data', {}),
                "timestamp": data.get('timestamp'),
                "session_id": session.get('session_id')
            }
        )
        
        return jsonify({
            "success": True,
            "message": "Interação registrada"
        }), 200
        
    except Exception as e:
        logger.error(f"Error tracking onboarding interaction: {e}")
        return jsonify({
            "success": False,
            "message": "Erro ao registrar interação"
        }), 500

# Middleware para verificar status do onboarding
@onboarding_bp.before_app_request
def check_onboarding_status():
    """Verificar se usuário precisa completar onboarding"""
    if (current_user.is_authenticated and 
        request.endpoint and 
        not request.endpoint.startswith('onboarding.') and
        not request.endpoint.startswith('static') and
        not request.endpoint.startswith('api.')):
        
        progress = onboarding_engine.get_user_progress(current_user.id)
        
        # Se não há progresso ou onboarding não está completo
        if not progress or progress.progress_percentage < 100:
            # Páginas que não requerem onboarding completo
            allowed_pages = ['auth.logout', 'main.profile', 'api.']
            
            if not any(request.endpoint.startswith(page) for page in allowed_pages):
                # Adicionar flag para mostrar prompt de onboarding
                session['show_onboarding_prompt'] = True
