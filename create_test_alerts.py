#!/usr/bin/env python3
"""
Criar condições para gerar alertas de teste
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

print("=== CRIAR CONDIÇÕES PARA ALERTAS ===")

with app.app_context():
    user = User.query.get(2)
    
    print(f"✅ Modificando dados para gerar alertas...")
    
    # 1. Criar uma cultura sem data de plantio
    print("1️⃣ Criando cultura sem data de plantio...")
    culture_no_date = Culture(
        nome="Cultura Teste Sem Data",
        user_id=user.id,
        active=True,
        area_plantada=5.0,
        data_plantio=None  # Sem data de plantio
    )
    db.session.add(culture_no_date)
    
    # 2. Modificar uma cultura existente para ter data antiga
    print("2️⃣ Modificando cultura para ter data de plantio antiga...")
    old_culture = Culture.query.filter_by(user_id=user.id, active=True).first()
    if old_culture:
        # Plantada há 10 dias (deveria gerar alerta de irrigação)
        old_culture.data_plantio = datetime.now().date() - timedelta(days=10)
        print(f"   Cultura '{old_culture.nome}' agora plantada há 10 dias")
    
    # 3. Criar uma atividade em atraso
    print("3️⃣ Criando atividade em atraso...")
    overdue_activity = Activity(
        titulo="Atividade em Atraso",
        descricao="Esta atividade deveria ter sido feita ontem",
        user_id=user.id,
        data_prevista=datetime.now() - timedelta(days=1),  # Era para ontem
        status="pendente"
    )
    db.session.add(overdue_activity)
    
    # Salvar alterações
    try:
        db.session.commit()
        print("✅ Alterações salvas com sucesso!")
        
        # Agora testar se os alertas aparecem
        print("\n🚨 Testando alertas após modificações...")
        
        from app.services.dashboard_service import DashboardService
        from flask_login import login_user
        
        with app.test_request_context():
            login_user(user)
            
            alerts = DashboardService.get_alerts_data()
            print(f"📊 Total de alertas gerados: {len(alerts)}")
            
            if alerts:
                print("🎉 SUCESSO! Alertas encontrados:")
                for i, alert in enumerate(alerts, 1):
                    print(f"   {i}. {alert.get('title')}")
                    print(f"      {alert.get('description')}")
                    print(f"      Prioridade: {alert.get('priority')}")
                    print()
            else:
                print("❌ Ainda nenhum alerta gerado. Vamos debugar mais...")
                
                # Debug individual
                culture_alerts = DashboardService._get_culture_alerts()
                task_alerts = DashboardService._get_task_alerts()
                
                print(f"   Culture alerts: {len(culture_alerts)}")
                for alert in culture_alerts:
                    print(f"   - {alert}")
                    
                print(f"   Task alerts: {len(task_alerts)}")
                for alert in task_alerts:
                    print(f"   - {alert}")
                
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
