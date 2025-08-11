"""force_user_location_column

Revision ID: force_location_20250802
Revises: fix_user_location_20250802
Create Date: 2025-08-02 22:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'force_location_20250802'
down_revision = 'fix_user_location_20250802'
branch_labels = None
depends_on = None


def upgrade():
    """
    FORÇAR adição da coluna location na tabela users
    """
    print("🔧 FORÇANDO criação da coluna location...")
    
    try:
        # Tentar adicionar a coluna diretamente
        op.add_column('users', sa.Column('location', sa.String(200), nullable=True))
        print("✅ Coluna 'location' adicionada com sucesso")
    except Exception as e:
        print(f"⚠️  Primeira tentativa falhou: {e}")
        
        # Fallback: usar SQL direto
        try:
            connection = op.get_bind()
            connection.execute(sa.text('ALTER TABLE users ADD COLUMN location VARCHAR(200)'))
            print("✅ Coluna 'location' adicionada via SQL direto")
        except Exception as e2:
            print(f"⚠️  SQL direto falhou: {e2}")
            
            # Último recurso: verificar se já existe
            try:
                connection = op.get_bind()
                result = connection.execute(sa.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'location'
                """))
                if result.fetchone():
                    print("✅ Coluna 'location' já existe!")
                else:
                    print("❌ Coluna 'location' ainda não existe")
            except Exception as e3:
                print(f"❌ Falha na verificação: {e3}")


def downgrade():
    """
    Remover coluna location
    """
    try:
        op.drop_column('users', 'location')
        print("✅ Coluna 'location' removida")
    except Exception as e:
        print(f"❌ Erro ao remover coluna: {e}")
