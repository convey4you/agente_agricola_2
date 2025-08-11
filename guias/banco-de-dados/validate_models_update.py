#!/usr/bin/env python3
"""
Script para validar se todos os modelos SQLAlchemy foram atualizados
conforme a estrutura otimizada do banco de dados.
"""

import os
import sys
import importlib

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import db, create_app
from app.models.user import User
from app.models.farm import Farm
from app.models.culture import Culture, CultureType
from app.models.alerts import Alert, UserAlertPreference, AlertRule
from app.models.activity import Activity
from app.models.marketplace import MarketplaceItem
from app.models.conversation import Conversation, Message
from app.models.weather import WeatherData, WeatherLocation, WeatherStats

def validate_model_fields():
    """Validar se os modelos têm os campos corretos"""
    
    print("🔍 VALIDANDO MODELOS SQLALCHEMY\n")
    
    validation_results = {}
    
    # 1. User Model
    print("1. 👤 User Model:")
    user_issues = []
    
    if hasattr(User, 'data_criacao'):
        user_issues.append("❌ Campo 'data_criacao' ainda existe (deve ser 'created_at')")
    elif hasattr(User, 'created_at'):
        print("   ✅ Campo 'created_at' encontrado")
    else:
        user_issues.append("❌ Campo 'created_at' não encontrado")
    
    if hasattr(User, 'ativo'):
        user_issues.append("❌ Campo 'ativo' ainda existe (deve ser 'is_active')")
    elif hasattr(User, 'is_active'):
        print("   ✅ Campo 'is_active' encontrado")
    else:
        user_issues.append("❌ Campo 'is_active' não encontrado")
    
    if hasattr(User, 'updated_at'):
        print("   ✅ Campo 'updated_at' encontrado")
    else:
        user_issues.append("❌ Campo 'updated_at' não encontrado")
    
    if hasattr(User, 'country'):
        print("   ✅ Campo 'country' encontrado")
    else:
        user_issues.append("❌ Campo 'country' não encontrado")
    
    if hasattr(User, 'timezone'):
        print("   ✅ Campo 'timezone' encontrado")
    else:
        user_issues.append("❌ Campo 'timezone' não encontrado")
    
    if hasattr(User, 'postal_code'):
        print("   ✅ Campo 'postal_code' encontrado")
    else:
        user_issues.append("❌ Campo 'postal_code' não encontrado")
    
    validation_results['User'] = user_issues
    
    # 2. Farm Model
    print("\n2. 🏠 Farm Model:")
    farm_issues = []
    
    if hasattr(Farm, 'data_criacao'):
        farm_issues.append("❌ Campo 'data_criacao' ainda existe (deve ser 'created_at')")
    elif hasattr(Farm, 'created_at'):
        print("   ✅ Campo 'created_at' encontrado")
    else:
        farm_issues.append("❌ Campo 'created_at' não encontrado")
    
    if hasattr(Farm, 'ativo'):
        farm_issues.append("❌ Campo 'ativo' ainda existe (deve ser 'is_active')")
    elif hasattr(Farm, 'is_active'):
        print("   ✅ Campo 'is_active' encontrado")
    else:
        farm_issues.append("❌ Campo 'is_active' não encontrado")
    
    if hasattr(Farm, 'updated_at'):
        print("   ✅ Campo 'updated_at' encontrado")
    else:
        farm_issues.append("❌ Campo 'updated_at' não encontrado")
    
    if hasattr(Farm, 'postal_code'):
        print("   ✅ Campo 'postal_code' encontrado")
    else:
        farm_issues.append("❌ Campo 'postal_code' não encontrado")
    
    validation_results['Farm'] = farm_issues
    
    # 3. Culture Model
    print("\n3. 🌱 Culture Model:")
    culture_issues = []
    
    if hasattr(Culture, 'active'):
        culture_issues.append("❌ Campo 'active' ainda existe (deve ser 'is_active')")
    elif hasattr(Culture, 'is_active'):
        print("   ✅ Campo 'is_active' encontrado")
    else:
        culture_issues.append("❌ Campo 'is_active' não encontrado")
    
    if hasattr(Culture, 'updated_at'):
        print("   ✅ Campo 'updated_at' encontrado")
    else:
        culture_issues.append("❌ Campo 'updated_at' não encontrado")
    
    validation_results['Culture'] = culture_issues
    
    # 4. Alert Model
    print("\n4. 🚨 Alert Model:")
    alert_issues = []
    
    if hasattr(Alert, 'updated_at'):
        print("   ✅ Campo 'updated_at' encontrado")
    else:
        alert_issues.append("❌ Campo 'updated_at' não encontrado")
    
    if hasattr(Alert, 'severity_level'):
        print("   ✅ Campo 'severity_level' encontrado")
    else:
        alert_issues.append("❌ Campo 'severity_level' não encontrado")
    
    if hasattr(Alert, 'expires_at'):
        print("   ✅ Campo 'expires_at' encontrado")
    else:
        alert_issues.append("❌ Campo 'expires_at' não encontrado")
    
    validation_results['Alert'] = alert_issues
    
    # 5. Conversation Model
    print("\n5. 💬 Conversation Model:")
    conversation_issues = []
    
    if hasattr(Conversation, 'active'):
        conversation_issues.append("❌ Campo 'active' ainda existe (deve ser 'is_active')")
    elif hasattr(Conversation, 'is_active'):
        print("   ✅ Campo 'is_active' encontrado")
    else:
        conversation_issues.append("❌ Campo 'is_active' não encontrado")
    
    validation_results['Conversation'] = conversation_issues
    
    # 6. Weather Models
    print("\n6. 🌤️ Weather Models:")
    weather_issues = []
    
    # WeatherData
    if hasattr(WeatherData, 'location_name'):
        print("   ✅ WeatherData.location_name encontrado")
    else:
        weather_issues.append("❌ WeatherData.location_name não encontrado")
    
    if hasattr(WeatherData, 'collected_at'):
        print("   ✅ WeatherData.collected_at encontrado")
    else:
        weather_issues.append("❌ WeatherData.collected_at não encontrado")
    
    # WeatherLocation
    if hasattr(WeatherLocation, 'is_active'):
        print("   ✅ WeatherLocation.is_active encontrado")
    else:
        weather_issues.append("❌ WeatherLocation.is_active não encontrado")
    
    if hasattr(WeatherLocation, 'is_default'):
        print("   ✅ WeatherLocation.is_default encontrado")
    else:
        weather_issues.append("❌ WeatherLocation.is_default não encontrado")
    
    # WeatherStats
    if hasattr(WeatherStats, 'period_date'):
        print("   ✅ WeatherStats.period_date encontrado")
    else:
        weather_issues.append("❌ WeatherStats.period_date não encontrado")
    
    validation_results['Weather'] = weather_issues
    
    # Resumo
    print("\n" + "="*60)
    print("📋 RESUMO DA VALIDAÇÃO")
    print("="*60)
    
    total_issues = 0
    for model_name, issues in validation_results.items():
        if issues:
            print(f"\n❌ {model_name} Model: {len(issues)} problemas")
            for issue in issues:
                print(f"   {issue}")
            total_issues += len(issues)
        else:
            print(f"\n✅ {model_name} Model: Todos os campos corretos")
    
    print(f"\n{'='*60}")
    if total_issues == 0:
        print("🎉 TODOS OS MODELOS ATUALIZADOS CORRETAMENTE!")
        print("✅ Os modelos estão sincronizados com o banco otimizado.")
    else:
        print(f"⚠️  ENCONTRADOS {total_issues} PROBLEMAS NOS MODELOS")
        print("❌ Alguns modelos ainda precisam ser atualizados.")
    
    return total_issues == 0

if __name__ == '__main__':
    # Criar contexto da aplicação para importar os modelos
    app = create_app()
    
    with app.app_context():
        try:
            success = validate_model_fields()
            sys.exit(0 if success else 1)
        except Exception as e:
            print(f"❌ Erro durante validação: {e}")
            sys.exit(1)
