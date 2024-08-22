import logging
from logging.config import fileConfig

from flask import current_app
from sqlalchemy import engine
from alembic import context

# This is the Alembic Config object, which provides
# access to the configuration.
from alembic.config import Config

# Import the models here for 'autogenerate' support
from projetoContasAPagar import models

# Define the Alembic Config object and load the configuration file
config = Config("migrations/alembic.ini")

# Interpret the config file for Python logging.
# This line sets up loggers.
fileConfig(config.config_file_name)

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
