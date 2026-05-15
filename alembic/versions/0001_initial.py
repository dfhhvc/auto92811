"""Initial migration — create all tables.

Revision ID: 0001
Revises:
Create Date: 2026-05-15 22:45:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── opportunities ─────────────────────────────────────────────
    op.create_table(
        "opportunities",
        sa.Column("id", sa.String(32), primary_key=True, index=True),
        sa.Column("title", sa.String(256), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("time_investment", sa.String(64), nullable=False),
        sa.Column("expected_income", sa.String(128), nullable=False),
        sa.Column("source", sa.String(128), nullable=False, index=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("verified", sa.Integer(), default=0),
        sa.Column("warning", sa.Text(), nullable=True),
        sa.Column("tags", sa.JSON(), default=list),
        sa.Column("score_total", sa.Float(), nullable=False, index=True),
        sa.Column("score_feasibility", sa.Float(), default=0.0),
        sa.Column("score_timeliness", sa.Float(), default=0.0),
        sa.Column("score_credibility", sa.Float(), default=0.0),
        sa.Column("score_roi", sa.Float(), default=0.0),
        sa.Column("score_replicability", sa.Float(), default=0.0),
        sa.Column("match_score", sa.Float(), nullable=True),
        sa.Column("merge_count", sa.Integer(), default=1),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), default=sa.func.now()),
    )

    # ── users ─────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.String(32), primary_key=True, index=True),
        sa.Column("email", sa.String(256), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("skills", sa.JSON(), default=list),
        sa.Column("time_budget", sa.String(16), default="2h"),
        sa.Column("risk_level", sa.String(16), default="moderate"),
        sa.Column("languages", sa.JSON(), default=lambda: ["zh"]),
        sa.Column("is_active", sa.Integer(), default=1),
        sa.Column("is_admin", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(), nullable=True),
    )

    # ── scan_logs ─────────────────────────────────────────────────
    op.create_table(
        "scan_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("raw_count", sa.Integer(), default=0),
        sa.Column("unique_count", sa.Integer(), default=0),
        sa.Column("merged_count", sa.Integer(), default=0),
        sa.Column("valid_count", sa.Integer(), default=0),
        sa.Column("recommended_count", sa.Integer(), default=0),
        sa.Column("elapsed_seconds", sa.Float(), default=0.0),
        sa.Column("status", sa.String(32), default="success"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
    )

    # ── token_blacklist ───────────────────────────────────────────
    op.create_table(
        "token_blacklist",
        sa.Column("jti", sa.String(32), primary_key=True, index=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
    )

    # ── security_audit_logs ───────────────────────────────────────
    op.create_table(
        "security_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_type", sa.String(64), nullable=False, index=True),
        sa.Column("user_id", sa.String(32), nullable=True, index=True),
        sa.Column("client_ip", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("success", sa.Integer(), default=1),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
    )

    # ── community_votes ───────────────────────────────────────────
    op.create_table(
        "community_votes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("opportunity_id", sa.String(32), nullable=False, index=True),
        sa.Column("user_id", sa.String(32), nullable=False, index=True),
        sa.Column("vote", sa.Integer(), nullable=False),  # 1=up, -1=down
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
    )

    # ── income_records ────────────────────────────────────────────
    op.create_table(
        "income_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(32), nullable=False, index=True),
        sa.Column("opportunity_id", sa.String(32), nullable=False, index=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(8), default="CNY"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), default=sa.func.now()),
    )

    # ── spider_status ─────────────────────────────────────────────
    op.create_table(
        "spider_status",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("spider_name", sa.String(64), nullable=False, index=True),
        sa.Column("status", sa.String(32), default="idle"),
        sa.Column("last_run", sa.DateTime(), nullable=True),
        sa.Column("last_success", sa.DateTime(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("total_runs", sa.Integer(), default=0),
        sa.Column("success_count", sa.Integer(), default=0),
        sa.Column("error_count", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime(), default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("spider_status")
    op.drop_table("income_records")
    op.drop_table("community_votes")
    op.drop_table("security_audit_logs")
    op.drop_table("token_blacklist")
    op.drop_table("scan_logs")
    op.drop_table("users")
    op.drop_table("opportunities")