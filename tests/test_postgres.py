import os

import pandas as pd
import pytest

from src.load.postgres import (
    get_database_url,
    create_db_engine,
)


def test_database_url_exists():
    """
    Verify PostgreSQL configuration is available.
    """

    required = [
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing = [
        variable
        for variable in required
        if not os.getenv(variable)
    ]

    if missing:
        pytest.skip(
            "PostgreSQL environment variables not configured."
        )

    url = get_database_url()

    assert url.startswith(
        "postgresql+psycopg2://"
    )


def test_create_database_engine():
    """
    Verify that SQLAlchemy can create a PostgreSQL engine.
    """

    required = [
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing = [
        variable
        for variable in required
        if not os.getenv(variable)
    ]

    if missing:
        pytest.skip(
            "PostgreSQL environment variables not configured."
        )

    engine = create_db_engine()

    assert engine is not None
    assert engine.dialect.name == "postgresql"
