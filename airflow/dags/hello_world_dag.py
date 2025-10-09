from datetime import datetime, timedelta

import psycopg2
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator


def hello_world():
    """Hello World function"""
    print("Hello from Airflow!")
    return "success"

def check_services():
    """Check the health of the airflow service"""
    try:
        response = requests.get("http://rag-api:8000/api/v1/health", timeout=5)
        print(f"API health": {response.status_code})

        conn = psycopg2.connect(host="postgres",port=5432,database = "rag_db",user="rag_user",password="rag_password")
        print("Database connected successfully")
        conn.close()

        return "Services are available"
    except Exception as e:
        print(f"Services check failed : {e}")
        raise

default_args = {
    "owner": "rag",
    "depends_on_post": False,
    "start_time": datetime(2024,1,1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes = 5), 
}

dag = DAG(
    "hello_world_task",
    default_args = default_args,
    description = "Health check service",
    schedule = None,
    catchup = False,
    tags = ["testing"],
)

hello_task = PythonOperator(
    task_id = "hello_world",
    python_callable = hello_world,
    dag = dag,
)

service_check_task = PythonOperator(
    task_id = "check_services",
    python_callable = check_services,
    dag = dag,
)

hello_task >> service_check_task
