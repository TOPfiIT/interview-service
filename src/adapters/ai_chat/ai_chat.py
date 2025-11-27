import os
import asyncio
from typing import AsyncGenerator
import dotenv
from openai import AsyncOpenAI

from src.adapters.ai_chat.ai_utils.map_enum import (
    map_user_type,
    map_assistant_type,
    map_task_language,
    map_task_type,
)
from src.core.setting import settings
from src.adapters.ai_chat.ai_utils.misc import (
    get_chat_completion_stream,
    remove_thinking_part,
)
from src.adapters.ai_chat.ai_utils.prompt_builders import (
    build_chat_plan_prompt,
    build_chat_plan_system_prompt,
    build_chat_system_prompt,
    build_response_prompts,
    build_create_task_system_prompt,
    build_create_task_user_prompt,
    build_metrics_block2_system_prompt,
    build_metrics_block2_user_prompt,
    build_metrics_block3_system_prompt,
    build_metrics_block3_user_prompt,
    build_chat_welcome_user_prompt,
    build_test_suite_system_prompt,
    build_test_suite_user_prompt,
    build_check_solution_system_prompt,
    build_check_solution_user_prompt,
)
from src.adapters.ai_chat.ai_utils.streams import strip_think_and_ctrl, filter_thinking_chunks
from src.domain.message.message import Message, RoleEnum, TypeEnum
from src.domain.metrics.metrics import MetricsBlock1, MetricsBlock2, MetricsBlock3
from src.domain.task.task import Task
from src.domain.test.test import CodeTestSuite
from src.domain.vacancy.vacancy import VacancyInfo
from src.usecases.interfaces.ai_chat import AIChatBase
from src.adapters.ai_chat.ai_utils.json_parsers import (
    parse_metrics_block2,
    parse_metrics_block3,
    parse_test_suite_json,
)

dotenv.load_dotenv()


class AIChat(AIChatBase):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    async def create_chat(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> VacancyInfo:
        """
        Generate or update the INTERNAL interview plan for the vacancy
        using streaming, then collect it into a single string.
        """
        system_prompt = build_chat_plan_system_prompt()
        plan_prompt = build_chat_plan_prompt(vacancy_info)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": plan_prompt},
        ]

        # Stream the completion instead of a single blocking call
        raw_stream = await get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )

        chunks: list[str] = []
        async for chunk in raw_stream:
            if chunk:
                chunks.append(chunk)

        full_text = "".join(chunks)
        interview_plan = remove_thinking_part(full_text).strip()

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

        raw_stream = await get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )

        stream = await filter_thinking_chunks(raw_stream)
        return stream

    async def create_response(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        task: Task,
    ) -> tuple[AsyncGenerator[str, None], Message, Message]:
        system_prompt, user_prompt = build_response_prompts(
            vacancy_info=vacancy_info,
            chat_history=chat_history,
            task=task,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_stream = await get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )

        control, body_stream = await strip_think_and_ctrl(raw_stream)

        user_type = map_user_type(control.get("user_type"))
        assistant_type = map_assistant_type(control.get("assistant_type"))

        user_message = Message(
            role=RoleEnum.USER,
            type=user_type,
            content="",
        )

        ai_message = Message(
            role=RoleEnum.AI,
            type=assistant_type,
            content="",
        )

        return body_stream, user_message, ai_message

    async def create_task(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> tuple[AsyncGenerator[str, None], Task]:
        system_prompt = build_create_task_system_prompt()
        user_prompt = build_create_task_user_prompt(vacancy_info, chat_history)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_stream = await get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )

        control, body_stream = await strip_think_and_ctrl(raw_stream)

        task_type = map_task_type(control.get("task_type"))
        task_language = map_task_language(control.get("task_language"))

        task = Task(
            type=task_type,
            language=task_language,
            description="",
        )

        return body_stream, task

    async def create_metrics(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        metrics_block1: MetricsBlock1,
    ) -> tuple[MetricsBlock1, MetricsBlock2, MetricsBlock3]:
        system_prompt_b2 = build_metrics_block2_system_prompt()
        user_prompt_b2 = build_metrics_block2_user_prompt(
            vacancy_info=vacancy_info,
            chat_history=chat_history,
            metrics_block1=metrics_block1,
        )

        messages_b2 = [
            {"role": "system", "content": system_prompt_b2},
            {"role": "user", "content": user_prompt_b2},
        ]

        completion_b2 = await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=messages_b2,
        )
        raw_json_b2 = completion_b2.choices[0].message.content
        metrics_block2 = parse_metrics_block2(raw_json_b2)

        system_prompt_b3 = build_metrics_block3_system_prompt()
        user_prompt_b3 = build_metrics_block3_user_prompt(
            vacancy_info=vacancy_info,
            chat_history=chat_history,
            metrics_block1=metrics_block1,
            metrics_block2=metrics_block2,
        )

        messages_b3 = [
            {"role": "system", "content": system_prompt_b3},
            {"role": "user", "content": user_prompt_b3},
        ]

        completion_b3 = await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=messages_b3,
        )
        raw_json_b3 = completion_b3.choices[0].message.content
        metrics_block3 = parse_metrics_block3(raw_json_b3)

        return metrics_block1, metrics_block2, metrics_block3

    async def create_test_suite(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        task: Task,
    ) -> CodeTestSuite:
        total_tests = settings.tests_per_task

        system_prompt = build_test_suite_system_prompt()
        user_prompt = build_test_suite_user_prompt(
            vacancy_info=vacancy_info,
            chat_history=chat_history,
            task=task,
            total_tests=total_tests,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_stream = await get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )

        chunks: list[str] = []
        async for chunk in raw_stream:
            if chunk:
                chunks.append(chunk)

        response_text = remove_thinking_part("".join(chunks))

        suite = parse_test_suite_json(
            response_text,
            task_id=getattr(task, "id", "task_without_id"),
        )

        return suite

    async def check_solution(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        task: Task,
        solution: str,
        tests: CodeTestSuite,
    ) -> tuple[AsyncGenerator[str, None], Message]:
        system_prompt = build_check_solution_system_prompt()
        user_prompt = build_check_solution_user_prompt(
            vacancy_info=vacancy_info,
            chat_history=chat_history,
            task=task,
            solution=solution,
            tests=tests,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_stream = await get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )

        stream = await filter_thinking_chunks(raw_stream)

        ai_message = Message(
            role=RoleEnum.AI,
            type=TypeEnum.CHECK_SOLUTION,
            content="",
        )

        return stream, ai_message
