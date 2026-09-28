import pandas as pd


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["customer_id"] = pd.to_numeric(
        result["customer_id"], errors="raise"
    ).astype("int64")

    result["name"] = result["name"].astype("string").str.strip()

    result["email"] = (
        result["email"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    result["country"] = (
        result["country"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    result["age"] = pd.to_numeric(
        result["age"], errors="raise"
    ).astype("int64")

    result["signup_date"] = pd.to_datetime(
        result["signup_date"], errors="raise"
    )

    result["marketing_opt_in"] = result["marketing_opt_in"].astype(bool)

    return result
