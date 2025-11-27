from fastapi import APIRouter, Depends, Response, Request, HTTPException
from fastapi.responses import StreamingResponse
from src.domain.room.room import Interviewee, Solution, SolutionType
from src.domain.test.test import CodeTestCase
from src.schemas.room import (
    InterviewRoom,
    QuestionSentResponse,
    SendSolutionRequest,
    Task,
    VacancyRoom,
    Message,
    TaskMetadata,
    QuestionSendRequest,
    CodeRunResponse,
    RunCodeRequest,
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
    try:
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    try:
        logger.info("Getting welcome message")

        room_id: UUID = UUID(request.cookies.get("room_id"))

        async def sse_generator():
            async for chunk in interview_service.generate_welcome_message(room_id):
                yield chunk.encode("utf-8")

        return StreamingResponse(
            sse_generator(),
            media_type="text/plain",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    try:
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
                "X-Accel-Buffering": "no",  # Важно для nginx
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    try:
        logger.info("Sending solution")

        room_id: UUID = UUID(request.cookies.get("room_id"))

        sol = Solution(
            content=solution_request.solution,
            language=solution_request.language,
            solution_type=SolutionType.CODE
            if solution_request.solution_type == "code"
            else SolutionType.TEXT,
            count_suspicious_copy_paste=solution_request.copy_paste_count,
        )
        await interview_service.send_solution(room_id, sol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/room/solution/response",
    description="Get a solution response",
    tags=["Interview"],
    summary="Get a solution response",
)
async def get_solution_response(
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
) -> StreamingResponse:
    try:
        logger.info("Getting solution response")

        room_id: UUID = UUID(request.cookies.get("room_id"))

        async def generator():
            async for chunk in interview_service.get_solution_response(room_id):
                yield chunk.encode("utf-8")

        return StreamingResponse(
            generator(),
            media_type="text/plain",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    try:
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
                "X-Accel-Buffering": "no",  # Важно для nginx
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/room/question",
    description="Send a question",
    tags=["Interview"],
    summary="Send a question",
)
async def create_question(
    question: QuestionSendRequest,
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
):
    try:
        logger.info("Sending question")

        room_id: UUID = UUID(request.cookies.get("room_id"))

        await interview_service.send_question(room_id, question.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/room/question/response",
    description="Get a question response",
    tags=["Interview"],
    summary="Get a question response",
)
async def get_question_response(
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
) -> StreamingResponse:
    try:
        logger.info("Getting question response")

        room_id: UUID = UUID(request.cookies.get("room_id"))

        async def generator():
            async for chunk in interview_service.get_response(room_id):
                yield chunk.encode("utf-8")

        return StreamingResponse(
            generator(),
            media_type="text/plain",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/room/question/response/sse",
    description="Get a question response via SSE",
    tags=["Interview"],
    summary="Get a question response via SSE",
)
async def get_question_response_sse(
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
) -> StreamingResponse:
    try:
        logger.info("Getting question response via SSE")

        room_id: UUID = UUID(request.cookies.get("room_id"))

        async def sse_generator():
            try:
                # Отправляем начальное событие
                yield "data: {}\n\n".format(
                    json.dumps(
                        {
                            "type": "start",
                            "message": "Starting question response generation",
                            "room_id": str(room_id),
                        },
                        ensure_ascii=False,
                    )
                )

                # Генерируем question response и отправляем как SSE
                async for chunk in interview_service.get_response(room_id):
                    yield "data: {}\n\n".format(
                        json.dumps(
                            {
                                "type": "message_chunk",
                                "content": chunk,
                                "timestamp": "2024-01-01T00:00:00Z",
                            },
                            ensure_ascii=False,
                        )
                    )

                # Отправляем событие завершения
                yield "data: {}\n\n".format(
                    json.dumps(
                        {"type": "complete", "message": "Question response completed"},
                        ensure_ascii=False,
                    )
                )

            except Exception as e:
                # Отправляем событие ошибки
                yield "data: {}\n\n".format(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"Error generating question response: {str(e)}",
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
                "X-Accel-Buffering": "no",  # Важно для nginx
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/room/task",
    description="Get a task",
    tags=["Interview"],
    summary="Get a task",
)
async def get_task(
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
) -> StreamingResponse:
    try:
        logger.info("Getting task")

        room_id: UUID = UUID(request.cookies.get("room_id"))

        async def generator():
            async for chunk in interview_service.new_task(room_id):
                yield chunk.encode("utf-8")

        return StreamingResponse(
            generator(),
            media_type="text/plain",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/room/task/sse",
    description="Get a task via SSE",
    tags=["Interview"],
    summary="Get a task via SSE",
)
async def get_task_sse(
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
) -> StreamingResponse:
    try:
        logger.info("Getting task via SSE")

        room_id: UUID = UUID(request.cookies.get("room_id"))

        async def sse_generator():
            try:
                # Отправляем начальное событие
                yield "data: {}\n\n".format(
                    json.dumps(
                        {
                            "type": "start",
                            "message": "Starting task generation",
                            "room_id": str(room_id),
                        },
                        ensure_ascii=False,
                    )
                )

                # Генерируем task и отправляем как SSE
                async for chunk in interview_service.new_tasks(room_id):
                    yield "data: {}\n\n".format(
                        json.dumps(
                            {
                                "type": "message_chunk",
                                "content": chunk,
                                "timestamp": "2024-01-01T00:00:00Z",
                            },
                            ensure_ascii=False,
                        )
                    )

                # Отправляем событие завершения
                yield "data: {}\n\n".format(
                    json.dumps(
                        {"type": "complete", "message": "Task completed"},
                        ensure_ascii=False,
                    )
                )

            except Exception as e:
                # Отправляем событие ошибки
                yield "data: {}\n\n".format(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"Error generating task: {str(e)}",
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
                "X-Accel-Buffering": "no",  # Важно для nginx
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/room/current-task-metadata",
    description="Get current task metadata",
    tags=["Interview"],
    summary="Get current task metadata",
)
async def get_current_task_metadata(
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
) -> TaskMetadata:
    try:
        logger.info("Getting current task metadata")

        room_id: UUID = UUID(request.cookies.get("room_id"))

        task_metadata = await interview_service.get_current_task_metadata(room_id)

        return TaskMetadata(
            type=task_metadata.type,
            language=str(task_metadata.language),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/room/run",
    description="Run code",
    tags=["Interview"],
    summary="Run code",
    response_model=list[CodeRunResponse],
)
async def run_code(
    request: Request,
    run_request: RunCodeRequest,
    interview_service: InterviewServiceBase = Depends(),
) -> list[CodeRunResponse]:
    try:
        logger.info("Running code")
        room_id: UUID = UUID(request.cookies.get("room_id"))
        results: list[CodeTestCase] = await interview_service.run_code(
            room_id, run_request.language, run_request.code
        )

        return [
            CodeRunResponse(
                input_data=result.input_data,
                expected_output=result.expected_output,
                correct=result.correct or False,
                status=result.status,
                exception=result.exception,
                stdin=result.stdin,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=result.execution_time,
            )
            for result in results
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/room",
    description="Stop a room",
    tags=["Interview"],
    summary="Stop a room",
)
async def stop_room(
    request: Request,
    interview_service: InterviewServiceBase = Depends(),
):
    try:
        logger.info("Stopping room")

        room_id: UUID = UUID(request.cookies.get("room_id"))

        await interview_service.stop_room(room_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
