import os
from jira import JIRA, JIRAError
from fastapi import HTTPException
from app.logging_config import get_logger

logger = get_logger(__name__)

def get_jira_client():
    """Initializes and returns a JIRA client."""
    try:
        server = os.environ['JIRA_INSTANCE_URL']
        username = os.environ['JIRA_USERNAME']
        api_token = os.environ['JIRA_API_TOKEN']
        jira_project_key = os.environ['JIRA_PROJECT_KEY']
        
        return JIRA(server=server, basic_auth=(username, api_token), options={'project_key': jira_project_key})
    except KeyError as e:
        logger.error(f"Missing Jira environment variable: {e}")
        raise HTTPException(status_code=500, detail=f"Jira configuration error: missing {e}")
    except JIRAError as e:
        logger.error(f"Jira authentication failed: {e.text}", exc_info=True)
        raise HTTPException(status_code=401, detail=f"Jira authentication failed: {e.text}")


def create_jira_issue(project_key: str, summary: str, description: str, issue_type: str):
    """Creates an issue in Jira."""
    logger.info(f"Attempting to create Jira issue in project {project_key} with summary: {summary}")
    try:
        jira = get_jira_client()
        issue_dict = {
            'project': jira.jira_project_key,
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
        }
        new_issue = jira.create_issue(fields=issue_dict)
        logger.info(f"Successfully created Jira issue {new_issue.key}")
        return new_issue
    except JIRAError as e:
        logger.error(f"Failed to create Jira issue: {e.text}", exc_info=True)
        raise HTTPException(status_code=e.status_code, detail=f"Jira error: {e.text}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while creating Jira issue: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}") 