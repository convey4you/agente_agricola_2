from flask import Blueprint, render_template, current_app, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app.models import User, Culture, Weather
from app.services.weather_data_service import WeatherDataService
from app.services.dashboard_service import DashboardService
from app.services.alert_service import AlertService

portugal = Blueprint('portugal', __name__, url_prefix='/portugal')

@portugal.route('/')
@login_required
def index():
    """Página inicial da versão portuguesa do sistema"""
    dashboard_service = DashboardService()
    alert_service = AlertService()
    weather_service = WeatherDataService()
    
    # Obter dados do dashboard
    dashboard_data = dashboard_service.get_dashboard_data_for_user(current_user)
    
    # Obter dados meteorológicos
    weather_data = weather_service.get_latest_weather_data_for_user(current_user)
    
    # Obter alertas
    alerts = alert_service.get_user_alerts(current_user.id)
    
    return render_template('dashboard/index-portugal.html', 
                          culturas_ativas=dashboard_data.get('culturas_ativas', 0),
                          area_total=dashboard_data.get('area_total', '0'),
                          receita_prevista=dashboard_data.get('receita_prevista', '0'),
                          tarefas_pendentes=dashboard_data.get('tarefas_pendentes', 0),
                          alertas=alerts,
                          alertas_count=len(alerts),
                          weather_data=weather_data)

@portugal.route('/clima/previsao')
@login_required
def weather_forecast():
    """Previsão climática versão portuguesa"""
    weather_service = WeatherDataService()
    weather_data = weather_service.get_latest_weather_data_for_user(current_user)
    forecast = weather_service.get_forecast_for_user_location(current_user)
    
    return render_template('clima/previsao-portugal.html',
                          weather_data=weather_data,
                          forecast=forecast)

@portugal.route('/alertas')
@login_required
def alerts():
    """Alertas versão portuguesa"""
    alert_service = AlertService()
    alerts = alert_service.get_user_alerts(current_user.id)
    
    return render_template('alertas/index-portugal.html',
                          alertas=alerts)

@portugal.route('/gestao/culturas')
@login_required
def cultures():
    """Gestão de culturas versão portuguesa"""
    cultures = Culture.query.filter_by(user_id=current_user.id).all()
    
    return render_template('cultures/index-portugal.html',
                          cultures=cultures)

@portugal.route('/gestao/culturas/nova')
@login_required
def new_culture():
    """Nova cultura versão portuguesa"""
    return render_template('cultures/new-portugal.html')

@portugal.route('/culturas/<int:culture_id>')
@login_required
def culture_detail(culture_id):
    """Detalhes de cultura específica versão portuguesa"""
    culture = Culture.query.filter_by(id=culture_id, user_id=current_user.id).first_or_404()
    
    return render_template('cultures/detail-portugal.html',
                          culture=culture)

@portugal.route('/toggle_version')
@login_required
def toggle_version():
    """Alterna entre versão portuguesa e versão internacional do sistema"""
    # Implementar lógica para alternar versão na sessão do usuário
    if 'portugal_version' in session:
        session.pop('portugal_version')
        flash('Versão internacional ativada', 'success')
    else:
        session['portugal_version'] = True
        flash('Versão portuguesa ativada', 'success')
    
    return redirect(request.referrer or url_for('dashboard.index'))
