import os
import requests
from datetime import datetime, timedelta

from airflow import DAG
from airflow.sdk import get_current_context, Variable
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.sensors.python import PythonSensor
from jinja2 import Template

from etl.extract import extract
from etl.transform import transform
from etl.load import load
from etl.email_cloud import send_email as send_email_cloud
from etl.email_local import send_email as send_email_local

def choose_email_backend():

    backend = os.getenv("EMAIL_BACKEND", "local")

    if backend == "cloud":
        return send_email_cloud
    else:
        return send_email_local

def build_api_url():

    api_url = Variable.get("weather_api_url")
    latitude = Variable.get("latitude")
    longitude = Variable.get("longitude")

    return f"{api_url}?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,precipitation"

def api_available():

    try:
        # Build the API URL from configuration
        url = build_api_url()

        # Perform the HTTP request with a short timeout
        response = requests.get(url, timeout=5)

        # API is reachable and returns HTTP 200
        if response.status_code == 200:
            return True

        # API responded but not with a success status code
        return False

    except Exception as e:
        print(f"API availability check failed: {e}")
        return False

def extract_task(ds):

    context = get_current_context()
    ti = context["ti"]

    try:
        # Read full_url from airflow varables
        full_url = build_api_url()
        
        # Call extract level
        raw_data = extract(ds, full_url)
        
        # Store raw data in JSON
        ti.xcom_push(key="raw_data", value=raw_data)

    except Exception as e:
        print(f"Extract task failed: {e}")
        raise
    
def transform_task():

    context = get_current_context()
    ti = context["ti"]

    try:
        # Read CSV filename from Variables
        filename = Variable.get("weather_csv_path")
    
        # Read JSON data from XCom
        raw = ti.xcom_pull(key="raw_data", task_ids="extract_task")
    
        # Call transform level and fill weather_staging.csv
        transform(raw, filename)

    except Exception as e:
        print(f"Transform task failed: {e}")
        raise
    
def load_task():

    try:
        # Read DB filename from Variables
        db_path = Variable.get("weather_db_path")
    
        # Read CSV filename from Variables
        filename = Variable.get("weather_csv_path")
        
        # Call load level to upsert into DuckDB
        load(filename, db_path)

    except Exception as e:
        print(f"Load task failed: {e}")
        raise
    
def send_alert_email_task(template_path, subject):

    context = get_current_context()
    send_email = choose_email_backend()

    try:
        alert_email = Variable.get("etl_alert_email")

        with open(template_path) as f:
            raw_html = f.read()

        # Render Jinja template using Airflow context
        template = Template(raw_html)
        rendered_html = template.render(**context)

        send_email(
            subject=subject,
            html=rendered_html,
            to=[alert_email]
        )

    except Exception as e:
        print(f"Send email task failed: {e}")
        raise

default_args = {
    "owner": Variable.get("etl_owner"),
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
        timeout=300
    )

    extract_op = PythonOperator(
        task_id="extract_task",
        python_callable=extract_task
    )

    transform_op = PythonOperator(
        task_id="transform_task",
        python_callable=transform_task
    )

    load_op = PythonOperator(
        task_id="load_task",
        python_callable=load_task
    )

    send_alert_email_ok_op = PythonOperator(
        task_id="send_alert_email_ok_task",
        python_callable=send_alert_email_task,
        op_kwargs={
            "template_path": Variable.get("etl_alert_template_ok_path"),
            "subject": Variable.get("etl_alert_ok_subject"),
        },
        trigger_rule="all_success",
    )

    send_alert_email_ko_op = PythonOperator(
        task_id="send_alert_email_ko_task",
        python_callable=send_alert_email_task,
        op_kwargs={
            "template_path": Variable.get("etl_alert_template_ko_path"),
            "subject": Variable.get("etl_alert_ko_subject"),
        },
        trigger_rule="one_failed"
    )

# Main Flow
api_sensor >> extract_op >> transform_op >> load_op

# Email send, template chosen by trigger_rule
load_op >> send_alert_email_ok_op
load_op >> send_alert_email_ko_op