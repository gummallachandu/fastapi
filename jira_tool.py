from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.jira_service import create_jira_issue
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


class JiraIssueRequest(BaseModel):
    project_key: str
    summary: str
    description: str
    issue_type: str = "Task"


@router.post("/create-jira-issue/")
async def create_issue(request: JiraIssueRequest):
    """
    Creates a new issue in Jira.
    """
    logger.info(f"Received request to create Jira issue in project: {request.project_key}")
    try:
        issue = create_jira_issue(
            project_key=request.project_key,
            summary=request.summary,
            description=request.description,
            issue_type=request.issue_type
        )
        return {"issue_key": issue.key, "url": issue.self}
    except HTTPException as e:
        # Service layer handles logging for these exceptions
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in Jira endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}") 