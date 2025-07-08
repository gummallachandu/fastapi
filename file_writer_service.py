import os
import boto3
from fastapi import HTTPException
from botocore.exceptions import NoCredentialsError, ClientError
from app.logging_config import get_logger

# Initialize S3 client
s3_client = boto3.client('s3')
logger = get_logger(__name__)

# Get S3 bucket from environment variable
S3_BUCKET = os.environ.get('S3_BUCKET_INPUT')

if not S3_BUCKET:
    logger.error("S3_BUCKET_INPUT environment variable is not set")


def write_s3_file(s3_key: str, content: str):
    """Writes content to a file in the configured S3 bucket using the provided key."""
    if not S3_BUCKET:
        logger.error("S3_BUCKET environment variable is not configured")
        raise HTTPException(status_code=500, detail="S3 bucket is not configured")
    
    try:
        logger.info(f"Writing to S3 bucket '{S3_BUCKET}' with key: {s3_key}")
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=content)
        logger.info(f"Successfully wrote to S3 key: {s3_key}")
    except NoCredentialsError:
        logger.error("AWS credentials not found for S3 write.")
        raise HTTPException(status_code=401, detail="AWS credentials not found.")
    except ClientError as e:
        logger.error(f"S3 Client Error for {s3_key}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"S3 Client Error: {str(e)}")
    except Exception as e:
        logger.error(f"An error occurred writing to S3 {s3_key}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred writing to S3: {str(e)}") 