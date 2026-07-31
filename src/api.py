from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from src.generation import explain

app = FastAPI()


class AskRequest(BaseModel):
    query: str
    level: Literal["beginner", "intermediate", "expert"] = "intermediate"


class AskResponse(BaseModel):
    response: str
    sources: list[str]


@app.post("/ask")
def ask(request: AskRequest):
    answer, sources = explain(request.query, request.level)
    return AskResponse(response=answer, sources=sources)
