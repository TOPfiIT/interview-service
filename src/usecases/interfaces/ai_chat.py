from typing import AsyncGenerator, Protocol
from src.domain.message.message import Message
from src.domain.metrics.metrics import MetricsBlock1, MetricsBlock2, MetricsBlock3
from src.domain.task.task import Task
from src.domain.test.test import CodeTestSuite
from src.domain.vacancy.vacancy import VacancyInfo


class AIChatBase(Protocol):
    """
    Interface for LLM-backed interview chat, task generation and metrics.
    """

    async def create_chat(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> VacancyInfo:
        """
        Generate or update the INTERNAL interview plan for the vacancy.

        :param vacancy_info: Vacancy information
        :param chat_history: Chat history (may be empty for the first call)
        :return: Updated VacancyInfo with interview_plan filled/updated
        """
        ...

    async def generate_welcome_message(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> AsyncGenerator[str, None]:
        """
        Stream the first welcome message for the candidate.

        :param vacancy_info: Vacancy information (with interview_plan already set)
        :param chat_history: Current chat history
        :return: Async generator of response chunks (text only, <think> stripped)
        """
        ...

    async def create_response(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        task: Task,
    ) -> tuple[AsyncGenerator[str, None], Message, Message]:
        """
        Stream the next interviewer reply and classify message types via <ctrl>.

        How to use:
        - stream all the text from the body_stream
        - pass it back into AI message content
        - Delete previous user message from chat history 
        - Add updated user message to chat history with old content and new type
        - Add updated AI message to chat history with the streamed text
        
        :param vacancy_info: Vacancy information
        :param chat_history: Full chat history up to the latest user message
        :param task: Current task context
        :return:
            - async generator of visible reply chunks (body_stream)
            - Message representing classified user message (type from control JSON)
            - Message representing classified AI message (type from control JSON)
        """
        ...

    async def create_task(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> tuple[AsyncGenerator[str, None], Task]:
        """
        Stream the next task description and derive its metadata from <ctrl>.

        How to use:
        - stream all the text from the body_stream
        - pass it back into Task object description
        - add to the list of tasks in the vacancy info

        :param vacancy_info: Vacancy information (with interview_plan)
        :param chat_history: Full chat history so far
        :return:
            - async generator of task text chunks
            - Task object with type/language from control JSON, empty description
        """
        ...

    async def create_metrics(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        metrics_block1: MetricsBlock1,
    ) -> tuple[MetricsBlock1, MetricsBlock2, MetricsBlock3]:
        """
        Compute higher-level interview metrics based on logs and basic numeric data.

        :param vacancy_info: Vacancy information
        :param chat_history: Full chat history (interviewer + candidate)
        :param metrics_block1: Raw numeric metrics from the platform (no LLM)
        :return:
            - MetricsBlock1 (echoed)
            - MetricsBlock2 (LLM summary + scores + tech fit)
            - MetricsBlock3 (LLM strengths/weaknesses + final verdict)
        """
        ...
    
    async def create_test_suite(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        task: Task,
    ) -> CodeTestSuite:
        """
        Create a test suite for a coding task.
        """
        ...

    async def check_solution(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        task: Task,
        solution: str,
        tests: CodeTestSuite
    ) -> tuple[AsyncGenerator[str, None], Message]:
        """
        Check the solution for a coding task.
        """
        ...