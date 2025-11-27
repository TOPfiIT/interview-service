from dataclasses import dataclass
from typing import Optional

@dataclass
class CodeTestCase:
    """
    One test case for a coding task.

    - input_data / expected_output describe the test itself.
    - The *result_* fields are filled after execution by copying from RunResult.
    """
    id: str
    input_data: str                 # canonical stdin for this test
    expected_output: str            # canonical expected stdout

    # High-level evaluation flags
    correct: Optional[bool] = None  # True = matched expected_output, False = mismatch, None = not run

    # Detailed execution data (mirrors RunResult)
    status: Optional[str] = None
    exception: Optional[str] = None
    stdin: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    execution_time: Optional[int] = None

    # Visibility
    is_hidden: bool = False         # False = visible example, True = hidden evaluation test


@dataclass
class CodeTestSuite:
    """
    All tests for a single coding task.
    """
    task_id: str
    tests: list[CodeTestCase]