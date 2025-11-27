from src.domain.message.message import Message, RoleEnum, TypeEnum
from src.domain.room.room import Room, Solution, SolutionType, Interviewee
from src.domain.task.task import Task, TaskMetadata
from src.domain.vacancy.vacancy import VacancyInfo
from uuid import UUID, uuid4
from src.usecases.interfaces.interview_service import InterviewServiceBase
from typing import AsyncGenerator, Any
from src.usecases.interfaces.vacancy_service import VacancyServiceBase
from src.usecases.interfaces.ai_chat import AIChatBase
import asyncio
from datetime import datetime, timedelta
from loguru import logger
from src.domain.metrics.metrics import MetricsBlock1

from datetime import datetime


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
            metrics=[],
            created_at=datetime.now(),
            last_task_time=datetime.now(),
            metrics_block1=MetricsBlock1(
                time_spent=timedelta(seconds=0),
                time_per_task=timedelta(seconds=0),
                answers_count=0,
                copy_paste_suspicion=0,
            ),
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

        message = Message(
            role=RoleEnum.AI,
            type=TypeEnum.RESPONSE,
            content="",
        )

        async for chunk in stream:  # type: ignore
            message.content += chunk
            yield chunk

        room.chat_history.append(message)

    async def get_room(self, room_id: UUID) -> Room:
        """
        Gets the room with the given id
        """
        return InterviewService._room_sessions[room_id]

    async def send_solution(self, room_id: UUID, solution: Solution):
        """
        Sends the solution to the room with the given id
        """

        logger.info(f"Sending solution {solution.content}")

        room: Room = InterviewService._room_sessions[room_id]
        room.solutions.append(solution)

        room.metrics_block1.copy_paste_suspicion += solution.count_suspicious_copy_paste

        room.chat_history.append(
            Message(
                role=RoleEnum.USER, type=TypeEnum.SOLUTION, content=solution.content
            )
        )

    async def get_solution_response(self, room_id: UUID) -> AsyncGenerator[str, None]:
        """
        Gets the solution response for the room with the given id
        """

        logger.info(f"Getting solution response for room {room_id}")

        room = InterviewService._room_sessions[room_id]
        stream, user_message, ai_message = await self.ai_chat.create_response(
            room.vacancy_info,
            room.chat_history,
            room.tasks[-1],
        )

        async for chunk in stream:  # type: ignore
            ai_message.content += chunk
            yield chunk

        room.chat_history.append(ai_message)

    async def new_task(self, room_id: UUID) -> AsyncGenerator[str, None]:
        """
        Creates a new task for the room with the given id
        """

        logger.info(f"Creating new task for room {room_id}")

        room = InterviewService._room_sessions[room_id]
        stream, task = await self.ai_chat.create_task(
            room.vacancy_info,
            room.chat_history,
        )

        async for chunk in stream:  # type: ignore
            task.description += chunk
            yield chunk

        room.chat_history.append(
            Message(role=RoleEnum.AI, type=TypeEnum.TASK, content=task.description)
        )
        room.vacancy_info.tasks.append(task)
        room.tasks.append(task)

    async def get_current_task_metadata(self, room_id: UUID) -> TaskMetadata:
        """
        Gets the current task metadata for the room with the given id
        """

        logger.info(f"Getting current task metadata for room {room_id}")

        room = InterviewService._room_sessions[room_id]
        return TaskMetadata(
            type=room.tasks[-1].type,
            language=room.tasks[-1].language,
        )

    async def send_question(self, room_id: UUID, question: str):
        """
        Creates a response for the room with the given id
        """

        logger.info(f"Sending question {question} for room {room_id}")

        room = InterviewService._room_sessions[room_id]
        room.chat_history.append(
            Message(
                role=RoleEnum.USER,
                type=TypeEnum.QUESTION,
                content=question,
            )
        )

    async def get_response(self, room_id: UUID) -> AsyncGenerator[str, None]:
        """
        Gets the response for the room with the given id
        """

        logger.info(f"Getting response for room {room_id}")

        room = InterviewService._room_sessions[room_id]

        stream, user_message, ai_message = await self.ai_chat.create_response(
            room.vacancy_info,
            room.chat_history,
            room.tasks[-1],
        )

        async for chunk in stream:  # type: ignore
            ai_message.content += chunk
            yield chunk

        room.chat_history[-1].type = user_message.type
        room.chat_history.append(ai_message)

    async def stop_room(self, room_id: UUID) -> None:
        """
        Stops the room with the given id
        """

        if room_id not in InterviewService._room_sessions:
            logger.info(f"Room {room_id} not found")
            return

        logger.info(f"Stopping room {room_id}")

        room: Room = InterviewService._room_sessions[room_id]
        del InterviewService._room_sessions[room_id]

        logger.info(f"Getting metrics for room {room_id}")

        user_message_len = len(
            [
                msg
                for msg in room.chat_history
                if msg.type == TypeEnum.ANSWER or msg.type == TypeEnum.SOLUTION
            ]
        )

        room.metrics_block1.time_spent = datetime.now() - room.created_at
        room.metrics_block1.time_per_task = (
            room.last_task_time - room.created_at
        ) / user_message_len
        room.metrics_block1.answers_count = user_message_len

        metrics1, metrics2, metrics3 = await self.ai_chat.create_metrics(
            room.vacancy_info,
            room.chat_history,
            room.metrics_block1,
        )

        room.metrics.append(metrics1.time_spent_str())
        room.metrics.append(metrics1.time_per_task_str())
        room.metrics.append(metrics1.answers_count_str())
        room.metrics.append(metrics1.copy_paste_suspicion_str())

        room.metrics.append(metrics2.summary_str())
        room.metrics.append(metrics2.clarity_score_str())
        room.metrics.append(metrics2.completeness_score_str())
        room.metrics.append(metrics2.feedback_response_str())
        room.metrics.append(metrics2.tech_fit_level_str())
        room.metrics.append(metrics2.tech_fit_comment_str())

        room.metrics.append(metrics3.strengths_str())
        room.metrics.append(metrics3.weaknesses_str())
        room.metrics.append(metrics3.cheating_summary_str())
        room.metrics.append(metrics3.seniority_guess_str())
        room.metrics.append(metrics3.recommendation_str())

        logger.info(metrics1.time_spent_str())
        logger.info(metrics1.time_per_task_str())
        logger.info(metrics1.answers_count_str())
        logger.info(metrics1.copy_paste_suspicion_str())

        logger.info(metrics2.summary_str())
        logger.info(metrics2.clarity_score_str())
        logger.info(metrics2.completeness_score_str())
        logger.info(metrics2.feedback_response_str())
        logger.info(metrics2.tech_fit_level_str())
        logger.info(metrics2.tech_fit_comment_str())

        logger.info(metrics3.strengths_str())
        logger.info(metrics3.weaknesses_str())
        logger.info(metrics3.cheating_summary_str())
        logger.info(metrics3.seniority_guess_str())
        logger.info(metrics3.recommendation_str())

        logger.info("Send metrics")

        await self.vacancy_service.add_interview_results(room)

        logger.info(f"Stopped room {room_id}")

    async def _stop_room_in(self, room_id: UUID) -> None:
        room = InterviewService._room_sessions[room_id]
        await asyncio.sleep(room.vacancy_info.duration.total_seconds())
        await self.stop_room(room_id)
