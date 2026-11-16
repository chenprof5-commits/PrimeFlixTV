from logging.config import fileConfig
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from app import Base, normalize_database_url

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
database_url = os.environ.get("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
# Vercel/Neon provide standard postgresql:// URLs, while this app installs
# psycopg v3 (not psycopg2). Escape '%' for ConfigParser URLs containing
# percent-encoded credentials before passing the URL to Alembic.
database_url = normalize_database_url(database_url).replace("%", "%%")
config.set_main_option("sqlalchemy.url", database_url)
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle":"named"})
    with context.begin_transaction(): context.run_migrations()

def run_migrations_online():
    connectable=engine_from_config(config.get_section(config.config_ini_section,{}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection,target_metadata=target_metadata)
        with context.begin_transaction(): context.run_migrations()

run_migrations_offline() if context.is_offline_mode() else run_migrations_online()
