from collections.abc import Iterable
from typing import Any, AsyncGenerator, Tuple

from src.adapters.ai_chat.ai_utils.ctrl_parser import parse_control_json


def strip_think_and_ctrl(
    raw_stream: Iterable[str],
) -> Tuple[dict[str, Any], AsyncGenerator[str, None]]:
    """
    Given a stream of chunks that looks like:

        (anything: may include <think>...</think>, newlines, spaces, etc)
        <ctrl>{...}</ctrl>VISIBLE_TEXT...

    - Ignore everything before the first <ctrl>.
    - Extract JSON between <ctrl> and </ctrl>, parse it into a dict.
    - Return (control_dict, body_stream), where body_stream yields the rest
      of the stream (only visible text) as an async generator.

    If <ctrl> or </ctrl> is not found, raise RuntimeError.
    """

    it = iter(raw_stream)
    buffer = ""

    # 1) Read until we find "<ctrl>"
    start_idx = -1
    for chunk in it:
        buffer += chunk
        start_idx = buffer.find("<ctrl>")
        if start_idx != -1:
            break

    if start_idx == -1:
        raise RuntimeError("No <ctrl> start tag found in model stream")

    # Drop everything before "<ctrl>"
    buffer = buffer[start_idx + len("<ctrl>") :]

    # 2) Read until we find "</ctrl>"
    end_idx = buffer.find("</ctrl>")
    while end_idx == -1:
        try:
            chunk = next(it)
        except StopIteration:
            break
        buffer += chunk
        end_idx = buffer.find("</ctrl>")

    if end_idx == -1:
        raise RuntimeError("No </ctrl> end tag found in model stream")

    # 3) Split into control JSON and first body chunk
    ctrl_content = buffer[:end_idx]
    first_body_chunk = buffer[end_idx + len("</ctrl>") :]

    control: dict[str, Any] = parse_control_json(ctrl_content)

    # 4) Async generator for the remaining body
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