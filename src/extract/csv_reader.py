import pandas as pd
from pathlib import Path


def read_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Read a CSV file into a Pandas DataFrame.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a CSV file, got: {path.suffix}")

    return pd.read_csv(path)
