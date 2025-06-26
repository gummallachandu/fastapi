from fastapi import FastAPI
from app.routers import file_reader, file_writer, jira_tool

app = FastAPI()

app.include_router(file_reader.router)
app.include_router(file_writer.router)
app.include_router(jira_tool.router)


@app.get("/")
async def root():
    return {"message": "Hello World221"} 