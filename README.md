# Luminis Blog — Deploying SageMaker Pipelines Using CDK
Code corresponding to the blog post [Deploying SageMaker Pipelines Using CDK](https://www.luminis.eu/blog/).

In this blog, my focus to clear up one such confusion about the deployment of SageMaker pipelines. 
I show you how you can write your own pipeline definitions and how to deploy them using AWS CDK into your SageMaker domain to be run.

## Structure
The project consists of two CDK projects:
* `infrastructure_project`: contains the infrastructure for the SageMaker domain, VPC and the source/data buckets.
  * `cdk.json`: contains the configuration for the CDK project. This is where you set the AWS account and `vpc_name` if you already have a VPC.
* `data_project`: contains pipeline deployment cdk project that depends on the infrastructure project.
  * `pipelines`: contains the pipeline definitions and the pipelines step sources.
  * `cdk.json`: contains the configuration for the CDK project. This is where you set the AWS account.
## Prerequisites
* Python 3.x
* [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)

## Deployment

Install python dependencies:
```bash
pip install -r requirements.txt
```

Deploy the infrastructure:
```bash
cd infrastructure_project
cdk deploy
```

Deploy the pipeline:
```bash
cd data_project
cdk deploy
```

Follow the instructions to run the pipeline.