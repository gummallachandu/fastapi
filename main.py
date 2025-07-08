from fastapi import FastAPI
from app.routers import file_tool, jira_tool

app = FastAPI()

app.include_router(file_tool.router)
app.include_router(jira_tool.router)


@app.get("/")
async def root():
    return {"message": "Hello World221"} 