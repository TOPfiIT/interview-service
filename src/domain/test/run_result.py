from dataclasses import dataclass


@dataclass
class RunResult:
    """
    The result of a single test case.
    """

    status: str
    exception: str | None
    stdin: str | None
    stdout: str | None
    stderr: str | None
    execution_time: int | None
