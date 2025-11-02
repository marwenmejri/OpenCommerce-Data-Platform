# OpenCommerce Data Platform

**A fully containerized, open-source data platform demo** that scrapes raw e‑commerce data, ingests it to Snowflake (raw/staging), runs dbt transformations & tests, stores analytics-ready results in PostgreSQL, and serves BI dashboards with Superset. Orchestrated with Apache Airflow and built for learning, iteration, and easy deployment via Docker Compose.

---

## Project goals

- Demonstrate a simple, production-like ELT pipeline using open-source tools.
- Show ingestion of *raw* scraped data, transformations with **dbt**, testing and alerting in **Airflow**.
- Use **Snowflake** as raw/staging storage (external), **Postgres** as analytics store and for Airflow metadata, and **Superset** for reporting.
- Provide extensible utilities (scraper, Snowflake loader, dbt helper, email alerts) and easy-to-run docker-compose setup for local experimentation.

---

## Architecture (high-level)

1. **Scraping layer** — Python scraper(s) (e.g. `scraper_utils.py`) produce raw JSON/Parquet files (products, reviews, categories, brands).
2. **Landing / Raw zone** — Raw files saved in MinIO (S3-compatible) or uploaded directly to Snowflake staging.
3. **Ingestion layer** — Airflow DAGs run ingestion tasks (PythonOperators) to load raw data into Snowflake (COPY/PUT or Snowflake connector).
4. **Transformation layer** — dbt project (models, macros, tests) for transforming raw into curated marts. dbt test outputs saved to `target/run_results.json`.
5. **Testing + Alerting** — Airflow runs dbt; on failures, we parse `run_results.json` and send alerts (email or Slack).
6. **Serving layer** — Transformed data loaded into PostgreSQL for BI; Superset connects to PostgreSQL for dashboards.

---

## Folder structure

```
opencommerce-data-platform/
├── dags/                         # Airflow DAGs (scrape, ingest, dbt, alerts)
├── dbt/                          # dbt project (models, tests, macros)
├── utils/                        # reusable helpers (scraper, dbt_utils, email_utils)
├── scripts/                      # small standalone scripts (loaders, local dev helpers)
├── docker-compose.yml            # local stack (Airflow, Postgres, MinIO, Superset)
├── .env                          # environment variables (not committed to git)
└── README.md                     # this file
```

---

## Quickstart (Local)

> assumes Docker & Docker Compose installed.

1. **Clone the repo**

```bash
git clone <your-repo-url>
cd opencommerce-data-platform
```

2. **Create `.env` file** (copy `.env.example` or create new) and populate secrets. Example variables used by the stack:

```env
# Postgres (Airflow metadata + analytics)
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow

# Airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__FERNET_KEY=<generate-a-random-fernet-key>
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow

# SMTP (for alerts) — use app password if using 2FA
AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
AIRFLOW__SMTP__SMTP_STARTTLS=True
AIRFLOW__SMTP__SMTP_SSL=False
AIRFLOW__SMTP__SMTP_USER=you@example.com
AIRFLOW__SMTP__SMTP_PASSWORD=<app-password-or-secret>
AIRFLOW__SMTP__SMTP_PORT=587
AIRFLOW__SMTP__SMTP_MAIL_FROM=Airflow <you@example.com>

# Snowflake (optional external service)
SNOWFLAKE_ACCOUNT=<account>
SNOWFLAKE_USER=<user>
SNOWFLAKE_PASSWORD=<password>
SNOWFLAKE_ROLE=<role>
SNOWFLAKE_DATABASE=RAW_DB
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
```

3. **Bring the stack up**

```bash
# from project root
docker compose --env-file .env up --build
```

4. **Confirm services**

- Airflow Web UI: `http://localhost:8080` (username/password created by the startup script)
- Superset: `http://localhost:8088`
- MinIO console: `http://localhost:9001`

5. **Run the sample DAGs**

- Open Airflow UI → enable the DAG `scrape_products_dag` and trigger it.
- Check logs and ensure artifacts appear in `minio/` or `dbt/target` as expected.

---

## DAGs included (starter)

- `scrape_products_dag.py` — scrape raw product data (products, reviews, categories) and save to MinIO.
- `ingest_snowflake_dag.py` — load JSON/CSV from MinIO into Snowflake staging and raw tables.
- `dbt_transform_dag.py` — run dbt seed/run/test; store `run_results.json`.
- `alert_dag.py` — parse `run_results.json`, push failures to XCom, and send alerts (email/Slack).

Each DAG uses small reusable functions in `utils/` for clarity and testability.

---

## Key implementation notes

- **dbt tests**: dbt returns non‑zero exit codes on test failures by default. When running dbt via a BashOperator we must propagate non‑zero return codes. Example: avoid `|| echo "DBT TEST FAILED"` which masks the exit code. Instead let the command fail or capture output and programmatically raise exceptions in PythonOperator.

- **Email alerts**: we recommend using Airflow connections (`smtp_default`) but we also provide a helper that calls `send_email_smtp(..., conn_id=None, **overrides)` so you can force env-based SMTP details if needed.

- **XCom & visibility**: dbt failure summaries are saved to `target/failed_tests_summary.json` and the DAG pushes the summary and failure count to XCom for easy inspection in the Airflow UI.

- **Local network**: if you run Docker Desktop or Linux containers, consider `network_mode: "host"` only when you need host network visibility; avoid unless necessary. For SMTP and Snowflake connectivity, containers generally work with default bridge networking.

---

## Development tips

- Keep secrets out of Git. Use `.env` and `.gitignore` for local runs.
- Use small, testable utility functions in `utils/` and unit-test them with pytest.
- Use `docker compose logs -f <service>` for service-specific logs while debugging.
- Run `dbt debug` inside the container to verify profiles and DB connectivity.

---

## How to extend & scale

- Replace local MinIO with cloud S3 (AWS/GCP/Azure) for production.
- Move Airflow to a CeleryExecutor/KubernetesExecutor for distributed workers.
- Replace local Postgres for BI with a managed data warehouse (BigQuery, Snowflake final marts).
- Add CI pipeline (GitHub Actions) to run linting, unit tests, and dbt tests on PRs.
- Add monitoring: Prometheus + Grafana or Datadog, plus alerting to Slack.

---

*Created by Marwen Mejri.*

