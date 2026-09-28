import pandas as pd


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["product_id"] = pd.to_numeric(
        result["product_id"], errors="raise"
    ).astype("int64")

    result["category"] = (
        result["category"]
        .astype("string")
        .str.strip()
    )

    result["name"] = (
        result["name"]
        .astype("string")
        .str.strip()
    )

    for column in ["price_usd", "cost_usd", "margin_usd"]:
        result[column] = pd.to_numeric(
            result[column], errors="raise"
        ).round(2)

    # Recalculate margin from source price and cost.
    result["margin_usd"] = (
        result["price_usd"] - result["cost_usd"]
    ).round(2)

    return result
