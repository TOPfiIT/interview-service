from typing import Any, Protocol
from src.domain.vacancy.vacancy import VacancyInfo
from src.domain.room.room import Room, Solution, Interviewee
from src.domain.task.task import Task, TaskMetadata
from uuid import UUID
from typing import AsyncGenerator


class InterviewServiceBase(Protocol):
    """
    Abstract class for the interview service
    """

    async def create_room(self, vacancy_id: UUID, interviewee: Interviewee) -> Room:
        """
        Creates a new room for the given vacancy
        """
        ...

    async def generate_welcome_message(
        self, room_id: UUID
    ) -> AsyncGenerator[str, None]:
        """
        Generates a welcome message for the room with the given id
        """
        ...

    async def get_room(self, room_id: UUID) -> Room:
        """
        Gets the room with the given id
        """
        ...

    async def send_solution(self, room_id: UUID, solution: Solution):
        """
        Sends the solution to the room with the given id
        """
        ...

    async def get_solution_response(self, room_id: UUID) -> AsyncGenerator[str, None]:
        """
        Gets the solution response for the room with the given id
        """
        ...

    async def get_current_task_metadata(self, room_id: UUID) -> TaskMetadata:
        """
        Gets the current task metadata for the room with the given id
        """
        ...

    async def new_task(self, room_id: UUID) -> AsyncGenerator[str, None]:
        """
        Creates a new task for the room with the given id
        """
        ...

    async def send_question(self, room_id: UUID, question: str):
        """
        Sends a question to the room with the given id
        """
        ...

    async def get_response(self, room_id: UUID) -> AsyncGenerator[str, None]:
        """
        Gets the response for the room with the given id
        """
        ...

    async def stop_room(self, room_id: UUID) -> None:
        """
        Stops the room with the given id
        """
        ...
