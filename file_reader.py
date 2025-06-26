from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.file_reader_service import read_local_file, read_s3_file
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


class FileReadRequest(BaseModel):
    file_path: str


@router.post("/read-file/")
async def read_file(request: FileReadRequest):
    """
    Reads the content of a file, given a local path or an S3 URI.
    """
    logger.info(f"Received request to read file: {request.file_path}")
    try:
        if request.file_path.startswith("s3://"):
            logger.info(f"Reading file from S3: {request.file_path}")
            content = read_s3_file(request.file_path)
        else:
            logger.info(f"Reading file from local path: {request.file_path}")
            content = read_local_file(request.file_path)

        logger.info(f"Successfully read file: {request.file_path}")
        return {"file_path": request.file_path, "content": content}
    except HTTPException as e:
        logger.error(f"HTTPException while reading {request.file_path}: {e.detail}")
        # Re-raise HTTP exceptions from helper functions
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while reading {request.file_path}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/read-file/test")
async def test_read_file():
    """
    A test endpoint that reads the 'requirements.txt' file.
    """
    logger.info("Received request to test read file.")
    try:
        content = read_local_file("requirements.txt")
        return {"file_path": "requirements.txt", "content": content}
    except HTTPException as e:
        logger.error(f"HTTPException during test read: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during test read: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}") 