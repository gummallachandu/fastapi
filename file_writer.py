from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.file_writer_service import write_local_file, write_s3_file
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


class FileWriteRequest(BaseModel):
    file_path: str
    content: str


@router.post("/write-file/")
async def write_file(request: FileWriteRequest):
    """
    Writes content to a file, given a local path or an S3 URI.
    """
    logger.info(f"Received request to write to file: {request.file_path}")
    try:
        if request.file_path.startswith("s3://"):
            logger.info(f"Writing to S3 path: {request.file_path}")
            write_s3_file(request.file_path, request.content)
        else:
            logger.info(f"Writing to local path: {request.file_path}")
            write_local_file(request.file_path, request.content)

        logger.info(f"Successfully wrote to file: {request.file_path}")
        return {"file_path": request.file_path, "status": "success"}
    except HTTPException as e:
        logger.error(f"HTTPException while writing to {request.file_path}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while writing to {request.file_path}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}") 