from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.file_reader_service import read_s3_file
from app.services.file_writer_service import write_s3_file
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


class FileWriteRequest(BaseModel): 
    file_path: str
    content: str


@router.get("/read-file/")
async def read_file(file_path: str):
    """
    Reads the content of a file from S3. File path should be the S3 key (e.g., 'folder/file.txt').
    The S3 bucket is configured via the S3_BUCKET environment variable.
    """
    logger.info(f"Received request to read file: {file_path}")
    
    try:
        content = read_s3_file(file_path)
        logger.info(f"Successfully read file: {file_path}")
        return {"file_path": file_path, "content": content}
    except HTTPException as e:
        logger.error(f"HTTPException while reading {file_path}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while reading {file_path}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.post("/write-file/")
async def write_file(request: FileWriteRequest):
    """
    Writes content to a file in S3. File path should be the S3 key (e.g., 'folder/file.txt').
    The S3 bucket is configured via the S3_BUCKET environment variable.
    """
    logger.info(f"Received request to write to file: {request.file_path}")
    
    try:
        write_s3_file(request.file_path, request.content)
        logger.info(f"Successfully wrote to file: {request.file_path}")
        return {"file_path": request.file_path, "status": "success"}
    except HTTPException as e:
        logger.error(f"HTTPException while writing to {request.file_path}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while writing to {request.file_path}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}") 