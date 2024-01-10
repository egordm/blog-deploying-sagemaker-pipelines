import logging
from abc import abstractmethod

import boto3
import sagemaker
from sagemaker.workflow.pipeline import Pipeline

from pydantic import BaseModel
from sagemaker.workflow.pipeline_context import LocalPipelineSession, PipelineSession

logger = logging.getLogger()


class SagemakerPipelineFactory(BaseModel):
    """Base class for all pipeline factories."""

    @abstractmethod
    def create(
        self,
        role: str,
        pipeline_name: str,
        sm_session: sagemaker.Session,
    ) -> Pipeline:
        raise NotImplementedError


def create_sagemaker_session(
    region: str,
    default_bucket: str,
    local_mode=False
) -> sagemaker.session.Session:
    """
    Gets the sagemaker session based on the region.
    :param region: the aws region to start the session
    :param default_bucket: the bucket to use for storing the artifacts
    :param local_mode: if True, the session will be created in local mode
    :return:
    """
    boto_session = boto3.Session(region_name=region)

    sagemaker_client = boto_session.client("sagemaker")
    try:
        if local_mode:
            sagemaker_session = LocalPipelineSession(
                default_bucket=default_bucket,
            )
        else:
            sagemaker_session = PipelineSession(
                boto_session=boto_session,
                sagemaker_client=sagemaker_client,
                default_bucket=default_bucket,
            )
        logger.info("SageMaker Session created")
    except Exception as e:
        logger.exception("Failed to generate a SageMaker Session")
        raise e

    return sagemaker_session
