from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agent import run_agent

app = FastAPI(title="AI Business Agent", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"name": "AI Business Agent", "status": "running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/agent")
def agent(request: AgentRequest):
    result = run_agent(request.message)
    return {
        "response": result.response,
        "selected_tool": result.tool,
        "tool_result": result.tool_result,
    }
