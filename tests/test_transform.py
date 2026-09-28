import pandas as pd

from src.transform.customers import transform_customers
from src.transform.products import transform_products
from src.transform.orders import transform_orders
from src.transform.order_items import transform_order_items


def test_customer_transformation():
    df = pd.DataFrame({
        "customer_id": ["1"],
        "name": ["  John Doe  "],
        "email": [" JOHN@EXAMPLE.COM "],
        "country": [" us "],
        "age": ["30"],
        "signup_date": ["2025-01-01"],
        "marketing_opt_in": [True],
    })

    result = transform_customers(df)

    assert result["name"].iloc[0] == "John Doe"
    assert result["email"].iloc[0] == "john@example.com"
    assert result["country"].iloc[0] == "US"
    assert result["customer_id"].dtype == "int64"
    assert result["age"].dtype == "int64"


def test_product_margin_recalculation():
    df = pd.DataFrame({
        "product_id": [1],
        "category": [" Electronics "],
        "name": [" Test Product "],
        "price_usd": [100.00],
        "cost_usd": [60.00],
        "margin_usd": [999.00],
    })

    result = transform_products(df)

    assert result["category"].iloc[0] == "Electronics"
    assert result["name"].iloc[0] == "Test Product"
    assert result["margin_usd"].iloc[0] == 40.00


def test_order_transformation():
    df = pd.DataFrame({
        "order_id": ["1"],
        "customer_id": ["10"],
        "order_time": ["2025-01-01T12:00:00"],
        "payment_method": [" CARD "],
        "discount_pct": ["10"],
        "subtotal_usd": ["100.00"],
        "total_usd": ["90.00"],
        "country": [" us "],
        "device": [" MOBILE "],
        "source": [" ORGANIC "],
    })

    result = transform_orders(df)

    assert result["order_id"].iloc[0] == 1
    assert result["customer_id"].iloc[0] == 10
    assert result["payment_method"].iloc[0] == "card"
    assert result["country"].iloc[0] == "US"
    assert result["device"].iloc[0] == "mobile"
    assert result["source"].iloc[0] == "organic"


def test_order_item_duplicate_removal():
    df = pd.DataFrame({
        "order_id": [1, 1],
        "product_id": [10, 10],
        "unit_price_usd": [50.00, 50.00],
        "quantity": [2, 2],
        "line_total_usd": [999.00, 999.00],
    })

    result = transform_order_items(df)

    assert len(result) == 1
    assert result["line_total_usd"].iloc[0] == 100.00
    assert result.attrs["input_rows"] == 2
    assert result.attrs["duplicates_removed"] == 1
    assert result.attrs["output_rows"] == 1
