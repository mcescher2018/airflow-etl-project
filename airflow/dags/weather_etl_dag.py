import os
import requests
from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.providers.standard.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.standard.sensors.python import PythonSensor
from jinja2 import Template

from etl.extract import extract
from etl.transform import transform
from etl.load import load

if os.getenv("EMAIL_BACKEND", "local") == "cloud":
    from etl.email_cloud import send_email
else:
    from etl.email_local import send_email

def build_api_url():
    api_url = Variable.get("api_url", default_var="https://api.open-meteo.com/v1/forecast")
    latitude = Variable.get("latitude", default_var=44.50)
    longitude = Variable.get("longitude", default_var=11.34)

    return f"{api_url}?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,precipitation"

def api_available():
    url = build_api_url()
    r = requests.get(url, timeout=5)
    return r.status_code == 200

def extract_task(ds, ti, **kwargs):
    try:
        # Read full_url from airflow varables
        full_url = build_api_url()
        
        # Call extract level
        raw_data = extract(ds, full_url)
        
        # Store raw data in JSON
        ti.xcom_push(key="raw_data", value=raw_data)
        return {"status": "ok"}
    except Exception:
        return {"status": "failed"}
    
def transform_task(ti, **kwargs):
    try:
        # Read CSV filename from Variables
        filename = Variable.get("weather_csv_path", default_var="/opt/airflow/data/weather_staging.csv")
    
        # Read JSON data from XCom
        raw = ti.xcom_pull(key="raw_data", task_ids="extract_task")
    
        # Call transform level and fill weather_staging.csv
        transform(raw, filename)
        return {"status": "ok"}
    except Exception:
        return {"status": "failed"}
    
def load_task(ti, **kwargs):
    try:
        # Read DB filename from Variables
        db_path = Variable.get("weather_db_path", default_var="/opt/airflow/data/weather.duckdb")
    
        # Read CSV filename from Variables
        filename = Variable.get("weather_csv_path", default_var="/opt/airflow/data/weather_staging.csv")
        
        # Call load level to upsert into DuckDB
        load(filename, db_path)
        return {"status": "ok"}
    except Exception:
        return {"status": "failed"}
    
def choose_email_branch(**kwargs):
    ti = kwargs["ti"]
    upstream = kwargs["task"].upstream_task_ids

    failed = []
    for t in upstream:
        x = ti.xcom_pull(task_ids=t)
        if not x or x.get("status") != "ok":
            failed.append(t)

    return "send_alert_email_ko_task" if failed else "send_alert_email_ok_task"

def send_alert_email_task(template_path, subject, **kwargs):
    alert_email = Variable.get("etl_alert_email")

    with open(template_path) as f:
        raw_html = f.read()

    # Render Jinja template using Airflow context
    template = Template(raw_html)
    rendered_html = template.render(**kwargs)

    send_email(
        subject=subject,
        html=rendered_html ,
        to=[alert_email]
    )

default_args = {
    "owner": Variable.get("etl_owner", default_var="unknown"),
    "retries": 3,
    "retry_delay": timedelta(minutes=15),
    "retry_exponential_backoff": True
}

with DAG(
    dag_id="weather_etl_dag",
    start_date=datetime(2026, 9, 1),
    schedule="0 */3 * * *", # every 3 hours
    catchup=False,
    default_args=default_args,
) as dag:

    api_sensor = PythonSensor(
        task_id="api_availability_sensor",
        python_callable=api_available,
        poke_interval=30,
        timeout=300,
    )

    extract_op = PythonOperator(
        task_id="extract_task",
        python_callable=extract_task,
    )

    transform_op = PythonOperator(
        task_id="transform_task",
        python_callable=transform_task,
    )

    load_op = PythonOperator(
        task_id="load_task",
        python_callable=load_task,
    )

    branch_op = BranchPythonOperator(
        task_id="branch_email_task",
        python_callable=choose_email_branch
    )

    send_alert_email_ok_op = PythonOperator(
        task_id="send_alert_email_ok_task",
        python_callable=send_alert_email_task,
        op_kwargs={
            "template_path": Variable.get("etl_alert_template_ok_path"),
            "subject": Variable.get("etl_alert_ok_subject"),
        },
        trigger_rule="none_failed",  # applied if not skipped by branch, case OK
    )

    send_alert_email_ko_op = PythonOperator(
        task_id="send_alert_email_ko_task",
        python_callable=send_alert_email_task,
        op_kwargs={
            "template_path": Variable.get("etl_alert_template_ko_path"),
            "subject": Variable.get("etl_alert_ko_subject"),
        },
        trigger_rule="none_failed",  # applied if not skipped by branch, case KO
    )

# make ETL status available for branch_op
extract_op >> branch_op
transform_op >> branch_op
load_op >> branch_op

# main flow
api_sensor >> extract_op >> transform_op >> load_op >> branch_op

# final branch
branch_op >> send_alert_email_ok_op
branch_op >> send_alert_email_ko_op