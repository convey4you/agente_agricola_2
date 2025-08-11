#!/usr/bin/env python3
"""
Script para inicializar banco de dados e criar usuário admin
"""
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializar banco de dados"""
    print("🗄️  Inicializando banco de dados...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas criadas com sucesso")
            
            # Verificar se já existe usuário admin
            admin_user = User.query.filter_by(email='admin@agrotech.pt').first()
            
            if not admin_user:
                # Criar usuário admin
                admin_user = User(
                    nome_completo='Admin AgroTech',
                    email='admin@agrotech.pt',
                    password_hash=generate_password_hash('admin123'),
                    ativo=True
                )
                
                db.session.add(admin_user)
                db.session.commit()
                
                print("✅ Usuário admin criado:")
                print("   📧 Email: admin@agrotech.pt")
                print("   🔑 Senha: admin123")
            else:
                print("ℹ️  Usuário admin já existe")
            
            # Estatísticas
            total_users = User.query.count()
            print(f"📊 Total de usuários no sistema: {total_users}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {e}")
            return False

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 INICIALIZAÇÃO DO BANCO DE DADOS")
    print("=" * 50)
    
    success = init_database()
    
    if success:
        print("\n🎉 Banco inicializado com sucesso!")
        print("🔗 Acesse: http://localhost:5000/auth/login")
        print("📧 Email: admin@agrotech.pt")
        print("🔑 Senha: admin123")
    else:
        print("\n❌ Falha na inicialização")
    
    print("=" * 50)
