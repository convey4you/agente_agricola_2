"""
Sistema de monitoramento em tempo real
"""
from flask import Blueprint, jsonify, render_template
from flask_login import login_required
from app.models.user import User
from app.models.culture import Culture
from app.models.activity import Activity
from app import db
import psutil
import os
from datetime import datetime, timezone, timedelta

monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/system-status')
@login_required
def system_status():
    """Status do sistema em tempo real"""
    try:
        # Informações do sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Estatísticas da aplicação
        total_users = User.query.count()
        total_cultures = Culture.query.count()
        total_activities = Activity.query.count()
        
        # Atividades recentes (últimas 24h)
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        recent_activities = Activity.query.filter(
            Activity.created_at >= yesterday
        ).count()
        
        return jsonify({
            'system': {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_total': memory.total // (1024*1024),  # MB
                'memory_used': memory.used // (1024*1024),    # MB
                'disk_usage': disk.percent,
                'disk_total': disk.total // (1024*1024*1024), # GB
                'disk_used': disk.used // (1024*1024*1024),   # GB
                'uptime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'database': {
                'total_users': total_users,
                'total_cultures': total_cultures,
                'total_activities': total_activities,
                'recent_activities': recent_activities
            },
            'status': 'healthy' if cpu_percent < 80 and memory.percent < 80 else 'warning'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@monitoring_bp.route('/health-check')
def health_check():
    """Health check simples para monitoramento externo"""
    try:
        # Testar conexão com banco de dados
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'database': 'connected',
            'version': '2.0.0'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@monitoring_bp.route('/dashboard-status')
def dashboard_status():
    """Dashboard de monitoramento em HTML"""
    return render_template('monitoring/dashboard.html')
