from typing import Protocol

from src.domain.test.run_result import RunResult


class CodeRunServiceBase(Protocol):
    async def run_code(self, language: str, stdin: str, code: str) -> RunResult: ...
