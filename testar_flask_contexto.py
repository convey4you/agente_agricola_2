#!/usr/bin/env python3
"""
Teste Flask com contexto da aplicação
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.culture import CultureType

def testar_flask_contexto():
    """Teste no contexto Flask"""
    print("🔍 TESTE FLASK COM CONTEXTO")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        from app import db
        
        # Verificar URL do banco
        print(f"🔗 Database URL: {db.engine.url}")
        
        try:
            # Testar conexão
            connection = db.engine.connect()
            print("✅ Conexão com banco estabelecida")
            
            # Contar registros via ORM
            total = CultureType.query.count()
            print(f"📊 Total registros via ORM: {total}")
            
            # Listar todas as culturas via ORM
            all_cultures = CultureType.query.all()
            print(f"🌱 Culturas via ORM:")
            for culture in all_cultures:
                print(f"   ID {culture.id}: '{culture.name}' ({culture.category})")
            
            # Buscar espinafre via ORM
            espinafre = CultureType.query.filter_by(name='Espinafre').first()
            print(f"🔍 Busca 'Espinafre' via ORM: {espinafre.name if espinafre else 'Não encontrado'}")
            
            # Busca case insensitive
            espinafre2 = CultureType.query.filter(
                CultureType.name.like('%espinafre%')
            ).first()
            print(f"🔍 Busca '%espinafre%' via ORM: {espinafre2.name if espinafre2 else 'Não encontrado'}")
            
            connection.close()
            
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    testar_flask_contexto()
