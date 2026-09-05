# Weather ETL DAG Test Report

The `weather_etl_dag` is a fully operational ETL workflow designed to extract weather data from an external API, transform it into a structured format, and load it into a DuckDB database for downstream analysis and dashboard visualization.

This DAG serves as the core functional pipeline of the project, validating not only Airflow’s scheduling and task‑execution capabilities but also the correctness of the ETL logic, branching behavior, data persistence, and email‑based notifications.

This document presents the results of the tests performed on this DAG.
Given the complexity of the workflow, all three testing layers — OS testing, container testing, and observability testing — have been applied.

Below are the screenshots collected during the various tests.
Comments are included only where necessary.

---

## 1. OS testing

### 1.1 ETL Modules

![ETL Modules](../../screenshots/os_testing/weather_etl_modules_tests.png)

### 1.2 Email Modules

![Email Modules](../../screenshots/os_testing/weather_etl_email_tests.png)

### 1.3 All Unit Tests

![All Unit Tests](../../screenshots/os_testing/weather_etl_all_unit_tests.png)

Module tests were executed using Python with real (local) inputs and outputs, without mocks.  
Unit tests validate key functional contracts and rely on synthetic data and mocked methods.

---

## 2. Container Testing

### 2.1 ETL Modules

![ETL Modules](../../screenshots/container_testing/weather_etl_python_etl_modules_tests.png)

### 2.2 Email Modules

![Email Modules](../../screenshots/container_testing/weather_etl_python_email_tests.png)

### 2.3 DAG Verification

![DAG Verification](../../screenshots/container_testing/weather_etl_dag_verification.png)

---

## 3. Observability Testing

Before examining the observability screenshots, it is important to clarify how timestamps should be interpreted.

Airflow displays all execution times in UTC, while the underlying server is configured with the Europe/Rome timezone (CEST, UTC+2 at the time of testing).

This means that Airflow’s timestamps appear two hours behind local Italian time.

All comments and interpretations in the following subsections refer to local server time unless explicitly stated otherwise.

Another important note.

The ETL does not preserve historical snapshots and each run inserts new values if necessary and updates values falling in the 168-hour API window.

As a result, `time` is unique and can safely serve as the primary key.

## 3.1 DAG Exists in UI

![Dag Exists in UI](../../screenshots/observability_testing/weather_etl_dag/01_weather_etl_exists_in_ui.png)

## 3.2 DAG Graph View

![Dag Graph View](../../screenshots/observability_testing/weather_etl_dag/02_weather_etl_dag-graph.png)

## 3.3 DAG Runs

![Dag Runs](../../screenshots/observability_testing/weather_etl_dag/03_weather_etl_runs_and_chosen_example.png)

For the chosen example, this is the tasks results summary:

![Tasks Runs](../../screenshots/observability_testing/weather_etl_dag/04a_weather_etl_single_run_tasks.png)

The `send_alert_email_ko_task` is skipped because all upstream tasks completed successfully (`trigger_rule`="all_success" in `send_alert_email_ok_task` vs "one_failed" in the complementary ko task).

The detailed log of each task is shown in the subsections below.

### 3.3.1 Api Sensor

![Api Sensor](../../screenshots/observability_testing/weather_etl_dag/05_weather_etl_single_run_task_api_sensor.png)

### 3.3.2 Extract

![Extract](../../screenshots/observability_testing/weather_etl_dag/06_weather_etl_single_run_task_extract.png)

### 3.3.3 Transform

![Transform](../../screenshots/observability_testing/weather_etl_dag/07_weather_etl_single_run_task_transform.png)

### 3.3.4 Load

![Load](../../screenshots/observability_testing/weather_etl_dag/08_weather_etl_single_run_task_load.png)

### 3.3.5 Send Email

![Send Mail](../../screenshots/observability_testing/weather_etl_dag/10_weather_etl_single_run_task_send_ok.png)

### 3.3.6 MailHog Dashboard

In the project configuration the local email sender was used.

Here is the MailHog Inbox, with highlited the mail sent in this run:

![MailHog UI](../../screenshots/observability_testing/weather_etl_dag/11_weather_etl_single_run_task_mailhog_all_mails.png)

This is the corresponding mail body:

![MailHog UI](../../screenshots/observability_testing/weather_etl_dag/12_weather_etl_single_run_task_mailhog_ui.png)

## 3.4 (Streamlit) Data Online View

The API always returns a 7‑day hourly forecast, starting from the 00:00 of the current day.

As a result, past hours of the first day are included and each job run always processes a fixed window of 168 (24*7) input rows.

### 3.4.1 Online Data Part 1

![Online Data Part 1](../../screenshots/observability_testing/weather_etl_dag/13_weather_etl_data_online_view_part1.png)

### 3.4.2 Online Data Part 2

![Online Data Part 2](../../screenshots/observability_testing/weather_etl_dag/14_weather_etl_data_online_view_part2.png)

## 3.5 CSV Direct Inspection

### 3.5.1 CSV Last Update

![CSV Last Update](../../screenshots/observability_testing/weather_etl_dag/15_weather_etl_data_inspection_csv_last_update.png)

This report was written on 05/09/2026 at 10:30 (Italian time).  

The latest update of the data files is at 08:00 (06:00 server time), as expected, based on the scheduling configuration (runs every 3 hours starting at 00:00 server time, displayed in UTC in the Airflow UI).

### 3.5.2 CSV Content

![CSV Content](../../screenshots/observability_testing/weather_etl_dag/16_weather_etl_data_inspection_csv_content.png)

The CSV contains data from 05/09/2026 at 00:00 through 11/09/2026 at 23:00, representing the full 7‑day hourly forecast window returned by the API.

## 3.6 SQL Direct Inspection

### 3.6.1 Staging Table Content

![Staging Table Content](../../screenshots/observability_testing/weather_etl_dag/17_weather_etl_data_inspection_staging_table.png)

Staging table records correspond to the CSV content, having 24 rows per each day and consisting in 168 rows.

### 3.6.2 Records Newly Created

![Records Newly Created](../../screenshots/observability_testing/weather_etl_dag/19_weather_etl_data_inspection_sql_newly_created.png)

As expected, we have 24 new records and no record with  `creation_date = modified_date`.  

The initial load sets both timestamps, but all subsequent ETL runs update the data and therefore modify the `modified_date` field.

## 3.7 (Streamlit) Data Dashboard

### 3.7.1

![Data Dashboard Part 1](../../screenshots/observability_testing/weather_etl_dag/21_weather_etl_dashboard_part1.png)

### 3.7.2

![Data Dashboard Part 2](../../screenshots/observability_testing/weather_etl_dag/22_weather_etl_dashboard_part2.png)

No anomalies detected:

* `time` is the primary key, as the ETL maintains a single moving 168‑hour window and updates existing timestamps rather than preserving historical snapshots.  
* Impossible values are defined as `temperature_2m` outside the interval (‑80, +80) or `precipitation` outside (0, 500), since extreme precipitation events can reach values around 100 mm/h.

### 3.7.3

![Data Dashboard Part 3](../../screenshots/observability_testing/weather_etl_dag/23_weather_etl_dashboard_part3.png)

Updated records are those where `modified_date > creation_date`, and there are 192 of them as expected.

They include:

* Yesterday’s unchanged values, inserted earlier and updated during the last daily run (23:00 Italian time, 21:00 server time), totaling 24 records.
* Yesterday’s updated values, inserted yesterday and updated during today's run, totaling 144 records.    
* Today’s new values (24 records), created during the first daily run (02:00 Italian time, 00:00 server time) and updated by subsequent runs.

## 4 Conclusions

All observability checks confirm that the ETL pipeline runs reliably, load and updates data consistently within the 168‑hour window, and that the Airflow environment is correctly configured for scheduling, branching, logging, and notifications.