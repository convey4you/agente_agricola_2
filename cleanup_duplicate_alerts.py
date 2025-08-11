#!/usr/bin/env python3
"""
Script para limpar alertas duplicados existentes no sistema
"""
from app import create_app, db
from app.models.alerts import Alert, AlertStatus
from datetime import datetime, timedelta
from collections import defaultdict

def cleanup_duplicate_alerts():
    """Limpar alertas duplicados existentes"""
    
    app = create_app()
    with app.app_context():
        try:
            print("🧹 Iniciando limpeza de alertas duplicados...")
            
            # Buscar todos os alertas ativos
            active_alerts = Alert.query.filter(
                Alert.status.in_([AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT])
            ).order_by(Alert.created_at.desc()).all()
            
            print(f"📊 Encontrados {len(active_alerts)} alertas ativos")
            
            # Agrupar por usuário, tipo e título
            grouped_alerts = defaultdict(list)
            for alert in active_alerts:
                key = f"{alert.user_id}:{alert.type.value}:{alert.title}"
                grouped_alerts[key].append(alert)
            
            duplicates_removed = 0
            
            for key, alerts_group in grouped_alerts.items():
                if len(alerts_group) > 1:
                    # Manter o mais recente, remover os outros
                    alerts_group.sort(key=lambda x: x.created_at, reverse=True)
                    keep_alert = alerts_group[0]
                    duplicate_alerts = alerts_group[1:]
                    
                    print(f"🔍 Encontrados {len(duplicate_alerts)} duplicados para: {keep_alert.title}")
                    
                    for dup_alert in duplicate_alerts:
                        print(f"   ❌ Removendo alerta #{dup_alert.id} (criado em {dup_alert.created_at})")
                        db.session.delete(dup_alert)
                        duplicates_removed += 1
            
            # Remover alertas muito antigos (mais de 60 dias)
            old_alerts = Alert.query.filter(
                Alert.created_at < datetime.now() - timedelta(days=60)
            ).all()
            
            print(f"🗂️ Encontrados {len(old_alerts)} alertas muito antigos (>60 dias)")
            
            for old_alert in old_alerts:
                print(f"   🗑️ Removendo alerta antigo #{old_alert.id}: {old_alert.title}")
                db.session.delete(old_alert)
            
            # Confirmar mudanças
            db.session.commit()
            
            print(f"\n✅ Limpeza concluída!")
            print(f"   🔄 Alertas duplicados removidos: {duplicates_removed}")
            print(f"   🗑️ Alertas antigos removidos: {len(old_alerts)}")
            print(f"   📈 Total removido: {duplicates_removed + len(old_alerts)}")
            
            # Mostrar estatísticas finais
            remaining_alerts = Alert.query.filter(
                Alert.status.in_([AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT])
            ).count()
            
            print(f"   📊 Alertas ativos restantes: {remaining_alerts}")
            
        except Exception as e:
            print(f"❌ Erro na limpeza: {str(e)}")
            db.session.rollback()

def show_alert_stats():
    """Mostrar estatísticas de alertas"""
    
    app = create_app()
    with app.app_context():
        try:
            print("\n📈 ESTATÍSTICAS DE ALERTAS:")
            
            # Total por status
            for status in AlertStatus:
                count = Alert.query.filter_by(status=status).count()
                print(f"   {status.value}: {count}")
            
            # Total por tipo
            from app.models.alerts import AlertType
            print("\n📊 POR TIPO:")
            for alert_type in AlertType:
                count = Alert.query.filter_by(type=alert_type).count()
                print(f"   {alert_type.value}: {count}")
            
            # Alertas por usuário
            print("\n👥 POR USUÁRIO:")
            user_stats = db.session.execute("""
                SELECT user_id, COUNT(*) as count 
                FROM alerts 
                WHERE status IN ('pending', 'active', 'sent')
                GROUP BY user_id 
                ORDER BY count DESC
            """).fetchall()
            
            for user_id, count in user_stats:
                print(f"   Usuário {user_id}: {count} alertas")
            
        except Exception as e:
            print(f"❌ Erro ao mostrar estatísticas: {str(e)}")

if __name__ == "__main__":
    print("=== LIMPEZA DE ALERTAS DUPLICADOS ===\n")
    show_alert_stats()
    cleanup_duplicate_alerts()
    show_alert_stats()
