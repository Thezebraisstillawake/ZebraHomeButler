import httpx

from config import settings
from schemas import ChatRequest, ChatResponse


SYSTEM_PROMPT = "你是一个友好的 AI 学习助手，用中文回答，回答后主动询问是否需要出题练习"


async def call_llm(req: ChatRequest) -> ChatResponse:
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.message},
        ],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            settings.llm_api_url,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    reply = data["choices"][0]["message"]["content"]
    return ChatResponse(reply=reply.strip())