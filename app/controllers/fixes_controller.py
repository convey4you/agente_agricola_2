"""
Controlador para correções críticas do sistema
"""
from flask import Blueprint, jsonify, request
import os
import logging
from flask_login import login_required, current_user

# Criar blueprint
fixes_bp = Blueprint('fixes', __name__)

logger = logging.getLogger(__name__)

def fix_alerts_table_direct():
    """
    Função direta para corrigir tabela de alertas (para testes)
    """
    try:
        from sqlalchemy import create_engine, text, inspect
        from flask import current_app
        
        # Obter URL do banco de dados
        database_url = current_app.config.get('DATABASE_URL')
        if not database_url:
            return {
                'success': False,
                'error': 'DATABASE_URL não configurada'
            }
        
        engine = create_engine(database_url)
        inspector = inspect(engine)
        
        # Verificar colunas existentes
        existing_columns = [col['name'] for col in inspector.get_columns('alerts')]
        logger.info(f"Colunas existentes na tabela alerts: {existing_columns}")
        
        # Colunas que devem existir
        required_columns = {
            'action_text': 'VARCHAR(100)',
            'action_url': 'VARCHAR(500)', 
            'alert_metadata': 'TEXT',
            'delivery_channels': 'VARCHAR(200)',
            'retry_count': 'INTEGER DEFAULT 0',
            'last_retry_at': 'TIMESTAMP'
        }
        
        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name not in existing_columns:
                missing_columns.append((col_name, col_type))
        
        if not missing_columns:
            return {
                'success': True,
                'message': 'Todas as colunas já existem!',
                'existing_columns': existing_columns
            }
        
        # Adicionar colunas faltantes
        added_columns = []
        with engine.connect() as conn:
            for col_name, col_type in missing_columns:
                try:
                    sql = f"ALTER TABLE alerts ADD COLUMN {col_name} {col_type};"
                    logger.info(f"Executando: {sql}")
                    conn.execute(text(sql))
                    added_columns.append(col_name)
                    logger.info(f"Coluna {col_name} adicionada com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao adicionar {col_name}: {e}")
                    # Continuar com as outras colunas
            
            # Commit das mudanças
            conn.commit()
        
        return {
            'success': True,
            'message': f'Correção concluída! Colunas adicionadas: {added_columns}',
            'added_columns': added_columns
        }
        
    except Exception as e:
        logger.error(f"Erro na correção da tabela alerts: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@fixes_bp.route('/fix-alerts-table', methods=['POST'])
@login_required
def fix_alerts_table():
    """
    Corrigir tabela de alertas adicionando colunas faltantes
    APENAS para administradores
    """
    try:
        # Verificar se é admin
        if not hasattr(current_user, 'email') or current_user.email != 'admin@agrotech.pt':
            return jsonify({
                'success': False,
                'error': 'Acesso negado - apenas administradores'
            }), 403
        
        from sqlalchemy import create_engine, text, inspect
        from flask import current_app
        
        # Obter URL do banco de dados
        database_url = current_app.config.get('DATABASE_URL')
        if not database_url:
            return jsonify({
                'success': False,
                'error': 'DATABASE_URL não configurada'
            }), 500
        
        engine = create_engine(database_url)
        inspector = inspect(engine)
        
        # Verificar colunas existentes
        existing_columns = [col['name'] for col in inspector.get_columns('alerts')]
        logger.info(f"Colunas existentes na tabela alerts: {existing_columns}")
        
        # Colunas que devem existir
        required_columns = {
            'action_text': 'VARCHAR(100)',
            'action_url': 'VARCHAR(500)', 
            'alert_metadata': 'TEXT',
            'delivery_channels': 'VARCHAR(200)',
            'retry_count': 'INTEGER DEFAULT 0',
            'last_retry_at': 'TIMESTAMP'
        }
        
        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name not in existing_columns:
                missing_columns.append((col_name, col_type))
        
        if not missing_columns:
            return jsonify({
                'success': True,
                'message': 'Todas as colunas já existem!',
                'existing_columns': existing_columns
            })
        
        # Adicionar colunas faltantes
        added_columns = []
        with engine.connect() as conn:
            for col_name, col_type in missing_columns:
                try:
                    sql = f"ALTER TABLE alerts ADD COLUMN {col_name} {col_type};"
                    logger.info(f"Executando: {sql}")
                    conn.execute(text(sql))
                    added_columns.append(col_name)
                    logger.info(f"Coluna {col_name} adicionada com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao adicionar {col_name}: {e}")
                    # Continuar com as outras colunas
            
            # Commit das mudanças
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Correção concluída! Colunas adicionadas: {added_columns}',
            'added_columns': added_columns,
            'admin_user': current_user.email
        })
        
    except Exception as e:
        logger.error(f"Erro na correção da tabela alerts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fixes_bp.route('/cache-stats', methods=['GET'])
@login_required  
def get_cache_statistics():
    """
    Obter estatísticas do cache
    """
    try:
        from app.utils.cache_optimization import get_cache_stats
        
        stats = get_cache_stats()
        
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do cache: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fixes_bp.route('/warm-cache', methods=['POST'])
@login_required
def warm_cache_manually():
    """
    Cache warming desabilitado - Sistema simplificado
    """
    return jsonify({
        'success': True,
        'message': 'Cache warming desabilitado - sistema simplificado',
        'user': current_user.email,
        'status': 'disabled'
    }), 500
