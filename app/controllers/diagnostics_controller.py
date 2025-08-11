"""
Endpoint de diagnóstico para problemas de sessão - Sprint 1
"""
from flask import Blueprint, jsonify, session, current_app
from flask_login import current_user, login_required
from app.utils.response_helpers import ResponseHandler, LoggingHelper
from app.models.user import User
from app import db
import logging

diagnostics_bp = Blueprint('diagnostics', __name__, url_prefix='/diagnostics')
logger = logging.getLogger(__name__)


@diagnostics_bp.route('/session')
def check_session():
    """Verificar estado da sessão atual"""
    try:
        session_data = {
            'session_exists': bool(session),
            'session_keys': list(session.keys()) if session else [],
            'user_authenticated': current_user.is_authenticated,
            'user_id': current_user.id if current_user.is_authenticated else None,
            'user_email': current_user.email if current_user.is_authenticated else None,
            'onboarding_completed': current_user.onboarding_completed if current_user.is_authenticated else None,
            'app_config': {
                'SECRET_KEY_SET': bool(current_app.secret_key),
                'SECRET_KEY_LENGTH': len(current_app.secret_key) if current_app.secret_key else 0,
                'SESSION_COOKIE_SECURE': current_app.config.get('SESSION_COOKIE_SECURE'),
                'SESSION_COOKIE_HTTPONLY': current_app.config.get('SESSION_COOKIE_HTTPONLY'),
                'SESSION_COOKIE_SAMESITE': current_app.config.get('SESSION_COOKIE_SAMESITE'),
                'LOGIN_VIEW': current_app.login_manager.login_view,
            }
        }
        
        return ResponseHandler.handle_success(session_data)
        
    except Exception as e:
        logger.error(f"Erro no diagnóstico de sessão: {e}")
        return ResponseHandler.handle_server_error("Erro no diagnóstico")


@diagnostics_bp.route('/auth/test')
@login_required
def test_auth():
    """Testar autenticação funcionando"""
    try:
        user_data = {
            'user_id': current_user.id,
            'email': current_user.email,
            'onboarding_completed': current_user.onboarding_completed,
            'last_access': current_user.ultimo_acesso.isoformat() if current_user.ultimo_acesso else None,
            'session_data': dict(session) if session else {}
        }
        
        LoggingHelper.log_user_action(current_user.email, 'DIAGNOSTICS_AUTH_TEST')
        
        return ResponseHandler.handle_success(user_data)
        
    except Exception as e:
        logger.error(f"Erro no teste de auth: {e}")
        return ResponseHandler.handle_server_error("Erro no teste de autenticação")


@diagnostics_bp.route('/onboarding/status')
@login_required
def onboarding_status():
    """Verificar status detalhado do onboarding"""
    try:
        user = current_user
        
        onboarding_data = {
            'user_id': user.id,
            'email': user.email,
            'onboarding_completed': user.onboarding_completed,
            'nome_completo': user.nome_completo,
            'telefone': user.telefone,
            'experience_level': user.experience_level,
            'propriedade_nome': user.propriedade_nome,
            'cidade': user.cidade,
            'estado': user.estado,
            'latitude': user.latitude,
            'longitude': user.longitude,
            'step_completion': {
                'step_1': bool(user.experience_level),
                'step_2': bool(user.nome_completo),
                'step_3': bool(user.latitude and user.longitude),
                'step_4': bool(user.propriedade_nome),
                'step_5': user.onboarding_completed
            }
        }
        
        return ResponseHandler.handle_success(onboarding_data)
        
    except Exception as e:
        logger.error(f"Erro no status do onboarding: {e}")
        return ResponseHandler.handle_server_error("Erro ao verificar onboarding")


@diagnostics_bp.route('/database/users')
def list_users():
    """Listar usuários para diagnóstico (apenas em desenvolvimento)"""
    try:
        if current_app.config.get('FLASK_ENV') != 'development':
            return ResponseHandler.handle_auth_error("Acesso negado")
        
        users = User.query.all()
        users_data = []
        
        for user in users:
            users_data.append({
                'id': user.id,
                'email': user.email,
                'onboarding_completed': user.onboarding_completed,
                'created': user.data_criacao.isoformat() if user.data_criacao else None,
                'last_access': user.ultimo_acesso.isoformat() if user.ultimo_acesso else None
            })
        
        return ResponseHandler.handle_success({'users': users_data, 'total': len(users_data)})
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        return ResponseHandler.handle_server_error("Erro ao listar usuários")


@diagnostics_bp.route('/fix/session')
@login_required
def fix_session():
    """Tentar corrigir problemas de sessão automaticamente"""
    try:
        fixes_applied = []
        
        # Verificar e corrigir sessão
        if not session or '_user_id' not in session:
            # Reautenticar usuário atual
            from flask_login import login_user
            login_user(current_user, remember=True)
            fixes_applied.append('session_reauth')
        
        # Verificar dados do usuário
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
            if user:
                # Atualizar último acesso
                from datetime import datetime, timezone
                user.ultimo_acesso = datetime.now(timezone.utc)
                db.session.commit()
                fixes_applied.append('last_access_updated')
        
        result = {
            'fixes_applied': fixes_applied,
            'session_status': 'fixed' if fixes_applied else 'already_ok',
            'user_authenticated': current_user.is_authenticated
        }
        
        LoggingHelper.log_user_action(current_user.email, 'SESSION_FIX_APPLIED', str(fixes_applied))
        
        return ResponseHandler.handle_success(result)
        
    except Exception as e:
        logger.error(f"Erro ao corrigir sessão: {e}")
        return ResponseHandler.handle_server_error("Erro ao corrigir sessão")
