"""
FORÇA MIGRAÇÃO POSTGRESQL - RAILWAY DEPLOY
Trigger para aplicar correções críticas da tabela alerts
Baseado no GUIA_MIGRACAO_POSTGRESQL_PRODUCAO.md
"""

# Este arquivo força um deploy no Railway para aplicar as migrações
# As migrações estão implementadas no run.py na função deploy()

print("🚀 FORÇANDO MIGRAÇÃO POSTGRESQL VIA RAILWAY DEPLOY")
print("📋 Migrações que serão aplicadas:")
print("   • action_text VARCHAR(100)")
print("   • action_url VARCHAR(500)")
print("   • location_data TEXT")
print("   • weather_data TEXT")
print("   • alert_metadata TEXT")
print("   • scheduled_for TIMESTAMP")
print("   • expires_at TIMESTAMP")
print("   • sent_at TIMESTAMP")
print("   • read_at TIMESTAMP")
print("   • dismissed_at TIMESTAMP")
print("   • delivery_channels VARCHAR(100) DEFAULT 'web'")
print("   • retry_count INTEGER DEFAULT 0")
print("   • last_retry_at TIMESTAMP")
print("✅ Deploy iniciado via git push")
