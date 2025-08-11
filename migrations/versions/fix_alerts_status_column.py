"""Add status column to alerts table - Production Sync

Revision ID: fix_alerts_status_column
Revises: d513ecc655f9
Create Date: 2025-08-01 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_alerts_status_column'
down_revision = 'd513ecc655f9'
branch_labels = None
depends_on = None


def upgrade():
    """
    Adicionar coluna status na tabela alerts para sincronizar com produção
    Esta migration é segura para executar tanto em desenvolvimento quanto produção
    """
    
    # Verificar se a coluna já existe (para evitar erro em desenvolvimento)
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    # Obter colunas existentes da tabela alerts
    existing_columns = [col['name'] for col in inspector.get_columns('alerts')]
    
    if 'status' not in existing_columns:
        # Adicionar coluna status apenas se não existir
        op.add_column('alerts', sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'))
        
        # Criar index para performance
        op.create_index('ix_alerts_status', 'alerts', ['status'])
        
        # Adicionar constraint para valores válidos (PostgreSQL compatible)
        op.execute("ALTER TABLE alerts ADD CONSTRAINT check_alert_status CHECK (status IN ('PENDING', 'SENT', 'READ', 'DISMISSED', 'EXPIRED'))")
        
        print("✅ Coluna 'status' adicionada com sucesso à tabela alerts")
    else:
        print("ℹ️ Coluna 'status' já existe na tabela alerts - nenhuma alteração necessária")


def downgrade():
    """
    Remover coluna status da tabela alerts
    """
    # Verificar se a coluna existe antes de tentar removê-la
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    existing_columns = [col['name'] for col in inspector.get_columns('alerts')]
    
    if 'status' in existing_columns:
        # Remover constraint se existir
        try:
            op.execute("ALTER TABLE alerts DROP CONSTRAINT IF EXISTS check_alert_status")
        except:
            pass  # Ignorar se constraint não existir
        
        # Remover index se existir
        try:
            op.drop_index('ix_alerts_status', table_name='alerts')
        except:
            pass  # Ignorar se index não existir
        
        # Remover coluna
        op.drop_column('alerts', 'status')
        
        print("✅ Coluna 'status' removida da tabela alerts")
    else:
        print("ℹ️ Coluna 'status' não existe na tabela alerts - nenhuma alteração necessária")
