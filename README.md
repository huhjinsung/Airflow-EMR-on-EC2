# Airflow-EMR-on-EC2
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/huhjinsung/Airflow-EMR-on-EC2/blob/main/README-en.md)

## 개요
이번 레포지토리에서는 Airflow를 활용해 AWS의 빅데이터 분석서비스인 EMR을 Scheduling하고 Spark Job을 제출하는 DAG를 설명합니다. 1/EMR Cluster 생성 2/Spark Job 제출 3/ Spark Job 모니터링 및 완료 4/ Cluster 종료의 순으로 Airflow Workflow가 구성됩니다.

실습을 위한 아키텍처는 아래와 같습니다.

![Alt text](/pic/architecture_aws.png)

## 사전 요구사항
1. 인프라 구성을 위해 Local Client에 Terraform 설치가 필요합니다.
2. Airflow Dag, Pyspark 이해를 위한 기본 Python 지식이 필요합니다.
3. 실습은 AWS의 us-east-1 리전에서 진행합니다.

## Terraform을 통한 인프라 구성
Git Repository를 Local Client에 Clone 합니다. Local Client는 Mac 또는 Linux 기반의 VM 또는 EC2 환경이면 됩니다.

<pre><code>git clone https://github.com/huhjinsung/Airflow-EMR-on-EC2.git</code>
<code>cd Airflow-EMR-on-EC2/1_Setup</code>
<code>terraform init</code>
<code>terraform apply -auto-approve </code></pre>

Terraform을 실행하기 위해서는 아래의 Input 값들이 필요합니다. 각 AWS 계정에 따라 Input 을 입력합니다.
| 값 | 내용 |
|---|---|
| AWS Access Key | AWS 계정의 Access Key를 입력합니다. |
| AWS Secret Key | AWS 계정의 Secret Key를 입력합니다. |
| Account ID | AWS 계정의 Account ID를 입력합니다. |

Terraform이 성공적으로 실행되면, Terraform 출력 값들이 표시됩니다.
1. 출력된 값 중 airflow_ip_addr에 표시된 ip 주소를 웹 브라우저에 접속하고 admin/admin으로 Airflow WebUI에 접속합니다. 
2. Airflow WebUI에 성공적으로 접속하게되면 아래와 같이 Airflow에 접속이 가능하게 됩니다.

![Alt text](/pic/airflowUI.png)

[Amazon EC2](https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#Home:)로 이동하여 Terraform으로 생성한 EC2의 Terminal로 이동합니다. 아래의 명령어를 통해 EC2와 Aurora Mysql과의 연결을 확인하고 Mysql 데이터베이스에 emr_table을 생성합니다.

<pre>
<code># 환경변수 설정</code>
<code>export AURORA_ENDPOINT=[AURORA_ENDOINT]</code>
<code>export S3_PATH=[S3_PATH]</code>

<code>#데이터베이스 접속 및 테이블 생성</code>
<code>mysql -u admin -p -h $AURORA_ENDPOINT # PASSWORD=Administrator</code>
<code>use airflow; </code>
<code>select database();</code>
<code>CREATE TABLE emr_table (
    date VARCHAR(255),
    value INT
);</code>

# 생성한 테이블 확인
<code>SHOW TABLES;</code>
+-------------------+
| Tables_in_airflow |
+-------------------+
| emr_table         |
+-------------------+
</pre>

## Airflow DAG 확인하기
Airflow는 workflow 작성을 Python 기반으로 작성하며 이를 DAG라고 표현합니다. Airflow의 DAG는 ~/airflow/dags 디렉토리 아래에 저장하며 해당 디렉토리에 저장된 DAG들은 Airflow WebUI를 통해서 확인이 가능합니다. EC2 인스턴스에 접속하여 아래의 명령어를 통해 S3에 저장된 DAG 파일을 DAG 디렉토리에 복사합니다.
<pre>
<code>##S3에 저장해둔 Python DAG파일을 Airflow로 이동 </code>

<code>sudo aws s3 cp $S3_PATH/EMR_DAG.py /root/airflow/dags/ </code>
</pre>
업로드를 완료하고 DAG가 업데이트되면 아래와 같이 Airflow WebServer에서 확인 가능합니다.(DAG가 업데이트까지 시간이 소요됩니다.)

![Alt text](/pic/EMR_DAG.png)

Airflow DAG를 살펴보기 위해 DAG를 클릭하여 Graph를 확인합니다.

![Alt text](/pic/workflowUI.png)

Workflow는 총 6단계로 구성됩니다.
1. **START_JOB** : [PythonOperator](https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/python.html)로, Python 기반으로 동작하며 Airflow에 저장된 변수들을 출력합니다.
2. **CREATE_EMR_CLUSTER** : [EmrCreateJobFlowOperator](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/emr/index.html#airflow.providers.amazon.aws.operators.emr.EmrCreateJobFlowOperator)이며, 사용자가 지정한 설정에 맞게 EMR 클러스터를 생성합니다.
3. **ADD_EMR_STEP** : [EmrAddStepsOperator](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/emr/index.html#airflow.providers.amazon.aws.operators.emr.EmrAddStepsOperato)이며, 생성한 클러스터에 Spark job을 제출합니다. Spark Job은 S3에 저장되어 있는 Job을 활용하며, Pyspark에서 Mysql에 Output을 저장하기 위하여 Mysql JAR도 함께 제출합니다.
4. **MONITOR_EMR_STEP** : [EmrStepSensor](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/sensors/emr/index.html)이며, 제출한 Spark Job이 정상적으로 완료되었는지 확인합니다. Spark Job이 완료 될 경우 Step을 Complete하고 다음 단계로 이동합니다.
5. **TERMINATE_CLUSTER** : [EmrTerminateJobFlowOperator](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/emr/index.html#airflow.providers.amazon.aws.operators.emr.EmrTerminateJobFlowOperator)이며, 데이터 처리가 완료되었으므로 2단계에서 생성한 Cluster를 종료합니다.
6. **END_JOB** : [DummyOperator](https://airflow.apache.org/docs/apache-airflow/2.2.4/_api/airflow/operators/dummy/index.html)로, 전체 Workflow의 종료를 확인하기 위한 Dummy Step입니다.

## Airflow 설정 및 DAG 실행하기

앞서 살펴본 DAG는 Airflow를 통해 변수를 전달받아 DAG를 실행합니다. DAG의 실행을 위해 **1/S3_PATH**, **2/SUBNET_ID**, **3/RAW_DATA_PATH**, **4/AURORA_ENDPOINT** 총 4개의 변수를 전달받습니다.
Airflow에서는 변수의 설정을 Variables에 저장하며, DAG에서는 [Variable.get()](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/variables.html)의 명령어를 통해 저장한 Variables을 가져옵니다. Variable 설정을 위해 Airflow UI에서 Admin > Variables로 이동하여 위에서 설명한 4개의 변수를 아래와 같이 등록합니다.

![Alt text](/pic/VariablesUI.png)

Airflow에서 AWS의 리소스를 생성하고 삭제하기위해서는 AWS와의 Connection 지정이 필요합니다. Airflow UI에서 Admin > Connections의 항목으로 이동하여 **aws_default** 항목을 편집하며, 사용자의 Access Key, Secret Key, Region을 설정해줍니다.

![Alt text](/pic/ConnectionUI.png)

Variables와 Connection 설정이 완료되었으면, DAG를 실행합니다.

![Alt text](/pic/RunUI.png)

## 결과 확인
최종 결과 확인을 위하여 EC2에 접속하여, 집계된 결과 값들이 Aurora Mysql 데이터베이스에 잘 저장되었는지 확인합니다.
<pre>
<code>mysql -u admin -p -h $AURORA_ENDPOINT # PASSWORD=Administrator</code>
<code>use airflow; </code>

# 결과 확인
<code>select * from emr_table;</code>

+------------+---------+
| date       | value   |
+------------+---------+
| 2024-03-31 | 5176450 |
+------------+---------+
</pre>

EMR Cluster가 데이터 처리 후 정상적으로 종료되었는지 확인하기위해 EMR CLUSTER로 이동합니다.

![Alt text](/pic/EMRUI.png)

Airflow의 Workflow Graph에서도 모든 Step이 정상적으로 Success 된 사항을 확인 할 수 있습니다.

![Alt text](/pic/CompleteUI.png)

## 리소스 정리
Local Client에서 아래의 명령어를 입력하여 실습에 사용한 모든 리소스들을 삭제합니다.
<pre>
<code>terraform destroy -auto-approve </code>
</pre>

## Reference
**Terraform AWS Provider** - https://registry.terraform.io/providers/hashicorp/aws/latest/docs

**Airflow AWS Provider** - https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/index.html