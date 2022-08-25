import datetime as dt

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowException
from de.utils.timeutils import UTC

dag = DAG(
    dag_id="test_dags",
    description="test_dags",
    start_date=dt.datetime(2022, 8, 24, 0, 0, tzinfo=UTC),
    schedule_interval="40 7 * * *",
    max_active_runs=4,
    default_args={
        "depends_on_past": False,
    },
)

def raise_airflow_exception():
    return AirflowException("Error!")


first_task = PythonOperator(
    task_id="first_task",
    python_callable=raise_airflow_exception,
    dag=dag,
)

must_do_it_task = BashOperator(
    task_id='must_do_it_task',
    bash_command="echo 'must do it task!'",
    trigger_rule="all_done",
    dag=dag,
)

first_task >> must_do_it_task
