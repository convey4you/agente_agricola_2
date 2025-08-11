"""
Reports Controller - Sistema de Relatórios Agrícolas
Gera relatórios detalhados sobre culturas, produção e performance.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from marshmallow import Schema, fields, ValidationError
import sqlite3
from datetime import datetime, timedelta
import logging
import os
import json

# Blueprint configuration
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportFilterSchema(Schema):
    """Schema para validação de filtros de relatório"""
    period = fields.Str(load_default='30d', validate=lambda x: x in ['7d', '30d', '90d', '1y', 'custom'])
    start_date = fields.Date(load_default=None)
    end_date = fields.Date(load_default=None)
    culture = fields.Str(load_default='')
    report_type = fields.Str(load_default='summary', validate=lambda x: x in [
        'summary', 'production', 'financial', 'performance', 'detailed'
    ])

class ReportsService:
    """Serviço para geração de relatórios"""
    
    def __init__(self):
        self.db_path = self._get_db_path()
    
    def _get_db_path(self):
        """Retorna o caminho do banco de dados"""
        if os.getenv('RAILWAY_ENVIRONMENT'):
            return None  # TODO: PostgreSQL
        else:
            return 'data/reports.db'
    
    def get_summary_report(self, user_id, filters=None):
        """Gera relatório resumo com métricas principais"""
        try:
            # Por enquanto, retornar dados demo
            return {
                'success': True,
                'data': {
                    'summary': {
                        'total_cultures': 12,
                        'total_area': 2.4,
                        'estimated_production': 1200,
                        'estimated_revenue': 4200,
                        'active_alerts': 3
                    },
                    'cultures': [
                        {
                            'name': 'Tomate',
                            'area': 0.8,
                            'production': 450,
                            'revenue': 1800,
                            'performance': 92,
                            'status': 'excellent'
                        },
                        {
                            'name': 'Alface',
                            'area': 0.6,
                            'production': 320,
                            'revenue': 960,
                            'performance': 88,
                            'status': 'good'
                        },
                        {
                            'name': 'Cenoura',
                            'area': 0.5,
                            'production': 280,
                            'revenue': 840,
                            'performance': 85,
                            'status': 'good'
                        },
                        {
                            'name': 'Milho',
                            'area': 0.5,
                            'production': 150,
                            'revenue': 600,
                            'performance': 78,
                            'status': 'warning'
                        }
                    ],
                    'recent_activities': [
                        {
                            'date': '2024-01-30',
                            'type': 'harvest',
                            'culture': 'Tomate',
                            'description': 'Colheita de tomates - lote A',
                            'quantity': 45
                        },
                        {
                            'date': '2024-01-28',
                            'type': 'maintenance',
                            'culture': 'Alface',
                            'description': 'Irrigação e controle de pragas',
                            'quantity': None
                        },
                        {
                            'date': '2024-01-25',
                            'type': 'planting',
                            'culture': 'Cenoura',
                            'description': 'Plantio de cenouras - área B',
                            'quantity': 100
                        }
                    ],
                    'alerts': [
                        {
                            'type': 'warning',
                            'message': 'Previsão de chuva forte nos próximos 3 dias',
                            'culture': 'Todas',
                            'priority': 'medium'
                        },
                        {
                            'type': 'info',
                            'message': 'Período ideal para colheita de alface',
                            'culture': 'Alface',
                            'priority': 'low'
                        },
                        {
                            'type': 'danger',
                            'message': 'Detectada praga em plantação de tomate',
                            'culture': 'Tomate',
                            'priority': 'high'
                        }
                    ],
                    'next_actions': [
                        {
                            'task': 'Aplicar fungicida nas plantas de tomate',
                            'priority': 'high',
                            'deadline': '2024-02-02',
                            'culture': 'Tomate'
                        },
                        {
                            'task': 'Preparar solo para próximo plantio',
                            'priority': 'medium',
                            'deadline': '2024-02-05',
                            'culture': 'Geral'
                        },
                        {
                            'task': 'Colher alface quando atingir tamanho ideal',
                            'priority': 'low',
                            'deadline': '2024-02-08',
                            'culture': 'Alface'
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório resumo: {e}")
            return {
                'success': False,
                'error': 'Erro ao gerar relatório'
            }
    
    def get_production_report(self, user_id, filters=None):
        """Gera relatório detalhado de produção"""
        try:
            return {
                'success': True,
                'data': {
                    'production_by_culture': [
                        {'culture': 'Tomate', 'planned': 500, 'actual': 450, 'variance': -10},
                        {'culture': 'Alface', 'planned': 300, 'actual': 320, 'variance': 6.7},
                        {'culture': 'Cenoura', 'planned': 250, 'actual': 280, 'variance': 12},
                        {'culture': 'Milho', 'planned': 200, 'actual': 150, 'variance': -25}
                    ],
                    'production_timeline': [
                        {'month': 'Janeiro', 'total': 1200, 'target': 1000},
                        {'month': 'Dezembro', 'total': 950, 'target': 900},
                        {'month': 'Novembro', 'total': 800, 'target': 850},
                        {'month': 'Outubro', 'total': 600, 'target': 700}
                    ],
                    'quality_metrics': {
                        'grade_a': 65,
                        'grade_b': 25,
                        'grade_c': 10,
                        'total_quality_score': 85
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de produção: {e}")
            return {
                'success': False,
                'error': 'Erro ao gerar relatório de produção'
            }
    
    def get_financial_report(self, user_id, filters=None):
        """Gera relatório financeiro"""
        try:
            return {
                'success': True,
                'data': {
                    'revenue_by_culture': [
                        {'culture': 'Tomate', 'revenue': 1800, 'cost': 900, 'profit': 900, 'margin': 50},
                        {'culture': 'Alface', 'revenue': 960, 'cost': 540, 'profit': 420, 'margin': 43.8},
                        {'culture': 'Cenoura', 'revenue': 840, 'cost': 420, 'profit': 420, 'margin': 50},
                        {'culture': 'Milho', 'revenue': 600, 'cost': 450, 'profit': 150, 'margin': 25}
                    ],
                    'cost_breakdown': {
                        'seeds': 15,
                        'fertilizers': 25,
                        'labor': 35,
                        'equipment': 15,
                        'other': 10
                    },
                    'monthly_flow': [
                        {'month': 'Janeiro', 'revenue': 4200, 'costs': 2310, 'profit': 1890},
                        {'month': 'Dezembro', 'revenue': 3800, 'costs': 2100, 'profit': 1700},
                        {'month': 'Novembro', 'revenue': 3200, 'costs': 1900, 'profit': 1300}
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório financeiro: {e}")
            return {
                'success': False,
                'error': 'Erro ao gerar relatório financeiro'
            }
    
    def export_report_pdf(self, user_id, report_data, report_type):
        """Exporta relatório em PDF"""
        try:
            # Simular geração de PDF
            filename = f"relatorio_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Em implementação real, usaria bibliotecas como ReportLab ou WeasyPrint
            logger.info(f"PDF simulado gerado: {filename}")
            
            return {
                'success': True,
                'filename': filename,
                'message': 'Relatório exportado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao exportar PDF: {e}")
            return {
                'success': False,
                'error': 'Erro ao exportar relatório'
            }

# Instância do serviço
reports_service = ReportsService()

@reports_bp.route('/')
def index():
    """Página principal de relatórios"""
    try:
        return render_template('reports/index.html')
    except Exception as e:
        logger.error(f"Erro ao renderizar relatórios: {e}")
        flash('Erro ao carregar relatórios', 'error')
        return redirect(url_for('dashboard.dashboard'))

@reports_bp.route('/api/summary', methods=['GET'])
def api_summary_report():
    """API para relatório resumo"""
    try:
        # Verificar se usuário está logado
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Login necessário'
            }), 401
        
        # Validar filtros
        schema = ReportFilterSchema()
        try:
            filters = schema.load(request.args)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Filtros inválidos',
                'details': e.messages
            }), 400
        
        # Gerar relatório
        user_id = session['user_id']
        result = reports_service.get_summary_report(user_id, filters)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"Erro na API de relatório resumo: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@reports_bp.route('/api/production', methods=['GET'])
def api_production_report():
    """API para relatório de produção"""
    try:
        # Verificar se usuário está logado
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Login necessário'
            }), 401
        
        # Validar filtros
        schema = ReportFilterSchema()
        try:
            filters = schema.load(request.args)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Filtros inválidos',
                'details': e.messages
            }), 400
        
        # Gerar relatório
        user_id = session['user_id']
        result = reports_service.get_production_report(user_id, filters)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"Erro na API de relatório de produção: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@reports_bp.route('/api/financial', methods=['GET'])
def api_financial_report():
    """API para relatório financeiro"""
    try:
        # Verificar se usuário está logado
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Login necessário'
            }), 401
        
        # Validar filtros
        schema = ReportFilterSchema()
        try:
            filters = schema.load(request.args)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Filtros inválidos',
                'details': e.messages
            }), 400
        
        # Gerar relatório
        user_id = session['user_id']
        result = reports_service.get_financial_report(user_id, filters)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"Erro na API de relatório financeiro: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@reports_bp.route('/api/export', methods=['POST'])
def api_export_report():
    """API para exportar relatório em PDF"""
    try:
        # Verificar se usuário está logado
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Login necessário'
            }), 401
        
        # Validar dados
        data = request.get_json()
        if not data or 'report_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Tipo de relatório não especificado'
            }), 400
        
        report_type = data['report_type']
        report_data = data.get('data', {})
        
        # Gerar PDF
        user_id = session['user_id']
        result = reports_service.export_report_pdf(user_id, report_data, report_type)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"Erro ao exportar relatório: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@reports_bp.route('/api/charts/production', methods=['GET'])
def api_production_chart():
    """API para dados do gráfico de produção"""
    try:
        return jsonify({
            'success': True,
            'chart_data': {
                'labels': ['Tomate', 'Alface', 'Cenoura', 'Milho'],
                'datasets': [
                    {
                        'label': 'Produção (kg)',
                        'data': [450, 320, 280, 150],
                        'backgroundColor': '#10b981',
                        'borderColor': '#059669',
                        'borderWidth': 1
                    },
                    {
                        'label': 'Meta (kg)',
                        'data': [500, 300, 250, 200],
                        'backgroundColor': '#f59e0b',
                        'borderColor': '#d97706',
                        'borderWidth': 1
                    }
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar dados do gráfico: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro ao gerar gráfico'
        }), 500

@reports_bp.route('/api/charts/financial', methods=['GET'])
def api_financial_chart():
    """API para dados do gráfico financeiro"""
    try:
        return jsonify({
            'success': True,
            'chart_data': {
                'labels': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
                'datasets': [
                    {
                        'label': 'Receita (€)',
                        'data': [800, 1200, 1500, 1800, 2200],
                        'backgroundColor': '#10b981',
                        'borderColor': '#059669',
                        'borderWidth': 2,
                        'fill': False
                    },
                    {
                        'label': 'Custos (€)',
                        'data': [600, 800, 1000, 1100, 1300],
                        'backgroundColor': '#f59e0b',
                        'borderColor': '#d97706',
                        'borderWidth': 2,
                        'fill': False
                    }
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar dados do gráfico financeiro: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro ao gerar gráfico financeiro'
        }), 500

# Error handlers
@reports_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint não encontrado'
    }), 404

@reports_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Erro interno do servidor'
    }), 500
