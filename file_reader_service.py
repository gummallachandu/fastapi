import os
import boto3
from fastapi import HTTPException
from botocore.exceptions import NoCredentialsError, ClientError
from app.logging_config import get_logger

# Get the project's root directory.
# Note: __file__ is 'app/services/file_reader_service.py'
# So we go up three levels to get to the project root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Initialize S3 client
s3_client = boto3.client('s3')
logger = get_logger(__name__)


def read_local_file(path: str):
    """Reads a file from the local filesystem."""
    # Create an absolute path from the project root and the relative path.
    file_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))

    # Security check: Ensure the resolved path is within the project directory.
    # if not file_path.startswith(PROJECT_ROOT):
    #     raise HTTPException(status_code=400, detail="File path is outside the allowed directory.")

    if not os.path.exists(file_path):
        logger.warning(f"Local file not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found.")

    if not os.path.isfile(file_path):
        logger.warning(f"Local path is not a file: {file_path}")
        raise HTTPException(status_code=400, detail="Path is not a file.")

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def read_s3_file(path: str):
    """Reads a file from an S3 bucket."""
    try:
        if not path.startswith("s3://"):
            err_msg = "Invalid S3 path format. Must start with s3://"
            logger.error(err_msg)
            raise ValueError(err_msg)
        
        bucket_name, key = path[5:].split('/', 1)
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        return response['Body'].read().decode('utf-8')
    except NoCredentialsError:
        logger.error("AWS credentials not found.")
        raise HTTPException(status_code=401, detail="AWS credentials not found.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.warning(f"S3 object not found: {path}")
            raise HTTPException(status_code=404, detail="S3 object not found.")
        else:
            logger.error(f"S3 Client Error for {path}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"S3 Client Error: {str(e)}")
    except Exception as e:
        logger.error(f"An error occurred reading from S3 {path}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred reading from S3: {str(e)}") 