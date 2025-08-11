#!/usr/bin/env python3
"""
Diagnóstico específico para alertas de plantio em Agosto
Usuário: francismarquesrosa@gmail.com
"""
import os
import sys
from datetime import datetime

# Carregar .env primeiro
from dotenv import load_dotenv
load_dotenv()

# Configurar ambiente
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_CONFIG'] = 'development'

# Adicionar path
sys.path.insert(0, os.path.abspath('.'))

def diagnose_planting_alerts():
    """Diagnosticar alertas de plantio para agosto"""
    
    try:
        from app import create_app, db
        from app.models.user import User
        from app.models.alerts import Alert, AlertType
        from app.services.alert_service import AlertService
        from app.services.base_conhecimento_culturas import CULTURAS_PORTUGAL
        
        print("🔍 DIAGNÓSTICO - Alertas de Plantio para Agosto")
        print("=" * 60)
        print(f"📅 Data atual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🗓️  Mês atual: Agosto (8)")
        
        # Criar aplicação
        app = create_app()
        
        with app.app_context():
            # 1. Verificar usuário
            print("\n1. VERIFICANDO USUÁRIO:")
            user = User.query.filter_by(email='francismarquesrosa@gmail.com').first()
            
            if not user:
                print("   ❌ Usuário não encontrado!")
                return False
            
            print(f"   ✅ Usuário encontrado: {user.email} (ID: {user.id})")
            
            # 2. Verificar culturas para agosto na biblioteca
            print("\n2. VERIFICANDO BIBLIOTECA DE CULTURAS:")
            culturas_agosto = []
            
            for cultura_nome, cultura_data in CULTURAS_PORTUGAL.items():
                epoca_plantio = cultura_data.get('epoca_plantio', [])
                if 'Agosto' in epoca_plantio:
                    culturas_agosto.append({
                        'nome': cultura_data.get('nome', cultura_nome.title()),
                        'categoria': cultura_data.get('categoria', ''),
                        'dificuldade': cultura_data.get('dificuldade', ''),
                        'epoca': epoca_plantio,
                        'rendimento': cultura_data.get('rendimento_m2', 0),
                        'area_minima': cultura_data.get('area_minima', 1)
                    })
            
            print(f"   📚 Culturas disponíveis para Agosto: {len(culturas_agosto)}")
            for cultura in culturas_agosto:
                print(f"      🌿 {cultura['nome']} ({cultura['categoria']}) - {cultura['dificuldade']}")
                print(f"         Época: {cultura['epoca']}")
                print(f"         Rendimento: {cultura['rendimento']} kg/m²")
            
            # 3. Verificar alertas existentes
            print("\n3. VERIFICANDO ALERTAS EXISTENTES:")
            
            # Todos os alertas de plantio do usuário
            alertas_plantio = Alert.query.filter_by(
                user_id=user.id,
                type=AlertType.PLANTING
            ).order_by(Alert.created_at.desc()).all()
            
            print(f"   📊 Total de alertas de plantio do usuário: {len(alertas_plantio)}")
            
            if alertas_plantio:
                print("   📋 Últimos alertas de plantio:")
                for alert in alertas_plantio[:3]:
                    print(f"      🔔 {alert.title}")
                    print(f"         Criado: {alert.created_at}")
                    print(f"         Status: {alert.status.value}")
                    
                    # Verificar metadados
                    if alert.alert_metadata:
                        import json
                        try:
                            metadata = json.loads(alert.alert_metadata)
                            month = metadata.get('month', 'N/A')
                            print(f"         Mês: {month}")
                        except:
                            print(f"         Metadados: {alert.alert_metadata}")
                    print()
            else:
                print("   ℹ️  Nenhum alerta de plantio encontrado")
            
            # 4. Testar geração de alertas
            print("\n4. TESTANDO GERAÇÃO DE ALERTAS:")
            
            print("   🔄 Executando AlertService.generate_planting_alerts()...")
            alert_service = AlertService()
            
            # Executar método diretamente
            novos_alertas = alert_service.generate_planting_alerts(user)
            
            print(f"   📊 Alertas gerados em memória: {len(novos_alertas)}")
            
            if novos_alertas:
                print("   📝 Detalhes dos alertas gerados:")
                for i, alert in enumerate(novos_alertas, 1):
                    print(f"      🎯 Alerta {i}:")
                    print(f"         Título: {alert.title}")
                    print(f"         Tipo: {alert.type.value}")
                    print(f"         Prioridade: {alert.priority.value}")
                    print(f"         Mensagem: {alert.message[:100]}...")
                    print(f"         Ação: {alert.action_text} → {alert.action_url}")
                    print()
                
                # Tentar salvar no banco
                print("   💾 Tentando salvar no banco...")
                try:
                    for alert in novos_alertas:
                        db.session.add(alert)
                    db.session.commit()
                    print("   ✅ Alertas salvos com sucesso!")
                except Exception as e:
                    print(f"   ❌ Erro ao salvar: {e}")
                    db.session.rollback()
            
            else:
                print("   ❌ Nenhum alerta foi gerado!")
                print("\n   🔍 INVESTIGANDO CAUSAS POSSÍVEIS:")
                
                # Verificar mês atual no código
                current_month = datetime.now().strftime('%B')
                month_mapping = {
                    'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
                    'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
                    'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
                    'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
                }
                current_month_pt = month_mapping.get(current_month, current_month)
                
                print(f"      📅 Mês detectado pelo sistema: {current_month} → {current_month_pt}")
                
                if current_month_pt != 'Agosto':
                    print("      ❌ Sistema não detectou agosto corretamente!")
                else:
                    print("      ✅ Sistema detectou agosto corretamente")
                
                # Verificar se há culturas para este mês
                found_cultures = []
                for cultura_nome, cultura_data in CULTURAS_PORTUGAL.items():
                    epoca_plantio = cultura_data.get('epoca_plantio', [])
                    if current_month_pt in epoca_plantio:
                        found_cultures.append(cultura_nome)
                
                print(f"      🌱 Culturas encontradas para {current_month_pt}: {len(found_cultures)}")
                for cultura in found_cultures[:3]:
                    print(f"         - {cultura}")
            
            # 5. Verificar configurações do usuário
            print("\n5. VERIFICANDO CONFIGURAÇÕES DO USUÁRIO:")
            
            from app.models.alerts import UserAlertPreference
            preferences = UserAlertPreference.query.filter_by(
                user_id=user.id,
                alert_type=AlertType.PLANTING
            ).first()
            
            if preferences:
                print(f"   📋 Preferências de alerta encontradas:")
                print(f"      Habilitado: {preferences.is_enabled}")
                print(f"      Prioridade mínima: {preferences.min_priority.value}")
                print(f"      Web: {preferences.web_enabled}")
                print(f"      Email: {preferences.email_enabled}")
            else:
                print("   ℹ️  Nenhuma preferência específica encontrada (usando padrões)")
            
            print("\n✅ Diagnóstico concluído!")
            return True
            
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de alertas de plantio...")
    success = diagnose_planting_alerts()
    
    if success:
        print("\n🎉 Diagnóstico executado com sucesso!")
    else:
        print("\n💥 Diagnóstico falhou!")
        sys.exit(1)
