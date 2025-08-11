#!/usr/bin/env python3
"""Script para importar usuários da tabela CSV para a base de dados"""

import csv
from datetime import datetime
from app import create_app
from app.models.user import User
from app import db

app = create_app()

# Dados dos usuários do CSV
users_data = [
    {
        'id': 1,
        'email': 'admin@agrotech.pt',
        'password_hash': 'scrypt:32768:8:1$wjabnvLKtOGC2DV9$37795901fb0378ad5f1937e75ced9ec16dae148d7f9ed2f5f7dd79dcfafb4fd2a4e57ec65fd4feceaf3f0dfda8ff1fed9fc7bf8bd547bea7b4684bc027e25bea',
        'username': 'Admin AgroTech',
        'phone': '',
        'experience_level': 'beginner',
        'latitude': None,
        'longitude': None,
        'location': None,
        'created_at': '2025-08-05 20:48:14.303052',
        'updated_at': '2025-08-05 21:53:13.484215',
        'is_active': True,
        'email_confirmed': False
    },
    {
        'id': 2,
        'email': 'msmaia.pt@gmail.com',
        'password_hash': 'scrypt:32768:8:1$PTLo821DTJRidIZ5$dfa3b789ca397b20862b7726591b9bb69c97b387548a18d98ed581718b953be3ac41198daf9ae21cf5c86170316a95bb7b4c94ad8c30081a8044f8c482070825',
        'username': 'mauricio.maia',
        'phone': '+351930461030',
        'experience_level': 'beginner',
        'latitude': 39.8052145,
        'longitude': -8.096441,
        'location': 'Sertã, Portugal',
        'created_at': '2025-08-05 20:51:02.201142',
        'updated_at': '2025-08-05 23:59:07.207039',
        'is_active': True,
        'email_confirmed': True
    }
]

with app.app_context():
    print(f"Base de dados: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    # Verificar se já existem usuários
    existing_users = User.query.all()
    print(f"Usuários existentes: {len(existing_users)}")
    
    if existing_users:
        print("Usuários já existem:")
        for user in existing_users:
            print(f"  - {user.email}")
        print("Pulando importação...")
    else:
        print("Importando usuários...")
        
        for user_data in users_data:
            try:
                # Converter strings de data para datetime
                created_at = datetime.strptime(user_data['created_at'], '%Y-%m-%d %H:%M:%S.%f')
                updated_at = datetime.strptime(user_data['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
                
                user = User(
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    username=user_data['username'] if user_data['username'] else None,
                    phone=user_data['phone'] if user_data['phone'] else None,
                    experience_level=user_data['experience_level'],
                    latitude=user_data['latitude'],
                    longitude=user_data['longitude'],
                    location=user_data['location'] if user_data['location'] else None,
                    created_at=created_at,
                    updated_at=updated_at,
                    is_active=user_data['is_active'],
                    email_confirmed=user_data['email_confirmed']
                )
                
                db.session.add(user)
                print(f"✓ Adicionado: {user.email}")
                
            except Exception as e:
                print(f"✗ Erro ao adicionar {user_data['email']}: {e}")
        
        try:
            db.session.commit()
            print("✓ Usuários importados com sucesso!")
        except Exception as e:
            print(f"✗ Erro ao salvar: {e}")
            db.session.rollback()
    
    # Verificar resultado final
    final_users = User.query.all()
    print(f"\nTotal de usuários na base: {len(final_users)}")
    for user in final_users:
        print(f"  - {user.email} (ID: {user.id})")
