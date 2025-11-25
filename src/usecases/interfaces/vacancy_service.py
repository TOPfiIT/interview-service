from abc import ABC, abstractmethod
from domain.vacancy.vacancy import VacancyInfo
from uuid import UUID
from domain.room.room import Room


class VacancyServiceBase(ABC):
    """
    Abstract class for the vacancy service
    """

    @abstractmethod
    async def get_vacancy(self, vacancy_id: UUID) -> VacancyInfo:
        """
        Gets the vacancy with the given id
        """
        pass

    @abstractmethod
    async def add_interview_results(self, room: Room) -> None:
        """
        Adds the interview results to the vacancy with the given id
        """
        pass
