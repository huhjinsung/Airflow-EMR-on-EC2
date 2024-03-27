# Airflow-EMR-on-EC2

## 개요
이번 레포지토리에서는 Airflow를 활용해 AWS의 빅데이터 분석서비스인 EMR을 Scheduling하고 Spark Job을 제출하는 DAG를 설명합니다. Spark Job을 실행시키기위해 1/EMR Cluster 생성 2/Spark Job 제출 3/ Spark Job 완료 4/ Cluster 종료의 순으로 Workflow가 구성됩니다.

실습을 위한 아키텍처는 아래와 같습니다.

![Alt text](/architecture_aws.png)

## 사전 요구사항
1. 인프라 구성을 위한 Terraform의 이해가 필요합니다.
2. Airflow Dag, Pyspark 이해를 위한 기본 Python 지식이 필요합니다.
3. 실습은 AWS의 us-east-1 리전에서 진행합니다.

## Terraform을 통한 인프라 구성
Git Repository를 Local Client에 Clone 합니다. Local Client는 Mac 또는 Linux 기반의 VM 또는 EC2 환경이면 됩니다.

<pre><code>https://github.com/huhjinsung/Airflow-EMR-on-EC2.git</code></pre>
<pre><code>cd 1_Setup</code></pre>
<pre><code>terraform init</code></pre>