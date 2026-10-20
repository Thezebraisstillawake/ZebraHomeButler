from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="用户输入的消息")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="AI 的回复")