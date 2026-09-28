from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator


with DAG(
    dag_id="automated_etl_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    tags=["etl", "postgresql", "docker"],
) as dag:

    run_incremental_etl = DockerOperator(
        task_id="run_incremental_etl",
        image="automated-etl-pipeline:latest",
        command="python main.py --mode incremental",

        docker_url="unix://var/run/docker.sock",
        network_mode="automated-etl-pipeline_default",

        environment={
            "POSTGRES_DB": "etl_database",
            "POSTGRES_USER": "etl_user",
            "POSTGRES_PASSWORD": "etl_password",
            "POSTGRES_HOST": "postgres",
            "POSTGRES_PORT": "5432",
        },

        auto_remove="success",
        force_pull=False,
        mount_tmp_dir=False,
    )
