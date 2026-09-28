import argparse

from src.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automated ETL/ELT Data Pipeline"
    )

    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="full",
        help=(
            "Database loading mode: "
            "full refresh or incremental upsert."
        ),
    )

    args = parser.parse_args()

    run_pipeline(mode=args.mode)


if __name__ == "__main__":
    main()
