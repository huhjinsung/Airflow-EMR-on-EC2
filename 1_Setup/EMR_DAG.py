from airflow import DAG
import airflow.utils.dates
from datetime import timedelta
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.operators.emr import EmrCreateJobFlowOperator
from airflow.providers.amazon.aws.operators.emr import EmrAddStepsOperator
from airflow.providers.amazon.aws.operators.emr import EmrTerminateJobFlowOperator
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor
import os

DS = '{{ ds }}'
RAW_DATA=Variable.get('RAW_DATA_PATH')
SUBNET_ID=Variable.get('SUBNET_ID')
SPARK_JOB_DIR=Variable.get('S3_PATH')+"/spark_job.py"
LOG_DIR=Variable.get('S3_PATH')+"/EMR/"
JAR_DIR=Variable.get('S3_PATH')+"/mysql-connector-j-8.3.0.jar"
AURORA_ENDPOINT=Variable.get('AURORA_ENDPOINT')

SPARK_STEPS = [
    {
        "Name": "AIRFLOW_EMR" + DS,
        "ActionOnFailure": "CONTINUE",
        #"ActionOnFailure": "TERMINATE_CLUSTER",
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": ["spark-submit", "--deploy-mode", "cluster", "--jars", JAR_DIR, SPARK_JOB_DIR, RAW_DATA, AURORA_ENDPOINT]
        },
    }
]

JOB_FLOW_OVERRIDES = {
    "Name": "EMR_CLUSTER" + DS,
    "ReleaseLabel": "emr-6.14.0",
    "LogUri":LOG_DIR,
    "Applications": [{"Name": "Spark"}],
    "Instances": {
        "InstanceGroups": [
            {
                'Name': "Master nodes",
                'Market': 'ON_DEMAND',
                'InstanceRole': 'MASTER',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 1,
            },
            {
                'Name': "Slave nodes",
                'Market': 'ON_DEMAND',
                'InstanceRole': 'CORE',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 1,
            },
                        {
                'Name': "Task nodes",
                'Market': 'ON_DEMAND',
                'InstanceRole': 'TASK',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 1,
            }
        ],
        "KeepJobFlowAliveWhenNoSteps": True,
        "TerminationProtected": False,
        'Ec2SubnetId': SUBNET_ID
    },
    "JobFlowRole": "emr-ec2-role",
    "ServiceRole": "emr-service-role",
}

def print_argument():
    print(f"RAW_DATA = {RAW_DATA}")
    print(f"SUBNET_ID = {SUBNET_ID}")
    print(f"SPARK_JOB_DIR = {SPARK_JOB_DIR}")
    print(f"LOG_DIR = {LOG_DIR}")
    print(f"JAR_DIR = {JAR_DIR}")
    print(f"AURORA_ENDPOINT = {AURORA_ENDPOINT}")

# Define DAG information
dag=DAG(
    dag_id='EMR_SCHEDULING_DAG',
    description="This is sample DAG for scheduling EMR",
    schedule_interval=None,
    dagrun_timeout=timedelta(hours=2),
    start_date=airflow.utils.dates.days_ago(0),
    catchup=True
)

start_job = PythonOperator(task_id='start_job', python_callable=print_argument,dag=dag)
end_job = DummyOperator(task_id='end_job', dag=dag)


create_emr_cluster = EmrCreateJobFlowOperator(
    task_id="CREATE_EMR_CLUSTER",
    job_flow_overrides=JOB_FLOW_OVERRIDES,
    aws_conn_id="aws_default",
    dag=dag,
    )

add_emr_step = EmrAddStepsOperator(
    task_id='ADD_EMR_STEP',
    job_flow_id="{{ ti.xcom_pull('CREATE_EMR_CLUSTER', key='return_value') }}",
    steps=SPARK_STEPS,
    aws_conn_id="aws_default",
    dag=dag
)

monitor_emr_step = EmrStepSensor(
    task_id='MONITOR_EMR_STEP',
    job_flow_id="{{ ti.xcom_pull('CREATE_EMR_CLUSTER', key='return_value') }}",
    step_id="{{ ti.xcom_pull('ADD_EMR_STEP', key='return_value')[0] }}",
    aws_conn_id="aws_default",
    dag=dag
)

terminate_cluster = EmrTerminateJobFlowOperator(
    task_id='TERMINATE_CLUSTER',
    job_flow_id="{{ ti.xcom_pull('CREATE_EMR_CLUSTER', key='return_value') }}",
    aws_conn_id="aws_default",
    dag=dag
)

start_job >> create_emr_cluster >> add_emr_step >> monitor_emr_step >> terminate_cluster >> end_job