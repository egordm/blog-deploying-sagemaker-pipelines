#!/usr/bin/env python3

import aws_cdk as cdk

from data_project.pipelines_stack import PipelinesStack

app = cdk.App()

LOGICAL_PREFIX = "DSM"

pipelines_stack = PipelinesStack(app, id=f"{LOGICAL_PREFIX}-PipelinesStack")

app.synth()
