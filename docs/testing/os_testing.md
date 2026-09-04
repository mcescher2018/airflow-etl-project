# OS Testing

This validates the ETL pipeline outside the Airflow environment.

## 1. Pre-Requisites

All test commands below assume that:

### 1.1. You are in the **project root**:

```bash
airflow-etl-project/
```

### 1.2. Mailhog is up and running

Start **MailHog** from the project root:

```bash
./mailhog
```

MailHog runs on:

- SMTP → `localhost:1025`
- UI → `http://localhost:8025`

### 1.3. Environment variables from `.env` are loaded into the shell:

```bash
set -a /
source .env /
set +a
```

This ensures that local tests use the same configuration values normally read by Airflow.

---

## 2. Direct Python Execution

Useful for quickly testing individual ETL modules with real data but outside Airflow.
Input and outputs are samples but no method is mocked.

### 2.1 Data Modules

To test main ETL functions use the followings commands, based on sample input and output files stored in airflow/etl_test/:

```bash
python airflow/etl/extract.py 2026-09-01 "https://api.open-meteo.com/v1/forecast?latitude=44.50&longitude=11.34&hourly=temperature_2m,precipitation"
python airflow/etl/transform.py airflow/etl_test/sample_extract_output.json airflow/etl_test/sample_transform_output.csv
python airflow/etl/load.py airflow/etl_test/sample_transform_output.csv airflow/etl_test/sample_db.duckdb
```

### 2.2 Local Email Backend

Test `email_local.py` requires valid values in `.env` file and MailHog running (see before).
In particular, EMAIL_BACKEND should be set to `local` and LOCAL_EMAIL_SENDER_ADDRESS to a sample address.
Use this command:

```bash
export EMAIL_BACKEND=local
python airflow/etl/email_local.py "Subject" "<p>Hello</p>" "your_destination_address@example.com"
```

After sending the command, check on your local MailHog if you see the email.

### 2.3 Cloud Email Backend

Test `email_cloud.py` requires valid values in `.env` file and MailGun (or another provider) correctly configured in cloud.
In particular, EMAIL_BACKEND should be set to `cloud`.
Use this command:

```bash
export EMAIL_BACKEND=cloud
python airflow/etl/email_cloud.py "Subject" "<p>Hello</p>" "your_destination_address@example.com"
```

After sending the command, check on your MailGun dashboard if you see the email.
Caution: with this test you are sending a real email.

---

## 3. Pytest

Useful for limit cases and to avoid regressions with future developments.

Commands for single unit tests:

```bash
pytest airflow/etl_test/test_extract.py -vv
pytest airflow/etl_test/test_transform.py -vv
pytest airflow/etl_test/test_load.py -vv
pytest airflow/etl_test/test_email_local.py -vv
pytest airflow/etl_test/test_email_cloud.py -vv
```

To run all unit tests, use this command:

```bash
pytest airflow/etl_test/ -vv
```

MailHog is **not required** here: SMTP calls are mocked.