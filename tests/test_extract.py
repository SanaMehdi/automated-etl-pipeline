from pathlib import Path

from src.extract.csv_reader import read_csv


def test_read_customers_csv():
    file_path = Path("data/raw/customers.csv")

    df = read_csv(file_path)

    assert not df.empty
    assert len(df.columns) > 0


def test_read_products_csv():
    file_path = Path("data/raw/products.csv")

    df = read_csv(file_path)

    assert not df.empty
    assert len(df.columns) > 0
