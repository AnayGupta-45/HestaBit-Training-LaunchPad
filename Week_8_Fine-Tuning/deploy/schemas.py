from pydantic import BaseModel, Field
from typing import Optional

class GenerateRequest(BaseModel):
    system_prompt: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)
    max_tokens: int = Field(256, ge=1, le=1024)
    temperature: float = Field(0.3, ge=0.0, le=2.0)
    top_p: float = Field(0.9, ge=0.0, le=1.0)
    top_k: int = Field(40, ge=1, le=100)

class ChatRequest(BaseModel):
    session_id: str
    system_prompt: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    max_tokens: int = Field(256, ge=1, le=1024)
    temperature: float = Field(0.3, ge=0.0, le=2.0)
    top_p: float = Field(0.9, ge=0.0, le=1.0)
    top_k: int = Field(40, ge=1, le=100)