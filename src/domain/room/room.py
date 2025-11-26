from dataclasses import dataclass
from src.domain.vacancy.vacancy import VacancyInfo
from uuid import UUID
from src.domain.task.task import Task
from src.domain.message.message import Message

from enum import Enum


@dataclass
class Interviewee:
    name: str
    surname: str
    resume_link: str


class SolutionType(Enum):
    CODE = "code"
    TEXT = "text"


@dataclass
class Solution:
    content: str
    solution_type: SolutionType
    language: str


@dataclass
class Room:
    id: UUID
    vacancy_info: VacancyInfo
    interviewee: Interviewee

    chat_history: list[Message]
    tasks: list[Task]
    solutions: list[Solution]
