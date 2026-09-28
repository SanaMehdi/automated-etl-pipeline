import pandas as pd


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["order_id"] = pd.to_numeric(
        result["order_id"], errors="raise"
    ).astype("int64")

    result["customer_id"] = pd.to_numeric(
        result["customer_id"], errors="raise"
    ).astype("int64")

    result["order_time"] = pd.to_datetime(
        result["order_time"], errors="raise"
    )

    result["payment_method"] = (
        result["payment_method"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    result["discount_pct"] = pd.to_numeric(
        result["discount_pct"], errors="raise"
    )

    result["subtotal_usd"] = pd.to_numeric(
        result["subtotal_usd"], errors="raise"
    ).round(2)

    result["total_usd"] = pd.to_numeric(
        result["total_usd"], errors="raise"
    ).round(2)

    result["country"] = (
        result["country"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    result["device"] = (
        result["device"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    result["source"] = (
        result["source"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    return result
