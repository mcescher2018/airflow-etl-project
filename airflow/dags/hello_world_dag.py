from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

def hello_python():
    print("Hello from PythonOperator!")

with DAG(
    dag_id="hello_world_dag",
    start_date=datetime(2026, 1, 1),
    schedule="*/5 * * * *",   # every 5 minutes
    catchup=False,
) as dag:

    hello_bash = BashOperator(
        task_id="hello_bash_task",
        bash_command='echo "Hello from BashOperator!"'
    )

    hello_py = PythonOperator(
        task_id="hello_python_task",
        python_callable=hello_python
    )

    hello_bash >> hello_py
