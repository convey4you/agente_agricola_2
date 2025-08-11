#!/usr/bin/env python3
"""
Script para criar usuário de teste para onboarding
"""

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_test_user():
    """Criar usuário de teste para onboarding"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar se usuário de teste já existe
            existing_user = User.query.filter_by(email='teste@agrotech.pt').first()
            if existing_user:
                print("👤 Usuário de teste já existe!")
                print(f"📧 Email: {existing_user.email}")
                print(f"✅ Onboarding completo: {existing_user.onboarding_completed}")
                return
            
            # Criar novo usuário de teste
            test_user = User(
                email='teste@agrotech.pt',
                nome_completo='Usuário Teste',
                password_hash=generate_password_hash('teste123'),
                onboarding_completed=False,  # Importante: onboarding não completado
                ativo=True
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Usuário de teste criado com sucesso!")
            print("📧 Email: teste@agrotech.pt")
            print("🔑 Senha: teste123")
            print("🎯 Onboarding: NÃO COMPLETADO (para teste)")
            print("🌐 Acesse: http://localhost:5000/auth/login")
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário de teste: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    create_test_user()
