"""
Script para criar atividade em atraso com tipo correto
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from app import create_app, db
from app.models.user import User
from app.models.activity import Activity
from app.models.culture import Culture
from datetime import datetime, timedelta

def create_overdue_activity():
    app = create_app()
    
    with app.app_context():
        print("=== CRIAR ATIVIDADE EM ATRASO ===")
        
        # Buscar usuário
        user = User.query.get(2)
        if not user:
            print("❌ Usuário não encontrado")
            return
            
        # Buscar uma cultura
        culture = Culture.query.filter_by(user_id=user.id).first()
        if not culture:
            print("❌ Nenhuma cultura encontrada")
            return
            
        print(f"👤 Usuário: {user.name}")
        print(f"🌱 Cultura: {culture.nome}")
        
        # Criar atividade em atraso com tipo obrigatório
        yesterday = datetime.now() - timedelta(days=1)
        
        activity = Activity(
            user_id=user.id,
            culture_id=culture.id,
            titulo="Atividade Teste em Atraso",
            descricao="Esta atividade deveria ter sido feita ontem",
            tipo="irrigacao",  # Definir tipo obrigatório
            data_prevista=yesterday,
            status="pendente",
            prioridade="alta"
        )
        
        try:
            db.session.add(activity)
            db.session.commit()
            print(f"✅ Atividade criada: {activity.titulo}")
            print(f"📅 Data prevista: {activity.data_prevista}")
            print(f"⏰ Status: {activity.status}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao criar atividade: {e}")
            return False

if __name__ == "__main__":
    create_overdue_activity()
