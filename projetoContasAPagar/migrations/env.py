from __future__ import with_statement
from logging.config import fileConfig

from flask import current_app
from alembic import context
from sqlalchemy import engine_from_config, pool
# This is the Alembic Config object, which provides
# access to the configuration.
from alembic.config import Config

# Import the models here for 'autogenerate' support
from projetoContasAPagar import models

# Define the Alembic Config object and load the configuration file
config = Config("migrations/alembic.ini")

# Configuração do Alembic
# config = context.config (novo)

# Configuração de logging (assegure-se que alembic.ini tem a seção [formatters])
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Interpret the config file for Python logging.
# This line sets up loggers.
# fileConfig(config.config_file_name) anterior

target_metadata = models.db.metadata

def run_migrations_online():
    connectable = current_app.extensions['migrate'].db.engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    raise RuntimeError("Offline mode not supported")
else:
    run_migrations_online()
