from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import StreamingResponse
from src.domain.room.room import Interviewee, Solution, SolutionType
from src.schemas.room import (
    InterviewRoom,
    QuestionSentResponse,
    SendSolutionRequest,
    Task,
    VacancyRoom,
    Message,
)
from src.schemas.interiewee import CreatedRoomRequest
from src.usecases.interfaces.interview_service import InterviewServiceBase
from loguru import logger
from uuid import UUID
from typing import Annotated
import json

router = APIRouter()


@router.post(
    "/room",
    response_model=InterviewRoom,
    description="Create a room",
    tags=["Interview"],
    summary="Create a room",
)
async def create_room(
    interviewee: CreatedRoomRequest,
    response: Response,
    interview_service: InterviewServiceBase = Depends(),
) -> InterviewRoom:
    logger.info(f"Creating room for {interviewee.name}")
    vacancy_id: UUID = UUID(interviewee.vacancy_id)

    room = await interview_service.create_room(
        vacancy_id,
        Interviewee(
            interviewee.name,
            interviewee.surname,
            interviewee.resume_link,
        ),
    )

    response.set_cookie(
        key="room_id",
        value=str(room.id),
        max_age=int(room.vacancy_info.duration.total_seconds()),
    )

    logger.info(f"Room plan: {room.vacancy_info.interview_plan}")

    tasks: list[Task] = []
    for task in room.tasks:
        tasks.append(
            Task(
                type=str(task.type),
                condition=str(task.description),
                language=task.language or "",
            )
        )

    messages: list[Message] = []
    for message in room.chat_history:
        messages.append(
            Message(
                sender=str(message.role),
                content=message.content,
            )
        )

    interview_room = InterviewRoom(
        vacancy=VacancyRoom(
            profession=room.vacancy_info.profession,
            position=room.vacancy_info.position,
        ),
        tasks=tasks,
        chat=messages,
    )

    return interview_room


@router.get(
    "/room/welcome",
    description="Get a welcome message",
    tags=["Interview"],
    summary="Get a welcome message",
)
async def get_welcome_message(
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
):
    logger.info("Getting welcome message")

    room_id: UUID = UUID(request.cookies.get("room_id"))

    async def sse_generator():
        async for chunk in interview_service.generate_welcome_message(room_id):
            yield chunk.encode("utf-8")

    return StreamingResponse(
        sse_generator(),
        media_type="text/plain",
    )


@router.get(
    "/room/welcome/sse",
    description="Get a welcome message via SSE",
    tags=["Interview"],
    summary="Get a welcome message via SSE",
)
async def get_welcome_message_sse(
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
):
    logger.info("Getting welcome message via SSE")

    room_id: UUID = UUID(request.cookies.get("room_id"))

    async def sse_generator():
        try:
            # Отправляем начальное событие
            yield "data: {}\n\n".format(
                json.dumps(
                    {
                        "type": "start",
                        "message": "Starting welcome message generation",
                        "room_id": str(room_id),
                    },
                    ensure_ascii=False,
                )
            )

            # Генерируем welcome message и отправляем как SSE
            async for chunk in interview_service.generate_welcome_message(room_id):
                yield "data: {}\n\n".format(
                    json.dumps(
                        {
                            "type": "message_chunk",
                            "content": chunk,
                            "timestamp": "2024-01-01T00:00:00Z",  # добавьте реальный timestamp
                        },
                        ensure_ascii=False,
                    )
                )

            # Отправляем событие завершения
            yield "data: {}\n\n".format(
                json.dumps(
                    {"type": "complete", "message": "Welcome message completed"},
                    ensure_ascii=False,
                )
            )

        except Exception as e:
            # Отправляем событие ошибки
            yield "data: {}\n\n".format(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"Error generating welcome message: {str(e)}",
                    },
                    ensure_ascii=False,
                )
            )

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no",  # Важно для nginx
        },
    )


@router.get(
    "/room",
    response_model=InterviewRoom,
    description="Get a room",
    tags=["Interview"],
    summary="Get a room",
)
async def get_room(
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
) -> InterviewRoom:
    logger.info("Getting room")

    room_id: UUID = UUID(request.cookies.get("room_id"))

    room = await interview_service.get_room(room_id)

    tasks: list[Task] = []
    for task in room.tasks:
        tasks.append(
            Task(
                type=str(task.type),
                condition=str(task.description),
                language=task.language or "",
            )
        )

    messages: list[Message] = []
    for message in room.chat_history:
        messages.append(
            Message(
                sender=str(message.role),
                content=message.content,
            )
        )

    interview_room = InterviewRoom(
        vacancy=VacancyRoom(
            profession=room.vacancy_info.profession,
            position=room.vacancy_info.position,
        ),
        tasks=tasks,
        chat=messages,
    )

    return interview_room


@router.post(
    "/room/solution",
    description="Send a solution",
    tags=["Interview"],
    summary="Send a solution",
)
async def send_solution(
    request: Request,
    solution_request: SendSolutionRequest,
    interview_service: InterviewServiceBase = Depends(),
):
    logger.info("Sending solution")

    room_id: UUID = UUID(request.cookies.get("room_id"))

    sol = Solution(
        content=solution_request.solution,
        language=solution_request.language,
        solution_type=SolutionType.CODE
        if solution_request.solution_type == "code"
        else SolutionType.TEXT,
    )
    await interview_service.send_solution(room_id, sol)


@router.get(
    "/room/solution/response/sse",
    description="Get a solution response via SSE",
    tags=["Interview"],
    summary="Get a solution response via SSE",
)
async def get_solution_response_sse(
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
) -> StreamingResponse:
    logger.info("Getting solution response via SSE")

    room_id: UUID = UUID(request.cookies.get("room_id"))

    async def sse_generator():
        try:
            # Отправляем начальное событие
            yield "data: {}\n\n".format(
                json.dumps(
                    {
                        "type": "start",
                        "message": "Starting solution response generation",
                        "room_id": str(room_id),
                    },
                    ensure_ascii=False,
                )
            )

            # Генерируем solution response и отправляем как SSE
            async for chunk in interview_service.get_solution_response(room_id):
                yield "data: {}\n\n".format(
                    json.dumps(
                        {
                            "type": "message_chunk",
                            "content": chunk,
                            "timestamp": "2024-01-01T00:00:00Z",  # добавьте реальный timestamp
                        },
                        ensure_ascii=False,
                    )
                )

            # Отправляем событие завершения
            yield "data: {}\n\n".format(
                json.dumps(
                    {"type": "complete", "message": "Solution response completed"},
                    ensure_ascii=False,
                )
            )

        except Exception as e:
            # Отправляем событие ошибки
            yield "data: {}\n\n".format(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"Error generating solution response: {str(e)}",
                    },
                    ensure_ascii=False,
                )
            )

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no",  # Важно для nginx
        },
    )


@router.post(
    "/room/question",
    response_model=QuestionSentResponse,
    description="Send a question",
    tags=["Interview"],
    summary="Send a question",
)
async def create_question(question: str) -> None:
    logger.info("Sending question")
    ...


@router.delete(
    "/room",
    description="Stop a room",
    tags=["Interview"],
    summary="Stop a room",
)
async def stop_room() -> None: ...
