import logging
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

PIPELINE_LOG = LOG_DIR / "pipeline.log"
ERROR_LOG = LOG_DIR / "errors.log"


logger = logging.getLogger("etl_pipeline")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    pipeline_handler = logging.FileHandler(
        PIPELINE_LOG,
        encoding="utf-8",
    )
    pipeline_handler.setLevel(logging.INFO)
    pipeline_handler.setFormatter(formatter)

    error_handler = logging.FileHandler(
        ERROR_LOG,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(pipeline_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)


def get_logger() -> logging.Logger:
    """Return the ETL pipeline logger."""
    return logger
