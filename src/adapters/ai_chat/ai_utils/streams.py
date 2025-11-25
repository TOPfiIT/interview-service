from collections.abc import Iterable
from typing import AsyncGenerator


async def filter_thinking_chunks(
    raw_stream: Iterable[str],
) -> AsyncGenerator[str, None]:
    """
    Wrap a raw token/segment stream and hide everything between <think>...</think>,
    while emitting "Thinking..." and "Finished thinking." markers.
    """
    inside_think = False

    for chunk in raw_stream:
        if chunk == "<think>":
            inside_think = True
            # you can drop these two user-facing messages if you don't want them
            yield "Thinking...\n"
            continue

        if chunk == "</think>":
            inside_think = False
            yield "Finished thinking.\n"
            continue

        if inside_think:
            continue

        yield chunk
