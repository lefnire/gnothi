"""groups_init

Revision ID: a30a10eb8528
Revises: 
Create Date: 2021-03-26 19:04:10.477286

"""
import pdb
from alembic import op, context
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils.types.encrypted.encrypted_type import StringEncryptedType, FernetEngine
from common.database import Base
import common.models as M

# revision identifiers, used by Alembic.
revision = 'a30a10eb8528'
down_revision = None
branch_labels = None
depends_on = None

# TODO setup the seed-data script for new devs, and skip alembic versions


def migrate_users(bind, sess):
    bind.execute(f"""
    insert into auth_old (id, email, hashed_password, updated_at)
    select id, email, hashed_password, updated_at from users;
    """)

    op.add_column('users', sa.Column('cognito_id', sa.Unicode(), nullable=True))
    op.add_column('users', sa.Column('username', sa.Unicode(), nullable=True))
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'hashed_password')
    op.create_index(op.f('ix_users_cognito_id'), 'users', ['cognito_id'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    # op.alter_column('users', 'is_superuser', existing_type=sa.BOOLEAN(), nullable=True)
    
    
def migrate_shares(bind, sess):
    op.add_column('shares', sa.Column('bio', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('shares', sa.Column('birthday', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('shares', sa.Column('first_name', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('shares', sa.Column('gender', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('shares', sa.Column('last_name', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('shares', sa.Column('orientation', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('shares', sa.Column('timezone', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('shares', sa.Column('username', sa.Boolean(), server_default='true', nullable=True))

    bind.execute(f"""
    with users_ as (
        select u.id as obj_id, s.*  
        from users u 
        inner join shares s 
            on lower(s.email)=lower(u.email)
    )
    insert into users_shares (share_id, user_id, obj_id)
    select users_.id, users_.user_id, users_.obj_id from users_
    """)
    
    op.drop_index('ix_shares_email', table_name='shares')
    op.drop_index('ix_shares_last_seen', table_name='shares')
    op.drop_column('shares', 'email')
    op.drop_column('shares', 'last_seen')
    op.drop_column('shares', 'new_entries')
    op.drop_column('shares', 'profile')
    


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    Base.metadata.create_all(bind=bind)
    
    migrate_users(bind, session)
    migrate_shares(bind, session)

    op.drop_table('profile_matches')
    op.add_column('jobs', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'jobs', 'users', ['user_id'], ['id'], ondelete='cascade')



def downgrade():
    pass
