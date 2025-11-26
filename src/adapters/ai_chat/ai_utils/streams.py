from collections.abc import Iterable
from typing import Any, AsyncGenerator, Tuple

from src.adapters.ai_chat.ai_utils.ctrl_parser import parse_control_json


def strip_think_and_ctrl(
    raw_stream: Iterable[str],
) -> Tuple[dict[str, Any], AsyncGenerator[str, None]]:
    """
    Given a stream of chunks that looks like:

        <think> ... may contain "<ctrl>" etc ... </think>
        <ctrl>{...}</ctrl>VISIBLE_TEXT...

    1) Skip everything inside <think>...</think> (if present).
       Any "<ctrl>" / "</ctrl>" inside <think> is ignored.
    2) After </think> (or from the start, if there was no <think>),
       find the first <ctrl>{...}</ctrl>, parse JSON inside.
    3) Return (control_dict, body_stream), where body_stream yields
       the rest of the stream (only visible text) as an async generator.

    If <ctrl> or </ctrl> is not found at all, raises RuntimeError.
    """

    it = iter(raw_stream)

    # -------- PHASE 1: skip <think>...</think> block if present --------
    buffer = ""
    after_think = ""
    in_think = False
    think_closed = False

    for chunk in it:
        buffer += chunk

        # If we haven't yet seen a <think>, check for it
        if not in_think:
            start_think = buffer.find("<think>")
            if start_think != -1:
                in_think = True

        if in_think and not think_closed:
            # Look for </think>
            end_think = buffer.find("</think>")
            if end_think != -1:
                think_closed = True
                # Everything after </think> is the "real" start for ctrl search
                after_think = buffer[end_think + len("</think>") :]
                break
    else:
        # Stream ended during phase 1. Either:
        # - No <think> at all: then buffer is just the whole stream.
        # - <think> without </think>: we just treat all as normal text.
        after_think = buffer

    # If there was no <think> block at all, we might not have broken the loop.
    # In that case, after_think is empty and buffer holds the full text.
    if not think_closed and not after_think:
        after_think = buffer

    # -------- PHASE 2: find <ctrl>...</ctrl> AFTER the think block --------
    ctrl_buffer = after_think

    # Find <ctrl>
    start_idx = ctrl_buffer.find("<ctrl>")
    while start_idx == -1:
        try:
            chunk = next(it)
        except StopIteration:
            break
        ctrl_buffer += chunk
        start_idx = ctrl_buffer.find("<ctrl>")

    if start_idx == -1:
        raise RuntimeError("No <ctrl> start tag found in model stream")

    # Drop everything before <ctrl>
    ctrl_buffer = ctrl_buffer[start_idx + len("<ctrl>") :]

    # Find </ctrl>
    end_idx = ctrl_buffer.find("</ctrl>")
    while end_idx == -1:
        try:
            chunk = next(it)
        except StopIteration:
            break
        ctrl_buffer += chunk
        end_idx = ctrl_buffer.find("</ctrl>")

    if end_idx == -1:
        raise RuntimeError("No </ctrl> end tag found in model stream")

    # Split into control JSON and first visible body chunk
    ctrl_content = ctrl_buffer[:end_idx]
    first_body_chunk = ctrl_buffer[end_idx + len("</ctrl>") :]

    control: dict[str, Any] = parse_control_json(ctrl_content)

    # -------- PHASE 3: async body stream --------
    async def body_stream() -> AsyncGenerator[str, None]:
        if first_body_chunk:
            yield first_body_chunk
        for rest in it:
            yield rest

    return control, body_stream()

def filter_thinking_chunks(
    raw_stream: Iterable[str],
) -> AsyncGenerator[str, None]:
    """
    Given a stream of chunks that may contain:

        ... (anything, including newlines)
        <think>internal reasoning...</think>VISIBLE_TEXT...

    - Ignore everything from the first "<think>" up to and including the
      matching "</think>".
    - Yield only the visible text after "</think>" and the rest of the stream.
    - If no "<think>" appears at all, pass the stream through unchanged.
    - If "<think>" appears but "</think>" never does, drop everything after
      "<think>" (fail-closed rather than leaking internal reasoning).
    """

    it = iter(raw_stream)
    buffer = ""

    # 1) Read until we find "<think>"
    start_idx = -1
    for chunk in it:
        buffer += chunk
        start_idx = buffer.find("<think>")
        if start_idx != -1:
            break

    if start_idx == -1:
        # No <think> at all -> just pass everything through
        async def passthrough() -> AsyncGenerator[str, None]:
            if buffer:
                yield buffer
            for rest in it:
                yield rest
        return passthrough()

    # Drop everything up to and including "<think>"
    buffer = buffer[start_idx + len("<think>") :]

    # 2) Read until we find "</think>"
    end_idx = buffer.find("</think>")
    while end_idx == -1:
        try:
            chunk = next(it)
        except StopIteration:
            break
        buffer += chunk
        end_idx = buffer.find("</think>")

    if end_idx == -1:
        # We saw "<think>" but never saw "</think>" -> drop the rest
        async def empty_stream() -> AsyncGenerator[str, None]:
            if False:
                yield ""  # keeps it an async generator
        return empty_stream()

    # 3) Everything after "</think>" in the buffer is the first visible chunk
    first_visible = buffer[end_idx + len("</think>") :]

    # 4) Async generator for visible output
    async def visible_stream() -> AsyncGenerator[str, None]:
        if first_visible:
            yield first_visible
        for rest in it:
            yield rest

    return visible_stream()