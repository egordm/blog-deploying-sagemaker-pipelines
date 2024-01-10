import aws_cdk as cdk
from aws_cdk import (
    aws_sagemaker as sm,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_ssm as ssm,
)
from constructs import Construct


class SagemakerStack(cdk.Stack):
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

        # Create IAM role for SageMaker Users
        self.sm_execution_role = self.create_execution_role()

        # Create S3 bucket for SageMaker code sources
        self.sm_sources_bucket = self.create_sm_sources_bucket()

        ssm.StringParameter(
            self, 'SourcesBucketName',
            string_value=self.sm_sources_bucket.bucket_name,
            parameter_name=f"/{self.prefix}/SourcesBucketName",
            description="SageMaker Sources Bucket Name",
        )

        # Grant read access to SageMaker execution role
        self.sm_sources_bucket.grant_read(self.sm_execution_role)

        # Create S3 bucket for SageMaker data
        self.sm_data_bucket = self.create_data_bucket()

        # Grant read/write access to SageMaker execution role
        self.sm_data_bucket.grant_read_write(self.sm_execution_role)

        # Fetch VPC information
        vpc_name = self.node.try_get_context("vpc_name")
        self.vpc = ec2.Vpc.from_lookup(
            self, id="ImportedVpc",
            vpc_name=vpc_name if vpc_name else f"{self.prefix}-vpc"
        )
        public_subnet_ids = [public_subnet.subnet_id for public_subnet in self.vpc.public_subnets]

        # Create SageMaker Studio domain
        self.domain = sm.CfnDomain(
            self, "SagemakerDomain",
            auth_mode='IAM',
            domain_name=f'{self.prefix}-SG-Project',
            default_user_settings=sm.CfnDomain.UserSettingsProperty(
                execution_role=self.sm_execution_role.role_arn
            ),
            app_network_access_type='PublicInternetOnly',
            vpc_id=self.vpc.vpc_id,
            subnet_ids=public_subnet_ids,
            tags=[cdk.CfnTag(
                key="project",
                value="example-pipelines"
            )],
        )

        # Create SageMaker Studio default user profile
        self.user = sm.CfnUserProfile(
            self, 'SageMakerStudioUserProfile',
            domain_id=self.domain.attr_domain_id,
            user_profile_name='default-user',
            user_settings=sm.CfnUserProfile.UserSettingsProperty(),
        )

    def create_execution_role(self) -> iam.Role:
        role = iam.Role(
            self, 'SagemakerExecutionRole',
            assumed_by=iam.ServicePrincipal('sagemaker.amazonaws.com'),
            role_name=f"{self.prefix}-sm-execution-role",
            managed_policies=[
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    id="SagemakerFullAccess",
                    managed_policy_arn="arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
                ),
            ],
        )
        ssm.StringParameter(
            self, 'SagemakerExecutionRoleArn',
            string_value=role.role_arn,
            parameter_name=f"/{self.prefix}/SagemakerExecutionRoleArn",
            description="SageMaker Execution Role ARN",
        )

        return role

    def create_sm_sources_bucket(self) -> s3.Bucket:
        return s3.Bucket(
            self,
            id="SourcesBucket",
            bucket_name=f"{self.prefix}-sm-sources",
            lifecycle_rules=[],
            versioned=False,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            # Access
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            public_read_access=False,
            object_ownership=s3.ObjectOwnership.OBJECT_WRITER,
            enforce_ssl=True,
            # Encryption
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

    def create_data_bucket(self):
        return s3.Bucket(
            self,
            id="DataBucket",
            bucket_name=f"{self.prefix}-sm-data",
            lifecycle_rules=[],
            versioned=False,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            # Access
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            public_read_access=False,
            object_ownership=s3.ObjectOwnership.OBJECT_WRITER,
            enforce_ssl=True,
            # Encryption
            encryption=s3.BucketEncryption.S3_MANAGED,
        )
