from src.usecases.interfaces.vacancy_service import VacancyServiceBase
from src.domain.vacancy.vacancy import VacancyInfo
from src.domain.room.room import (
    Room,
    Interviewee,
    SolutionType,
    Solution,
)
from src.domain.message.message import Message, RoleEnum, TypeEnum
from src.domain.task.task import TaskType, Task
from uuid import UUID
from src.domain.room.room import Room
from loguru import logger
import aiohttp
from datetime import timedelta
from typing import Any

import asyncio


class VacancyService(VacancyServiceBase):
    """
    Vacancy service implementation
    """

    def __init__(self, base_url: str):
        """
        Initializes the vacancy service
        """
        self.base_url = base_url.rstrip("/")

    async def get_vacancy(self, vacancy_id: UUID) -> VacancyInfo:
        """
        Gets the vacancy with the given id
        """

        logger.info(f"Getting vacancy {vacancy_id}")
        url = f"{self.base_url}/vacancies/{vacancy_id}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        json_response = await response.json()

                        return VacancyInfo(
                            profession=json_response["profession"],
                            position=json_response["position"],
                            requirements=json_response["requirements"],
                            questions="",
                            tasks=json_response["tasks"],
                            task_ides=json_response["task_ideas"],
                            duration=timedelta(minutes=json_response["duration"]),
                            interview_plan="",
                        )
                    else:
                        logger.error(
                            f"Failed to get vacancy {vacancy_id}, status {response.status}, reason {response.reason}"
                        )
                        raise Exception("Failed to get vacancy")

            except Exception as e:
                logger.error(f"Failed to get vacancy {vacancy_id}, error {e}")
                raise e

    async def add_interview_results(self, room: Room) -> None:
        """
        Adds the interview results to the vacancy with the given id
        """

        logger.info(f"Adding interview results to vacancy {room.vacancy_id}")
        url = f"{self.base_url}/vacancies/{str(room.vacancy_id)}/interview"

        data: dict[str, Any] = {
            "name": room.interviewee.name,
            "surname": room.interviewee.surname,
            "resume_link": room.interviewee.resume_link,
            "tasks": [task.description for task in room.tasks],
            "solitions": [solution.to_string() for solution in room.solutions],
            "chat_history": [message.to_string() for message in room.chat_history],
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info(
                            f"Added interview results to vacancy {room.vacancy_id}"
                        )
                    else:
                        logger.error(
                            f"Failed to add interview results to vacancy {room.vacancy_id}, status {response.status}, reason {response.reason}"
                        )
                        raise Exception("Failed to add interview results")

            except Exception as e:
                logger.error(
                    f"Failed to add interview results to vacancy {room.vacancy_id}, error {e}"
                )
                raise e
