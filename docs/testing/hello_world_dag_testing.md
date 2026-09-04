# Hello World DAG Test Report

The `hello_world_dag` is a minimal DAG used to validate the Airflow environment and confirm that basic task execution, logging, and UI visibility are functioning correctly.

This document presents the results of the tests performed on this DAG.

Given the simplicity of the code, only a subset of test categories has been applied.

Below are the screenshots collected during the variuos tests.
Comments are included only where necessary.

---

## 1. OS testing

No tests performed.

---

## 2. Container Testing

No tests performed.

---

## 3. Observability Testing

## 3.1 DAG Exists in UI

![Dag Exists in UI](../../screenshots/observability_testing/hello_world_dag/01_hello_world_exists_in_ui.png)

## 3.2 DAG Graph View

![Dag Graph View](../../screenshots/observability_testing/hello_world_dag/02_hello_world_dag-graph.png)

## 3.3 DAG Runs

![Dag Runs](../../screenshots/observability_testing/hello_world_dag/03_hello_world_runs.png)

The highlighted run is detailed in the component tasks shown in the sub‑sections below.

## 3.3.1 Hello World Bash Task

![Hello World Bash Task](../../screenshots/observability_testing/hello_world_dag/05_hello_world_log_bash_task.png)

## 3.3.2 Hello World Python Task

![Hello World Python Task](../../screenshots/observability_testing/hello_world_dag/06_hello_world_log_python_task.png)

## 4 Conclusions

All tests confirm that the DAG executes correctly and that the Airflow environment handles scheduling, logging, and notifications as expected.