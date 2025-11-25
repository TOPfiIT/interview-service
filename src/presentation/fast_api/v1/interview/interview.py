from fastapi import APIRouter
from src.schemas.room import InterviewRoom, SolutionSentResponse, QuestionSentResponse
from src.schemas.interiewee import CreatedRoomRequest
from loguru import logger

router = APIRouter()


@router.post(
    "/room",
    response_model=InterviewRoom,
    description="Create a room",
    tags=["Interview"],
    summary="Create a room",
)
async def create_room(interviewee: CreatedRoomRequest) -> None:
    logger.info(f"Creating room for {interviewee.name}")
    pass


@router.get(
    "/room",
    response_model=InterviewRoom,
    description="Get a room",
    tags=["Interview"],
    summary="Get a room",
)
async def get_room() -> InterviewRoom:
    logger.info("Getting room")
    pass


@router.post(
    "/room/solution",
    description="Send a solution",
    response_model=SolutionSentResponse,
    tags=["Interview"],
    summary="Send a solution",
)
async def create_solution(solution: str) -> None:
    logger.info("Sending solution for")
    pass


@router.post(
    "/room/question",
    response_model=QuestionSentResponse,
    description="Send a question",
    tags=["Interview"],
    summary="Send a question",
)
async def create_question(question: str) -> None:
    logger.info("Sending question")
    pass


@router.delete(
    "/room",
    description="Stop a room",
    tags=["Interview"],
    summary="Stop a room",
)
async def stop_room() -> None:
    pass
