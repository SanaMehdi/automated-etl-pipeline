from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection

from src.logger import get_logger


# ============================================================
# PATHS / ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

load_dotenv(
    dotenv_path=BASE_DIR / ".env",
    override=True,
)

logger = get_logger()


# ============================================================
# INCREMENTAL LOAD CONFIGURATION
# ============================================================

INCREMENTAL_CONFIG = {
    "customers": {
        "file": "customers.csv",
        "primary_keys": ["customer_id"],
        "columns": [
            "customer_id",
            "name",
            "email",
            "country",
            "age",
            "signup_date",
            "marketing_opt_in",
        ],
    },
    "products": {
        "file": "products.csv",
        "primary_keys": ["product_id"],
        "columns": [
            "product_id",
            "category",
            "name",
            "price_usd",
            "cost_usd",
            "margin_usd",
        ],
    },
    "orders": {
        "file": "orders.csv",
        "primary_keys": ["order_id"],
        "columns": [
            "order_id",
            "customer_id",
            "order_time",
            "payment_method",
            "discount_pct",
            "subtotal_usd",
            "total_usd",
            "country",
            "device",
            "source",
        ],
    },
    "order_items": {
        "file": "order_items.csv",
        "primary_keys": [
            "order_id",
            "product_id",
        ],
        "columns": [
            "order_id",
            "product_id",
            "unit_price_usd",
            "quantity",
            "line_total_usd",
        ],
    },
}


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_database_url() -> str:
    host = os.getenv(
        "POSTGRES_HOST",
        "localhost",
    )
    port = os.getenv(
        "POSTGRES_PORT",
        "5432",
    )
    database = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")

    if not all(
        [
            database,
            user,
            password,
        ]
    ):
        raise ValueError(
            "Missing PostgreSQL environment variables. "
            "Check your .env file."
        )

    return (
        f"postgresql+psycopg2://"
        f"{user}:{password}@{host}:{port}/{database}"
    )


def create_db_engine() -> Engine:
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
    )


def test_connection(engine: Engine) -> None:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT 1")
        )
        value = result.scalar()

    if value != 1:
        raise RuntimeError(
            "PostgreSQL connection test failed."
        )

    print(
        "PostgreSQL connection successful."
    )


# ============================================================
# FULL REFRESH LOAD
# ============================================================

def clear_tables(connection: Connection) -> None:
    """
    Clear all ETL tables in dependency-safe order.
    """

    connection.execute(
        text(
            """
            TRUNCATE TABLE
                order_items,
                orders,
                products,
                customers
            RESTART IDENTITY CASCADE
            """
        )
    )


def load_dataframe(
    connection: Connection,
    df: pd.DataFrame,
    table_name: str,
) -> None:
    """
    Load a dataframe into an existing PostgreSQL table.
    """

    df.to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False,
        method="multi",
    )

    print(
        f"Loaded {len(df):,} rows into "
        f"'{table_name}'."
    )


def load_customers(
    connection: Connection,
) -> None:
    path = PROCESSED_DIR / "customers.csv"
    df = pd.read_csv(path)

    load_dataframe(
        connection,
        df,
        "customers",
    )


def load_products(
    connection: Connection,
) -> None:
    path = PROCESSED_DIR / "products.csv"
    df = pd.read_csv(path)

    load_dataframe(
        connection,
        df,
        "products",
    )


def load_orders(
    connection: Connection,
) -> None:
    path = PROCESSED_DIR / "orders.csv"
    df = pd.read_csv(path)

    load_dataframe(
        connection,
        df,
        "orders",
    )


def load_order_items(
    connection: Connection,
) -> None:
    path = PROCESSED_DIR / "order_items.csv"
    df = pd.read_csv(path)

    load_dataframe(
        connection,
        df,
        "order_items",
    )


def load_all_tables(
    engine: Engine,
) -> None:
    """
    Perform a complete transactional full refresh.

    If any load fails, the entire transaction
    is rolled back.
    """

    with engine.begin() as connection:

        print(
            "Clearing existing ETL tables..."
        )

        clear_tables(connection)

        print(
            "Loading customers..."
        )

        load_customers(connection)

        print(
            "Loading products..."
        )

        load_products(connection)

        print(
            "Loading orders..."
        )

        load_orders(connection)

        print(
            "Loading order items..."
        )

        load_order_items(connection)

    print(
        "Database transaction committed successfully."
    )


# ============================================================
# IDENTIFIER HELPER
# ============================================================

def _quote_identifier(
    identifier: str,
) -> str:
    """
    Safely quote a PostgreSQL identifier.

    Identifiers originate from fixed internal
    configuration, not user input.
    """

    return (
        '"'
        + identifier.replace('"', '""')
        + '"'
    )


# ============================================================
# INCREMENTAL DATA PREPARATION
# ============================================================

def prepare_incremental_dataframe(
    df: pd.DataFrame,
    table_name: str,
) -> pd.DataFrame:
    """
    Normalize dataframe types before incremental loading.

    This is important because CSV files do not preserve
    PostgreSQL types.
    """

    result = df.copy()

    if table_name == "customers":

        result["customer_id"] = pd.to_numeric(
            result["customer_id"],
            errors="raise",
        ).astype("int64")

        result["age"] = pd.to_numeric(
            result["age"],
            errors="raise",
        ).astype("int64")

        result["signup_date"] = pd.to_datetime(
            result["signup_date"],
            errors="raise",
        ).dt.date

        result["marketing_opt_in"] = (
            result["marketing_opt_in"]
            .astype(bool)
        )

    elif table_name == "products":

        result["product_id"] = pd.to_numeric(
            result["product_id"],
            errors="raise",
        ).astype("int64")

        for column in [
            "price_usd",
            "cost_usd",
            "margin_usd",
        ]:
            result[column] = pd.to_numeric(
                result[column],
                errors="raise",
            ).round(2)

    elif table_name == "orders":

        result["order_id"] = pd.to_numeric(
            result["order_id"],
            errors="raise",
        ).astype("int64")

        result["customer_id"] = pd.to_numeric(
            result["customer_id"],
            errors="raise",
        ).astype("int64")

        result["order_time"] = pd.to_datetime(
            result["order_time"],
            errors="raise",
        )

        result["discount_pct"] = pd.to_numeric(
            result["discount_pct"],
            errors="raise",
        ).round(2)

        result["subtotal_usd"] = pd.to_numeric(
            result["subtotal_usd"],
            errors="raise",
        ).round(2)

        result["total_usd"] = pd.to_numeric(
            result["total_usd"],
            errors="raise",
        ).round(2)

    elif table_name == "order_items":

        result["order_id"] = pd.to_numeric(
            result["order_id"],
            errors="raise",
        ).astype("int64")

        result["product_id"] = pd.to_numeric(
            result["product_id"],
            errors="raise",
        ).astype("int64")

        result["unit_price_usd"] = pd.to_numeric(
            result["unit_price_usd"],
            errors="raise",
        ).round(2)

        result["quantity"] = pd.to_numeric(
            result["quantity"],
            errors="raise",
        ).astype("int64")

        result["line_total_usd"] = pd.to_numeric(
            result["line_total_usd"],
            errors="raise",
        ).round(2)

    else:
        raise ValueError(
            f"Unsupported incremental table: "
            f"{table_name}"
        )

    return result


# ============================================================
# INCREMENTAL UPSERT
# ============================================================

def incremental_upsert(
    connection: Connection,
    df: pd.DataFrame,
    table_name: str,
    primary_keys: list[str],
    columns: list[str],
) -> None:
    """
    Incrementally upsert a dataframe into PostgreSQL.

    New primary keys are inserted.
    Existing primary keys are updated.

    A temporary staging table is created using the
    exact PostgreSQL types of the target table.
    """

    if df.empty:
        logger.info(
            "No rows to incrementally load into '%s'.",
            table_name,
        )
        return

    # --------------------------------------------------------
    # Validate columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns for {table_name}: "
            f"{missing_columns}"
        )

    # --------------------------------------------------------
    # Prepare dataframe types
    # --------------------------------------------------------

    load_df = prepare_incremental_dataframe(
        df[columns].copy(),
        table_name,
    )

    # --------------------------------------------------------
    # Remove duplicate primary keys
    # --------------------------------------------------------

    before_dedup = len(load_df)

    load_df = (
        load_df
        .drop_duplicates(
            subset=primary_keys,
            keep="last",
        )
        .reset_index(drop=True)
    )

    duplicates_removed = (
        before_dedup - len(load_df)
    )

    if duplicates_removed:
        logger.warning(
            "Removed %s duplicate keys from "
            "incremental batch for '%s'.",
            f"{duplicates_removed:,}",
            table_name,
        )

    # --------------------------------------------------------
    # Temporary typed staging table
    # --------------------------------------------------------

    staging_table = (
        f"_staging_{table_name}"
    )

    quoted_target = _quote_identifier(
        table_name
    )

    quoted_staging = _quote_identifier(
        staging_table
    )

    # The important fix:
    #
    # CREATE TEMP TABLE ... LIKE target
    #
    # This makes signup_date DATE,
    # order_time TIMESTAMP,
    # numeric columns NUMERIC, etc.
    #
    # instead of letting pandas create them as TEXT.
    connection.execute(
        text(
            f"""
            DROP TABLE IF EXISTS
                {quoted_staging};

            CREATE TEMP TABLE
                {quoted_staging}
            (LIKE {quoted_target}
             INCLUDING DEFAULTS)
            """
        )
    )

    try:

        # ----------------------------------------------------
        # Load dataframe into typed staging table
        # ----------------------------------------------------

        load_df.to_sql(
            staging_table,
            con=connection,
            if_exists="append",
            index=False,
            method="multi",
        )

        # ----------------------------------------------------
        # Build INSERT / UPSERT SQL
        # ----------------------------------------------------

        quoted_columns = ", ".join(
            _quote_identifier(column)
            for column in columns
        )

        quoted_primary_keys = ", ".join(
            _quote_identifier(column)
            for column in primary_keys
        )

        update_columns = [
            column
            for column in columns
            if column not in primary_keys
        ]

        if update_columns:

            update_clause = ", ".join(
                f"{_quote_identifier(column)} = "
                f"EXCLUDED.{_quote_identifier(column)}"
                for column in update_columns
            )

            conflict_action = (
                f"DO UPDATE SET "
                f"{update_clause}"
            )

        else:
            conflict_action = "DO NOTHING"

        sql = f"""
            INSERT INTO {quoted_target}
                ({quoted_columns})
            SELECT
                {quoted_columns}
            FROM {quoted_staging}
            ON CONFLICT ({quoted_primary_keys})
            {conflict_action}
        """

        result = connection.execute(
            text(sql)
        )

        logger.info(
            "Incrementally processed %s rows "
            "for '%s'.",
            f"{len(load_df):,}",
            table_name,
        )

        logger.info(
            "Database rowcount for '%s': %s",
            table_name,
            result.rowcount,
        )

    finally:

        # ----------------------------------------------------
        # Cleanup staging table
        # ----------------------------------------------------

        connection.execute(
            text(
                f"""
                DROP TABLE IF EXISTS
                    {quoted_staging}
                """
            )
        )


# ============================================================
# INCREMENTAL TABLE LOADER
# ============================================================

def load_incremental_table(
    connection: Connection,
    table_name: str,
) -> None:

    if table_name not in INCREMENTAL_CONFIG:
        raise ValueError(
            f"No incremental configuration "
            f"found for '{table_name}'."
        )

    config = INCREMENTAL_CONFIG[
        table_name
    ]

    file_path = (
        PROCESSED_DIR / config["file"]
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Processed file not found: "
            f"{file_path}"
        )

    df = pd.read_csv(
        file_path
    )

    incremental_upsert(
        connection=connection,
        df=df,
        table_name=table_name,
        primary_keys=config[
            "primary_keys"
        ],
        columns=config[
            "columns"
        ],
    )


# ============================================================
# INCREMENTAL LOAD ALL TABLES
# ============================================================

def load_incremental_tables(
    engine: Engine,
) -> None:
    """
    Transactional incremental load.

    Tables are processed in foreign-key
    dependency order:

        customers
        products
        orders
        order_items
    """

    load_order = [
        "customers",
        "products",
        "orders",
        "order_items",
    ]

    with engine.begin() as connection:

        logger.info(
            "Starting transactional "
            "incremental load..."
        )

        for table_name in load_order:

            logger.info(
                "Incrementally loading '%s'...",
                table_name,
            )

            load_incremental_table(
                connection,
                table_name,
            )

        logger.info(
            "Incremental database transaction "
            "committed successfully."
        )


# ============================================================
# STANDALONE EXECUTION
# ============================================================

def main() -> None:

    print("=" * 60)
    print("POSTGRESQL DATA LOADER")
    print("=" * 60)

    engine = create_db_engine()

    print()
    print("Testing PostgreSQL connection...")

    test_connection(engine)

    print()
    print(
        "Starting transactional full refresh..."
    )

    load_all_tables(engine)

    print()
    print("=" * 60)
    print(
        "POSTGRESQL LOADING COMPLETED "
        "SUCCESSFULLY"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()

