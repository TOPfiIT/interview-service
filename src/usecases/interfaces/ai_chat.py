from typing import AsyncGenerator, Protocol
from src.domain.message.message import Message
from src.domain.metrics.metrics import Metrics
from src.domain.task.task import Task
from src.domain.vacancy.vacancy import VacancyInfo


class AIChatBase(Protocol):
    """
    Abstract class for AI Chat
    """

    async def create_chat(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> VacancyInfo:
        """
        Create AI chat

        :param vacancy_info: Vacancy information
        :param chat_history: Chat history
        :return: Updated vacancy information and generator of response chunks
        """
        ...

    async def generate_welcome_message(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> AsyncGenerator[str, None]:
        """
        Generate welcome message
        """
        ...

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
        ...

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
        ...

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
        ...
