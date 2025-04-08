# File: cd4a8b6c730b_fix_user_id_column_in_tasks.py

# Definir la revisión de esta migración
revision = 'cd4a8b6c730b'  # Este es el ID de la migración actual

# La primera migración no tiene una migración anterior, por lo que down_revision es None
down_revision = None

# Dependiendo del uso de Alembic, también puede ser necesario agregar 'branch_labels' y 'depends_on'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from alembic import context

# Usar batch mode para SQLite si estamos usando SQLite
def upgrade():
    if context.get_context().dialect.name == 'sqlite':
        from alembic import batch
        with batch.alter_table('tasks', schema=None) as batch_op:
            # Eliminar la restricción de clave foránea (si existe)
            batch_op.drop_constraint('fk_user_id')  # Asegúrate de que el nombre de la restricción sea correcto
            # Añadir la columna 'user_id' si no existe
            batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))

def downgrade():
    if context.get_context().dialect.name == 'sqlite':
        from alembic import batch
        with batch.alter_table('tasks', schema=None) as batch_op:
            # Eliminar la columna 'user_id'
            batch_op.drop_column('user_id')
            # Si es necesario, restaurar la clave foránea (esto puede ser necesario si había una antes)
            batch_op.create_foreign_key('fk_user_id', 'tasks', 'users', ['user_id'], ['id'])
