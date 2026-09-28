import pandas as pd


def transform_order_items(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
        "order_id",
        "product_id",
        "unit_price_usd",
        "quantity",
        "line_total_usd",
    ]

    # Validate required columns
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    input_rows = len(df)

    result = df.copy()

    # Remove completely identical records.
    result = result.drop_duplicates().reset_index(drop=True)

    # Normalize numeric columns.
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

    # Recalculate line totals from normalized values.
    result["line_total_usd"] = (
        result["unit_price_usd"] * result["quantity"]
    ).round(2)

    # Aggregate repeated products within the same order.
    #
    # The database uses (order_id, product_id) as the primary key,
    # so each order/product combination must appear only once.
    result = (
        result.groupby(
            ["order_id", "product_id"],
            as_index=False,
            sort=False,
        )
        .agg(
            unit_price_usd=("unit_price_usd", "first"),
            quantity=("quantity", "sum"),
            line_total_usd=("line_total_usd", "sum"),
        )
    )

    # Ensure final monetary values have two decimal places.
    result["unit_price_usd"] = result["unit_price_usd"].round(2)
    result["line_total_usd"] = result["line_total_usd"].round(2)

    # Reset index after transformation.
    result = result.reset_index(drop=True)

    # Store transformation statistics.
    duplicates_removed = input_rows - len(result)

    result.attrs["input_rows"] = input_rows
    result.attrs["duplicates_removed"] = duplicates_removed
    result.attrs["output_rows"] = len(result)

    return result
