#!/usr/bin/env python3
"""
Validação final: Verificar que a tabela user_alert_preferences está sendo atualizada
"""
from app import create_app, db
from app.models.user import User
from app.models.alerts import UserAlertPreference, AlertType
from app.models.farm import Farm
import sqlite3

def validate_complete_system():
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(email='msmaia.pt@gmail.com').first()
        if not user:
            print("❌ Usuário não encontrado")
            return
        
        print("🎯 VALIDAÇÃO FINAL DO SISTEMA")
        print("=" * 50)
        
        # 1. Dados do usuário
        print(f"👤 Usuário: {user.email}")
        print(f"📝 Nome: {user.nome_completo}")
        print(f"📞 Telefone: {user.telefone}")
        print(f"🏙️ Cidade: {user.cidade}")
        print(f"📍 Coordenadas: {user.latitude}, {user.longitude}")
        print(f"🎯 Onboarding: {'✅ Completo' if user.onboarding_completed else '❌ Incompleto'}")
        print(f"⭐ Experiência: {getattr(user, 'experience_level', 'não definido')}")
        
        # 2. Fazendas
        farms = Farm.query.filter_by(user_id=user.id).all()
        print(f"\n🏡 FAZENDAS ({len(farms)}):")
        for farm in farms:
            print(f"   - {farm.name} em {farm.city or farm.address}")
            print(f"     Área: {farm.area_total}ha")
            print(f"     Descrição: {farm.description}")
            print(f"     Coordenadas: {farm.latitude}, {farm.longitude}")
        
        # 3. Preferências de alerta
        preferences = UserAlertPreference.query.filter_by(user_id=user.id).all()
        print(f"\n🔔 PREFERÊNCIAS DE ALERTA ({len(preferences)}):")
        
        if preferences:
            for pref in preferences:
                channels = []
                if pref.web_enabled: channels.append("Web")
                if pref.email_enabled: channels.append("Email")
                if pref.sms_enabled: channels.append("SMS")
                
                status = "✅ Ativo" if pref.is_enabled else "❌ Inativo"
                print(f"   - {pref.alert_type.value.title()}: {status}")
                print(f"     Canais: {', '.join(channels) if channels else 'Nenhum'}")
                print(f"     Prioridade mín: {pref.min_priority.value}")
                if pref.quiet_hours_start and pref.quiet_hours_end:
                    print(f"     Silêncio: {pref.quiet_hours_start} - {pref.quiet_hours_end}")
        else:
            print("   ❌ Nenhuma preferência configurada")
        
        # 4. Verificação direta no banco
        print(f"\n💾 VERIFICAÇÃO DIRETA NO BANCO:")
        try:
            conn = sqlite3.connect('instance/agente_agricola.db')
            cursor = conn.cursor()
            
            # Contar registros por tabela
            tables_to_check = [
                ('users', f"email = '{user.email}'"),
                ('farms', f"user_id = {user.id}"),
                ('user_alert_preferences', f"user_id = {user.id}")
            ]
            
            for table, condition in tables_to_check:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {condition}")
                count = cursor.fetchone()[0]
                print(f"   - {table}: {count} registros")
            
            # Detalhes das preferências
            cursor.execute(f"""
                SELECT alert_type, is_enabled, web_enabled, email_enabled, sms_enabled, min_priority
                FROM user_alert_preferences 
                WHERE user_id = {user.id}
                ORDER BY alert_type
            """)
            
            pref_details = cursor.fetchall()
            if pref_details:
                print(f"\n   📋 Detalhes das preferências:")
                for detail in pref_details:
                    alert_type, enabled, web, email, sms, priority = detail
                    print(f"      {alert_type}: {enabled} (W:{web}, E:{email}, S:{sms}, P:{priority})")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Erro ao verificar banco: {e}")
        
        print(f"\n✅ VALIDAÇÃO CONCLUÍDA")
        print("=" * 50)
        
        # Resumo final
        success_count = 0
        total_checks = 4
        
        if user.onboarding_completed:
            success_count += 1
            print("✅ Onboarding completo")
        else:
            print("❌ Onboarding incompleto")
        
        if farms:
            success_count += 1
            print("✅ Fazenda(s) criada(s)")
        else:
            print("❌ Nenhuma fazenda criada")
        
        if preferences and len(preferences) >= 9:
            success_count += 1
            print("✅ Preferências de alerta configuradas")
        else:
            print("❌ Preferências de alerta incompletas")
        
        if user.latitude and user.longitude:
            success_count += 1
            print("✅ Coordenadas geográficas salvas")
        else:
            print("❌ Coordenadas não salvas")
        
        print(f"\n🎯 RESULTADO: {success_count}/{total_checks} verificações aprovadas")
        
        if success_count == total_checks:
            print("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        else:
            print("⚠️ Sistema precisa de ajustes")

if __name__ == "__main__":
    validate_complete_system()
