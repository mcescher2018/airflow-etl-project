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

Then run single modules or validate the whole DAG.

## 2 Run single modules

```bash
python /opt/weather_airflow/etl/extract.py 2026-09-01 "https://api.open-meteo.com/v1/forecast?latitude=44.50&longitude=11.34&hourly=temperature_2m,precipitation"
python /opt/weather_airflow/etl/transform.py /opt/weather_airflow/etl_test/sample_extract_output.json /opt/weather_airflow/etl_test/sample_transform_output.csv
python /opt/weather_airflow/etl/load.py /opt/weather_airflow/etl_test/sample_transform_output.csv /opt/weather_airflow/etl_test/sample_db.duckdb
python /opt/weather_airflow/etl/email_local.py "Subject" "<p>Hello</p>" "your_destination_address@example.com"
python /opt/weather_airflow/etl/email_cloud.py "Subject" "<p>Hello</p>" "your_destination_address@example.com"
```

Note: Inside Docker, MailHog is already available as:

```bash
mailhog:1025
```

## 3 Validate the DAG

Before moving a DAG (for example `weather_etl_dag.py`) from `dags_dev` to `dags`, is important to perform the following preliminar test.

Enter the scheduler container:

```bash
docker exec -it airflow-etl-project-airflow-scheduler-1 bash
```

Then run:

```bash
python -m py_compile /opt/weather_airflow/dags_dev/weather_etl_dag.py
```

This checks pure Python syntax (indentation, missing parentheses, typos) and should give no output messages.

Note: It does not import Airflow modules or execute the DAG, it is possible only from the UI (see observability documents).