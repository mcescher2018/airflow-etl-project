# Weather ETL Project — Getting Started

This project runs a weather ETL pipeline using **Apache Airflow**, with local storage in **DuckDB** and an optional **Streamlit** UI.  

All commands are executed from the **project root**.

---

## 1. Requirements

Core project requirements:

* Docker + Docker Compose  
* `.env` file in the project root  
* `variables.json` in `airflow/include/`  

Optional requirements for Streamlit UI and ETL tests:

* Python 3.10+  
* `pip install -r requirements.txt`

---

## 2. Configuration

### 2.1 Environment file (`.env`)

The repository includes a template:

```text
.env.example
```

Create your local environment file:

```bash
cp .env.example .env
```

Then edit `.env` with your personal values:

```text
FERNET_KEY
EMAIL_BACKEND (local or cloud)
LOCAL_EMAIL_SENDER_ADDRESS
CLOUD_EMAIL_ENDPOINT
CLOUD_EMAIL_SENDER_ADDRESS
CLOUD_EMAIL_API_KEY
```

#### Local email (MailHog)

If you set:

```text
EMAIL_BACKEND=local
```

Airflow sends emails to MailHog, which runs as a service inside the Docker Compose stack.
MailHog web UI:

```text
http://localhost:8025
```

#### Cloud email (Mailgun, adaptable to other providers)

If you set:

```text
EMAIL_BACKEND=cloud
```

Airflow uses Mailgun via its HTTP API.

This “cloud” email backend is implemented in a way that can be adapted to other providers (see comments in `email_cloud.py`).

You must provide valid values for:

```text
CLOUD_EMAIL_ENDPOINT
CLOUD_EMAIL_SENDER_ADDRESS
CLOUD_EMAIL_API_KEY
```

### 2.2 Airflow variables (variables.json)
The repository includes a template:

```text
airflow/include/variables.example.json
```

Create your local variables file:

```bash
cp airflow/include/variables.example.json airflow/include/variables.json
```

Edit `variables.json` with your personal settings, for example:

```json
{
  "etl_owner": "your_owner_name",
  "etl_alert_email": "recipient@example.com",
  "etl_alert_ok_subject": "ETL Weather - Successful run",
  "etl_alert_ko_subject": "ETL Weather - Error alert",
  "etl_alert_template_ok_path": "/opt/airflow/include/alert_template_ok.html",
  "etl_alert_template_ko_path": "/opt/airflow/include/alert_template_ko.html",
  "weather_db_path": "/opt/airflow/data/weather.duckdb",
  "weather_csv_path": "/opt/airflow/data/weather_staging.csv",
  "weather_api_url" : "https://api.open-meteo.com/v1/forecast",
  "latitude" : 45.00,
  "longitude" : 11.00
}
```

These values are used by the DAG for notifications and weather API configuration.

## 3. Start Airflow

Launch the Airflow stack:

```bash
docker compose up -d
```

Airflow UI:

```text
http://localhost:8080
```

Default credentials:

```text
user: airflow
pass: airflow
```

## 4. Import Airflow variables

Import the variables into the Airflow instance:

```bash
docker exec -it airflow-etl-project-airflow-apiserver-1 \
  airflow variables import /opt/airflow/include/variables.json
```

This loads all required configuration values (paths, email settings, coordinates, etc.).

## 5. Run the pipeline

In the Airflow UI:

* Open DAGs
* Enable weather_etl_dag
* Trigger it manually or wait for the scheduled run
* Logs and task details are available directly from the UI.

## 6. Stop the stack

Shut down the stack:

```bash
docker compose down
```

## 7. Optional tools

### 7.1 Streamlit UI

A minimal viewer (`weather_online.py`) allows inspecting DuckDB data.

A simple dashboard (`weather_dashboard.py`) is dedicated to data quality and KPI.

Run them from the project root with commands like this:

```bash
streamlit run weather_online.py
```

### 7.2 DuckDB Client

For interactive SQL exploration of the DuckDB database, you can optionally use duckcli:

```bash
duckcli airflow/data/weather.duckdb
```

### 7.3 ETL tests

Refer to the [testing section](docs/testing/) for OS, container, and observability tests.

## 8. Minimal workflow

* Copy .env.example → .env and fill in your secrets
* Copy variables.example.json → variables.json and fill in your settings
* Start Airflow with docker compose up -d
* Import variables into Airflow
* Enable and trigger weather_etl_dag
* Inspect logs or use the optional UI
* Stop the stack with docker compose down