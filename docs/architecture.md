# Architecture Overview

This project implements a minimal, modular ETL pipeline orchestrated with Apache Airflow.  
Its purpose is to extract weather data from a public API, transform it into a tabular format, and load it into a DuckDB database for lightweight analytics and inspection.

The architecture is intentionally simple: the DAG orchestrates the workflow, while the ETL logic lives in standalone Python modules that can be executed and tested independently of Airflow.

---

## 1. Pipeline Structure

The pipeline consists of three core ETL steps:

- **Extract** — retrieves hourly weather data from the Open‑Meteo API  
- **Transform** — converts the JSON payload into a CSV file  
- **Load** — inserts the transformed data into a DuckDB database  

Additional reliability and observability features include:

- an API availability check (`ApiSensor`)  
- explicit error propagation inside each ETL module  
- branching logic for success/failure notifications  
- structured logs visible in the Airflow UI  

---

## 2. Airflow Layout

The `airflow/` directory contains all components required by Airflow, plus development and testing support:

- `dags/` — production DAGs  
- `dags_dev/` — development DAGs  
- `etl/` — pure Python modules implementing extract, transform, and load  
- `etl_test/` — standalone test scripts for ETL modules  
- `include/` — support files (variables, email templates, sample data)  
- `data/` — staging CSV files and the DuckDB database  
- `logs/` — Airflow execution logs  
- `config/` and `plugins/` — optional configuration and extensions  

Inside the container, this directory is mounted at `/opt/airflow`.

---

## 3. DAG–Module Decoupling

The DAG does not contain ETL logic. It only:

- calls the Python modules  
- defines dependencies  
- handles scheduling and retries  
- manages notifications  

The ETL modules are standalone Python functions that can be executed directly from the OS, tested without Airflow, and reused in other contexts.

---

## 4. Reliability & Observability

The pipeline includes lightweight features that improve robustness and make execution easy to inspect:

- `API availability check`  
  Ensures the upstream weather API is reachable before the ETL begins.

- `explicit error propagation`  
  ETL modules raise meaningful exceptions, allowing Airflow to surface failures cleanly.

- `success/failure branching`  
  The DAG sends different emails depending on the final outcome of the pipeline.

- `structured logs in Airflow UI`  
  All modules log key steps and errors for straightforward debugging.

---

## 5. Email Backend Support

The project supports two email backends, selectable via the `EMAIL_BACKEND` environment variable:

- **local backend** — uses MailHog for development and testing  
- **cloud backend** — uses Mailgun for real email delivery  

The implementation is modular and can be easily extended to additional providers by adding new backend classes and updating the configuration in `include/variables.json`.

---

## 6. Optional Components

Two optional elements complement the core ETL pipeline:

- `ui/` — Streamlit viewers for inspecting DuckDB data directly from the host machine  
- `etl_test/` — lightweight Python unit tests for the ETL modules  

Additional testing procedures (OS‑level, container‑level, and observability checks) are documented in the `docs/` folder.

---

## 7. Summary

The architecture is designed to be clear and approachable:

- Airflow orchestrates the workflow  
- Python modules implement the ETL logic  
- DuckDB stores the final data  
- Optional UI and tests enhance inspection and validation  
- Email backends provide flexible notification support