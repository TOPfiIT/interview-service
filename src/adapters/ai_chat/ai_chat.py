import os
import asyncio
from typing import Any, AsyncGenerator, Coroutine
import dotenv
from openai import OpenAI

from src.core.setting import settings
from src.adapters.ai_chat.ai_utils.misc import get_chat_completion_stream, remove_thinking_part
from src.adapters.ai_chat.ai_utils.prompt_builders import build_chat_plan_prompt, build_chat_system_prompt, build_chat_welcome_user_prompt, build_response_prompts, build_stream_task_prompt
from src.adapters.ai_chat.ai_utils.streams import filter_thinking_chunks
from src.domain.message.message import Message
from src.domain.metrics.metrics import Metrics
from src.domain.task.task import Task, TaskType
from src.domain.vacancy.vacancy import VacancyInfo
from src.usecases.interfaces.ai_chat import AIChatBase


dotenv.load_dotenv()


class AIChat(AIChatBase):
    """
    AI Chat implementation
    """
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    async def create_chat( 
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> tuple[VacancyInfo, AsyncGenerator[str, None]]:  
        # 1) PLAN STEP (non-streaming)
        plan_prompt = build_chat_plan_prompt(vacancy_info)
        plan_completion = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": plan_prompt}],
        )
        interview_plan = plan_completion.choices[0].message.content.strip()
        interview_plan = remove_thinking_part(interview_plan)

        updated_vacancy = vacancy_info
        updated_vacancy.interview_plan = interview_plan

        return updated_vacancy

    async def generate_welcome_message(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> AsyncGenerator[str, None]:
        
        system_prompt = build_chat_system_prompt()
        user_prompt = build_chat_welcome_user_prompt(vacancy_info, chat_history)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_stream = get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )
        filtered_stream = filter_thinking_chunks(raw_stream)
        return filtered_stream

    async def create_response(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        task: Task,
    ) -> AsyncGenerator[str, None]: 
        system_prompt, user_prompt = build_response_prompts(
            vacancy_info=vacancy_info,
            chat_history=chat_history,
            task=task,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_stream = get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )

        # IMPORTANT: we don't yield here; we return an async generator object
        return filter_thinking_chunks(raw_stream)

    async def create_task(self, vacancy_info: VacancyInfo, chat_history: list[Message]) -> Task:
        ...
        return Task(type=TaskType.THEORY, language=None, description="Напиши теорию для решения задачи")
    
    async def stream_task(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> AsyncGenerator[str, None]:
        """
        Stream the next task description selected according to the interview_plan.
        The output is just text, including [coding]/[theory] and optionally language.
        """

        prompt = build_stream_task_prompt(vacancy_info, chat_history)

        messages = [
            {"role": "user", "content": prompt},
        ]

        raw_stream = get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )

        # Reuse the same <think> filtering you already use elsewhere
        return filter_thinking_chunks(raw_stream)

    async def create_metrics(self, vacancy_info: VacancyInfo, chat_history: list[Message]) -> Metrics:
        ...
        return Metrics()

if __name__ == "__main__":
    ...