from dataclasses import dataclass
from typing import Optional

@dataclass
class CodeTestCase:
    """
    One test case for a coding task.
    input_data and expected_output are raw stdin/stdout strings.
    """
    id: str
    input_data: str
    expected_output: str
    result: Optional[str] = None     # None = not executed yet
    correct: Optional[bool] = None   # None = not evaluated yet
    is_hidden: bool = False          # False = visible example, True = hidden evaluation test

@dataclass
class CodeTestSuite:
    """
    All tests for a single coding task.
    """
    task_id: str
    tests: list[CodeTestCase]