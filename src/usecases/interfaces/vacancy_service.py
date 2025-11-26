from typing import Protocol
from src.domain.vacancy.vacancy import VacancyInfo
from uuid import UUID
from src.domain.room.room import Room


class VacancyServiceBase(Protocol):
    """
    Abstract class for the vacancy service
    """

    async def get_vacancy(self, vacancy_id: UUID) -> VacancyInfo:
        """
        Gets the vacancy with the given id
        """
        ...

    async def add_interview_results(self, room: Room) -> None:
        """
        Adds the interview results to the vacancy with the given id
        """
        ...
