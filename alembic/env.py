from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from XR7.models.base import Base
from xr7_common.settings import settings

# Import model modules so metadata is complete for autogenerate/use.
import XR7.models.anomaly  # noqa: F401
import XR7.models.artist  # noqa: F401
import XR7.models.catalog_confirmation  # noqa: F401
import XR7.models.catalog_graph  # noqa: F401
import XR7.models.claim  # noqa: F401
import XR7.models.contract  # noqa: F401
import XR7.models.evidence_anchor  # noqa: F401
import XR7.models.event  # noqa: F401
import XR7.models.metadata_issue  # noqa: F401
import XR7.models.immutable_ledger_entry  # noqa: F401
import XR7.models.notification_preference  # noqa: F401
import XR7.models.oauth_connector  # noqa: F401
import XR7.models.parser_plugin  # noqa: F401
import XR7.models.payment  # noqa: F401
import XR7.models.recovery_intelligence  # noqa: F401
import XR7.models.statement  # noqa: F401
import XR7.models.sync_job  # noqa: F401
import XR7.models.forensic_universal_event  # noqa: F401
import XR7.models.catalog_graph_adj  # noqa: F401
import XR7.models.team_access  # noqa: F401
import XR7.models.terms_acceptance  # noqa: F401
import XR7.models.universal_royalty_event  # noqa: F401
import XR7.models.work  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
