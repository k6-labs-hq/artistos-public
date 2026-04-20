"""Add Invoice FeatureFlag PartnerAPIKey SloMetric TenantCostLedger for Sprint 6

Revision ID: e97a0aed10b5
Revises: fbec60e49504
Create Date: 2026-04-20 10:07:57.273211
"""
from alembic import op
import sqlalchemy as sa


revision = 'e97a0aed10b5'
down_revision = 'fbec60e49504'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('claim_id', sa.String(), nullable=False),
        sa.Column('artist_id', sa.String(), nullable=False),
        sa.Column('recovered_amount', sa.Float(), nullable=False),
        sa.Column('contingency_fee', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False, server_default='USD'),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('claim_id', name='uq_invoice_claim_id')
    )
    op.create_index(op.f('ix_invoices_artist_id'), 'invoices', ['artist_id'])
    op.create_index(op.f('ix_invoices_status'), 'invoices', ['status'])
    
    # Create feature_flags table
    op.create_table(
        'feature_flags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('rollout_percentage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('target_user_ids', sa.Text(), nullable=True),
        sa.Column('conditions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key', name='uq_feature_flag_key')
    )
    
    # Create partner_api_keys table
    op.create_table(
        'partner_api_keys',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('partner_id', sa.String(), nullable=False),
        sa.Column('key_hash', sa.String(), nullable=False),
        sa.Column('key_prefix', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('scopes', sa.Text(), nullable=True),
        sa.Column('tier', sa.String(), nullable=False, server_default='sandbox'),
        sa.Column('rate_limit_per_hour', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_partner_api_keys_partner_id'), 'partner_api_keys', ['partner_id'])
    op.create_index(op.f('ix_partner_api_keys_key_prefix'), 'partner_api_keys', ['key_prefix'])
    
    # Create slo_metrics table
    op.create_table(
        'slo_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('metric_name', sa.String(), nullable=True),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create tenant_cost_ledger table  
    op.create_table(
        'tenant_cost_ledger',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('cost_usd', sa.Float(), nullable=False),
        sa.Column('cost_type', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('cost_metadata', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenant_cost_ledger_tenant_id'), 'tenant_cost_ledger', ['tenant_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_tenant_cost_ledger_tenant_id'), table_name='tenant_cost_ledger')
    op.drop_table('tenant_cost_ledger')
    op.drop_table('slo_metrics')
    op.drop_index(op.f('ix_partner_api_keys_key_prefix'), table_name='partner_api_keys')
    op.drop_index(op.f('ix_partner_api_keys_partner_id'), table_name='partner_api_keys')
    op.drop_table('partner_api_keys')
    op.drop_table('feature_flags')
    op.drop_index(op.f('ix_invoices_status'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_artist_id'), table_name='invoices')
    op.drop_table('invoices')
