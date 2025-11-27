from dataclasses import dataclass
from src.domain.metrics.metrics import MetricsBlock1
from src.domain.vacancy.vacancy import VacancyInfo
from uuid import UUID
from src.domain.task.task import Task
from src.domain.message.message import Message
from datetime import timedelta
from datetime import datetime
from src.domain.test.test import CodeTestSuite

from enum import Enum


@dataclass
class Interviewee:
    name: str
    surname: str
    resume_link: str


class SolutionType(Enum):
    CODE = "code"
    TEXT = "text"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other


@dataclass
class Solution:
    content: str
    solution_type: SolutionType
    language: str
    count_suspicious_copy_paste: int = 0

    def to_string(self) -> str:
        """
        Convert solution to string
        """

        return f"{self.solution_type.value} [{self.language}]: {self.content}"


@dataclass
class Room:
    id: UUID
    vacancy_id: UUID
    vacancy_info: VacancyInfo
    interviewee: Interviewee

    chat_history: list[Message]
    tasks: list[Task]
    solutions: list[Solution]
    metrics: list[str]

    created_at: datetime
    last_task_time: datetime

    metrics_block1: MetricsBlock1
    current_test_suite: CodeTestSuite | None
