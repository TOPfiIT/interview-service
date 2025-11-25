from typing import Generator, List, Dict, Any

def get_chat_completion_stream(
    client: Any,
    model: str,
    messages: List[Dict[str, str]],
    max_tokens: int = 20000,
) -> Generator[str, None, None]:
    """
    Yields content chunks from an OpenAI chat completion stream.
    """
    with client.chat.completions.stream(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    ) as stream:
        for event in stream:
            if event.type == "chunk":
                # Access the delta content safely
                if hasattr(event, 'chunk') and event.chunk.choices:
                    delta = getattr(event.chunk.choices[0].delta, "content", None)
                    if delta:
                        yield delta

def get_chat_completion(
    client: Any,
    model: str,
    messages: List[Dict[str, str]],
    max_tokens: int = 20000,
) -> str:
    """
    Get chat completion
    """
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )
    
    return resp.choices[0].message.content

