import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
from constructs import Construct


class VpcStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs
    ) -> None:
        """CloudFormation stack to create AWS KMS Key, Amazon S3 resources such as buckets and bucket policies."""
        super().__init__(scope, id, env={
            "account": scope.node.try_get_context("account"),
            "region": scope.node.try_get_context("region"),
        }, **kwargs)

        self.prefix = self.node.try_get_context("resource_prefix")

        self.vpc = self._create_vpc()
        self.shared_security_group = self._create_shared_security_group(self.vpc)

    def _create_vpc(self):
        vpc = ec2.Vpc(
            self,
            id="VpcConstruct",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            vpc_name=f"{self.prefix}-vpc",
            max_azs=3,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                ec2.SubnetConfiguration(
                    cidr_mask=23,
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                ),
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name="Isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                ),
            ],
        )

        return vpc

    def _create_shared_security_group(self, vpc: ec2.Vpc):
        shared_security_group_ingress = ec2.SecurityGroup(
            self,
            id="SharedIngressSecurityGroup",
            vpc=vpc,
            description="Shared Security Group for Data Lake resources with self-referencing ingress rule.",
            security_group_name=f"{self.prefix}-shared-ingress-sg"
        )
        shared_security_group_ingress.add_ingress_rule(
            peer=shared_security_group_ingress,
            connection=ec2.Port.all_traffic(),
            description="Self-referencing ingress rule",
        )
