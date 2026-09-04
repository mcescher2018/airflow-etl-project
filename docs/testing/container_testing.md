# Container testing

This validates the ETL pipeline in the same environment used by Airflow.

## 1 Pre-Requisites

Before running tests inside a container, make sure the full Airflow environment is up and running and file `variables.json` is imported.

Airflow Variables are stored in the metadata database and shared across all Airflow components.

If needed, verify that they are available with:

```bash
airflow variables export -
```

As first, enter the worker container:

```bash
docker exec -it airflow-etl-project-airflow-worker-1 bash
```

Then run single modules or trigger the whole DAG.

## 2 Run single modules

```bash
python /opt/airflow/etl/extract.py 2026-09-01 "https://api.open-meteo.com/v1/forecast?latitude=44.50&longitude=11.34&hourly=temperature_2m,precipitation"
python /opt/airflow/etl/transform.py /opt/airflow/etl_test/sample_extract_output.json /opt/airflow/etl_test/sample_transform_output.csv
python /opt/airflow/etl/load.py /opt/airflow/etl_test/sample_transform_output.csv /opt/airflow/etl_test/sample_db.duckdb
python /opt/airflow/etl/email_local.py "Subject" "<p>Hello</p>" "your_destination_address@example.com"
python /opt/airflow/etl/email_cloud.py "Subject" "<p>Hello</p>" "your_destination_address@example.com"
```

Note: Inside Docker, MailHog is already available as:

```bash
mailhog:1025
```

## 3 Validate the DAG

Enter the scheduler container:

```bash
docker exec -it airflow-etl-project-airflow-scheduler-1 bash
```

Before moving a DAG (for example `weather_etl_dag.py`) from `dags_dev` to `dags`, run two validation steps.

### 3.1 Validate Python syntax

This checks pure Python syntax (indentation, missing parentheses, typos).

It does not import Airflow modules or execute the DAG.

```bash
python -c "import dags_dev.weather_etl_dag"
```

If the command returns no output, the file is syntactically valid.

### 3.2 Validate DAG importability

This simulates what Airflow does when loading a DAG.

It imports the module, resolves all imports, and builds the DAG object.

```bash
python -m py_compile /opt/airflow/dags_dev/weather_etl_dag.py
```

If the command returns no output, the DAG is importable and safe to move into `dags/`.

If errors appear, fix them while the DAG is still in `dags_dev` to avoid breaking the scheduler.