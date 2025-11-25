from types import CoroutineType
from domain.room.room import Room, Solution, SolutionType, Interviewee
from domain.task.task import Task, TaskMetadata
from domain.vacancy.vacancy import VacancyInfo
from uuid import UUID, uuid4
from usecases.interfaces.interview_service import InterviewServiceBase
from typing import AsyncGenerator, Any
from usecases.interfaces.vacancy_service import VacancyServiceBase
from usecases.interfaces.ai_chat import AIChatBase
import asyncio


class InterviewService(InterviewServiceBase):
    """
    Interview service implementation
    """

    def __init__(
        self,
        vacancy_service: VacancyServiceBase,
        ai_chat: AIChatBase,
    ):
        self.vacancy_service = vacancy_service
        self.ai_chat = ai_chat
        self.room_sessions = {}

    async def create_room(self, vacancy_id: UUID, interviewee: Interviewee) -> Room:
        """
        Creates a new room for the given vacancy
        """

        vacancy_info = await self.vacancy_service.get_vacancy(vacancy_id)
        vacancy_info = await self.ai_chat.create_chat(
            vacancy_info=vacancy_info,
            chat_history=[],
        )

        room = Room(
            id=uuid4(),
            vacancy_info=vacancy_info,
            interviewee=interviewee,
            chat_history=[],
            tasks=[],
            solutions=[],
        )

        self.room_sessions[room.id] = room
        asyncio.create_task(self._stop_room_in(room.id))

        return room

    async def generate_welcome_message(  # type: ignore
        self, room_id: UUID
    ) -> AsyncGenerator[str, None]:
        """
        Generates a welcome message for the room with the given id
        """

        room = self.room_sessions[room_id]
        stream = self.ai_chat.generate_welcome_message(
            vacancy_info=room.vacancy_info,
            chat_history=room.chat_history,
        )
        async for chunk in stream:  # type: ignore
            yield chunk

    async def get_room(self, room_id: UUID) -> Room:
        """
        Gets the room with the given id
        """
        return self.room_sessions[room_id]

    async def send_solution(
        self, room_id: UUID, solution: Solution
    ) -> AsyncGenerator[str, None]:
        """
        Sends the solution to the room with the given id
        """

        ...

    async def get_current_task_metadata(self, room_id: UUID) -> TaskMetadata:
        """
        Gets the current task metadata for the room with the given id
        """

        room = self.room_sessions[room_id]
        return TaskMetadata(
            type=room.tasks[0].type,
            language=room.tasks[0].language,
        )

    async def send_question(
        self, room_id: UUID, question: str
    ) -> AsyncGenerator[str, None]: ...

    async def stop_room(self, room_id: UUID) -> None:
        pass

    async def _stop_room_in(self, room_id: UUID) -> None:
        room = self.room_sessions[room_id]
        await asyncio.sleep(room.vacancy_info.duration.total_seconds())
        await self.stop_room(room_id)
