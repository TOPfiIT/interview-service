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
