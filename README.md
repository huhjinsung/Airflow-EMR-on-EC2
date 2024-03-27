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

<pre><code>https://github.com/huhjinsung/Airflow-EMR-on-EC2.git</code>
<code>cd /1_Setup</code>
<code>terraform init</code>
<code>terraform plan</code>
<code>terraform apply -auto-approve </code></pre>

Terraform을 실행하기 위해서는 아래의 Input 값들이 필요합니다. 각 AWS 계정에 따라 Input 을 입력합니다.
| 값 | 내용 |
|---|---|
| AWS Access Key | AWS의 계정의 Access Key를 입력합니다. |
| AWS Secret Key | AWS의 계정의 Secret Key를 입력합니다. |
| Bucket Name | 생성하려는 Bucket의 이름을 입력합니다. |
## Reference
