"""
Script para criar regras padrão de alertas para Portugal
Regras específicas para agricultura portuguesa
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.alerts import AlertRule, AlertType, AlertPriority
import json

def create_default_alert_rules():
    """Criar regras padrão de alertas para Portugal"""
    
    app = create_app()
    with app.app_context():
        
        rules = [
            # Alertas Climáticos
            {
                'name': 'Alerta de Geada',
                'description': 'Alerta quando temperatura pode causar geada',
                'alert_type': AlertType.WEATHER,
                'priority': AlertPriority.HIGH,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'weather.temperature', 'operator': 'lte', 'value': 2},
                        {'field': 'datetime.month', 'operator': 'in', 'value': [11, 12, 1, 2, 3]}
                    ]
                }),
                'title_template': '🧊 Alerta de Geada - {weather.temperature}°C',
                'message_template': 'Temperatura prevista de {weather.temperature}°C pode causar geada. Proteja suas culturas sensíveis e considere irrigação preventiva.',
                'action_text': 'Ver Previsão',
                'action_url_template': '/weather',
                'cooldown_hours': 12,
                'expires_after_hours': 24
            },
            
            {
                'name': 'Chuva Intensa',
                'description': 'Alerta para chuva intensa que pode afetar culturas',
                'alert_type': AlertType.WEATHER,
                'priority': AlertPriority.MEDIUM,
                'conditions': json.dumps({
                    'field': 'weather.precipitation', 'operator': 'gt', 'value': 20
                }),
                'title_template': '🌧️ Chuva Intensa Prevista',
                'message_template': 'Previsão de {weather.precipitation}mm de chuva. Verifique drenagem e considere adiar aplicações de defensivos.',
                'action_text': 'Ver Detalhes',
                'action_url_template': '/weather',
                'cooldown_hours': 6,
                'expires_after_hours': 12
            },
            
            {
                'name': 'Vento Forte',
                'description': 'Alerta para ventos fortes',
                'alert_type': AlertType.WEATHER,
                'priority': AlertPriority.MEDIUM,
                'conditions': json.dumps({
                    'field': 'weather.wind_speed', 'operator': 'gt', 'value': 40
                }),
                'title_template': '💨 Vento Forte - {weather.wind_speed} km/h',
                'message_template': 'Ventos de {weather.wind_speed} km/h previstos. Evite aplicações e verifique estruturas de suporte.',
                'action_text': 'Ver Previsão',
                'action_url_template': '/weather',
                'cooldown_hours': 8,
                'expires_after_hours': 16
            },
            
            # Alertas de Irrigação
            {
                'name': 'Necessidade de Irrigação',
                'description': 'Alerta quando não chove há muito tempo',
                'alert_type': AlertType.IRRIGATION,
                'priority': AlertPriority.MEDIUM,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'weather.days_without_rain', 'operator': 'gt', 'value': 7},
                        {'field': 'datetime.month', 'operator': 'in', 'value': [5, 6, 7, 8, 9]}
                    ]
                }),
                'title_template': '💧 Irrigação Recomendada',
                'message_template': 'Sem chuva há {weather.days_without_rain} dias. Verifique umidade do solo e considere irrigação.',
                'action_text': 'Planejar Irrigação',
                'action_url_template': '/cultures',
                'cooldown_hours': 48,
                'expires_after_hours': 72
            },
            
            # Alertas de Adubação
            {
                'name': 'Época de Adubação Primavera',
                'description': 'Lembrete de adubação na primavera',
                'alert_type': AlertType.FERTILIZATION,
                'priority': AlertPriority.LOW,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'datetime.month', 'operator': 'eq', 'value': 3},
                        {'field': 'datetime.season', 'operator': 'eq', 'value': 'spring'}
                    ]
                }),
                'title_template': '🌱 Época de Adubação',
                'message_template': 'Início da primavera é ideal para adubação de base. Analise o solo e aplique nutrientes necessários.',
                'action_text': 'Ver Culturas',
                'action_url_template': '/cultures',
                'cooldown_hours': 336,  # 2 semanas
                'expires_after_hours': 168  # 1 semana
            },
            
            # Alertas de Poda
            {
                'name': 'Época de Poda Inverno',
                'description': 'Lembrete de poda no inverno',
                'alert_type': AlertType.PRUNING,
                'priority': AlertPriority.LOW,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'datetime.month', 'operator': 'in', 'value': [1, 2]},
                        {'field': 'datetime.season', 'operator': 'eq', 'value': 'winter'}
                    ]
                }),
                'title_template': '✂️ Época de Poda',
                'message_template': 'Inverno é época ideal para poda de árvores frutíferas. Remova ramos doentes e forme a copa.',
                'action_text': 'Ver Culturas',
                'action_url_template': '/cultures',
                'cooldown_hours': 720,  # 1 mês
                'expires_after_hours': 336  # 2 semanas
            },
            
            # Alertas de Pragas e Doenças
            {
                'name': 'Condições para Míldio',
                'description': 'Condições favoráveis ao desenvolvimento de míldio',
                'alert_type': AlertType.DISEASE,
                'priority': AlertPriority.HIGH,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'weather.humidity', 'operator': 'gt', 'value': 80},
                        {'field': 'weather.temperature', 'operator': 'gte', 'value': 15},
                        {'field': 'weather.temperature', 'operator': 'lte', 'value': 25}
                    ]
                }),
                'title_template': '🦠 Risco de Míldio',
                'message_template': 'Condições favoráveis ao míldio: umidade {weather.humidity}% e temperatura {weather.temperature}°C. Monitore plantas sensíveis.',
                'action_text': 'Ver Recomendações',
                'action_url_template': '/cultures',
                'cooldown_hours': 24,
                'expires_after_hours': 48
            },
            
            {
                'name': 'Condições para Oídio',
                'description': 'Condições favoráveis ao desenvolvimento de oídio',
                'alert_type': AlertType.DISEASE,
                'priority': AlertPriority.MEDIUM,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'weather.humidity', 'operator': 'lt', 'value': 60},
                        {'field': 'weather.temperature', 'operator': 'gte', 'value': 20},
                        {'field': 'weather.temperature', 'operator': 'lte', 'value': 30}
                    ]
                }),
                'title_template': '🍄 Risco de Oídio',
                'message_template': 'Condições secas e quentes favorecem oídio. Umidade {weather.humidity}% e temperatura {weather.temperature}°C.',
                'action_text': 'Ver Tratamentos',
                'action_url_template': '/cultures',
                'cooldown_hours': 48,
                'expires_after_hours': 72
            },
            
            # Alertas de Colheita
            {
                'name': 'Época de Colheita Verão',
                'description': 'Lembrete para época de colheita no verão',
                'alert_type': AlertType.HARVEST,
                'priority': AlertPriority.MEDIUM,
                'conditions': json.dumps({
                    'operator': 'AND',
                    'operands': [
                        {'field': 'datetime.month', 'operator': 'in', 'value': [7, 8, 9]},
                        {'field': 'datetime.season', 'operator': 'eq', 'value': 'summer'}
                    ]
                }),
                'title_template': '🌾 Época de Colheita',
                'message_template': 'Verão é época de colheita para muitas culturas. Verifique o ponto de colheita de suas plantas.',
                'action_text': 'Ver Culturas',
                'action_url_template': '/cultures',
                'cooldown_hours': 168,  # 1 semana
                'expires_after_hours': 336  # 2 semanas
            },
            
            # Alerta Geral de Boas-vindas
            {
                'name': 'Boas-vindas Sistema',
                'description': 'Alerta de boas-vindas para novos usuários',
                'alert_type': AlertType.GENERAL,
                'priority': AlertPriority.LOW,
                'conditions': json.dumps({
                    'field': 'user.experiencia', 'operator': 'eq', 'value': 'iniciante'
                }),
                'title_template': '🌱 Bem-vindo ao AgroTech Portugal!',
                'message_template': 'Explore as funcionalidades do sistema e configure suas culturas para receber alertas personalizados.',
                'action_text': 'Começar Tour',
                'action_url_template': '/onboarding',
                'cooldown_hours': 99999,  # Apenas uma vez
                'expires_after_hours': 168  # 1 semana
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for rule_data in rules:
            # Verificar se regra já existe
            existing_rule = AlertRule.query.filter_by(name=rule_data['name']).first()
            
            if not existing_rule:
                rule = AlertRule(**rule_data)
                db.session.add(rule)
                created_count += 1
                print(f"✅ Criada regra: {rule_data['name']}")
            else:
                # Atualizar regra existente se necessário
                existing_rule.description = rule_data['description']
                existing_rule.conditions = rule_data['conditions']
                existing_rule.title_template = rule_data['title_template']
                existing_rule.message_template = rule_data['message_template']
                existing_rule.action_text = rule_data.get('action_text')
                existing_rule.action_url_template = rule_data.get('action_url_template')
                existing_rule.cooldown_hours = rule_data['cooldown_hours']
                existing_rule.expires_after_hours = rule_data['expires_after_hours']
                updated_count += 1
                print(f"🔄 Atualizada regra: {rule_data['name']}")
        
        db.session.commit()
        
        total_rules = AlertRule.query.count()
        
        print(f"\n📋 Resumo:")
        print(f"   ✅ Regras criadas: {created_count}")
        print(f"   🔄 Regras atualizadas: {updated_count}")
        print(f"   📊 Total de regras: {total_rules}")
        print(f"\n🎉 Processo concluído com sucesso!")

if __name__ == '__main__':
    create_default_alert_rules()
