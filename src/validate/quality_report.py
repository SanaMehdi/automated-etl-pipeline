from pathlib import Path
from datetime import datetime, timezone
import json

import pandas as pd

from src.validate.validators import (
    find_duplicate_rows,
    find_missing_values,
    validate_customer_data,
    validate_product_data,
    validate_order_data,
    validate_order_item_data,
)


BASE_DIR = Path(__file__).resolve().parents[2]
REPORTS_DIR = BASE_DIR / "reports"
REPORT_PATH = REPORTS_DIR / "data_quality_report.json"


VALIDATORS = {
    "customers": validate_customer_data,
    "products": validate_product_data,
    "orders": validate_order_data,
    "order_items": validate_order_item_data,
}


def build_dataset_report(
    dataset_name: str,
    df: pd.DataFrame,
) -> dict:
    validator = VALIDATORS[dataset_name]

    duplicate_rows = find_duplicate_rows(df)
    missing_values = find_missing_values(df)
    validation_errors = validator(df)

    if validation_errors:
        status = "FAIL"
    elif duplicate_rows > 0 or missing_values:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "duplicate_rows": duplicate_rows,
        "missing_values": missing_values,
        "validation_errors": validation_errors,
        "status": status,
    }


def generate_quality_report(
    datasets: dict[str, pd.DataFrame],
) -> dict:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "report_generated_at": datetime.now(timezone.utc).isoformat(),
        "datasets": {},
    }

    for dataset_name, df in datasets.items():
        if dataset_name not in VALIDATORS:
            raise ValueError(
                f"No validator configured for dataset: {dataset_name}"
            )

        report["datasets"][dataset_name] = build_dataset_report(
            dataset_name,
            df,
        )

    statuses = [
        dataset["status"]
        for dataset in report["datasets"].values()
    ]

    if "FAIL" in statuses:
        report["overall_status"] = "FAIL"
    elif "WARN" in statuses:
        report["overall_status"] = "WARN"
    else:
        report["overall_status"] = "PASS"

    with REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    return report


def print_quality_report(report: dict) -> None:
    print()
    print("=" * 60)
    print("DATA QUALITY REPORT")
    print("=" * 60)

    for dataset_name, dataset in report["datasets"].items():
        print(
            f"{dataset_name:<15} "
            f"rows={dataset['rows']:<7} "
            f"duplicates={dataset['duplicate_rows']:<5} "
            f"status={dataset['status']}"
        )

    print("-" * 60)
    print(f"Overall status: {report['overall_status']}")
    print(f"Report: {REPORT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    from src.extract.csv_reader import read_csv

    datasets = {
        "customers": read_csv(BASE_DIR / "data" / "raw" / "customers.csv"),
        "products": read_csv(BASE_DIR / "data" / "raw" / "products.csv"),
        "orders": read_csv(BASE_DIR / "data" / "raw" / "orders.csv"),
        "order_items": read_csv(
            BASE_DIR / "data" / "raw" / "order_items.csv"
        ),
    }

    report = generate_quality_report(datasets)
    print_quality_report(report)
