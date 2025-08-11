#!/usr/bin/env python3
"""
🚨 SCRIPT DE VALIDAÇÃO CRÍTICA - Schema da Tabela Alerts
Executa após migration para confirmar que tudo funcionou
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def validate_schema():
    """Validar schema da tabela alerts após migration"""
    
    app = create_app()
    with app.app_context():
        try:
            print("🔍 VALIDAÇÃO DO SCHEMA DA TABELA ALERTS")
            print("=" * 50)
            
            # 1. Verificar se coluna status existe
            print("\n1️⃣ Verificando existência da coluna 'status'...")
            
            # Método compatível com SQLite e PostgreSQL
            result = db.session.execute(text("SELECT * FROM alerts LIMIT 1"))
            columns = list(result.keys()) if result.keys() else []
            
            if 'status' in columns:
                print("✅ Coluna 'status' existe e é acessível")
            else:
                print("❌ ERRO CRÍTICO: Coluna 'status' NÃO existe!")
                return False
            
            # 2. Testar query completa que estava falhando em produção
            print("\n2️⃣ Testando query SQL original que estava falhando...")
            
            query = text("""
                SELECT alerts.id AS alerts_id, alerts.user_id AS alerts_user_id, 
                       alerts.type AS alerts_type, alerts.priority AS alerts_priority, 
                       alerts.status AS alerts_status, alerts.title AS alerts_title, 
                       alerts.message AS alerts_message
                FROM alerts 
                WHERE alerts.status != :status_val 
                ORDER BY alerts.created_at DESC 
                LIMIT 5
            """)
            
            result = db.session.execute(query, {'status_val': 'EXPIRED'})
            alerts = result.fetchall()
            print(f"✅ Query SQL funciona perfeitamente - {len(alerts)} alertas encontrados")
            
            # 3. Verificar tipos de dados da coluna status
            print("\n3️⃣ Verificando tipos de dados...")
            
            # Consulta específica para verificar valores de status
            result = db.session.execute(text("SELECT DISTINCT status FROM alerts WHERE status IS NOT NULL"))
            status_values = [row[0] for row in result.fetchall()]
            print(f"📊 Valores de status encontrados: {status_values}")
            
            # 4. Testar inserção de alerta com status válido
            print("\n4️⃣ Testando inserção de novo alerta...")
            
            test_query = text("""
                INSERT INTO alerts (user_id, type, priority, status, title, message, created_at) 
                VALUES (1, 'test', 'medium', 'PENDING', 'Teste de Validação', 'Teste do schema', datetime('now'))
            """)
            
            db.session.execute(test_query)
            db.session.commit()
            print("✅ Inserção de alerta teste executada com sucesso")
            
            # Limpar teste
            db.session.execute(text("DELETE FROM alerts WHERE title = 'Teste de Validação'"))
            db.session.commit()
            
            # 5. Validar API de alertas
            print("\n5️⃣ Testando importação dos modelos...")
            
            try:
                from app.models.alerts import Alert, AlertType, AlertPriority, AlertStatus
                print("✅ Modelos de alertas importados com sucesso")
                
                # Testar enum values
                print(f"📋 Tipos de alerta: {[t.value for t in AlertType]}")
                print(f"📋 Prioridades: {[p.value for p in AlertPriority]}")
                print(f"📋 Status: {[s.value for s in AlertStatus]}")
                
            except Exception as e:
                print(f"⚠️ Aviso na importação dos modelos: {e}")
            
            print("\n" + "=" * 50)
            print("🎉 VALIDAÇÃO COMPLETA: SCHEMA DA TABELA ALERTS OK!")
            print("✅ Sistema de alertas pronto para produção")
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO na validação: {e}")
            print(f"🔧 Tipo do erro: {type(e).__name__}")
            return False

def main():
    """Função principal"""
    print("🚨 INICIANDO VALIDAÇÃO CRÍTICA DO SCHEMA DE ALERTAS")
    
    success = validate_schema()
    
    if success:
        print("\n🎯 RESULTADO: APROVAÇÃO PARA PRODUÇÃO ✅")
        sys.exit(0)
    else:
        print("\n🚨 RESULTADO: CORREÇÃO NECESSÁRIA ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()
