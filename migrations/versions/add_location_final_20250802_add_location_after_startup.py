"""add_location_after_startup

Revision ID: add_location_final_20250802
Revises: force_location_20250802
Create Date: 2025-08-02 22:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_location_final_20250802'
down_revision = 'force_location_20250802'
branch_labels = None
depends_on = None


def upgrade():
    """
    Adicionar coluna location após startup da aplicação
    """
    print("🔧 Adicionando coluna location após startup...")
    
    try:
        # Verificar se a coluna já existe
        bind = op.get_bind()
        inspector = sa.inspect(bind)
        
        if 'users' in inspector.get_table_names():
            columns = inspector.get_columns('users')
            column_names = [col['name'] for col in columns]
            
            if 'location' not in column_names:
                # Adicionar coluna location
                op.add_column('users', sa.Column('location', sa.String(200), nullable=True))
                print("✅ Coluna 'location' adicionada com sucesso!")
                
                # Após adicionar a coluna, descomentar no modelo
                print("ℹ️  IMPORTANTE: Descomente a linha 'location' no modelo User após este deploy")
            else:
                print("✅ Coluna 'location' já existe")
        else:
            print("⚠️  Tabela 'users' não encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna location: {e}")
        
        # Tentar com SQL direto
        try:
            connection = op.get_bind()
            connection.execute(sa.text('ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR(200)'))
            print("✅ Coluna 'location' adicionada via SQL direto")
        except Exception as e2:
            print(f"❌ Falha no SQL direto: {e2}")


def downgrade():
    """
    Remover coluna location
    """
    try:
        op.drop_column('users', 'location')
        print("✅ Coluna 'location' removida")
    except Exception as e:
        print(f"❌ Erro ao remover coluna: {e}")
