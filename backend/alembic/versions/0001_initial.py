"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-10-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Создаем ENUM-типы (используем checkfirst=True, чтобы избежать ошибки, если они уже есть)
    sport_enum = postgresql.ENUM('RUN', 'BIKE', 'WORKOUT', name='sport')
    sport_enum.create(op.get_bind(), checkfirst=True)
    
    weather_source_enum = postgresql.ENUM('FORECAST', 'AIR_QUALITY', name='weathersource')
    weather_source_enum.create(op.get_bind(), checkfirst=True)
    
    subscription_status_enum = postgresql.ENUM('ACTIVE', 'NOTIFIED', 'CANCELLED', name='subscriptionstatus')
    subscription_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Таблица users
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('sport_prefs', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('temp_min', sa.Float(), nullable=True),
        sa.Column('temp_max', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 3. Таблица workouts
    op.create_table('workouts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sport', sport_enum, nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_min', sa.Integer(), nullable=False),
        sa.Column('weather_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Таблица plans
    op.create_table('plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('degraded', sa.Boolean(), nullable=False),
        sa.Column('degraded_reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Таблица subscriptions
    op.create_table('subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('window_index', sa.Integer(), nullable=False),
        sa.Column('window_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('window_end', sa.DateTime(timezone=True
