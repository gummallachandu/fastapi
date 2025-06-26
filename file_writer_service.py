import os
import boto3
from fastapi import HTTPException
from botocore.exceptions import NoCredentialsError, ClientError
from app.logging_config import get_logger

# Get the project's root directory.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Initialize S3 client
s3_client = boto3.client('s3')
logger = get_logger(__name__)


def write_local_file(path: str, content: str):
    """Writes content to a file on the local filesystem, ensuring it's within the project boundary."""
    # Prevent directory traversal attacks and absolute paths.
    if ".." in path or os.path.isabs(path):
        logger.error(f"Directory traversal or absolute path detected: {path}")
        raise HTTPException(status_code=400, detail="Invalid file path.")
        
    # Construct the full path and resolve any symlinks.
    full_path = os.path.join(PROJECT_ROOT, path)
    real_path = os.path.realpath(full_path)
    real_project_root = os.path.realpath(PROJECT_ROOT)

    # Final security check: Ensure the resolved path is within the project directory.
    if not real_path.startswith(real_project_root):
        logger.error(f"File path is outside the allowed directory: {real_path}")
        raise HTTPException(status_code=400, detail="File path is outside the allowed directory.")

    try:
        os.makedirs(os.path.dirname(real_path), exist_ok=True)
        with open(real_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully wrote to local file: {real_path}")
    except Exception as e:
        logger.error(f"Error writing to local file {real_path}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Could not write to file: {str(e)}")


def write_s3_file(path: str, content: str):
    """Writes content to a file in an S3 bucket."""
    try:
        if not path.startswith("s3://"):
            raise ValueError("Invalid S3 path format. Must start with s3://")
        
        bucket_name, key = path[5:].split('/', 1)
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=content)
        logger.info(f"Successfully wrote to S3 path: {path}")
    except NoCredentialsError:
        logger.error("AWS credentials not found for S3 write.")
        raise HTTPException(status_code=401, detail="AWS credentials not found.")
    except ClientError as e:
        logger.error(f"S3 Client Error for {path}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"S3 Client Error: {str(e)}")
    except Exception as e:
        logger.error(f"An error occurred writing to S3 {path}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred writing to S3: {str(e)}") 