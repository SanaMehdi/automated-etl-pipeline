import pandas as pd

from src.validate.validators import (
    find_duplicate_rows,
    find_missing_values,
    validate_customer_data,
    validate_product_data,
    validate_order_data,
    validate_order_item_data,
)


def test_duplicate_detection():
    df = pd.DataFrame({
        "id": [1, 2, 2, 3]
    })

    assert find_duplicate_rows(df) == 1


def test_missing_value_detection():
    df = pd.DataFrame({
        "name": ["Alice", None, "Bob"]
    })

    result = find_missing_values(df)

    assert result["name"] == 1


def test_valid_customer_data():
    df = pd.DataFrame({
        "customer_id": [1],
        "name": ["Alice"],
        "email": ["alice@example.com"],
        "country": ["PK"],
        "age": [25],
        "signup_date": ["2025-01-01"],
        "marketing_opt_in": [True],
    })

    assert validate_customer_data(df) == []


def test_invalid_customer_email():
    df = pd.DataFrame({
        "customer_id": [1],
        "name": ["Alice"],
        "email": ["invalid-email"],
        "country": ["PK"],
        "age": [25],
        "signup_date": ["2025-01-01"],
        "marketing_opt_in": [True],
    })

    errors = validate_customer_data(df)

    assert len(errors) > 0


def test_valid_product_data():
    df = pd.DataFrame({
        "product_id": [1],
        "category": ["Electronics"],
        "name": ["SSD"],
        "price_usd": [100.0],
        "cost_usd": [60.0],
        "margin_usd": [40.0],
    })

    assert validate_product_data(df) == []


def test_invalid_product_price():
    df = pd.DataFrame({
        "product_id": [1],
        "category": ["Electronics"],
        "name": ["SSD"],
        "price_usd": [-100.0],
        "cost_usd": [60.0],
        "margin_usd": [40.0],
    })

    errors = validate_product_data(df)

    assert len(errors) > 0


def test_valid_order_data():
    df = pd.DataFrame({
        "order_id": [1],
        "customer_id": [10],
        "order_time": ["2025-01-01T10:00:00"],
        "payment_method": ["card"],
        "discount_pct": [10],
        "subtotal_usd": [100.0],
        "total_usd": [90.0],
        "country": ["PK"],
        "device": ["desktop"],
        "source": ["organic"],
    })

    assert validate_order_data(df) == []


def test_invalid_order_discount():
    df = pd.DataFrame({
        "order_id": [1],
        "customer_id": [10],
        "order_time": ["2025-01-01T10:00:00"],
        "payment_method": ["card"],
        "discount_pct": [150],
        "subtotal_usd": [100.0],
        "total_usd": [90.0],
        "country": ["PK"],
        "device": ["desktop"],
        "source": ["organic"],
    })

    errors = validate_order_data(df)

    assert len(errors) > 0


def test_valid_order_items():
    df = pd.DataFrame({
        "order_id": [1],
        "product_id": [10],
        "unit_price_usd": [50.0],
        "quantity": [2],
        "line_total_usd": [100.0],
    })

    assert validate_order_item_data(df) == []


def test_invalid_order_item_quantity():
    df = pd.DataFrame({
        "order_id": [1],
        "product_id": [10],
        "unit_price_usd": [50.0],
        "quantity": [0],
        "line_total_usd": [0.0],
    })

    errors = validate_order_item_data(df)

    assert len(errors) > 0
