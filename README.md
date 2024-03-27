# Airflow-EMR-on-EC2

### 개요
이번 레포지토리에서는 Airflow를 활용해 AWS의 빅데이터 분석서비스인 EMR을 Scheduling하고 Spark Job을 제출하는 DAG를 설명합니다. Spark Job을 실행시키기위해 1/EMR Cluster 생성 2/Spark Job 제출 3/ Spark Job 완료 4/ Cluster 종료의 순으로 Workflow가 구성됩니다.

실습을 위한 아키텍처는 아래와 같습니다.
![Alt text](/architecture.png)
