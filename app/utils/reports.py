"""
Sistema de Relatórios Automatizados - AgroTech Portugal
Geração de relatórios executivos e análises de dados
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from flask import current_app
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import plotly.graph_objs as go
import plotly.express as px
from plotly.offline import plot
import io
import base64

logger = logging.getLogger(__name__)

@dataclass
class ReportMetric:
    """Métrica para relatório"""
    name: str
    value: float
    previous_value: float
    unit: str
    target: Optional[float] = None
    
    @property
    def change_percent(self) -> float:
        """Calcular mudança percentual"""
        if self.previous_value == 0:
            return 100.0 if self.value > 0 else 0.0
        return ((self.value - self.previous_value) / self.previous_value) * 100
    
    @property
    def status(self) -> str:
        """Status da métrica"""
        if self.target:
            return "success" if self.value >= self.target else "warning"
        return "success" if self.change_percent >= 0 else "warning"

@dataclass
class ReportSection:
    """Seção do relatório"""
    title: str
    metrics: List[ReportMetric]
    charts: List[Dict[str, Any]]
    insights: List[str]

class AnalyticsReportGenerator:
    """Gerador de relatórios de analytics"""
    
    def __init__(self):
        self.influx_client = None
        self._init_influx_client()
    
    def _init_influx_client(self):
        """Inicializar cliente InfluxDB"""
        try:
            from influxdb_client import InfluxDBClient
            
            self.influx_client = InfluxDBClient(
                url=current_app.config.get('INFLUXDB_URL'),
                token=current_app.config.get('INFLUXDB_TOKEN'),
                org=current_app.config.get('INFLUXDB_ORG')
            )
        except ImportError:
            logger.warning("InfluxDB client not available for reports")
        except Exception as e:
            logger.error(f"Error initializing InfluxDB client: {e}")
    
    def generate_daily_report(self, date: datetime = None) -> Dict[str, Any]:
        """Gerar relatório diário"""
        if not date:
            date = datetime.now() - timedelta(days=1)
        
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        previous_start = start_date - timedelta(days=1)
        
        report = {
            "report_type": "daily",
            "date": start_date.strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "sections": []
        }
        
        # Seção: Visão Geral
        overview_section = self._generate_overview_section(start_date, end_date, previous_start, start_date)
        report["sections"].append(overview_section)
        
        # Seção: Engajamento de Usuários
        engagement_section = self._generate_engagement_section(start_date, end_date, previous_start, start_date)
        report["sections"].append(engagement_section)
        
        # Seção: Performance Técnica
        performance_section = self._generate_performance_section(start_date, end_date, previous_start, start_date)
        report["sections"].append(performance_section)
        
        # Seção: Funcionalidades
        features_section = self._generate_features_section(start_date, end_date, previous_start, start_date)
        report["sections"].append(features_section)
        
        return report
    
    def generate_weekly_report(self, date: datetime = None) -> Dict[str, Any]:
        """Gerar relatório semanal"""
        if not date:
            date = datetime.now() - timedelta(days=7)
        
        # Última semana completa (segunda a domingo)
        days_since_monday = date.weekday()
        start_date = date - timedelta(days=days_since_monday)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
        previous_start = start_date - timedelta(days=7)
        
        report = {
            "report_type": "weekly",
            "week_start": start_date.strftime("%Y-%m-%d"),
            "week_end": (end_date - timedelta(days=1)).strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "sections": []
        }
        
        # Seções específicas da semana
        growth_section = self._generate_growth_section(start_date, end_date, previous_start, start_date)
        report["sections"].append(growth_section)
        
        retention_section = self._generate_retention_section(start_date, end_date)
        report["sections"].append(retention_section)
        
        conversion_section = self._generate_conversion_section(start_date, end_date, previous_start, start_date)
        report["sections"].append(conversion_section)
        
        return report
    
    def generate_monthly_report(self, date: datetime = None) -> Dict[str, Any]:
        """Gerar relatório mensal"""
        if not date:
            date = datetime.now().replace(day=1) - timedelta(days=1)  # Último dia do mês anterior
        
        # Primeiro e último dia do mês
        start_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)
        
        # Mês anterior para comparação
        if start_date.month == 1:
            previous_start = start_date.replace(year=start_date.year - 1, month=12)
        else:
            previous_start = start_date.replace(month=start_date.month - 1)
        
        report = {
            "report_type": "monthly",
            "month": start_date.strftime("%Y-%m"),
            "generated_at": datetime.now().isoformat(),
            "sections": []
        }
        
        # Seções específicas do mês
        business_section = self._generate_business_section(start_date, end_date, previous_start, start_date)
        report["sections"].append(business_section)
        
        technical_section = self._generate_technical_health_section(start_date, end_date)
        report["sections"].append(technical_section)
        
        recommendations_section = self._generate_recommendations_section(start_date, end_date)
        report["sections"].append(recommendations_section)
        
        return report
    
    def _generate_overview_section(self, start_date: datetime, end_date: datetime, 
                                 previous_start: datetime, previous_end: datetime) -> ReportSection:
        """Gerar seção de visão geral"""
        metrics = []
        
        # Usuários únicos
        unique_users = self._query_unique_users(start_date, end_date)
        previous_unique_users = self._query_unique_users(previous_start, previous_end)
        metrics.append(ReportMetric("Usuários Únicos", unique_users, previous_unique_users, "usuários"))
        
        # Page views
        page_views = self._query_page_views(start_date, end_date)
        previous_page_views = self._query_page_views(previous_start, previous_end)
        metrics.append(ReportMetric("Visualizações de Página", page_views, previous_page_views, "views"))
        
        # Sessões
        sessions = self._query_sessions(start_date, end_date)
        previous_sessions = self._query_sessions(previous_start, previous_end)
        metrics.append(ReportMetric("Sessões", sessions, previous_sessions, "sessões"))
        
        # Gráficos
        charts = [
            self._create_daily_users_chart(start_date, end_date),
            self._create_traffic_sources_chart(start_date, end_date)
        ]
        
        # Insights
        insights = self._generate_overview_insights(metrics)
        
        return ReportSection("Visão Geral", metrics, charts, insights)
    
    def _generate_engagement_section(self, start_date: datetime, end_date: datetime,
                                   previous_start: datetime, previous_end: datetime) -> ReportSection:
        """Gerar seção de engajamento"""
        metrics = []
        
        # Duração média de sessão
        avg_session_duration = self._query_avg_session_duration(start_date, end_date)
        previous_avg_session = self._query_avg_session_duration(previous_start, previous_end)
        metrics.append(ReportMetric("Duração Média de Sessão", avg_session_duration, 
                                  previous_avg_session, "minutos", target=5.0))
        
        # Taxa de rejeição
        bounce_rate = self._query_bounce_rate(start_date, end_date)
        previous_bounce_rate = self._query_bounce_rate(previous_start, previous_end)
        metrics.append(ReportMetric("Taxa de Rejeição", bounce_rate, previous_bounce_rate, "%"))
        
        # Páginas por sessão
        pages_per_session = self._query_pages_per_session(start_date, end_date)
        previous_pages_per_session = self._query_pages_per_session(previous_start, previous_end)
        metrics.append(ReportMetric("Páginas por Sessão", pages_per_session, 
                                  previous_pages_per_session, "páginas", target=3.0))
        
        charts = [
            self._create_engagement_timeline_chart(start_date, end_date),
            self._create_popular_pages_chart(start_date, end_date)
        ]
        
        insights = self._generate_engagement_insights(metrics)
        
        return ReportSection("Engajamento de Usuários", metrics, charts, insights)
    
    def _generate_performance_section(self, start_date: datetime, end_date: datetime,
                                    previous_start: datetime, previous_end: datetime) -> ReportSection:
        """Gerar seção de performance técnica"""
        metrics = []
        
        # Tempo de resposta médio
        avg_response_time = self._query_avg_response_time(start_date, end_date)
        previous_avg_response = self._query_avg_response_time(previous_start, previous_end)
        metrics.append(ReportMetric("Tempo de Resposta Médio", avg_response_time, 
                                  previous_avg_response, "ms", target=500.0))
        
        # Taxa de erro
        error_rate = self._query_error_rate(start_date, end_date)
        previous_error_rate = self._query_error_rate(previous_start, previous_end)
        metrics.append(ReportMetric("Taxa de Erro", error_rate, previous_error_rate, "%", target=1.0))
        
        # Uptime
        uptime = self._query_uptime(start_date, end_date)
        previous_uptime = self._query_uptime(previous_start, previous_end)
        metrics.append(ReportMetric("Uptime", uptime, previous_uptime, "%", target=99.9))
        
        charts = [
            self._create_response_time_chart(start_date, end_date),
            self._create_error_distribution_chart(start_date, end_date)
        ]
        
        insights = self._generate_performance_insights(metrics)
        
        return ReportSection("Performance Técnica", metrics, charts, insights)
    
    def _generate_features_section(self, start_date: datetime, end_date: datetime,
                                 previous_start: datetime, previous_end: datetime) -> ReportSection:
        """Gerar seção de funcionalidades"""
        metrics = []
        
        # Uso de funcionalidades
        feature_usage = self._query_feature_usage(start_date, end_date)
        previous_feature_usage = self._query_feature_usage(previous_start, previous_end)
        
        for feature, usage in feature_usage.items():
            previous_usage = previous_feature_usage.get(feature, 0)
            metrics.append(ReportMetric(f"Uso: {feature}", usage, previous_usage, "usos"))
        
        charts = [
            self._create_feature_usage_chart(start_date, end_date),
            self._create_feature_adoption_chart(start_date, end_date)
        ]
        
        insights = self._generate_features_insights(feature_usage)
        
        return ReportSection("Uso de Funcionalidades", metrics, charts, insights)
    
    def _generate_growth_section(self, start_date: datetime, end_date: datetime,
                               previous_start: datetime, previous_end: datetime) -> ReportSection:
        """Gerar seção de crescimento"""
        metrics = []
        
        # Novos usuários
        new_users = self._query_new_users(start_date, end_date)
        previous_new_users = self._query_new_users(previous_start, previous_end)
        metrics.append(ReportMetric("Novos Usuários", new_users, previous_new_users, "usuários"))
        
        # Taxa de crescimento
        if previous_new_users > 0:
            growth_rate = ((new_users - previous_new_users) / previous_new_users) * 100
        else:
            growth_rate = 100.0 if new_users > 0 else 0.0
        metrics.append(ReportMetric("Taxa de Crescimento Semanal", growth_rate, 0, "%", target=10.0))
        
        charts = [
            self._create_user_growth_chart(start_date, end_date),
            self._create_acquisition_channels_chart(start_date, end_date)
        ]
        
        insights = self._generate_growth_insights(metrics)
        
        return ReportSection("Crescimento", metrics, charts, insights)
    
    def _generate_retention_section(self, start_date: datetime, end_date: datetime) -> ReportSection:
        """Gerar seção de retenção"""
        metrics = []
        
        # Taxa de retenção
        retention_rate = self._query_retention_rate(start_date, end_date)
        metrics.append(ReportMetric("Taxa de Retenção", retention_rate, 0, "%", target=70.0))
        
        # Usuários ativos recorrentes
        returning_users = self._query_returning_users(start_date, end_date)
        metrics.append(ReportMetric("Usuários Recorrentes", returning_users, 0, "usuários"))
        
        charts = [
            self._create_cohort_chart(start_date, end_date),
            self._create_user_lifecycle_chart(start_date, end_date)
        ]
        
        insights = self._generate_retention_insights(metrics)
        
        return ReportSection("Retenção de Usuários", metrics, charts, insights)
    
    def _query_unique_users(self, start_date: datetime, end_date: datetime) -> int:
        """Query para usuários únicos"""
        # Implementar query InfluxDB ou usar dados mock
        return 150  # Mock data
    
    def _query_page_views(self, start_date: datetime, end_date: datetime) -> int:
        """Query para page views"""
        return 2500  # Mock data
    
    def _query_sessions(self, start_date: datetime, end_date: datetime) -> int:
        """Query para sessões"""
        return 300  # Mock data
    
    def _query_avg_session_duration(self, start_date: datetime, end_date: datetime) -> float:
        """Query para duração média de sessão"""
        return 6.5  # Mock data em minutos
    
    def _query_bounce_rate(self, start_date: datetime, end_date: datetime) -> float:
        """Query para taxa de rejeição"""
        return 35.5  # Mock data em percentual
    
    def _query_pages_per_session(self, start_date: datetime, end_date: datetime) -> float:
        """Query para páginas por sessão"""
        return 4.2  # Mock data
    
    def _query_avg_response_time(self, start_date: datetime, end_date: datetime) -> float:
        """Query para tempo de resposta médio"""
        return 450.0  # Mock data em ms
    
    def _query_error_rate(self, start_date: datetime, end_date: datetime) -> float:
        """Query para taxa de erro"""
        return 0.8  # Mock data em percentual
    
    def _query_uptime(self, start_date: datetime, end_date: datetime) -> float:
        """Query para uptime"""
        return 99.95  # Mock data em percentual
    
    def _query_feature_usage(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """Query para uso de funcionalidades"""
        return {
            "dashboard": 890,
            "culturas": 650,
            "clima": 420,
            "marketplace": 280,
            "ia_assistant": 150
        }  # Mock data
    
    def _query_new_users(self, start_date: datetime, end_date: datetime) -> int:
        """Query para novos usuários"""
        return 25  # Mock data
    
    def _query_retention_rate(self, start_date: datetime, end_date: datetime) -> float:
        """Query para taxa de retenção"""
        return 75.0  # Mock data
    
    def _query_returning_users(self, start_date: datetime, end_date: datetime) -> int:
        """Query para usuários recorrentes"""
        return 95  # Mock data
    
    def _create_daily_users_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de usuários diários"""
        # Mock data para demonstração
        dates = pd.date_range(start_date, end_date - timedelta(days=1), freq='D')
        users = [45, 52, 48, 61, 59, 67, 73][:len(dates)]
        
        return {
            "type": "line",
            "title": "Usuários Únicos Diários",
            "data": {
                "x": [d.strftime("%Y-%m-%d") for d in dates],
                "y": users
            }
        }
    
    def _create_traffic_sources_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de fontes de tráfego"""
        return {
            "type": "pie",
            "title": "Fontes de Tráfego",
            "data": {
                "labels": ["Direto", "Google", "Redes Sociais", "Email", "Outros"],
                "values": [45, 30, 15, 7, 3]
            }
        }
    
    def _create_engagement_timeline_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de timeline de engajamento"""
        return {
            "type": "line",
            "title": "Duração de Sessão ao Longo do Tempo",
            "data": {
                "x": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
                "y": [3.2, 4.1, 6.8, 7.5, 6.9, 5.4]
            }
        }
    
    def _create_popular_pages_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de páginas populares"""
        return {
            "type": "bar",
            "title": "Páginas Mais Visitadas",
            "data": {
                "x": ["Dashboard", "Culturas", "Clima", "Marketplace", "Perfil"],
                "y": [850, 650, 420, 280, 180]
            }
        }
    
    def _create_response_time_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de tempo de resposta"""
        return {
            "type": "line",
            "title": "Tempo de Resposta Médio",
            "data": {
                "x": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
                "y": [380, 420, 520, 580, 650, 480]
            }
        }
    
    def _create_error_distribution_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de distribuição de erros"""
        return {
            "type": "pie",
            "title": "Distribuição de Erros",
            "data": {
                "labels": ["404 Not Found", "500 Server Error", "403 Forbidden", "Timeout", "Outros"],
                "values": [60, 25, 10, 3, 2]
            }
        }
    
    def _create_feature_usage_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de uso de funcionalidades"""
        return {
            "type": "bar",
            "title": "Uso de Funcionalidades",
            "data": {
                "x": ["Dashboard", "Culturas", "Clima", "Marketplace", "IA"],
                "y": [890, 650, 420, 280, 150]
            }
        }
    
    def _create_feature_adoption_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de adoção de funcionalidades"""
        return {
            "type": "line",
            "title": "Adoção de Funcionalidades ao Longo do Tempo",
            "data": {
                "x": ["Semana 1", "Semana 2", "Semana 3", "Semana 4"],
                "y": [120, 180, 250, 320]
            }
        }
    
    def _create_user_growth_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de crescimento de usuários"""
        return {
            "type": "bar",
            "title": "Crescimento de Usuários",
            "data": {
                "x": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"],
                "y": [8, 12, 15, 18, 22, 10, 6]
            }
        }
    
    def _create_acquisition_channels_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de canais de aquisição"""
        return {
            "type": "pie",
            "title": "Canais de Aquisição",
            "data": {
                "labels": ["Orgânico", "Redes Sociais", "Email Marketing", "Indicação", "Publicidade"],
                "values": [40, 25, 20, 10, 5]
            }
        }
    
    def _create_cohort_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de cohort"""
        return {
            "type": "heatmap",
            "title": "Análise de Cohort - Retenção",
            "data": {
                "description": "Matriz de retenção por cohort de usuários"
            }
        }
    
    def _create_user_lifecycle_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Criar gráfico de ciclo de vida do usuário"""
        return {
            "type": "funnel",
            "title": "Ciclo de Vida do Usuário",
            "data": {
                "labels": ["Visitantes", "Registros", "Ativos", "Engajados", "Fiéis"],
                "values": [1000, 150, 120, 80, 45]
            }
        }
    
    def _generate_overview_insights(self, metrics: List[ReportMetric]) -> List[str]:
        """Gerar insights da visão geral"""
        insights = []
        
        for metric in metrics:
            if metric.change_percent > 10:
                insights.append(f"📈 {metric.name} cresceu {metric.change_percent:.1f}% - excelente performance!")
            elif metric.change_percent < -10:
                insights.append(f"📉 {metric.name} diminuiu {abs(metric.change_percent):.1f}% - requer atenção")
        
        if not insights:
            insights.append("📊 Métricas estáveis com variações dentro do esperado")
        
        return insights
    
    def _generate_engagement_insights(self, metrics: List[ReportMetric]) -> List[str]:
        """Gerar insights de engajamento"""
        insights = []
        
        session_duration = next((m for m in metrics if "Duração" in m.name), None)
        if session_duration and session_duration.value >= session_duration.target:
            insights.append("✅ Duração de sessão acima da meta - usuários engajados")
        elif session_duration:
            insights.append("⚠️ Duração de sessão abaixo da meta - revisar conteúdo")
        
        bounce_rate = next((m for m in metrics if "Rejeição" in m.name), None)
        if bounce_rate and bounce_rate.value < 30:
            insights.append("✅ Taxa de rejeição baixa - boa experiência do usuário")
        elif bounce_rate and bounce_rate.value > 50:
            insights.append("⚠️ Taxa de rejeição alta - revisar landing pages")
        
        return insights or ["📊 Métricas de engajamento dentro do esperado"]
    
    def _generate_performance_insights(self, metrics: List[ReportMetric]) -> List[str]:
        """Gerar insights de performance"""
        insights = []
        
        response_time = next((m for m in metrics if "Resposta" in m.name), None)
        if response_time and response_time.value <= response_time.target:
            insights.append("🚀 Tempo de resposta excelente - usuários satisfeitos")
        elif response_time:
            insights.append("⚠️ Tempo de resposta alto - otimizar performance")
        
        error_rate = next((m for m in metrics if "Erro" in m.name), None)
        if error_rate and error_rate.value <= error_rate.target:
            insights.append("✅ Taxa de erro baixa - sistema estável")
        elif error_rate:
            insights.append("🔴 Taxa de erro alta - investigar problemas")
        
        return insights or ["📊 Performance técnica estável"]
    
    def _generate_features_insights(self, feature_usage: Dict[str, int]) -> List[str]:
        """Gerar insights de funcionalidades"""
        insights = []
        
        most_used = max(feature_usage.items(), key=lambda x: x[1])
        least_used = min(feature_usage.items(), key=lambda x: x[1])
        
        insights.append(f"🏆 Funcionalidade mais usada: {most_used[0]} ({most_used[1]} usos)")
        insights.append(f"💡 Oportunidade de melhoria: {least_used[0]} ({least_used[1]} usos)")
        
        # Análise de adoção
        total_usage = sum(feature_usage.values())
        for feature, usage in feature_usage.items():
            percentage = (usage / total_usage) * 100
            if percentage > 30:
                insights.append(f"📈 {feature} representa {percentage:.1f}% do uso total")
        
        return insights
    
    def _generate_growth_insights(self, metrics: List[ReportMetric]) -> List[str]:
        """Gerar insights de crescimento"""
        insights = []
        
        growth_rate = next((m for m in metrics if "Crescimento" in m.name), None)
        if growth_rate and growth_rate.value >= growth_rate.target:
            insights.append("🚀 Taxa de crescimento acima da meta - tendência positiva")
        elif growth_rate:
            insights.append("📊 Crescimento moderado - oportunidades de marketing")
        
        new_users = next((m for m in metrics if "Novos" in m.name), None)
        if new_users and new_users.change_percent > 20:
            insights.append("📈 Forte crescimento de novos usuários")
        
        return insights or ["📊 Crescimento estável"]
    
    def _generate_retention_insights(self, metrics: List[ReportMetric]) -> List[str]:
        """Gerar insights de retenção"""
        insights = []
        
        retention_rate = next((m for m in metrics if "Retenção" in m.name), None)
        if retention_rate and retention_rate.value >= retention_rate.target:
            insights.append("🎯 Taxa de retenção excelente - usuários fiéis")
        elif retention_rate:
            insights.append("📊 Retenção pode ser melhorada com engagement")
        
        return insights or ["📊 Retenção dentro do esperado"]

class ReportRenderer:
    """Renderizador de relatórios em diferentes formatos"""
    
    def render_html(self, report: Dict[str, Any]) -> str:
        """Renderizar relatório em HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relatório AgroTech - {report.get('report_type', '').title()}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2E8B57; color: white; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
                .metric.success {{ border-left: 4px solid #4CAF50; }}
                .metric.warning {{ border-left: 4px solid #ff9800; }}
                .insights {{ background: #e8f5e8; padding: 15px; margin: 10px 0; }}
                .chart {{ margin: 20px 0; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>AgroTech Portugal - Relatório {report.get('report_type', '').title()}</h1>
                <p>Gerado em: {report.get('generated_at', '')}</p>
            </div>
        """
        
        for section_data in report.get('sections', []):
            html += f"""
            <div class="section">
                <h2>{section_data['title']}</h2>
                
                <div class="metrics">
            """
            
            for metric in section_data['metrics']:
                status_class = metric.status
                change_icon = "📈" if metric.change_percent >= 0 else "📉"
                
                html += f"""
                <div class="metric {status_class}">
                    <h3>{metric.name}</h3>
                    <p><strong>{metric.value} {metric.unit}</strong></p>
                    <p>{change_icon} {metric.change_percent:+.1f}%</p>
                </div>
                """
            
            html += """
                </div>
                
                <div class="insights">
                    <h3>📊 Insights</h3>
            """
            
            for insight in section_data['insights']:
                html += f"<p>{insight}</p>"
            
            html += """
                </div>
                
                <div class="charts">
                    <h3>📈 Gráficos</h3>
            """
            
            for chart in section_data['charts']:
                html += f"""
                <div class="chart">
                    <h4>{chart['title']}</h4>
                    <p>Tipo: {chart['type']}</p>
                </div>
                """
            
            html += """
                </div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def render_json(self, report: Dict[str, Any]) -> str:
        """Renderizar relatório em JSON"""
        return json.dumps(report, indent=2, ensure_ascii=False)

class ReportDistributor:
    """Distribuidor de relatórios via email"""
    
    def __init__(self):
        self.smtp_server = current_app.config.get('SMTP_SERVER')
        self.smtp_port = current_app.config.get('SMTP_PORT', 587)
        self.smtp_user = current_app.config.get('SMTP_USER')
        self.smtp_password = current_app.config.get('SMTP_PASSWORD')
    
    def send_report(self, report: Dict[str, Any], recipients: List[str], 
                   format: str = 'html') -> bool:
        """Enviar relatório por email"""
        try:
            # Renderizar relatório
            renderer = ReportRenderer()
            if format == 'html':
                content = renderer.render_html(report)
                content_type = 'html'
            else:
                content = renderer.render_json(report)
                content_type = 'plain'
            
            # Preparar email
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"AgroTech - Relatório {report.get('report_type', '').title()}"
            
            # Adicionar conteúdo
            msg.attach(MIMEText(content, content_type, 'utf-8'))
            
            # Enviar email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.smtp_user, recipients, text)
            server.quit()
            
            logger.info(f"Report sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending report: {e}")
            return False

# Instâncias globais
report_generator = AnalyticsReportGenerator()
report_distributor = ReportDistributor()
