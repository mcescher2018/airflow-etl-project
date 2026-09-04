# Weather ETL Project

## 1. Overview

A lightweight, modular ETL pipeline built with Apache Airflow.  

It retrieves weather data from a public API, processes it through a small set of Python modules, and stores the final results in a DuckDB data warehouse.  

The project is intentionally minimal: easy to read, easy to extend, and suitable both for learning and for small production‑grade workflows.

---

## 2. Project Structure & Architecture

This is the project structure, showing how the main components are organized within the repository.

```text
.
├── airflow
│   ├── config
│   ├── dags
│   ├── dags_dev
│   ├── data
│   ├── etl
│   ├── etl_test
│   ├── include
│   ├── logs
│   └── plugins
├── docs
├── screenshots
└── ui
```

For more design details see [Architecture](docs/architecture.md) document.

---

## 3. Requirements

This project requires:

- Docker + Docker Compose
- Python 3.10+ (for optional UI and local tests)

For full setup instructions, see [Getting Started](docs/getting_started.md).

## 4. Testing

Testing in this project is organized into three complementary layers, each targeting a different aspect of the Airflow ecosystem:

- [OS Testing](docs/testing/os_testing.md) — validates ETL and email modules directly on the host machine, outside of Airflow.
- [Container Testing](docs/testing/container_testing.md) — verifies modules and DAG behavior inside the Airflow Docker environment.
- [Observability Guidelines](docs/testing/observability_testing_guidelines.md) — provides instructions for inspecting DAG runs, logs, KPIs, and data outputs through the Airflow UI and dashboards.

In addition to these guidelines, full test reports are available for each DAG:

- [Hello World DAG Test Report](docs/testing/hello_world_dag_testing.md)
- [Weather ETL DAG Test Report](docs/testing/weather_etl_testing.md)

These documents include screenshots, execution traces, and detailed results across all three testing layers.

---

## 5. Environment

The entire Airflow ETL system — including development, execution, and testing — runs on the following setup:

- Host machine: Windows 10, Intel i7  
- Virtualization: Hyper‑V  
- Guest OS: Ubuntu 22.04 (GUI)  
- Airflow environment: Airflow 3.3 running inside Docker containers within the VM