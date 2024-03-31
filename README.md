# Airflow-EMR-on-EC2

## 개요
이번 레포지토리에서는 Airflow를 활용해 AWS의 빅데이터 분석서비스인 EMR을 Scheduling하고 Spark Job을 제출하는 DAG를 설명합니다. Spark Job을 실행시키기위해 1/EMR Cluster 생성 2/Spark Job 제출 3/ Spark Job 완료 4/ Cluster 종료의 순으로 Workflow가 구성됩니다.

실습을 위한 아키텍처는 아래와 같습니다.

![Alt text](/pic/architecture_aws.png)

## 사전 요구사항
1. 인프라 구성을 위해 Local Client에 Terraform 설치가 필요합니다.
2. Airflow Dag, Pyspark 이해를 위한 기본 Python 지식이 필요합니다.
3. 실습은 AWS의 us-east-1 리전에서 진행합니다.

## Terraform을 통한 인프라 구성
Git Repository를 Local Client에 Clone 합니다. Local Client는 Mac 또는 Linux 기반의 VM 또는 EC2 환경이면 됩니다.

<pre><code>git clone https://github.com/huhjinsung/Airflow-EMR-on-EC2.git</code>
<code>cd /1_Setup</code>
<code>terraform init</code>
<code>terraform plan</code>
<code>terraform apply -auto-approve </code></pre>

Terraform을 실행하기 위해서는 아래의 Input 값들이 필요합니다. 각 AWS 계정에 따라 Input 을 입력합니다.
| 값 | 내용 |
|---|---|
| AWS Access Key | AWS의 계정의 Access Key를 입력합니다. |
| AWS Secret Key | AWS의 계정의 Secret Key를 입력합니다. |
| Account ID | AWS 계정의 Account ID를 입력합니다. |

Terraform이 성공적으로 실행되면, Terraform output 값들이 출력됩니다. 출력된 값 중 airflow_ip_addr에 표시된 ip 주소를 웹 브라우저에 접속하고 admin/admin으로 Airflow WebUI에 접속합니다. Airflow WebUI에 성공적으로 접속하게되면 아래와 같이 Airflow에 접속이 가능하게 됩니다.

<img src="/pic/airflowUI.png" width="70%" height="70%"></img><br/>

Aurora와 EC2 인스턴스간 연결을 확인하고, Aurora에서 Table을 생성하기 위해서 airflow_ec2에 접속합니다. airflow_ec2에 접속하여 아래의 명령어를 통해 terraform output 출력 값들을 환경 변수에 저장해주고 Aurora Mysql과의 연결을 확인하고 Table을 생성합니다.

<pre>
<code># 환경변수 설정</code>
<code>export S3_PATH=[S3_PATH]</code>
<code>export DAG_PATH=[DAG_PATH]</code>
<code>export SPARK_JOB_PATH=[SPARK_JOB_PATH]</code>
<code>export RAW_DATA_PATH=[RAW_DATA_PATH]</code>
<code>export AURORA_ENDPOINT=[AURORA_ENDOINT]</code>
<code>export SUBNET_ID=[SUBNET_ID]</code>

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

## Airflow DAG 구성하기
Airflow는 workflow 작성을 Python 기반으로 작성하며 이를 DAG라고 표현합니다. Airflow의 DAG는 ~/airflow/dags 디렉토리 아래에 저장하며 해당 디렉토리에 저장된 DAG들은 Airflow WebUI를 통해서 확인이 가능합니다. EC2 인스턴스에 접속하여 아래의 명령어를 통해 S3에 저장된 DAG 파일을 DAG 디렉토리에 복사합니다.
<pre>
<code>sudo aws s3 cp $S3_PATH/EMR_DAG.py /root/airflow/dags/ </code>
</pre>
업로드를 완료하고 DAG가 업데이트되면 아래와 같이 Airflow WebServer에서 확인 가능합니다.

![Alt text](/pic/EMR_DAG.png)
## 실행 및 결과 확인
최종 결과 확인을 위하여 EC2에 접속하여, 집계된 결과 값들이 Aurora Mysql 데이터베이스에 잘 저장되었는지 확인합니다.
<pre>
<code>mysql -u admin -p -h $AURORA_ENDPOINT # PASSWORD=Administrator</code>
<code>use airflow; </code>
<code>select * from emr_table;</code>
+------------+---------+
| date       | value   |
+------------+---------+
| 2024-03-31 | 5176450 |
+------------+---------+
</pre>

EMR Cluster가 데이터 처리 후 정상적으로 종료되었는지 확인하기위해 EMR CLUSTER로 이동합니다.

![Alt text](/pic/EMR_UI.png)

## 리소스 정리
Local Client에서 아래의 명령어를 입력하여 실습에 사용한 모든 리소스들을 삭제합니다.
<pre>
<code>terraform destroy -auto-approve </code>
</pre>

## Reference
