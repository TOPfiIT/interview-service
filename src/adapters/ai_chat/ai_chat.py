import os
import asyncio
from typing import Any, AsyncGenerator, Coroutine
import dotenv
from openai import OpenAI

from src.adapters.ai_chat.ai_utils.misc import get_chat_completion_stream
from src.adapters.ai_chat.ai_utils.prompt_builders import build_chat_plan_prompt, build_chat_system_prompt, build_chat_welcome_user_prompt, build_response_prompts
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
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))

    async def create_chat(  #type: ignore
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> tuple[VacancyInfo, AsyncGenerator[str, None]]:  # type: ignore
        # 1) PLAN STEP (non-streaming)
        plan_prompt = build_chat_plan_prompt(vacancy_info)
        plan_completion = self.client.chat.completions.create(
            model="qwen3-32b-awq",
            messages=[{"role": "user", "content": plan_prompt}],
        )
        interview_plan = plan_completion.choices[0].message.content.strip()

        updated_vacancy = VacancyInfo(
            **{**vacancy_info.__dict__, "interview_plan": interview_plan}
        )

        # 2) WELCOME STEP (streaming)
        system_prompt = build_chat_system_prompt()
        user_prompt = build_chat_welcome_user_prompt(updated_vacancy, chat_history)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_stream = get_chat_completion_stream(
            self.client,
            "qwen3-32b-awq",
            messages,
            20000,
        )
        filtered_stream = filter_thinking_chunks(raw_stream)

        return updated_vacancy, filtered_stream


    async def create_response( #type: ignore
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        task: Task,
    ) -> AsyncGenerator[str, None]: # type: ignore
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
            "qwen3-32b-awq",
            messages,
            20000,
        )

        # IMPORTANT: we don't yield here; we return an async generator object
        return filter_thinking_chunks(raw_stream)

    
    async def create_task(self, vacancy_info: VacancyInfo, chat_history: list[Message]) -> Task:
        ...
        return Task(type=TaskType.THEORY, language=None, description="Напиши теорию для решения задачи")
    
    async def create_metrics(self, vacancy_info: VacancyInfo, chat_history: list[Message]) -> Metrics:
        ...
        return Metrics()

if __name__ == "__main__":
    async def main():
        ai_chat = AIChat()
        result = await ai_chat.create_chat(
            VacancyInfo(
                profession="Программист",
                position="Программист",
                requirements="Программист",
                questions="Программист",
                tasks=["Программист"],
                task_ides=["Программист"],
                interview_plan=""
            ),
            []
        )
        # Use the result to avoid "must be used" warning
        if result:
            pass
    
    asyncio.run(main())