import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

files = [
    "customers.csv",
    "products.csv",
    "orders.csv",
    "order_items.csv",
]

for filename in files:
    path = DATA_DIR / filename

    print("\n" + "=" * 70)
    print(f"FILE: {filename}")
    print("=" * 70)

    df = pd.read_csv(path)

    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nFirst 5 rows:")
    print(df.head())
