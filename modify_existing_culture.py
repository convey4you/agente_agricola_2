#!/usr/bin/env python3
"""
Modificar cultura existente para gerar alertas
"""
import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.models.user import User
from app.models.culture import Culture
from app.models.activity import Activity
from app import db
from datetime import datetime, timedelta

app = create_app()

print("=== MODIFICAR CULTURA EXISTENTE PARA ALERTAS ===")

with app.app_context():
    user = User.query.get(2)
    
    print(f"✅ Modificando cultura existente...")
    
    # Encontrar uma cultura existente
    existing_culture = Culture.query.filter_by(user_id=user.id, active=True).first()
    
    if existing_culture:
        print(f"📱 Cultura encontrada: {existing_culture.nome} (ID: {existing_culture.id})")
        print(f"   Data atual: {existing_culture.data_plantio}")
        
        # Modificar para data antiga (plantada há 10 dias)
        old_date = datetime.now().date() - timedelta(days=10)
        existing_culture.data_plantio = old_date
        
        print(f"   Nova data: {old_date} (há 10 dias)")
        
        try:
            db.session.commit()
            print("✅ Cultura modificada com sucesso!")
            
            # Testar alertas agora
            print("\n🚨 Testando alertas após modificação...")
            
            from app.services.dashboard_service import DashboardService
            from flask_login import login_user
            
            with app.test_request_context():
                login_user(user)
                
                # Testar função específica primeiro
                culture_alerts = DashboardService._get_culture_alerts()
                print(f"📊 Culture alerts: {len(culture_alerts)}")
                
                for alert in culture_alerts:
                    print(f"   - {alert.get('title')}: {alert.get('description')}")
                
                # Testar função geral
                all_alerts = DashboardService.get_alerts_data()
                print(f"📊 Total alertas: {len(all_alerts)}")
                
                for alert in all_alerts:
                    print(f"   - {alert.get('title')}: {alert.get('description')}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
    else:
        print("❌ Nenhuma cultura encontrada!")
    
    # Também tentar criar uma atividade em atraso
    print("\n📅 Criando atividade em atraso...")
    try:
        overdue_activity = Activity(
            titulo="Atividade Teste em Atraso",
            descricao="Esta atividade deveria ter sido feita ontem",
            user_id=user.id,
            data_prevista=datetime.now() - timedelta(days=1),  # Era para ontem
            status="pendente"
        )
        db.session.add(overdue_activity)
        db.session.commit()
        print("✅ Atividade em atraso criada!")
        
    except Exception as e:
        print(f"❌ Erro ao criar atividade: {e}")
        db.session.rollback()
