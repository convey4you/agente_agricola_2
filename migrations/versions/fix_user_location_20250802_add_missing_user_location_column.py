"""add_missing_user_location_column

Revision ID: fix_user_location_20250802
Revises: railway_sync_20250802
Create Date: 2025-08-02 21:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_user_location_20250802'
down_revision = 'railway_sync_20250802'
branch_labels = None
depends_on = None


def upgrade():
    """
    Adicionar coluna location que está faltando na tabela users do Railway
    """
    print("🔧 Corrigindo coluna location faltante na tabela users...")
    
    # Verificar se a coluna já existe antes de tentar adicionar
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    try:
        # Verificar se a tabela users existe
        if 'users' in inspector.get_table_names():
            columns = inspector.get_columns('users')
            column_names = [col['name'] for col in columns]
            
            # Adicionar coluna location se não existir
            if 'location' not in column_names:
                op.add_column('users', sa.Column('location', sa.String(200), nullable=True))
                print("✅ Coluna 'location' adicionada à tabela users")
            else:
                print("✅ Coluna 'location' já existe na tabela users")
        else:
            print("⚠️ Tabela 'users' não encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao verificar/adicionar coluna location: {e}")
        # Se falhar, tentar adicionar mesmo assim (pode ser que só a verificação falhou)
        try:
            op.add_column('users', sa.Column('location', sa.String(200), nullable=True))
            print("✅ Coluna 'location' adicionada (fallback)")
        except Exception as e2:
            print(f"❌ Erro no fallback: {e2}")


def downgrade():
    """
    Remover coluna location da tabela users
    """
    print("🔧 Removendo coluna location da tabela users...")
    
    try:
        op.drop_column('users', 'location')
        print("✅ Coluna 'location' removida da tabela users")
    except Exception as e:
        print(f"❌ Erro ao remover coluna location: {e}")
