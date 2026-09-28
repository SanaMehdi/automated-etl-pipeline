# Automated ETL/ELT Data Pipeline

A production-style Python ETL/ELT pipeline for ingesting, validating, transforming, and incrementally loading e-commerce data into PostgreSQL, with automated data-quality reporting, analytics SQL, Docker containerization, and Apache Airflow orchestration.

## Overview

This project implements an end-to-end automated data pipeline:

```text
CSV / JSON / REST API
        │
        ▼
   Python ETL
        │
        ▼
 Validation
        │
        ▼
Transformation
        │
        ▼
   PostgreSQL
        │
        ├──────────────► Analytics SQL
        │
        └──────────────► Data Quality Reports

             ▲
             │
        Apache Airflow
             │
             ▼
       DockerOperator
```

The pipeline supports both **full database refreshes** and **incremental loading**, with transactional PostgreSQL upserts and dependency-aware loading.

---

## Key Features

* CSV-based data ingestion
* Input validation
* Data cleaning and normalization
* Duplicate detection and removal
* Data-quality reporting
* PostgreSQL storage
* Full-refresh loading
* Incremental/upsert loading
* Transactional database operations
* Idempotent incremental processing
* Analytics SQL queries
* Structured logging
* Error handling
* Automated tests
* Docker containerization
* Docker Compose
* Apache Airflow orchestration
* Daily automated scheduling

---

## Dataset

The pipeline processes four core e-commerce datasets:

| Dataset     | Raw Rows | Transformed Rows |
| ----------- | -------: | ---------------: |
| Customers   |   20,000 |           20,000 |
| Products    |    1,197 |            1,197 |
| Orders      |   33,580 |           33,580 |
| Order Items |   59,163 |           59,053 |

The `order_items` transformation removes duplicate records and normalizes repeated `(order_id, product_id)` combinations.

---

## Technology Stack

### Programming

* Python 3.11
* Pandas
* SQLAlchemy
* psycopg2
* Pydantic
* Requests
* Pytest

### Database

* PostgreSQL 16

### Infrastructure

* Docker
* Docker Compose

### Orchestration

* Apache Airflow 3.0.6
* DockerOperator

### Analytics

* PostgreSQL SQL
* Analytical aggregation queries
* Customer and product performance analysis

---

## Project Structure

```text
automated-etl-pipeline/
│
├── airflow/
│   ├── dags/
│   │   └── etl_pipeline_dag.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── logs/
│   ├── plugins/
│   └── requirements.txt
│
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   └── order_items.csv
│   │
│   └── processed/
│
├── reports/
│   └── data_quality_report.json
│
├── logs/
│
├── sql/
│   ├── analytics.sql
│   ├── schema.sql
│   └── tables.sql
│
├── src/
│   ├── extract/
│   │   ├── csv_reader.py
│   │   ├── json_reader.py
│   │   └── api_client.py
│   │
│   ├── validate/
│   │   ├── validators.py
│   │   └── quality_report.py
│   │
│   ├── transform/
│   │   ├── customers.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   ├── order_items.py
│   │   ├── writer.py
│   │   └── run_transformations.py
│   │
│   ├── load/
│   │   ├── postgres.py
│   │   └── run_load.py
│   │
│   ├── config.py
│   ├── logger.py
│   └── pipeline.py
│
├── tests/
│   ├── test_extract.py
│   ├── test_postgres.py
│   ├── test_quality_report.py
│   ├── test_transform.py
│   ├── test_validation.py
│   └── test_incremental_load.py
│
├── Dockerfile
├── docker-compose.yml
├── main.py
├── pytest.ini
└── README.md
```

---

## ETL Pipeline

### 1. Extraction

The extraction layer reads source data from CSV files.

Supported extraction modules include:

```text
src/extract/csv_reader.py
src/extract/json_reader.py
src/extract/api_client.py
```

CSV extraction validates that the requested file exists and has the expected `.csv` extension before loading it with Pandas.

---

### 2. Validation

The validation layer checks incoming datasets before transformation.

Examples include:

* Required column validation
* Duplicate detection
* Missing-value detection
* Email-format validation
* Customer age validation
* Product price validation
* Product cost validation
* Discount validation
* Order-total validation
* Order-item quantity validation

This separates data-quality checks from transformation logic.

---

### 3. Transformation

Each dataset has its own transformation module.

#### Customers

Transformations include:

* Numeric ID normalization
* Name cleanup
* Lowercase email normalization
* Uppercase country normalization
* Age conversion
* Date conversion
* Marketing opt-in normalization

#### Products

Transformations include:

* Numeric IDs
* Category/name cleanup
* Numeric price and cost conversion
* Monetary rounding
* Margin calculation

```text
margin_usd = price_usd - cost_usd
```

#### Orders

Transformations include:

* ID normalization
* Timestamp conversion
* Payment-method normalization
* Country normalization
* Device normalization
* Traffic-source normalization
* Monetary field normalization

#### Order Items

The order-item transformation:

1. Removes exact duplicate records
2. Normalizes numeric fields
3. Recalculates line totals
4. Aggregates repeated order/product combinations

```text
line_total_usd = unit_price_usd × quantity
```

The raw order-item dataset contained 59,163 rows and the transformed dataset contains 59,053 rows.

---

## PostgreSQL Loading

The PostgreSQL loader supports two modes.

### Full Refresh

```bash
python main.py --mode full
```

This mode rebuilds the target data from the processed datasets.

### Incremental Loading

```bash
python main.py --mode incremental
```

Incremental loading uses staging tables and PostgreSQL:

```sql
INSERT ... ON CONFLICT DO UPDATE
```

The load order follows table dependencies:

```text
customers
    ↓
products
    ↓
orders
    ↓
order_items
```

Primary keys:

```text
customers       → customer_id
products        → product_id
orders          → order_id
order_items     → (order_id, product_id)
```

Database operations are performed transactionally so the incremental load can be committed as a unit.

---

## Incremental Processing

The pipeline was specifically tested for repeated execution.

After an incremental run, the database contained:

```text
customers      20,000
products        1,197
orders         33,580
order_items    59,053
```

A subsequent incremental execution preserved the same database row counts, demonstrating idempotent behavior for the tested dataset.

---

## Data Quality Reporting

The pipeline generates:

```text
reports/data_quality_report.json
```

The raw-data quality report records:

```text
customers
rows:       20,000
duplicates: 0
status:     PASS

products
rows:        1,197
duplicates: 0
status:     PASS

orders
rows:       33,580
duplicates: 0
status:     PASS

order_items
rows:       59,163
duplicates: 73
status:     WARN
```

The report describes the source data before transformation. The transformation stage subsequently reduces the order-item dataset to 59,053 rows.

---

## Analytics

The project includes an analytical SQL layer in:

```text
sql/analytics.sql
```

The queries cover:

* Overall KPIs
* Total customers
* Total units sold
* Revenue by country
* Revenue by category
* Top products
* Product profitability
* Monthly revenue
* Daily orders
* Payment-method distribution
* Device performance
* Traffic-source performance
* Discount impact
* Customer purchase frequency
* Customer lifetime value
* Customer segmentation
* Top customers
* Order-value distribution

Example calculated metrics include:

```text
Distinct customers with orders: 16,268
Orders:                         33,580
Revenue:                 4,493,217.47
Average Order Value:           133.81
```

---

## Logging

The pipeline provides structured logging through:

```text
logs/pipeline.log
logs/errors.log
```

The logging system provides:

* INFO-level pipeline events
* ERROR-level failures
* Console output
* Timestamped messages
* Separate error logging

Example:

```text
2026-09-28 05:28:26 | INFO | etl_pipeline | Starting ETL pipeline
```

---

## Testing

The project uses Pytest.

The test suite covers:

* Extraction
* Validation
* Transformation
* PostgreSQL loading
* Data-quality reporting
* Incremental loading

Latest test result:

```text
33 passed
```

Run the complete test suite:

```bash
pytest
```

---

## Docker

The ETL application is containerized using Docker.

Build the ETL image:

```bash
docker build -t automated-etl-pipeline:latest .
```

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Run the ETL container:

```bash
docker compose run --rm etl
```

The container connects to PostgreSQL through the Docker Compose network.

Inside Docker:

```text
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

From the host machine:

```text
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
```

---

## Docker Compose

The Compose environment provides:

```text
PostgreSQL
    │
    └── automated-etl-pipeline
```

PostgreSQL uses a persistent Docker volume.

The ETL container is configured to execute incremental processing:

```bash
python main.py --mode incremental
```

---

## Airflow Orchestration

Apache Airflow orchestrates the ETL pipeline.

The DAG is:

```text
airflow/dags/etl_pipeline_dag.py
```

The DAG uses:

```text
DockerOperator
```

to execute:

```bash
python main.py --mode incremental
```

inside the ETL Docker image.

Architecture:

```text
Apache Airflow
      │
      ▼
DockerOperator
      │
      ▼
automated-etl-pipeline:latest
      │
      ▼
Python ETL
      │
      ▼
PostgreSQL
```

The DAG is scheduled using:

```python
schedule="0 2 * * *"
```

Therefore, the configured schedule is:

```text
Every day at 02:00
```

The DAG has been manually executed successfully, with the ETL task reaching:

```text
success
```

---

## Running Airflow

Start Airflow:

```bash
docker compose -f airflow/docker-compose.yml up -d
```

Check the DAG:

```bash
docker exec etl_airflow airflow dags list
```

Trigger the DAG manually:

```bash
docker exec etl_airflow airflow dags trigger automated_etl_pipeline
```

Check scheduler health:

```bash
docker exec etl_airflow airflow jobs check --job-type SchedulerJob
```

The Airflow web interface is available at:

```text
http://localhost:8080
```

---

## Complete Execution Flow

The complete system can be summarized as:

```text
                SOURCE DATA
                    │
                    ▼
              ┌───────────┐
              │ Extraction│
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │ Validation│
              └─────┬─────┘
                    │
                    ▼
             ┌──────────────┐
             │Transformation│
             └──────┬───────┘
                    │
                    ▼
             ┌──────────────┐
             │  PostgreSQL  │
             └──────┬───────┘
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   ┌─────────────┐     ┌───────────────┐
   │  Analytics  │     │ Quality Report│
   └─────────────┘     └───────────────┘

                    ▲
                    │
              ┌─────┴─────┐
              │  Airflow  │
              └─────┬─────┘
                    │
              DockerOperator
                    │
                    ▼
                 ETL Job
```

---

## Configuration

Create a `.env` file:

```env
POSTGRES_DB=etl_database
POSTGRES_USER=etl_user
POSTGRES_PASSWORD=etl_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
```

The `.env` file should not be committed to Git.

---

## Local Setup

Clone the repository:

```bash
git clone <your-repository-url>
cd automated-etl-pipeline
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Run a full load:

```bash
python main.py --mode full
```

Run an incremental load:

```bash
python main.py --mode incremental
```

---

## Engineering Highlights

This project demonstrates several practical data-engineering concepts:

* Modular ETL architecture
* Separation of extraction, validation, transformation, and loading
* Schema-aware PostgreSQL loading
* Incremental upsert processing
* Transaction management
* Data-quality monitoring
* Idempotent pipeline execution
* Structured logging
* Automated testing
* Containerized execution
* Workflow orchestration
* Scheduled data processing

---

## Current Scope

The current implementation is designed as a local/dev portfolio demonstration of an automated ETL/ELT architecture.

Airflow currently uses a local SQLite metadata database and LocalExecutor configuration. A production deployment would typically use a dedicated PostgreSQL metadata database and a production-oriented Airflow deployment architecture.

---

## Future Improvements

Potential extensions include:

* REST API ingestion
* JSON ingestion
* Cloud object-storage sources
* PostgreSQL metadata for Airflow
* Production Airflow deployment
* Data warehouse integration
* dbt transformations
* Data lineage
* Monitoring dashboards
* Alerting
* CI/CD
* Cloud deployment
* Kubernetes orchestration
* Streaming ingestion

---

## Project Status

```text
Extraction              ✓
Validation              ✓
Transformation          ✓
PostgreSQL              ✓
Incremental Loading     ✓
Idempotency             ✓
Data Quality            ✓
Analytics               ✓
Logging                 ✓
Testing                 ✓
Docker                  ✓
Docker Compose          ✓
Airflow                 ✓
DockerOperator          ✓
Automatic Scheduling    ✓
Documentation           ✓
```

**Status: Complete end-to-end ETL/ELT portfolio project**
