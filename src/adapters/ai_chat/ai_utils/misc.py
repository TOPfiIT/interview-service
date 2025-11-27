from typing import Generator, List, Dict, Any
from src.core.setting import settings
from collections.abc import AsyncGenerator
from typing import Dict, List
from openai import AsyncOpenAI

async def get_chat_completion_stream(
    client: AsyncOpenAI,
    model: str,
    messages: List[Dict[str, str]],
) -> AsyncGenerator[str, None]:
    """
    Call OpenAI Chat Completions in streaming mode and yield *text chunks*.

    Usage:
        raw_stream = await get_chat_completion_stream(client, model, messages)
        async for chunk in raw_stream:
            ...
    """
    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )

    async def gen() -> AsyncGenerator[str, None]:
        async for event in stream:
            delta = event.choices[0].delta.content
            if delta:
                yield delta

    return gen()

def get_chat_completion(
    client: Any,
    model: str,
    messages: List[Dict[str, str]],
) -> str:
    """
    Get chat completion
    """
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    
    return resp.choices[0].message.content

def remove_thinking_part(message: str) -> str:
    """
    Remove the thinking part from the message
    """
    if "<think>" not in message:
        return message
    return message.split("</think>")[1].strip()