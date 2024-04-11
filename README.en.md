# EMR Scheduling by Airflow DAG

## Introduction
This repository describe airflow DAG which schudling EMR cluster to complete big data processing. Airflow Dag contains as below workflow step.
 1. EMR cluster create 
 2. ADD step - submit spark job
 3. Monitoring step - check processing is completed or not
 4. Terminate cluster - Terminate cluster after big data processing
 
Below architecure is for HoL.

![Alt text](/pic/architecture_aws.png)

## Prerequisites
1. We are going to use Terraform for provisioning infrastrucutre. you have to download terraform on your local pc.
2. You have to have basic knowledge on python to understand Airflow dag and Pyspark.
3. HoL is proceeded in 'us-east-1' region.

## Provisioning infra by Terraform.
Clone this repository on your local pc. Mac or linux is good option to proceed it.

<pre><code>git clone git@ssh.gitlab.aws.dev:jinsungh/emr-scheduling-by-airflow.git</code>
<code>cd emr-scheduling-by-airflow</code>
<code>terraform init</code>
<code>terraform apply -auto-approve </code></pre>

For provisioning infra by terraform, you have to input some records for terraform could run.

| Subject | Value |
|---|---|
| AWS Access Key | Input your aws access key. |
| AWS Secret Key | Input your aws secret key. |
| Account ID | Input your aws account id |

You can see terraform output on your terminal after provisioning is completed successfully.

1. Among the output values, open the IP address shown in airflow_ip_addr in a web browser and access the Airflow WebUI as admin/admin. 
2. After successfully connecting to the Airflow WebUI, you will be able to access Airflow as shown below.

![Alt text](/pic/airflowUI.png)

Go to [Amazon EC2](https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#Home:) and navigate to the terminal on the EC2 you created with terraform. Execute the command below to verify the connection between EC2 and Aurora Mysql and create an emr_table in the Mysql database.

<pre>
<code># Set enviroment varialbes/code>
<code>export AURORA_ENDPOINT=[AURORA_ENDOINT]</code>
<code>export S3_PATH=[S3_PATH]</code>

<code>#Connect database and create table.</code>
<code>mysql -u admin -p -h $AURORA_ENDPOINT # PASSWORD=Administrator</code>
<code>use airflow; </code>
<code>select database();</code>
<code>CREATE TABLE emr_table (
    date VARCHAR(255),
    value INT
);</code>

# Check table
<code>SHOW TABLES;</code>
+-------------------+
| Tables_in_airflow |
+-------------------+
| emr_table         |
+-------------------+
</pre>

## Check Airflow DAG
Airflow builds workflows in Python and represents them as DAGs. Airflow stores DAGs under the ~/airflow/dags directory, and you can view DAGs stored in that directory through the Airflow WebUI. Connect to your EC2 instance and execute the command below to copy the DAG file stored in S3 to the DAG directory.
<pre>
<code>##Copy Python Dag to airflow directory </code>

<code>sudo aws s3 cp $S3_PATH/EMR_DAG.py /root/airflow/dags/ </code>
</pre>
Once the upload is complete and the DAG is updated, you will see it in the Airflow UI as shown below (it will take a while for the DAG to update).

![Alt text](/pic/EMR_DAG.png)

To explore the Airflow DAG, click the DAG to view the graph.

![Alt text](/pic/workflowUI.png)

The workflow consists of six steps.
1. **START_JOB** : [PythonOperator](https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/python.html)which is Python-based and outputs variables stored in Airflow.
2. **CREATE_EMR_CLUSTER** : [EmrCreateJobFlowOperator](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/emr/index.html#airflow.providers.amazon.aws.operators.emr.EmrCreateJobFlowOperator), creates an EMR cluster with the settings you specify.
3. **ADD_EMR_STEP** : [EmrAddStepsOperator](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/emr/index.html#airflow.providers.amazon.aws.operators.emr.EmrAddStepsOperato), submits a Spark job to the cluster you created. The Spark job utilizes the job stored in S3 and also submits a Mysql JAR to store the output in Mysql in Pyspark.
4. **MONITOR_EMR_STEP** : [EmrStepSensor](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/sensors/emr/index.html),  checks to see if the Spark Job you submitted completed successfully. If the Spark Job will complete, it completes the step and moves to the next step.
5. **TERMINATE_CLUSTER** : [EmrTerminateJobFlowOperator](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/emr/index.html#airflow.providers.amazon.aws.operators.emr.EmrTerminateJobFlowOperator), terminate the cluster created in step 2 because data processing is complete.
6. **END_JOB** : [DummyOperator](https://airflow.apache.org/docs/apache-airflow/2.2.4/_api/airflow/operators/dummy/index.html), Dummy Operator to confirm the end of the entire workflow.

## Setting up Airflow and running a DAG

The DAG we saw earlier uses Airflow to pass variables to run the DAG. To run the DAG , it receives four variables:1/S3_PATH, 2/SUBNET_ID, 3/RAW_DATA_PATH,  and4/AURORA_ENDPOINT. Airflow saves the variable settings in Variables, and DAG gets the saved variables through the [Variable.get()](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/variables.html) command. To set the variables, go to Admin > Variables in the Airflow UI and register the four variables described above as follows.


![Alt text](/pic/VariablesUI.png)

In order to create and delete resources in AWS, you need to specify a connection with AWS. In the Airflow UI, go to Admin > Connections and edit the **aws_default** entry, which sets the Access Key, Secret Key, and Region for the user.

![Alt text](/pic/ConnectionUI.png)

Once you've set up your Variables and Connections, run the DAG.

![Alt text](/pic/RunUI.png)

## Check output.
To verify the final result, connect to EC2 and verify that the aggregated result values have been successfully stored in the Aurora Mysql database.

<pre>
<code>mysql -u admin -p -h $AURORA_ENDPOINT # PASSWORD=Administrator</code>
<code>use airflow; </code>

# check result.
<code>select * from emr_table;</code>

+------------+---------+
| date       | value   |
+------------+---------+
| 2024-03-31 | 5176450 |
+------------+---------+
</pre>

Go to EMR CLUSTER to verify that EMR Cluster has shut down properly after processing data.

![Alt text](/pic/EMRUI.png)

You can also see in Airflow's Workflow Graph that all steps succeeded as expected.

![Alt text](/pic/CompleteUI.png)

## Clean resource.
In the Local Client, enter the command below to delete all resources used in the lab.
<pre>
<code>terraform destroy -auto-approve </code>
</pre>

## Reference
**Terraform AWS Provider** - https://registry.terraform.io/providers/hashicorp/aws/latest/docs

**Airflow AWS Provider** - https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/index.html