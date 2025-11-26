from dataclasses import dataclass
from datetime import timedelta


@dataclass
class VacancyInfo:
    """
    Vacancy class
    """

    profession: str
    position: str
    requirements: str
    questions: str
    tasks: list[str]
    task_ides: list[str]
    interview_plan: str
    duration: timedelta

