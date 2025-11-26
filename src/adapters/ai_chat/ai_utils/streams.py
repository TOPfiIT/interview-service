from collections.abc import Iterable, Generator
from typing import Any

from src.adapters.ai_chat.ai_utils.ctrl_parser import parse_control_json


def strip_think_and_ctrl(
    raw_stream: Iterable[str],
) -> tuple[dict[str, Any], Iterable[str]]:
    """
    Given a stream of chunks in the form:
        <think> ... </think><ctrl>{...}</ctrl>VISIBLE_TEXT...
    - skip everything inside <think>...</think>
    - read everything inside <ctrl>...</ctrl>, parse it as JSON
    - return (control_dict, body_stream), where body_stream yields the rest

    If <ctrl>...</ctrl> is missing or malformed, control_dict will be {}.
    """

    it = iter(raw_stream)

    # 1) Skip <think>...</think>
    inside_think = False
    for chunk in it:
        if not inside_think and chunk == "<think>":
            inside_think = True
            continue
        if inside_think:
            if chunk == "</think>":
                inside_think = False
                # we continue reading after </think>
            continue
        # once we see the first chunk after </think>, we break and handle ctrl
        first_after_think = chunk
        break
    else:
        # Stream ended before anything useful
        return {}, ()

    # 2) Read <ctrl>...</ctrl>
    control: dict[str, Any] = {}
    ctrl_buf: list[str] = []
    in_ctrl = False

    # first chunk after think may be <ctrl> or something else (bad model)
    chunk = first_after_think

    # enter ctrl if present
    if chunk == "<ctrl>":
        in_ctrl = True
    else:
        # no ctrl header at all, just start body from this chunk
        def body_stream_no_ctrl() -> Generator[str, None, None]:
            yield chunk
            for rest in it:
                yield rest
        return {}, body_stream_no_ctrl()

    # read ctrl content
    for chunk in it:
        if in_ctrl:
            if chunk == "</ctrl>":
                # ctrl block finished
                control = parse_control_json("".join(ctrl_buf))
                break
            ctrl_buf.append(chunk)
        else:
            # shouldn't happen, but keep it simple
            break

    # 3) The rest of the stream is body
    def body_stream() -> Generator[str, None, None]:
        for rest in it:
            yield rest

    return control, body_stream()
