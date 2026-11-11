

import boto3
from botocore.config import Config

from app.database.connection import settings


# Create connection with Storj S3 gateway
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.STORJ_ENDPOINT,
    aws_access_key_id=settings.STORJ_ACCESS_KEY,
    aws_secret_access_key=settings.STORJ_SECRET_KEY,
    region_name="us-east-1",
    config=Config(
        s3={"addressing_style": "path"},
        request_checksum_calculation="when_required",
        response_checksum_validation="when_required"
    )
)


def upload_file_to_storj(
    file_bytes: bytes,
    object_name: str,
    content_type: str
):
    s3_client.put_object(
        Bucket=settings.STORJ_BUCKET_NAME,
        Key=object_name,
        Body=file_bytes,
        ContentType=content_type
    )

    return object_name


def delete_file_from_storj(object_name: str):
    s3_client.delete_object(
        Bucket=settings.STORJ_BUCKET_NAME,
        Key=object_name
    )


def generate_file_url(object_name: str):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.STORJ_BUCKET_NAME,
            "Key": object_name
        },
        ExpiresIn=3600
    )

def generate_presigned_url(object_name: str):
    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.STORJ_BUCKET_NAME,
            "Key": object_name
        },
        ExpiresIn=7200
    )