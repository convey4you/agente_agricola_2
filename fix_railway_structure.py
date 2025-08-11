#!/usr/bin/env python3
"""
Script para forçar criação completa da estrutura no Railway
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import upgrade, init, migrate
import sqlalchemy as sa


def create_complete_migration():
    """Criar migration completo com todas as tabelas e colunas"""
    
    # Configurar Flask app temporário
    app = Flask(__name__)
    
    # Configuração para Railway PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///temp.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # Definir modelo User completo
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        nome_completo = db.Column(db.String(200))
        telefone = db.Column(db.String(20))
        experience_level = db.Column(db.String(20), default='beginner')
        propriedade_nome = db.Column(db.String(120))
        location = db.Column(db.String(200))  # COLUNA QUE ESTAVA FALTANDO
        latitude = db.Column(db.Float, nullable=True)
        longitude = db.Column(db.Float, nullable=True)
        cidade = db.Column(db.String(100), nullable=True)
        estado = db.Column(db.String(50), nullable=True)
        data_criacao = db.Column(db.DateTime, default=sa.func.now())
        ultimo_acesso = db.Column(db.DateTime)
        ativo = db.Column(db.Boolean, default=True)
        onboarding_completed = db.Column(db.Boolean, default=False)
    
    with app.app_context():
        try:
            # Conectar ao banco
            engine = db.engine
            inspector = sa.inspect(engine)
            
            print("🔍 Verificando estrutura atual...")
            
            # Verificar se tabela users existe
            if 'users' in inspector.get_table_names():
                print("✅ Tabela users encontrada")
                
                # Verificar colunas
                columns = inspector.get_columns('users')
                column_names = [col['name'] for col in columns]
                
                print(f"📊 Colunas existentes: {column_names}")
                
                if 'location' not in column_names:
                    print("❌ Coluna 'location' FALTANDO!")
                    print("🔧 Adicionando coluna location...")
                    
                    # Adicionar coluna location
                    with engine.connect() as conn:
                        conn.execute(sa.text('ALTER TABLE users ADD COLUMN location VARCHAR(200)'))
                        conn.commit()
                    
                    print("✅ Coluna 'location' adicionada com sucesso!")
                else:
                    print("✅ Coluna 'location' já existe")
            else:
                print("❌ Tabela users não encontrada!")
                print("🔧 Criando todas as tabelas...")
                db.create_all()
                print("✅ Todas as tabelas criadas!")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False


if __name__ == '__main__':
    success = create_complete_migration()
    if success:
        print("\n🎉 Estrutura do banco corrigida com sucesso!")
        print("🚀 Aplicação pode ser iniciada normalmente")
    else:
        print("\n❌ Falha ao corrigir estrutura do banco")
        sys.exit(1)
