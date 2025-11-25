from abc import ABC, abstractmethod

from domain.message.message import Message
from domain.metrics.metrics import Metrics
from domain.task.task import Task
from domain.vacancy.vacancy import VacancyInfo


class AIChatBase(ABC):
    """
    Abstract class for AI Chat
    """

    @abstractmethod
    async def create_chat(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> tuple[str, Task]:
        """
        Create AI chat

        :param vacancy_info: Vacancy information
        :param chat_history: Chat history
        :return: Welcome message and task
        """
        pass

    @abstractmethod
    async def create_response(
        self,
        VacancyInfo: VacancyInfo,
        chat_history: list[Message],
        task: Task,
    ) -> str:
        """
        Create AI response

        :param VacancyInfo: Vacancy information
        :param chat_history: Chat history
        :param task: Task
        :return: AI response
        """
        pass

    @abstractmethod
    async def create_task(
        self,
        VacancyInfo: VacancyInfo,
        chat_history: list[Message],
    ) -> Task:
        """
        Create AI task
        :param VacancyInfo: Vacancy information
        :param chat_history: Chat history
        :return: Task
        """
        pass

    @abstractmethod
    async def create_metrics(
        self,
        VacancyInfo: VacancyInfo,
        ChatHistory: list[Message],
    ) -> Metrics:
        """
        Create metrics
        :param VacancyInfo: Vacancy information
        :param ChatHistory: Chat history
        :return: Metrics
        """
        pass
