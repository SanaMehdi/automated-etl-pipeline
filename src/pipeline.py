from pathlib import Path

from src.extract.csv_reader import read_csv
from src.logger import get_logger

from src.transform import (
    transform_customers,
    transform_products,
    transform_orders,
    transform_order_items,
    write_processed_csv,
)

from src.load.postgres import (
    create_db_engine,
    test_connection,
    load_all_tables,
    load_incremental_tables,
)

from src.validate.validators import (
    validate_customer_data,
    validate_product_data,
    validate_order_data,
    validate_order_item_data,
)

logger = get_logger()

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"


def run_pipeline(mode: str = "full") -> None:
    if mode not in {"full", "incremental"}:
        raise ValueError(
            "Invalid mode. Use 'full' or 'incremental'."
        )

    logger.info("=" * 60)
    logger.info(
        "Starting ETL pipeline | mode=%s",
        mode.upper(),
    )
    logger.info("=" * 60)

    try:
        # -------------------------------------------------
        # EXTRACTION
        # -------------------------------------------------

        logger.info("Starting extraction")

        customers = read_csv(
            RAW_DIR / "customers.csv"
        )

        products = read_csv(
            RAW_DIR / "products.csv"
        )

        orders = read_csv(
            RAW_DIR / "orders.csv"
        )

        order_items = read_csv(
            RAW_DIR / "order_items.csv"
        )

        logger.info(
            "Extracted %s customers",
            f"{len(customers):,}",
        )

        logger.info(
            "Extracted %s products",
            f"{len(products):,}",
        )

        logger.info(
            "Extracted %s orders",
            f"{len(orders):,}",
        )

        logger.info(
            "Extracted %s order items",
            f"{len(order_items):,}",
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        logger.info("Starting data validation")

        validation_results = {
            "customers": validate_customer_data(
                customers
            ),
            "products": validate_product_data(
                products
            ),
            "orders": validate_order_data(
                orders
            ),
            "order_items": validate_order_item_data(
                order_items
            ),
        }

        validation_errors = {
            name: errors
            for name, errors in validation_results.items()
            if errors
        }

        if validation_errors:
            for dataset, errors in validation_errors.items():
                for error in errors:
                    logger.error(
                        "Validation error in %s: %s",
                        dataset,
                        error,
                    )

            raise ValueError(
                f"Data validation failed: "
                f"{validation_errors}"
            )

        logger.info(
            "Data validation completed successfully"
        )

        # -------------------------------------------------
        # TRANSFORMATION
        # -------------------------------------------------

        logger.info("Starting data transformation")

        customers_t = transform_customers(customers)
        products_t = transform_products(products)
        orders_t = transform_orders(orders)
        order_items_t = transform_order_items(
            order_items
        )

        logger.info(
            "Customers transformed: %s → %s",
            f"{len(customers):,}",
            f"{len(customers_t):,}",
        )

        logger.info(
            "Products transformed: %s → %s",
            f"{len(products):,}",
            f"{len(products_t):,}",
        )

        logger.info(
            "Orders transformed: %s → %s",
            f"{len(orders):,}",
            f"{len(orders_t):,}",
        )

        logger.info(
            "Order items transformed: %s → %s",
            f"{len(order_items):,}",
            f"{len(order_items_t):,}",
        )

        duplicates_removed = order_items_t.attrs.get(
            "duplicates_removed",
            0,
        )

        logger.info(
            "Removed %s duplicate order-item rows",
            f"{duplicates_removed:,}",
        )

        # -------------------------------------------------
        # WRITE PROCESSED DATA
        # -------------------------------------------------

        logger.info(
            "Writing processed datasets"
        )

        write_processed_csv(
            customers_t,
            "customers.csv",
        )

        write_processed_csv(
            products_t,
            "products.csv",
        )

        write_processed_csv(
            orders_t,
            "orders.csv",
        )

        write_processed_csv(
            order_items_t,
            "order_items.csv",
        )

        logger.info(
            "Processed datasets written successfully"
        )

        # -------------------------------------------------
        # DATABASE LOAD
        # -------------------------------------------------

        logger.info("Connecting to PostgreSQL")

        engine = create_db_engine()

        test_connection(engine)

        logger.info(
            "PostgreSQL connection successful"
        )

        if mode == "full":
            logger.info(
                "Starting PostgreSQL full-refresh load"
            )

            load_all_tables(engine)

            logger.info(
                "PostgreSQL full-refresh load "
                "completed successfully"
            )

        else:
            logger.info(
                "Starting PostgreSQL incremental load"
            )

            load_incremental_tables(engine)

            logger.info(
                "PostgreSQL incremental load "
                "completed successfully"
            )

        # -------------------------------------------------
        # COMPLETE
        # -------------------------------------------------

        logger.info("=" * 60)
        logger.info(
            "ETL PIPELINE COMPLETED SUCCESSFULLY"
        )
        logger.info(
            "Load mode: %s",
            mode.upper(),
        )
        logger.info("=" * 60)

    except Exception:
        logger.exception(
            "ETL pipeline failed"
        )
        raise


if __name__ == "__main__":
    run_pipeline()
