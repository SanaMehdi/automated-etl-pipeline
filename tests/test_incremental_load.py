import pandas as pd
import pytest

from src.load.postgres import (
    prepare_incremental_dataframe,
    INCREMENTAL_CONFIG,
)


def test_customers_incremental_dataframe_types():
    df = pd.DataFrame(
        {
            "customer_id": ["1", "2"],
            "name": ["Alice", "Bob"],
            "email": ["alice@example.com", "bob@example.com"],
            "country": ["US", "UK"],
            "age": ["30", "40"],
            "signup_date": ["2025-01-01", "2025-02-01"],
            "marketing_opt_in": [True, False],
        }
    )

    result = prepare_incremental_dataframe(
        df,
        "customers",
    )

    assert result["customer_id"].dtype == "int64"
    assert result["age"].dtype == "int64"
    assert str(result["signup_date"].dtype) == "object"
    assert result["signup_date"].iloc[0].isoformat() == "2025-01-01"


def test_products_incremental_dataframe_types():
    df = pd.DataFrame(
        {
            "product_id": ["1", "2"],
            "category": ["Electronics", "Books"],
            "name": ["Phone", "Book"],
            "price_usd": ["999.999", "49.995"],
            "cost_usd": ["700.111", "20.001"],
            "margin_usd": ["299.888", "29.994"],
        }
    )

    result = prepare_incremental_dataframe(
        df,
        "products",
    )

    assert result["product_id"].dtype == "int64"
    assert result["price_usd"].iloc[0] == 1000.00
    assert result["cost_usd"].iloc[0] == 700.11


def test_orders_incremental_dataframe_types():
    df = pd.DataFrame(
        {
            "order_id": ["100"],
            "customer_id": ["10"],
            "order_time": ["2025-01-01 12:00:00"],
            "payment_method": ["card"],
            "discount_pct": ["10.555"],
            "subtotal_usd": ["100.999"],
            "total_usd": ["90.444"],
            "country": ["US"],
            "device": ["mobile"],
            "source": ["web"],
        }
    )

    result = prepare_incremental_dataframe(
        df,
        "orders",
    )

    assert result["order_id"].dtype == "int64"
    assert result["customer_id"].dtype == "int64"
    assert pd.api.types.is_datetime64_any_dtype(
        result["order_time"]
    )
    assert result["discount_pct"].iloc[0] == 10.56
    assert result["subtotal_usd"].iloc[0] == 101.00


def test_order_items_incremental_dataframe_types():
    df = pd.DataFrame(
        {
            "order_id": ["100", "100"],
            "product_id": ["1", "2"],
            "unit_price_usd": ["10.555", "20.999"],
            "quantity": ["2", "3"],
            "line_total_usd": ["21.11", "62.997"],
        }
    )

    result = prepare_incremental_dataframe(
        df,
        "order_items",
    )

    assert result["order_id"].dtype == "int64"
    assert result["product_id"].dtype == "int64"
    assert result["quantity"].dtype == "int64"
    assert result["unit_price_usd"].iloc[0] == 10.56
    assert result["line_total_usd"].iloc[1] == 63.00


def test_incremental_configuration_contains_all_tables():
    expected_tables = {
        "customers",
        "products",
        "orders",
        "order_items",
    }

    assert set(INCREMENTAL_CONFIG.keys()) == expected_tables


def test_incremental_primary_keys_are_defined():
    assert INCREMENTAL_CONFIG["customers"]["primary_keys"] == [
        "customer_id"
    ]

    assert INCREMENTAL_CONFIG["products"]["primary_keys"] == [
        "product_id"
    ]

    assert INCREMENTAL_CONFIG["orders"]["primary_keys"] == [
        "order_id"
    ]

    assert INCREMENTAL_CONFIG["order_items"]["primary_keys"] == [
        "order_id",
        "product_id",
    ]


def test_incremental_dataframe_rejects_invalid_customer_id():
    df = pd.DataFrame(
        {
            "customer_id": ["INVALID"],
            "name": ["Test"],
            "email": ["test@example.com"],
            "country": ["US"],
            "age": ["30"],
            "signup_date": ["2025-01-01"],
            "marketing_opt_in": [True],
        }
    )

    with pytest.raises(Exception):
        prepare_incremental_dataframe(
            df,
            "customers",
        )


def test_incremental_dataframe_rejects_invalid_order_quantity():
    df = pd.DataFrame(
        {
            "order_id": ["100"],
            "product_id": ["1"],
            "unit_price_usd": ["10.00"],
            "quantity": ["INVALID"],
            "line_total_usd": ["10.00"],
        }
    )

    with pytest.raises(Exception):
        prepare_incremental_dataframe(
            df,
            "order_items",
        )


def test_incremental_dataframe_rejects_unknown_table():
    df = pd.DataFrame({"id": [1]})

    with pytest.raises(ValueError):
        prepare_incremental_dataframe(
            df,
            "unknown_table",
        )


def test_incremental_configuration_files_exist():
    for table_name, config in INCREMENTAL_CONFIG.items():
        assert "file" in config
        assert "primary_keys" in config
        assert "columns" in config
        assert len(config["primary_keys"]) > 0
        assert len(config["columns"]) > 0
