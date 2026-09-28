import re
import pandas as pd


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str]
) -> list[str]:
    """Return required columns that are missing."""
    return [
        column
        for column in required_columns
        if column not in df.columns
    ]


def find_duplicate_rows(df: pd.DataFrame) -> int:
    """Count completely duplicated rows."""
    return int(df.duplicated().sum())


def find_missing_values(df: pd.DataFrame) -> dict[str, int]:
    """Return missing-value counts for each column."""
    return {
        column: int(count)
        for column, count in df.isnull().sum().items()
        if count > 0
    }


def validate_email(email: str) -> bool:
    """Basic email-format validation."""
    if not isinstance(email, str):
        return False

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))


def validate_customer_data(df: pd.DataFrame) -> list[str]:
    errors = []

    required = [
        "customer_id",
        "name",
        "email",
        "country",
        "age",
        "signup_date",
        "marketing_opt_in",
    ]

    errors.extend(
        f"Missing required column: {column}"
        for column in validate_required_columns(df, required)
    )

    if "email" in df.columns:
        invalid_emails = (~df["email"].apply(validate_email)).sum()

        if invalid_emails:
            errors.append(
                f"Invalid email addresses: {invalid_emails}"
            )

    if "age" in df.columns:
        invalid_age = (
            (df["age"] < 0) |
            (df["age"] > 120)
        ).sum()

        if invalid_age:
            errors.append(
                f"Invalid customer ages: {invalid_age}"
            )

    return errors


def validate_product_data(df: pd.DataFrame) -> list[str]:
    errors = []

    required = [
        "product_id",
        "category",
        "name",
        "price_usd",
        "cost_usd",
        "margin_usd",
    ]

    errors.extend(
        f"Missing required column: {column}"
        for column in validate_required_columns(df, required)
    )

    for column in ["price_usd", "cost_usd", "margin_usd"]:
        if column in df.columns:
            invalid = (df[column] < 0).sum()

            if invalid:
                errors.append(
                    f"Negative values in {column}: {invalid}"
                )

    return errors


def validate_order_data(df: pd.DataFrame) -> list[str]:
    errors = []

    required = [
        "order_id",
        "customer_id",
        "order_time",
        "payment_method",
        "discount_pct",
        "subtotal_usd",
        "total_usd",
        "country",
        "device",
        "source",
    ]

    errors.extend(
        f"Missing required column: {column}"
        for column in validate_required_columns(df, required)
    )

    if "discount_pct" in df.columns:
        invalid = (
            (df["discount_pct"] < 0) |
            (df["discount_pct"] > 100)
        ).sum()

        if invalid:
            errors.append(
                f"Invalid discount percentages: {invalid}"
            )

    if "total_usd" in df.columns:
        invalid = (df["total_usd"] < 0).sum()

        if invalid:
            errors.append(
                f"Negative order totals: {invalid}"
            )

    return errors


def validate_order_item_data(df: pd.DataFrame) -> list[str]:
    errors = []

    required = [
        "order_id",
        "product_id",
        "unit_price_usd",
        "quantity",
        "line_total_usd",
    ]

    errors.extend(
        f"Missing required column: {column}"
        for column in validate_required_columns(df, required)
    )

    if "quantity" in df.columns:
        invalid = (df["quantity"] <= 0).sum()

        if invalid:
            errors.append(
                f"Invalid quantities: {invalid}"
            )

    if "unit_price_usd" in df.columns:
        invalid = (df["unit_price_usd"] < 0).sum()

        if invalid:
            errors.append(
                f"Negative unit prices: {invalid}"
            )

    if "line_total_usd" in df.columns:
        invalid = (df["line_total_usd"] < 0).sum()

        if invalid:
            errors.append(
                f"Negative line totals: {invalid}"
            )

    return errors
