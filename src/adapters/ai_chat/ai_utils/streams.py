from collections.abc import AsyncIterable
from typing import Any, AsyncGenerator, Tuple

from src.adapters.ai_chat.ai_utils.ctrl_parser import parse_control_json


async def strip_think_and_ctrl(
    raw_stream: AsyncIterable[str],
) -> Tuple[dict[str, Any], AsyncGenerator[str, None]]:
    """
    Async version.

    raw_stream is an async iterable of string chunks:

        <think> ... may contain "<ctrl>" etc ... </think>
        <ctrl>{...}</ctrl>VISIBLE_TEXT...

    1) Skip everything inside <think>...</think> (if present).
    2) After </think>, find first <ctrl>{...}</ctrl>, parse JSON.
    3) Return (control_dict, body_stream) where body_stream yields the rest
       of the stream (visible text only).
    """

    it = raw_stream.__aiter__()

    # -------- PHASE 1: skip <think>...</think> --------
    buffer = ""
    after_think = ""
    in_think = False
    think_closed = False

    while True:
        try:
            chunk = await it.__anext__()
        except StopAsyncIteration:
            break
        buffer += chunk

        if not in_think:
            start_think = buffer.find("<think>")
            if start_think != -1:
                in_think = True

        if in_think and not think_closed:
            end_think = buffer.find("</think>")
            if end_think != -1:
                think_closed = True
                after_think = buffer[end_think + len("</think>") :]
                break

    if not think_closed and not after_think:
        after_think = buffer

    # -------- PHASE 2: find <ctrl>...</ctrl> --------
    ctrl_buffer = after_think

    # Find <ctrl>
    start_idx = ctrl_buffer.find("<ctrl>")
    while start_idx == -1:
        try:
            chunk = await it.__anext__()
        except StopAsyncIteration:
            break
        ctrl_buffer += chunk
        start_idx = ctrl_buffer.find("<ctrl>")

    if start_idx == -1:
        raise RuntimeError("No <ctrl> start tag found in model stream")

    ctrl_buffer = ctrl_buffer[start_idx + len("<ctrl>") :]

    # Find </ctrl>
    end_idx = ctrl_buffer.find("</ctrl>")
    while end_idx == -1:
        try:
            chunk = await it.__anext__()
        except StopAsyncIteration:
            break
        ctrl_buffer += chunk
        end_idx = ctrl_buffer.find("</ctrl>")

    if end_idx == -1:
        raise RuntimeError("No </ctrl> end tag found in model stream")

    ctrl_content = ctrl_buffer[:end_idx]
    first_body_chunk = ctrl_buffer[end_idx + len("</ctrl>") :]

    control: dict[str, Any] = parse_control_json(ctrl_content)

    async def body_stream() -> AsyncGenerator[str, None]:
        if first_body_chunk:
            yield first_body_chunk
        async for rest in it:
            yield rest

    return control, body_stream()

async def filter_thinking_chunks(
    raw_stream: AsyncIterable[str],
) -> AsyncGenerator[str, None]:
    """
    Async version.

    Drop everything between <think> and </think>, yield only visible text.
    If no <think> appears, pass stream through unchanged.
    """

    it = raw_stream.__aiter__()
    buffer = ""
    start_idx = -1

    # 1) Read until we find "<think>"
    while True:
        try:
            chunk = await it.__anext__()
        except StopAsyncIteration:
            break

        buffer += chunk
        start_idx = buffer.find("<think>")
        if start_idx != -1:
            break

    if start_idx == -1:
        # No <think> -> passthrough
        async def passthrough() -> AsyncGenerator[str, None]:
            if buffer:
                yield buffer
            async for rest in it:
                yield rest

        return passthrough()

    # Drop everything up to and including "<think>"
    buffer = buffer[start_idx + len("<think>") :]

    # 2) Read until we find "</think>"
    end_idx = buffer.find("</think>")
    while end_idx == -1:
        try:
            chunk = await it.__anext__()
        except StopAsyncIteration:
            # Saw "<think>" but no "</think>" -> fail-closed, leak nothing
            async def empty_stream() -> AsyncGenerator[str, None]:
                if False:
                    yield ""  # keep async generator type
            return empty_stream()

        buffer += chunk
        end_idx = buffer.find("</think>")

    first_visible = buffer[end_idx + len("</think>") :]

    async def visible_stream() -> AsyncGenerator[str, None]:
        if first_visible:
            yield first_visible
        async for rest in it:
            yield rest

    return visible_stream()