"""Migration para sincronizacao com Railway - 02/08/2025

Revision ID: railway_sync_20250802
Revises: fix_alerts_status_column
Create Date: 2025-08-02 21:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'railway_sync_20250802'
down_revision = 'fix_alerts_status_column'
branch_labels = None
depends_on = None


def upgrade():
    """
    Migration de sincronização para Railway
    
    Este migration garante que a estrutura do banco no Railway 
    esteja sincronizada com o desenvolvimento local.
    
    Como o banco local já está atualizado, este migration 
    não faz alterações estruturais, apenas marca o ponto 
    de sincronização.
    """
    # Verificar se tabelas essenciais existem
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    expected_tables = [
        'users', 'farms', 'cultures', 'culture_types', 
        'activities', 'alerts', 'alert_rules', 
        'user_alert_preferences', 'marketplace_items',
        'conversations', 'messages'
    ]
    
    # Verificar se todas as tabelas essenciais existem
    missing_tables = [table for table in expected_tables if table not in existing_tables]
    
    if missing_tables:
        print(f"⚠️ Tabelas faltando: {missing_tables}")
        print("Este migration não criará tabelas - use db.create_all() primeiro")
    else:
        print("✅ Todas as tabelas essenciais estão presentes")
        print("✅ Sincronização com Railway completa")


def downgrade():
    """
    Não há downgrade para este migration de sincronização
    """
    print("ℹ️ Este é um migration de sincronização - não há downgrade")
    pass
