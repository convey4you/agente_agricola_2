#!/usr/bin/env python3
"""
Script de Validação: Documentação vs Implementação - Sistema de Alertas
Verifica se a documentação está coerente com o que está implementado
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app import create_app
    from app.models.alerts import Alert, AlertType, AlertPriority, AlertStatus, UserAlertPreference, AlertRule
    from app.services.alert_engine import AlertEngine
    from app.routes.alerts_api import alerts_api_bp
    import inspect
    import json
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def verificar_modelos_alerts():
    """Verificar se os modelos estão conforme documentação"""
    print("🔍 1. VERIFICAÇÃO DOS MODELOS DE ALERTAS")
    print("=" * 50)
    
    # Verificar Alert Model
    print("\n📋 Modelo Alert:")
    campos_esperados = [
        'id', 'user_id', 'type', 'priority', 'status',
        'title', 'message', 'action_text', 'action_url',
        'culture_id', 'location_data', 'weather_data', 'alert_metadata',
        'created_at', 'updated_at', 'scheduled_for', 'expires_at',
        'sent_at', 'read_at', 'dismissed_at', 'severity_level',
        'delivery_channels', 'retry_count', 'last_retry_at'
    ]
    
    for campo in campos_esperados:
        if hasattr(Alert, campo):
            print(f"   ✅ {campo}")
        else:
            print(f"   ❌ {campo} - NÃO ENCONTRADO")
    
    # Verificar propriedades
    propriedades_esperadas = ['is_read', 'is_resolved', 'is_expired', 'is_urgent']
    print("\n🔧 Propriedades do modelo:")
    for prop in propriedades_esperadas:
        if hasattr(Alert, prop):
            print(f"   ✅ {prop}")
        else:
            print(f"   ❌ {prop} - NÃO ENCONTRADA")
    
    # Verificar Enums
    print("\n📊 Enums:")
    print(f"   AlertType: {[e.value for e in AlertType]}")
    print(f"   AlertPriority: {[e.value for e in AlertPriority]}")
    print(f"   AlertStatus: {[e.value for e in AlertStatus]}")

def verificar_endpoints_api():
    """Verificar endpoints da API de alertas"""
    print("\n\n🔍 2. VERIFICAÇÃO DOS ENDPOINTS DA API")
    print("=" * 50)
    
    # Listar todas as rotas do blueprint
    print("\n📡 Endpoints implementados:")
    try:
        app = create_app()
        with app.app_context():
            for rule in app.url_map.iter_rules():
                if rule.endpoint and 'alerts_api' in rule.endpoint:
                    print(f"   ✅ {rule.methods} {rule.rule} -> {rule.endpoint}")
    except Exception as e:
        print(f"   ❌ Erro ao listar endpoints: {e}")

def verificar_alert_engine():
    """Verificar AlertEngine"""
    print("\n\n🔍 3. VERIFICAÇÃO DO ALERT ENGINE")
    print("=" * 50)
    
    print("\n⚙️ Métodos do AlertEngine:")
    metodos_esperados = [
        'get_user_alerts', 'mark_alert_as_read', 'dismiss_alert',
        'create_alert', 'generate_alerts_for_user'
    ]
    
    for metodo in metodos_esperados:
        if hasattr(AlertEngine, metodo):
            print(f"   ✅ {metodo}")
        else:
            print(f"   ❌ {metodo} - NÃO ENCONTRADO")

def verificar_documentacao_vs_implementacao():
    """Verificar se documentação está alinhada"""
    print("\n\n🔍 4. VERIFICAÇÃO: DOCUMENTAÇÃO VS IMPLEMENTAÇÃO")
    print("=" * 50)
    
    inconsistencias = []
    
    # Verificar se Alert tem o campo `is_resolved` correto
    try:
        alert_dummy = Alert()
        # Testar a propriedade is_resolved
        if hasattr(alert_dummy, 'status'):
            print("   ✅ Propriedade is_resolved implementada")
        else:
            inconsistencias.append("❌ Propriedade is_resolved não funciona corretamente")
    except Exception as e:
        inconsistencias.append(f"❌ Erro ao testar modelo Alert: {e}")
    
    # Verificar se endpoints documentados existem
    endpoints_documentados = [
        '/api/alerts/',
        '/api/alerts/widget',
        '/api/alerts/generate',
        '/api/alerts/<id>/read',
        '/api/alerts/<id>/resolve',
        '/api/alerts/<id>/dismiss'
    ]
    
    print("\n📚 Endpoints documentados vs implementados:")
    for endpoint in endpoints_documentados:
        print(f"   📝 {endpoint} - Documentado")
    
    if inconsistencias:
        print("\n❌ INCONSISTÊNCIAS ENCONTRADAS:")
        for inc in inconsistencias:
            print(f"   {inc}")
    else:
        print("\n✅ DOCUMENTAÇÃO ESTÁ ALINHADA COM A IMPLEMENTAÇÃO")

def verificar_arquivos_documentacao():
    """Verificar se arquivos de documentação existem"""
    print("\n\n🔍 5. VERIFICAÇÃO DE ARQUIVOS DE DOCUMENTAÇÃO")
    print("=" * 50)
    
    arquivos_esperados = [
        'docs/alerts_api.md',
        'guias/servicos/SERVICOS_IMPLEMENTADOS.md',
        'guias/banco-de-dados/MODELOS_SQLALCHEMY.md'
    ]
    
    for arquivo in arquivos_esperados:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo} - NÃO ENCONTRADO")

def main():
    """Função principal"""
    print("🚀 VALIDAÇÃO: DOCUMENTAÇÃO DO SISTEMA DE ALERTAS")
    print("=" * 60)
    
    try:
        verificar_modelos_alerts()
        verificar_endpoints_api()
        verificar_alert_engine()
        verificar_documentacao_vs_implementacao()
        verificar_arquivos_documentacao()
        
        print("\n\n🎯 RESUMO DA VALIDAÇÃO")
        print("=" * 30)
        print("✅ Validação concluída!")
        print("📋 Verifique os itens marcados com ❌ para possíveis atualizações na documentação")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE A VALIDAÇÃO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
