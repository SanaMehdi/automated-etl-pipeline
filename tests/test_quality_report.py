from pathlib import Path

import pandas as pd

from src.validate.quality_report import generate_quality_report


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"


def load_datasets():
    return {
        "customers": pd.read_csv(RAW_DIR / "customers.csv"),
        "products": pd.read_csv(RAW_DIR / "products.csv"),
        "orders": pd.read_csv(RAW_DIR / "orders.csv"),
        "order_items": pd.read_csv(RAW_DIR / "order_items.csv"),
    }


def test_quality_report_contains_all_datasets():
    datasets = load_datasets()
    report = generate_quality_report(datasets)

    assert "datasets" in report

    assert "customers" in report["datasets"]
    assert "products" in report["datasets"]
    assert "orders" in report["datasets"]
    assert "order_items" in report["datasets"]


def test_customers_quality():
    datasets = load_datasets()
    report = generate_quality_report(datasets)

    customers = report["datasets"]["customers"]

    assert customers["rows"] == 20000
    assert customers["duplicate_rows"] == 0
    assert customers["status"] == "PASS"


def test_products_quality():
    datasets = load_datasets()
    report = generate_quality_report(datasets)

    products = report["datasets"]["products"]

    assert products["rows"] == 1197
    assert products["duplicate_rows"] == 0
    assert products["status"] == "PASS"


def test_orders_quality():
    datasets = load_datasets()
    report = generate_quality_report(datasets)

    orders = report["datasets"]["orders"]

    assert orders["rows"] == 33580
    assert orders["duplicate_rows"] == 0
    assert orders["status"] == "PASS"


def test_order_items_duplicates_detected():
    datasets = load_datasets()
    report = generate_quality_report(datasets)

    order_items = report["datasets"]["order_items"]

    assert order_items["rows"] == 59163
    assert order_items["duplicate_rows"] == 73
    assert order_items["status"] == "WARN"
