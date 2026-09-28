from pathlib import Path
import pandas as pd


PROCESSED_DIR = Path("data/processed")


def write_processed_csv(
    df: pd.DataFrame,
    filename: str,
) -> Path:
    """
    Write a transformed DataFrame to the processed-data directory.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_path = PROCESSED_DIR / filename

    df.to_csv(output_path, index=False)

    return output_path
