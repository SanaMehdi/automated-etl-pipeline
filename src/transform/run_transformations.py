from pathlib import Path

from src.extract.csv_reader import read_csv
from src.transform import (
    transform_customers,
    transform_products,
    transform_orders,
    transform_order_items,
    write_processed_csv,
)


RAW_DIR = Path("data/raw")


def main() -> None:
    print("=" * 60)
    print("TRANSFORMATION PIPELINE")
    print("=" * 60)

    print("\n[1/4] Reading raw datasets...")

    customers = read_csv(RAW_DIR / "customers.csv")
    products = read_csv(RAW_DIR / "products.csv")
    orders = read_csv(RAW_DIR / "orders.csv")
    order_items = read_csv(RAW_DIR / "order_items.csv")

    print(f"Customers:   {len(customers):,}")
    print(f"Products:    {len(products):,}")
    print(f"Orders:      {len(orders):,}")
    print(f"Order Items: {len(order_items):,}")

    print("\n[2/4] Transforming datasets...")

    customers_t = transform_customers(customers)
    products_t = transform_products(products)
    orders_t = transform_orders(orders)
    order_items_t = transform_order_items(order_items)

    print("Transformations completed.")

    print("\n[3/4] Writing processed datasets...")

    paths = [
        write_processed_csv(customers_t, "customers.csv"),
        write_processed_csv(products_t, "products.csv"),
        write_processed_csv(orders_t, "orders.csv"),
        write_processed_csv(order_items_t, "order_items.csv"),
    ]

    print("\nProcessed files:")

    for path in paths:
        print(f"  ✓ {path}")

    print("\n[4/4] Transformation summary")
    print("-" * 60)

    print(
        f"Customers:   {len(customers):,} → "
        f"{len(customers_t):,}"
    )

    print(
        f"Products:    {len(products):,} → "
        f"{len(products_t):,}"
    )

    print(
        f"Orders:      {len(orders):,} → "
        f"{len(orders_t):,}"
    )

    print(
        f"Order Items: {len(order_items):,} → "
        f"{len(order_items_t):,}"
    )

    print(
        f"Duplicates removed from order_items: "
        f"{order_items_t.attrs['duplicates_removed']:,}"
    )

    print("\nTransformation pipeline completed successfully.")


if __name__ == "__main__":
    main()
