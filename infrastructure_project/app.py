#!/usr/bin/env python3

import aws_cdk as cdk

from infrastructure_project.vpc_stack import VpcStack
from infrastructure_project.sagemaker_stack import SagemakerStack

app = cdk.App()

LOGICAL_PREFIX = "DSM"

vpc_name = app.node.try_get_context("vpc_name")
if not vpc_name:
    vpc_stack = VpcStack(app, id=f"{LOGICAL_PREFIX}-VpcStack")
else:
    vpc_stack = None

infra_stack = SagemakerStack(app, id=f"{LOGICAL_PREFIX}-SagemakerStack")
if vpc_stack:
    infra_stack.add_dependency(vpc_stack)

app.synth()
