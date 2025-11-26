from src.domain.message.message import Message, TypeEnum
from src.domain.room.room import Room, Solution, SolutionType, Interviewee
from src.domain.task.task import Task, TaskMetadata
from src.domain.vacancy.vacancy import VacancyInfo
from uuid import UUID, uuid4
from src.usecases.interfaces.interview_service import InterviewServiceBase
from typing import AsyncGenerator, Any
from src.usecases.interfaces.vacancy_service import VacancyServiceBase
from src.usecases.interfaces.ai_chat import AIChatBase
import asyncio
from loguru import logger


class InterviewService(InterviewServiceBase):
    """
    Interview service implementation
    """

    _room_sessions: dict[UUID, Any] = {}
    _instance = None

    def __new__(cls, *args, **kwargs):
        logger.info(cls._instance)
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        vacancy_service: VacancyServiceBase,
        ai_chat: AIChatBase,
    ):
        self.vacancy_service = vacancy_service
        self.ai_chat = ai_chat

    async def create_room(self, vacancy_id: UUID, interviewee: Interviewee) -> Room:
        """
        Creates a new room for the given vacancy
        """

        logger.info(f"Creating room for vacancy {vacancy_id}")

        vacancy_info = await self.vacancy_service.get_vacancy(vacancy_id)
        vacancy_info = await self.ai_chat.create_chat(
            vacancy_info=vacancy_info,
            chat_history=[],
        )

        room = Room(
            id=uuid4(),
            vacancy_id=vacancy_id,
            vacancy_info=vacancy_info,
            interviewee=interviewee,
            chat_history=[],
            tasks=[],
            solutions=[],
        )

        InterviewService._room_sessions[room.id] = room
        logger.info(f"Created room {room.id}")

        asyncio.create_task(self._stop_room_in(room.id))

        return room

    async def generate_welcome_message(  # type: ignore
        self, room_id: UUID
    ) -> AsyncGenerator[str, None]:
        """
        Generates a welcome message for the room with the given id
        """

        logger.info(InterviewService._room_sessions)

        room = InterviewService._room_sessions[room_id]
        stream = await self.ai_chat.generate_welcome_message(
            vacancy_info=room.vacancy_info,
            chat_history=room.chat_history,
        )

        async for chunk in stream:  # type: ignore
            yield chunk

    async def get_room(self, room_id: UUID) -> Room:
        """
        Gets the room with the given id
        """
        return InterviewService._room_sessions[room_id]

    async def send_solution(
        self, room_id: UUID, solution: Solution
    ) -> AsyncGenerator[str, None]:
        """
        Sends the solution to the room with the given id
        """

        room = InterviewService._room_sessions[room_id]
        return room

    async def get_current_task_metadata(self, room_id: UUID) -> TaskMetadata:
        """
        Gets the current task metadata for the room with the given id
        """

        room = InterviewService._room_sessions[room_id]
        return TaskMetadata(
            type=room.tasks[0].type,
            language=room.tasks[0].language,
        )

    async def send_question(
        self, room_id: UUID, question: str
    ) -> AsyncGenerator[str, None]: ...

    async def stop_room(self, room_id: UUID) -> None:
        """
        Stops the room with the given id
        """

        logger.info(f"Stopping room {room_id}")

        room = InterviewService._room_sessions[room_id]
        del InterviewService._room_sessions[room_id]

        logger.info("Send metrics")

        await self.vacancy_service.add_interview_results(room)

        logger.info(f"Stopped room {room_id}")

    async def _stop_room_in(self, room_id: UUID) -> None:
        room = InterviewService._room_sessions[room_id]
        await asyncio.sleep(room.vacancy_info.duration.total_seconds())
        await self.stop_room(room_id)
