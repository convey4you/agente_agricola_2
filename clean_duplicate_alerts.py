#!/usr/bin/env python3
"""
Script para limpar alertas duplicados existentes no sistema
"""
from app import create_app, db
from app.models.alerts import Alert, AlertStatus
from sqlalchemy import func
from datetime import datetime

def clean_duplicate_alerts():
    """Remove alertas duplicados do sistema"""
    
    app = create_app()
    with app.app_context():
        try:
            print("🧹 Iniciando limpeza de alertas duplicados...")
            
            # Buscar alertas duplicados por usuário, tipo e cultura
            duplicates_query = db.session.query(
                Alert.user_id,
                Alert.type,
                Alert.culture_id,
                Alert.title,
                func.count(Alert.id).label('count')
            ).filter(
                Alert.status.in_([AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT])
            ).group_by(
                Alert.user_id,
                Alert.type,
                Alert.culture_id,
                Alert.title
            ).having(
                func.count(Alert.id) > 1
            ).all()
            
            total_removed = 0
            
            for duplicate in duplicates_query:
                print(f"📋 Encontrados {duplicate.count} alertas duplicados:")
                print(f"   Usuário: {duplicate.user_id}")
                print(f"   Tipo: {duplicate.type}")
                print(f"   Cultura: {duplicate.culture_id}")
                print(f"   Título: {duplicate.title}")
                
                # Buscar todos os alertas duplicados
                duplicate_alerts = Alert.query.filter_by(
                    user_id=duplicate.user_id,
                    type=duplicate.type,
                    culture_id=duplicate.culture_id,
                    title=duplicate.title
                ).filter(
                    Alert.status.in_([AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT])
                ).order_by(Alert.created_at.desc()).all()
                
                if len(duplicate_alerts) > 1:
                    # Manter apenas o mais recente
                    to_keep = duplicate_alerts[0]
                    to_remove = duplicate_alerts[1:]
                    
                    print(f"   ✅ Mantendo alerta ID {to_keep.id} (mais recente)")
                    
                    for alert in to_remove:
                        print(f"   🗑️ Removendo alerta ID {alert.id}")
                        db.session.delete(alert)
                        total_removed += 1
            
            # Buscar alertas muito antigos de irrigação (mais de 7 dias)
            old_irrigation_alerts = Alert.query.filter_by(
                type='irrigation'
            ).filter(
                Alert.created_at < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                Alert.status.in_([AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT])
            ).all()
            
            if old_irrigation_alerts:
                print(f"🗓️ Removendo {len(old_irrigation_alerts)} alertas de irrigação antigos...")
                for alert in old_irrigation_alerts:
                    alert.status = AlertStatus.EXPIRED
                    total_removed += 1
            
            db.session.commit()
            
            print(f"✅ Limpeza concluída!")
            print(f"📊 Total de alertas processados: {total_removed}")
            
            # Mostrar estatísticas finais
            remaining_alerts = Alert.query.filter(
                Alert.status.in_([AlertStatus.PENDING, AlertStatus.ACTIVE, AlertStatus.SENT])
            ).count()
            
            print(f"📈 Alertas ativos restantes: {remaining_alerts}")
            
        except Exception as e:
            print(f"❌ Erro na limpeza: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    clean_duplicate_alerts()
