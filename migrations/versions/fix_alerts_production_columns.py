"""Fix alerts production columns - Add missing columns

Revision ID: fix_alerts_production_columns
Revises: railway_sync_20250802_sync_local_to_railway
Create Date: 2025-08-06 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_alerts_production_columns'
down_revision = 'railway_sync_20250802'
branch_labels = None
depends_on = None


def upgrade():
    """
    Adicionar colunas que estão faltando na tabela alerts em produção
    Esta migration é segura para executar tanto em desenvolvimento quanto produção
    """
    
    # Verificar se as colunas já existem (para evitar erro)
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    try:
        # Obter colunas existentes da tabela alerts
        existing_columns = [col['name'] for col in inspector.get_columns('alerts')]
        
        columns_to_add = {
            'action_text': sa.Column('action_text', sa.String(100), nullable=True),
            'action_url': sa.Column('action_url', sa.String(500), nullable=True),
            'location_data': sa.Column('location_data', sa.Text(), nullable=True),
            'weather_data': sa.Column('weather_data', sa.Text(), nullable=True),
            'alert_metadata': sa.Column('alert_metadata', sa.Text(), nullable=True),
            'scheduled_for': sa.Column('scheduled_for', sa.DateTime(), nullable=True),
            'expires_at': sa.Column('expires_at', sa.DateTime(), nullable=True),
            'sent_at': sa.Column('sent_at', sa.DateTime(), nullable=True),
            'delivery_channels': sa.Column('delivery_channels', sa.String(100), nullable=True, server_default='web'),
            'retry_count': sa.Column('retry_count', sa.Integer(), nullable=True, server_default='0'),
            'last_retry_at': sa.Column('last_retry_at', sa.DateTime(), nullable=True),
        }
        
        added_columns = []
        
        for column_name, column_def in columns_to_add.items():
            if column_name not in existing_columns:
                op.add_column('alerts', column_def)
                added_columns.append(column_name)
                print(f"✅ Coluna '{column_name}' adicionada à tabela alerts")
            else:
                print(f"ℹ️ Coluna '{column_name}' já existe na tabela alerts")
        
        # Criar índices para performance em algumas colunas importantes
        try:
            if 'scheduled_for' in added_columns:
                op.create_index('ix_alerts_scheduled_for', 'alerts', ['scheduled_for'])
                print("✅ Índice ix_alerts_scheduled_for criado")
        except Exception as e:
            print(f"⚠️ Erro ao criar índice ix_alerts_scheduled_for: {e}")
            
        try:
            if 'expires_at' in added_columns:
                op.create_index('ix_alerts_expires_at', 'alerts', ['expires_at'])
                print("✅ Índice ix_alerts_expires_at criado")
        except Exception as e:
            print(f"⚠️ Erro ao criar índice ix_alerts_expires_at: {e}")
        
        if added_columns:
            print(f"✅ Migration concluída - {len(added_columns)} colunas adicionadas: {', '.join(added_columns)}")
        else:
            print("ℹ️ Todas as colunas já existem - nenhuma alteração necessária")
            
    except Exception as e:
        print(f"❌ Erro durante a migration: {e}")
        raise


def downgrade():
    """
    Remover colunas adicionadas desta migration
    """
    
    columns_to_remove = [
        'action_text', 'action_url', 'location_data', 'weather_data', 
        'alert_metadata', 'scheduled_for', 'expires_at', 'sent_at',
        'delivery_channels', 'retry_count', 'last_retry_at'
    ]
    
    # Verificar se as colunas existem antes de tentar removê-las
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    try:
        existing_columns = [col['name'] for col in inspector.get_columns('alerts')]
        
        # Remover índices
        for index_name in ['ix_alerts_scheduled_for', 'ix_alerts_expires_at']:
            try:
                op.drop_index(index_name, table_name='alerts')
                print(f"✅ Índice {index_name} removido")
            except:
                print(f"ℹ️ Índice {index_name} não existe ou já foi removido")
        
        removed_columns = []
        
        for column_name in columns_to_remove:
            if column_name in existing_columns:
                op.drop_column('alerts', column_name)
                removed_columns.append(column_name)
                print(f"✅ Coluna '{column_name}' removida da tabela alerts")
            else:
                print(f"ℹ️ Coluna '{column_name}' não existe na tabela alerts")
        
        if removed_columns:
            print(f"✅ Rollback concluído - {len(removed_columns)} colunas removidas: {', '.join(removed_columns)}")
        else:
            print("ℹ️ Nenhuma coluna foi removida")
            
    except Exception as e:
        print(f"❌ Erro durante rollback: {e}")
        raise
