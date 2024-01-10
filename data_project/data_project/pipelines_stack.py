import json
import os
from typing import Tuple

import aws_cdk as cdk
import sagemaker
from aws_cdk import (
    aws_sagemaker as sm,
    aws_ssm as ssm,
)
from constructs import Construct

from pipelines.definitions.base import SagemakerPipelineFactory, create_sagemaker_session
from pipelines.definitions.example_pipeline_definition import ExamplePipeline


class PipelinesStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, env={
            "account": scope.node.try_get_context("account"),
            "region": scope.node.try_get_context("region"),
        }, **kwargs)

        self.prefix = self.node.try_get_context("resource_prefix")

        # Load infrastructure stack outputs as value parameters (resolved at cdk deploy time)
        sources_bucket_name = ssm.StringParameter.value_from_lookup(
            self, f"/{self.prefix}/SourcesBucketName")
        sm_execution_role_arn = ssm.StringParameter.value_from_lookup(
            self, f"/{self.prefix}/SagemakerExecutionRoleArn")

        # Create a configured pipeline
        self.example_pipeline, self.example_pipeline_arn = self.create_pipeline(
            pipeline_name='example-pipeline',
            pipeline_factory=ExamplePipeline(
                pipeline_config_parameter="Hello world!"
            ),
            sources_bucket_name=sources_bucket_name,
            sm_execution_role_arn=sm_execution_role_arn,
        )

    def create_pipeline(
        self,
        pipeline_name: str,
        pipeline_factory: SagemakerPipelineFactory,
        sources_bucket_name: str,
        sm_execution_role_arn: str,
    ) -> Tuple[sm.CfnPipeline, str]:
        # Initialize the SageMaker session (local mode if running locally or mocking)
        local_mode = os.getenv('LOCAL_MODE', 'false').lower() == 'true'
        sm_session: sagemaker.Session = create_sagemaker_session(
            region=self.region,
            default_bucket=sources_bucket_name,
            local_mode=local_mode
        )

        # Define the pipeline (this step uploads required code and packages by the pipeline to S3)
        if 'dummy-value-for-' in sources_bucket_name:
            # Value from lookup uses dummy value when doing synth for the first time.
            pipeline_def_json = '{}'
        else:
            pipeline = pipeline_factory.create(
                pipeline_name=pipeline_name,
                role=sm_execution_role_arn,
                sm_session=sm_session,
            )

            pipeline_def_json = json.dumps(json.loads(pipeline.definition()), indent=2, sort_keys=True)

        # Define CloudFormation resource for the pipeline, so it can be deployed to your account
        pipeline_cfn = sm.CfnPipeline(
            self,
            id=f"SagemakerPipeline-{pipeline_name}",
            pipeline_name=pipeline_name,
            pipeline_definition={"PipelineDefinitionBody": pipeline_def_json},
            role_arn=sm_execution_role_arn,
        )
        arn = self.format_arn(
            service='sagemaker',
            resource='pipeline',
            resource_name=pipeline_cfn.pipeline_name,
        )
        return pipeline_cfn, arn
