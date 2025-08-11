#!/usr/bin/env python3
"""
Script para criar usuário administrador
"""

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Criar usuário administrador"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar se admin já existe
            existing_admin = User.query.filter_by(email='admin@agrotech.pt').first()
            if existing_admin:
                print("👤 Usuário admin já existe!")
                print(f"📧 Email: {existing_admin.email}")
                return
            
            # Criar novo usuário admin
            admin_user = User(
                email='admin@agrotech.pt',
                nome_completo='Administrador AgroTech',
                password_hash=generate_password_hash('admin123'),
                onboarding_completed=True,
                ativo=True,
                experience_level='advanced'
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Usuário administrador criado com sucesso!")
            print("📧 Email: admin@agrotech.pt")
            print("🔑 Senha: admin123")
            print("🌐 Acesse: http://localhost:5000/auth/login")
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário admin: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    create_admin_user()
