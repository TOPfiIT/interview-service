from dataclasses import dataclass


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
