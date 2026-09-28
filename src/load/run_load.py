from src.load.postgres import (
    create_db_engine,
    test_connection,
    load_customers,
    load_products,
    load_orders,
    load_order_items,
)


def main() -> None:
    print("=" * 60)
    print("DATABASE LOAD PIPELINE")
    print("=" * 60)

    engine = create_db_engine()

    print()
    print("[1/5] Testing PostgreSQL connection...")
    test_connection(engine)

    print()
    print("[2/5] Loading customers...")
    load_customers(engine)

    print()
    print("[3/5] Loading products...")
    load_products(engine)

    print()
    print("[4/5] Loading orders...")
    load_orders(engine)

    print()
    print("[5/5] Loading order items...")
    load_order_items(engine)

    print()
    print("=" * 60)
    print("DATABASE LOAD COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
